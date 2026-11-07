"""Fresh D1 stage. Draft configurations cannot launch either backend."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from .config import Config
from .runner import build_command
from .prompts import relay_prompt
from .integrity import require_ready,ensure_published,digest,git
from .reliability import AttemptRunner,Control,stamp,write_new,replace_state
from .d1v2_score import PAIRS,task_summary
from .claude_stream import parse_claude,version_number,verify_project_state
from .exposure import audit,ADAPTERS
from .runtime_checkpoint import checkpoint


def calls(task,files,group):
    inputs=[('',n) for n in range(1,4)] if group=='free' else [(pair,n) for pair in PAIRS for n in (1,2)]
    return [{'name':f"{task['id']}-{group}-{pair or 'none'}-r{n}",'task_id':task['id'],
             'group':group,'incoming_pair':pair or None,'replicate':n,
             'prompt':relay_prompt([f'handoff_refs/{c}.txt' for c in pair],task,files)} for pair,n in inputs]


def command(config,workspace,schema):
    require_ready(config)
    if config['backend']=='codex':
        return build_command(Config(Path(workspace),Path('.'),model=config['model'],reasoning_effort=config['effort'],stub=False,cli=config['cli']),Path(schema))
    if config['backend']=='claude':
        # No guessed Claude flags: the reviewed configuration supplies the complete argv.
        schema_json=json.dumps(json.loads(Path(schema).read_text()),separators=(',',':'),ensure_ascii=False)
        args=[s.replace('{workspace}',str(Path(workspace).resolve())).replace('{schema}',str(Path(schema).resolve())).replace('{schema_json}',schema_json) for s in config['argv']]
        if '-p' not in args:raise RuntimeError('Claude configuration must use -p')
        return args
    raise ValueError('unknown backend')


def parse_stream(stdout,method):
    events=[];answer=None
    for line in stdout.splitlines():
        try:event=json.loads(line)
        except ValueError:continue
        if isinstance(event,dict):events.append(event)
    if method=='codex_jsonl':
        for event in events:
            item=event.get('item',{})
            if not isinstance(item,dict):continue
            if event.get('type')=='item.completed' and item.get('type')=='agent_message':
                try:answer=json.loads(item.get('text',''))
                except ValueError:answer=None
    elif method=='single_json_answer':
        try:answer=json.loads(stdout)
        except ValueError:answer=None
    else:raise RuntimeError('unreviewed output method')
    return answer,events


class Backend:
    def __init__(self,config,workspace,schema,publication_check):
        require_ready(config);self.config=config;self.workspace=Path(workspace).resolve()
        self.argv=command(config,workspace,schema);self.publication_check=publication_check
    def preflight(self):
        version=subprocess.check_output([self.config['cli'],'--version'],text=True,timeout=15,env={**os.environ,**self.config.get('env',{})}).strip()
        normalized=version_number(version) if self.config['backend']=='claude' else version
        self.version_raw=version
        if normalized!=self.config['version']:raise RuntimeError('CLI version mismatch: '+version)
        if self.config['backend']=='claude' and not self.config.get('output_method_reviewed'):raise RuntimeError('Claude output method not reviewed')
    def __call__(self,name,prompt,control,reserve=None):
        self.publication_check()
        try:
            if self.config['backend']=='codex':self.preflight()
            if self.config['backend']=='claude':
                verify_project_state(self.workspace,self.config.get('state_root') or self.config.get('env',{}).get('CLAUDE_CONFIG_DIR') or os.environ.get('CLAUDE_CONFIG_DIR'))
        except (RuntimeError,OSError,subprocess.SubprocessError) as error:
            if reserve is not None:reserve()
            return {'exit_code':None,'answer':None,'configuration_fault':[str(error)],'cli_version_raw':getattr(self,'version_raw',None)}
        while True:
            stop=control.before_launch()
            if stop:return {'administrative_status':stop,'call':name}
            with control.lock:
                if control.blocked or control.pause_until:continue
                # Check directly before process creation, after all preflight/publication I/O.
                if control.clock.now()>=control.latest_launch:return {'administrative_status':'stopped_by_cutoff','call':name}
                if reserve is not None:reserve()
                if control.clock.now()>=control.latest_launch:return {'administrative_status':'stopped_by_cutoff','call':name}
                started=control.clock.now();tick=time.monotonic()
                try:
                    process=subprocess.Popen(self.argv,cwd=self.workspace,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,env={**os.environ,**self.config.get('env',{})})
                except OSError as error:
                    return {'exit_code':None,'answer':None,'error':str(error),'started_at_utc':stamp(started),'process_launched':False}
                break
        timeout=False
        try:stdout,stderr=process.communicate(prompt.encode(),timeout=180)
        except subprocess.TimeoutExpired:
            timeout=True
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            stdout,stderr=process.communicate()
        text=stdout.decode('utf-8',errors='replace')
        if self.config['backend']=='claude':parsed=parse_claude(text,self.workspace,self.config,process.returncode)
        else:
            answer,events=parse_stream(text,self.config['output_method'])
            parsed={'answer':answer,'events':events,'cli_version':self.config['version'],'cli_version_raw':self.version_raw}
        record={'exit_code':process.returncode,**parsed,
                'stdout':stdout.decode('utf-8',errors='replace'),'stderr':stderr.decode('utf-8',errors='replace'),
                'started_at_utc':stamp(started),'ended_at_utc':stamp(control.clock.now()),
                'wall_seconds':time.monotonic()-tick,'timed_out':timeout}
        sources={a:(Path(self.workspace)/'dogwhistle'/a).read_text() for a in ADAPTERS if (Path(self.workspace)/'dogwhistle'/a).is_file()}
        record['exposure_audit']=audit(record,self.workspace,sources)
        return record


def run_stage(tasks,files,attempts,workers=4):
    if not 1<=workers<=4:raise ValueError('workers must be 1 to 4')
    summaries={};results=[];missing=0
    for task in tasks:
        if task['role']=='reserve' and missing<=0:continue
        if task['role']=='reserve' and hasattr(attempts.control,'latest_launch') and attempts.control.clock.now()>=attempts.control.latest_launch:break
        rows=[]
        if hasattr(attempts,'folder'):
            path=attempts.folder/'plan.json'
            plan=json.loads(path.read_text()) if path.exists() else {'calls':{}}
            for group in ['free','incoming']:
                for spec in calls(task,files,group):
                    plan['calls'][spec['name']]={k:v for k,v in spec.items() if k!='prompt'} | {'prompt_sha256':hashlib.sha256(spec['prompt'].encode()).hexdigest()}
            replace_state(path,plan)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for group in ['free','incoming']:
                specs=calls(task,files,group)
                # Bounded batches: no outstanding queue across a pause or task boundary.
                for start in range(0,len(specs),workers):
                    batch=specs[start:start+workers]
                    def run(spec):
                        row=attempts.run(spec['name'],spec['prompt'])
                        return dict(row,**{k:spec[k] for k in ['task_id','group','incoming_pair','replicate']})
                    rows.extend(pool.map(run,batch))
                    if attempts.control.blocked:break
                if attempts.control.blocked:break
                # All three free-choice calls finish before any incoming pair starts.
        summary=task_summary(task,rows);summaries[task['id']]=summary;results.extend(rows)
        if task['role']=='primary' and not summary['valid']:missing+=1
        elif task['role']=='reserve' and summary['valid']:missing-=1
        if attempts.control.blocked:break
    if hasattr(attempts,'folder') and attempts.control.blocked and attempts.control.blocked.startswith('manual:'):
        record_drained_pause(attempts.folder,attempts.control)
    return {'tasks':summaries,'calls':results}


def record_drained_pause(folder,control):
    plan=json.loads((folder/'plan.json').read_text())['calls']
    finished=sorted(p.stem for p in (folder/'traces').glob('*.json'))
    left=sorted(set(plan)-set(finished))
    events=json.loads((folder/'pauses.json').read_text())
    for event in reversed(events):
        if event['event'] in ('resume_authorized_by_rick','resume'):break
        if event['event']=='manual_pause':
            event.update(calls_finished=finished,calls_left=left,drained_at_utc=stamp(control.clock.now()))
    replace_state(folder/'pauses.json',events)


def finalize_cutoff(folder,control):
    if control.clock.now()<control.latest_launch:raise RuntimeError('last-launch deadline has not arrived')
    plan=json.loads((folder/'plan.json').read_text())['calls']
    for name,metadata in plan.items():
        if (folder/'traces'/f'{name}.json').exists() or (folder/'stopped'/f'{name}.json').exists() or list((folder/'configuration_fault').glob(f'{name}-attempt*.json')):continue
        attempts=len(list((folder/'attempt_state'/name).glob('attempt*.json')))
        write_new(folder/'stopped'/f'{name}.json',dict(metadata,administrative_status='stopped_by_cutoff',attempts=attempts,at_utc=stamp(control.clock.now())))


def verify_workspace(workspace,data):
    workspace=Path(workspace).resolve()
    if set(p.resolve() for p in workspace.parent.iterdir())!={workspace.resolve()}:
        raise RuntimeError('workspace parent must contain only the workspace')
    if git(workspace,'rev-parse','HEAD')!=data['source_commit'] or git(workspace,'status','--porcelain'):
        raise RuntimeError('task workspace is not clean at the registered commit')
    for path,expected in data['candidate_sha256'].items():
        if digest(workspace/path)!=expected:raise RuntimeError('candidate source bytes changed')
    for letter in 'ABCD':
        if digest(workspace/'handoff_refs'/f'{letter}.txt')!=data['ref_sha256']:raise RuntimeError('reference bytes changed')


def main(argv=None):
    p=argparse.ArgumentParser()
    for name in ['repo','branch','registration','seal','seal-digest','backend-config','workspace','run-dir']:p.add_argument('--'+name,required=True)
    p.add_argument('--backend',choices=['codex','claude'],required=True)
    p.add_argument('--resume-rick',action='store_true',help='Use only after Rick explicitly authorizes this resume')
    p.add_argument('--finalize-cutoff',action='store_true',help='Record unlaunched calls after the last-launch deadline, without starting models')
    args=p.parse_args(argv);repo=Path(args.repo).resolve()
    registration=json.loads(Path(args.registration).read_text());require_ready(registration)
    config=json.loads(Path(args.backend_config).read_text());require_ready(config)
    if config['backend']!=args.backend:raise RuntimeError('backend/config mismatch')
    check=lambda:ensure_published(repo,args.branch,args.seal,args.seal_digest)
    seal_info=check()
    seal=json.loads(Path(args.seal).read_text())
    sealed={e['path']:e['sha256'] for e in seal['files']}
    for path in [Path(args.registration),Path(args.backend_config)]:
        relative=path.resolve().relative_to(repo).as_posix()
        if sealed.get(relative)!=digest(path):raise RuntimeError('registration/configuration is not sealed')
    taskfile=repo/registration['tasks_path'];schema=repo/registration['schema_path'];patternsfile=repo/registration['patterns_path']
    for path in [taskfile,schema,patternsfile]:
        if sealed.get(path.relative_to(repo).as_posix())!=digest(path):raise RuntimeError('runtime input is not sealed')
    if set(sealed)!=set(registration['seal_1_files']):raise RuntimeError('seal coverage differs from registration')
    data=json.loads(taskfile.read_text())
    verify_workspace(args.workspace,data)
    original_check=check
    def check():
        original_check();verify_workspace(args.workspace,data)
    backend=Backend(config,args.workspace,schema,check)
    folder=Path(args.run_dir);folder.mkdir(parents=True,exist_ok=True)
    with (folder/'worker.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        control=Control(folder,datetime.fromisoformat(registration['cutoff_utc'].replace('Z','+00:00')))
        planfile=folder/'plan.json'
        if not planfile.exists():
            plan={'calls':{s['name']:{k:v for k,v in s.items() if k!='prompt'} | {'prompt_sha256':hashlib.sha256(s['prompt'].encode()).hexdigest()} for t in data['tasks'] if t['role']=='primary' for g in ['free','incoming'] for s in calls(t,data['candidate_files'],g)}}
            write_new(planfile,plan)
        def save_checkpoint():
            import sys
            sys.stdout.flush();sys.stderr.flush()
            info=checkpoint(repo,folder,args.backend,seal_info['seal_commit'],digest(args.seal),digest(args.registration))
            print('runtime checkpoint published: '+info['branch']+' '+info['commit'])
        if not (folder/'pauses.json').exists():write_new(folder/'pauses.json',[])
        if not (folder/'control.json').exists():control.persist()
        if args.finalize_cutoff or control.clock.now()>=control.latest_launch:
            finalize_cutoff(folder,control);save_checkpoint();print('stopped by the cutoff');return
        if args.resume_rick:control.resume_by_rick()
        if control.blocked:
            save_checkpoint()
            print('paused: '+control.blocked.removeprefix('manual: '));raise SystemExit(75)
        if config['backend']=='claude':
            try:backend.preflight()
            except (RuntimeError,OSError,subprocess.SubprocessError) as error:
                write_new(folder/'configuration_fault'/'preflight.json',{'scope':'arm','configuration_fault':[str(error)],'cli_version_raw':getattr(backend,'version_raw',None)})
                control.stop('configuration fault: preflight');save_checkpoint();raise SystemExit(78)
        patterns=json.loads(patternsfile.read_text())
        # Persist task metadata inside each final trace, not just the transient scheduler result.
        metadata={s['name']:{k:s[k] for k in ['task_id','group','incoming_pair','replicate']} for t in data['tasks'] for g in ['free','incoming'] for s in calls(t,data['candidate_files'],g)}
        def execute(name,prompt,ctl,reserve):return dict(backend(name,prompt,ctl,reserve),**metadata[name])
        attempts=AttemptRunner(folder,patterns,control,execute,reserve_at_launch=True)
        run_stage(data['tasks'],data['candidate_files'],attempts)
        save_checkpoint()
        if control.blocked:
            print('paused: '+control.blocked.removeprefix('manual: '))
            raise SystemExit(75)

if __name__=='__main__':main()
