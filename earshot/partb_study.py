"""Part B block scheduler. Live execution requires a published registration.

The explicit simulation backend is scripted and labelled throughout; it cannot
contact a model. Importing this module never prepares a workspace or a call.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import uuid

from . import partb as b
from .partb_artifacts import separate_scratch
from .partb_cli import opaque_session,initialize_runtime
from .partb_design import validate_schedule
from .partb_integrity import StudyPermit,digest,ready
from .partb_launch import (PracticeControl,prepare_practice,CredentialCopy,run_prepared,
                           preparation_digest,atomic_json,stamp,utcnow,LaunchPaused)

ENVIRONMENT_PROBE='''import sys,json,platform,importlib.metadata as m,importlib.util
print(json.dumps({'python':sys.version,'platform':platform.platform(),
 'packages':dict(sorted((d.metadata['Name'].lower(),d.version) for d in m.distributions())),
 'external_radon_spec':None if importlib.util.find_spec('radon') is None else importlib.util.find_spec('radon').origin}))'''


class ScriptedBackend:
    kind='scripted_fixture'

    def __init__(self,program=None):self.program=program

    def prepare(self,session,call):
        text='scripted_fixture = true\n'
        (session.config/'config.toml').write_text(text)
        program=self.program(call,session) if self.program else 'import json;print(json.dumps({"type":"item.completed","item":{"type":"agent_message","text":"Scripted no-edit fixture."}}))'
        value={'argv':[sys.executable,'-B','-c',program],
            'env':{'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1'},
            'purpose':'study','transport':'scripted_process','workspace':str(session.workspace),
            'codex_home':str(session.config),'config_sha256':b.digest(text.encode()),
            'backend_policy':{'name':'scripted_fixture'}}
        value['preparation_sha256']=preparation_digest(value)
        return value


class StudyRunner:
    def __init__(self,repo,registration,run,*,live=False,permit=None,auth_file=None,
                 fixture_backend=None,evaluator=None):
        self.repo=Path(repo).resolve();self.registration=registration;self.run=Path(run).resolve()
        self.live=live;self.permit=permit;self.auth_file=auth_file
        if live:
            ready(registration)
            expected=(self.repo/registration['run_dir']).resolve()
            if self.run!=expected or not self.run.is_relative_to(self.repo/'sprint/partB'):
                raise RuntimeError('live run directory must be the registered Part B folder')
            if not isinstance(permit,StudyPermit):raise RuntimeError('published study permit required')
            binding=permit.verify()
            if binding['registration']!=registration:raise RuntimeError('registration argument differs from published source')
            if auth_file is None:raise RuntimeError('explicit private auth file path required')
            self.binding={k:binding[k] for k in ['seal_commit','seal_sha256','registration_sha256']}
        else:
            if not isinstance(fixture_backend,ScriptedBackend):raise RuntimeError('simulation requires explicit scripted backend')
            if self.run.is_relative_to(self.repo):raise RuntimeError('simulation output must be outside the repository')
            self.binding={'simulation':True,'registration_sha256':b.digest(json.dumps(registration,sort_keys=True).encode())}
        self.fixture_backend=fixture_backend
        self.evaluator=evaluator or b.evaluate
        self.tasks=json.loads(self.input('tasks').read_text());self.calls=json.loads(self.input('schedule').read_text())['calls']
        self.groups=validate_schedule(self.tasks['tasks'],self.calls,registration['schedule_seed'])
        if live and (len(self.tasks['tasks'])!=12 or len(self.calls)!=180):raise RuntimeError('live task/call count mismatch')
        self.by_id={t['id']:t for t in self.tasks['tasks']}
        self.pristine=json.loads(self.input('pristine').read_text())
        for value in self.pristine.values():b.contents(value)
        self.targets=json.loads(self.input('buggy_targets').read_text())
        self.diagnostics=json.loads(self.input('diagnostics').read_text())
        self.expected=json.loads(self.input('baseline_case_ids').read_text())
        self.patterns=json.loads(self.input('system_issue_patterns').read_text())['patterns']
        self.prompts=json.loads(self.input('prompts').read_text())
        if live:
            expected=json.loads(self.input('environment').read_text())
            actual=json.loads(subprocess.check_output([registration['backend']['python'],'-B','-c',ENVIRONMENT_PROBE],
                cwd=self.repo,env={'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'},text=True,timeout=20))
            if actual!=expected or actual['external_radon_spec'] is not None:raise RuntimeError('dependency environment drift or external Radon import')
        self.run.mkdir(parents=True,exist_ok=True,mode=0o700)
        plan={'status':'LIVE_REGISTERED_STUDY' if live else 'SCRIPTED_FIXTURE_NOT_STUDY_DATA',
            'binding':self.binding,'registration_sha256':self.binding['registration_sha256'],
            'calls':self.calls,'source_inputs':{key:digest(self.input(key)) for key in registration['inputs']}}
        plan_path=self.run/'PLAN.json'
        if plan_path.exists():
            if json.loads(plan_path.read_text())!=plan:raise RuntimeError('run directory belongs to another plan/source')
        else:b.write_json(plan_path,plan)
        self.control=PracticeControl(self.run/'journal',registration['cutoff_utc'],
            max_attempts=registration['max_attempts'],scheduled=[c['name'] for c in self.calls])
        self.shutdown=threading.Event()

    def input(self,key):
        path=(self.repo/self.registration['inputs'][key]).resolve()
        if not path.is_relative_to(self.repo):raise RuntimeError('input outside repository')
        return path

    def status(self,status,**extra):
        atomic_json(self.run/'STATUS.json',{'status':status,'simulation':not self.live,
            'at_utc':stamp(utcnow()),**extra})

    def state(self):
        with self.control.locked() as state:return json.loads(json.dumps(state))

    def execute(self,call,launched):
        name=call['name'];task=self.by_id[call['task_id']];folder=self.run/'calls'/name
        folder.mkdir(parents=True,exist_ok=True)
        metadata=folder/'CALL.json'
        if not metadata.exists():b.write_json(metadata,call)
        elif json.loads(metadata.read_text())!=call:raise RuntimeError('call metadata changed')
        current=self.state()['calls'].get(name)
        if current and current.get('final'):
            launched.set()
            if current['status']=='stopped_by_cutoff':return
            result_path=Path(current['record'])
        else:
            if self.shutdown.is_set():launched.set();return
            number=(current['attempts'] if current else 0)+1
            setup=folder/f'setup-{number:02d}-{uuid.uuid4().hex}';setup.mkdir(exist_ok=False)
            buggy=dict(self.pristine);source_file=self.targets[task['id']]['source_file']
            buggy[source_file]=self.targets[task['id']]['record']
            session=opaque_session();assert not list(session.root.iterdir())
            baseline=b.make_workspace(self.pristine,buggy,session.workspace);initialize_runtime(session)
            prompt=self.prompts[name]
            if prompt!=b.render_prompt(task,call,self.tasks['candidate_files']):raise RuntimeError('rendered prompt differs')
            if self.live:
                prepared=prepare_practice(session,Path(self.registration['backend']['cli']),Path(self.registration['backend']['python']),
                    self.registration['backend']['model'],self.registration['backend']['effort'])
                if prepared['cli_sha256']!=self.registration['backend']['cli_sha256']:raise RuntimeError('registered CLI digest changed')
                prepared['purpose']='study';prepared['preparation_sha256']=preparation_digest(prepared)
            else:prepared=self.fixture_backend.prepare(session,call)
            b.write_json(setup/'PREPARED.json',prepared)
            b.write_json(setup/'BASELINE.json',baseline)
            b.write_json(setup/'WORKSPACE.json',{'root':str(session.root),'workspace':str(session.workspace),
                'fresh_CODEX_HOME':True,'git_commits':1,'git_remotes':[]})
            (setup/'prompt.txt').write_text(prompt)
            kwargs={'authorized':self.live,'fixture':not self.live,'study_permit':self.permit,'on_launch':launched.set}
            args=(self.control,name,session,prepared,prompt,self.registration['timeout_seconds'],
                  self.registration['termination_grace_seconds'],self.patterns)
            if self.live:
                with CredentialCopy(self.auth_file,session) as credentials:
                    result=run_prepared(*args,sanitize=credentials.sanitize,**kwargs)
            else:result=run_prepared(*args,**kwargs)
            if result['status'] in {'stopped_by_cutoff','already_final'}:return
            result_path=Path(self.state()['calls'][name]['record'])
        artifact_path=result_path.parent/'artifact.json'
        if not artifact_path.exists():return
        result=json.loads(result_path.read_text());artifact=json.loads(artifact_path.read_text())
        if artifact['files'] is None or not result.get('session_cleanup',{}).get('verified'):return
        if result['status']=='system_issue' and artifact['baseline']==artifact['files']:return
        # Completed artifacts remain final even without a final prose message.
        # A system/protocol pause is retained; no answer text is needed to evaluate.
        previous=sorted(folder.glob('evaluation-*/result.json'))
        if any(json.loads(p.read_text()).get('evaluation_available') for p in previous):return
        evaluation_dir=folder/f'evaluation-{len(previous)+1:02d}'
        _,_,scratch=separate_scratch(artifact['baseline'],artifact['files'])
        qualification=self.targets[task['id']]['qualification']
        evaluation=self.evaluator(artifact['baseline'],self.pristine,artifact['files'],qualification,Path(self.registration['backend']['python']),
            evaluation_dir,self.expected,self.diagnostics[task['id']],metadata=artifact.get('excluded_metadata'))
        evaluation_dir.mkdir(exist_ok=True)
        if not (evaluation_dir/'result.json').exists():b.write_json(evaluation_dir/'result.json',evaluation)
        b.write_json(evaluation_dir/'INPUTS.json',{'artifact':str(artifact_path.relative_to(self.run)),
            'result':str(result_path.relative_to(self.run)),'scratch_inventory':scratch})
        if not evaluation['evaluation_available']:
            with self.control.locked() as state:self.control.pause(state,'independent_evaluator_unavailable',name)

    def worker(self,call,launched):
        try:self.execute(call,launched)
        except LaunchPaused:
            # Prepared but never launched. Preserve setup evidence and leave
            # the scheduled cell pending; this is not an agent failure.
            return
        except Exception as error:
            with self.control.locked() as state:self.control.pause(state,'controller_fault: '+type(error).__name__,call['name'])
            fault=self.run/('FAULT-'+call['name']+'-'+os.urandom(6).hex()+'.json')
            b.write_json(fault,{'call':call['name'],'type':type(error).__name__,'reason':str(error)})
            raise
        finally:launched.set()

    def run_blocks(self,max_blocks=None):
        if self.live and max_blocks is not None:raise RuntimeError('outcome/block stopping unavailable for live study')
        with (self.run/'worker.lock').open('a') as lease:
            try:fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError as error:raise RuntimeError('another worker owns this run') from error
            self.status('running');self.control.finish_cutoff()
            try:
                with ThreadPoolExecutor(max_workers=self.registration['workers']) as pool:
                    try:
                        for block_number,group in enumerate(self.groups):
                            active=[]
                            for call in group:
                                if self.state()['paused']:break
                                if len(active)>=self.registration['workers']:
                                    active.pop(0).result()
                                if self.state()['paused']:break
                                event=threading.Event();future=pool.submit(self.worker,call,event)
                                active.append(future)
                                # Next admission follows Popen or final/refusal.
                                event.wait()
                                if future.done():future.result()
                            for future in active:future.result()
                            if self.state()['paused']:break
                            if max_blocks is not None and block_number+1>=max_blocks:break
                    except BaseException:
                        self.shutdown.set()
                        with self.control.locked() as state:self.control.pause(state,'controller interrupted; drain active calls',None)
                        raise
                state=self.state()
                if state['paused']:self.status('paused',reason=state.get('pause_reason'))
                elif all(state['calls'].get(c['name'],{}).get('final') for c in self.calls):
                    stopped=any(v['status']=='stopped_by_cutoff' for v in state['calls'].values())
                    self.status('stopped_by_cutoff' if stopped else 'completed')
                else:self.status('simulation_stopped' if not self.live else 'incomplete')
            except BaseException:
                self.shutdown.set();self.status('paused',reason='controller exception; preserve in-flight state')
                raise
            return json.loads((self.run/'STATUS.json').read_text())


def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path('.'))
    p.add_argument('--registration',type=Path,required=True);p.add_argument('--run-dir',type=Path,required=True)
    mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--live',action='store_true');mode.add_argument('--simulate',action='store_true')
    mode.add_argument('--finalize-cutoff',action='store_true')
    p.add_argument('--branch',default='main');p.add_argument('--seal',type=Path);p.add_argument('--seal-digest',type=Path)
    p.add_argument('--auth-file',type=Path);p.add_argument('--resume-rick');p.add_argument('--max-blocks',type=int)
    args=p.parse_args();registration=json.loads(args.registration.read_text())
    if (args.live or args.finalize_cutoff) and (not args.seal or not args.seal_digest):raise RuntimeError('published source seal required')
    permit=StudyPermit(args.repo,args.branch,args.registration,args.seal,args.seal_digest) if args.live or args.finalize_cutoff else None
    if args.finalize_cutoff:
        binding=permit.verify();plan=json.loads((args.run_dir/'PLAN.json').read_text())
        expected={k:binding[k] for k in ['seal_commit','seal_sha256','registration_sha256']}
        if plan.get('status')!='LIVE_REGISTERED_STUDY' or plan.get('binding')!=expected:raise RuntimeError('runtime binding differs')
        with (args.run_dir/'worker.lock').open('a') as lease:
            try:fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError as error:raise RuntimeError('worker still active') from error
            control=PracticeControl(args.run_dir/'journal',registration['cutoff_utc'],registration['max_attempts'],
                scheduled=[c['name'] for c in plan['calls']])
            if utcnow()<control.cutoff:raise RuntimeError('cutoff has not been reached')
            control.finish_cutoff()
            with control.locked() as state:
                if any(v['status']=='in_flight' for v in state['calls'].values()):raise RuntimeError('in-flight attempts require reconciliation')
            atomic_json(args.run_dir/'STATUS.json',{'status':'stopped_by_cutoff','simulation':False,'at_utc':stamp(utcnow())})
        print('cutoff finalized; no calls launched');return
    runner=StudyRunner(args.repo,registration,args.run_dir,live=args.live,permit=permit,auth_file=args.auth_file,
        fixture_backend=ScriptedBackend() if args.simulate else None)
    if args.resume_rick:runner.control.resume_rick(args.resume_rick)
    print(json.dumps(runner.run_blocks(args.max_blocks if args.live else args.max_blocks or 1),indent=2))


if __name__=='__main__':main()
