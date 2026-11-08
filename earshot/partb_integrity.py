"""Part B publication, source coverage and final runtime-ledger guards."""
import ast
import argparse
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import subprocess

from .integrity import (digest,git,safe_path,verify_digest,published_head,committed_bytes)


def ready(registration):
    if registration.get('status')!='REGISTERED' or 'PENDING_' in json.dumps(registration):
        raise RuntimeError('Part B requires REGISTERED with no pending fields')
    try:cutoff=datetime.fromisoformat(registration['cutoff_utc'].replace('Z','+00:00'))
    except (KeyError,TypeError,ValueError) as error:raise RuntimeError('absolute cutoff required') from error
    if cutoff.tzinfo is None:raise RuntimeError('cutoff timezone required')
    if (registration.get('timeout_seconds')!=180 or registration.get('primary_calls')!=180
            or registration.get('task_count')!=12 or registration.get('blocks_per_task')!=3
            or registration.get('conditions')!=['H0','H-in','H-out','C-in','C-out']):
        raise RuntimeError('Part B frozen design mismatch')
    if registration.get('workers') not in (1,2) or registration.get('max_attempts')!=5:
        raise RuntimeError('invalid worker/attempt policy')
    paths=registration.get('seal_1_files',[])
    if not paths or paths!=sorted(set(paths)):raise RuntimeError('seal coverage must be unique and sorted')
    for name in paths:
        p=Path(name)
        if p.is_absolute() or '..' in p.parts or '.git' in p.parts or any(v in p.parts for v in ['run','codex','traces','journal']):
            raise RuntimeError('unsafe/runtime seal path: '+name)


def source_closure(repo,modules):
    """AST closure includes nested imports, without importing/executing modules."""
    repo=Path(repo);seen=set();todo=list(modules)
    while todo:
        module=todo.pop();path=repo/Path(*module.split('.')).with_suffix('.py')
        if not path.exists():path=repo/Path(*module.split('.'))/'__init__.py'
        if not path.exists():raise RuntimeError('unresolved internal import: '+module)
        relative=path.relative_to(repo).as_posix()
        if relative in seen:continue
        seen.add(relative)
        package=module.split('.')[:-1] if path.name!='__init__.py' else module.split('.')
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node,ast.Import):
                todo.extend(alias.name for alias in node.names if alias.name.startswith('earshot.'))
            elif isinstance(node,ast.ImportFrom):
                if node.level:
                    prefix=package[:len(package)-node.level+1]
                    target='.'.join(prefix+([node.module] if node.module else []))
                    if node.module:todo.append(target)
                    else:
                        for alias in node.names:
                            candidate=target+'.'+alias.name
                            if (repo/Path(*candidate.split('.')).with_suffix('.py')).exists():todo.append(candidate)
                elif node.module and node.module.startswith('earshot.'):todo.append(node.module)
        init=repo/'earshot/__init__.py'
        if init.exists() and 'earshot/__init__.py' not in seen:todo.append('earshot')
    return sorted(seen)


def verify_source(repo,branch,registration_path,seal_path,seal_digest,require_head=True):
    repo=Path(repo).resolve();registration_path=Path(registration_path).resolve()
    registration=json.loads(registration_path.read_text());ready(registration)
    verify_digest(seal_path,seal_digest);seal=json.loads(Path(seal_path).read_text())
    listed=[entry['path'] for entry in seal['files']]
    if listed!=registration['seal_1_files']:raise RuntimeError('seal file set/order mismatch')
    head=published_head(repo,branch)
    relative=committed_bytes(repo,seal_path,head);committed_bytes(repo,seal_digest,head)
    committed_bytes(repo,registration_path,head)
    seal_commit=git(repo,'log','-1','--format=%H',head,'--',relative)
    if not seal_commit:raise RuntimeError('seal not committed')
    if require_head and head!=seal_commit:raise RuntimeError('commit exists after source seal')
    if subprocess.run(['git','merge-base','--is-ancestor',seal_commit,head],cwd=repo,capture_output=True).returncode:
        raise RuntimeError('source seal is not an ancestor')
    for entry in seal['files']:
        p=safe_path(repo,entry['path'])
        if (repo/entry['path']).is_symlink() or digest(p)!=entry['sha256']:
            raise RuntimeError('sealed file changed: '+entry['path'])
        committed_bytes(repo,p,head);committed_bytes(repo,p,seal_commit)
    if registration_path.relative_to(repo).as_posix() not in listed:raise RuntimeError('registration not sealed')
    if not set(registration.get('inputs',{}).values())<=set(listed):raise RuntimeError('repository data input not sealed')
    required=source_closure(repo,['earshot.partb_study','earshot.partb_score'])
    if not set(required)<=set(listed):raise RuntimeError('import closure missing from seal')
    return {'seal_commit':seal_commit,'seal_sha256':digest(seal_path),'registration_sha256':digest(registration_path),
            'head':head,'registration':registration}


@dataclass(frozen=True)
class StudyPermit:
    repo: Path
    branch: str
    registration: Path
    seal: Path
    seal_digest: Path

    def verify(self):
        return verify_source(self.repo,self.branch,self.registration,self.seal,self.seal_digest)

    def verify_call(self,call,prepared,prompt,timeout,grace):
        binding=self.verify();reg=binding['registration']
        prompts=json.loads((self.repo/reg['inputs']['prompts']).read_text())
        schedule=json.loads((self.repo/reg['inputs']['schedule']).read_text())['calls']
        if call not in {c['name'] for c in schedule} or prompts.get(call)!=prompt:
            raise RuntimeError('call/prompt not in sealed plan')
        if timeout!=reg['timeout_seconds'] or grace!=reg['termination_grace_seconds']:
            raise RuntimeError('call limits differ from registration')
        policy=prepared['backend_policy'];backend=reg['backend']
        for key in ['model','effort','setup_version']:
            if policy.get(key)!=backend[key]:raise RuntimeError('prepared backend differs from registration')
        if prepared['cli_sha256']!=backend['cli_sha256']:raise RuntimeError('CLI differs from registration')
        if prepared['env'].get('PYTEST_DISABLE_PLUGIN_AUTOLOAD')!='1' or prepared['env'].get('PYTEST_PLUGINS')!='pytest_mock':
            raise RuntimeError('registered test environment changed')
        return binding


def runtime_files(run):
    run=Path(run).resolve();paths=[]
    for p in sorted(run.rglob('*')):
        if p.is_symlink():raise RuntimeError('runtime filesystem symlink; hold for review')
        if p.is_file() and p.name not in {'control.lock','worker.lock'}:
            if p.name=='auth.json':raise RuntimeError('credential file cannot enter runtime ledger')
            paths.append(p)
    return paths


def ledger_record(run,binding):
    run=Path(run).resolve();status=json.loads((run/'STATUS.json').read_text())['status']
    if status not in {'completed','stopped_by_cutoff'}:raise RuntimeError('runtime not terminal; cannot ledger')
    plan=json.loads((run/'PLAN.json').read_text())
    keys=['seal_commit','seal_sha256','registration_sha256']
    if plan.get('status')!='LIVE_REGISTERED_STUDY' or plan.get('binding')!={k:binding[k] for k in keys}:
        raise RuntimeError('simulation or runtime binding cannot be ledgered as study data')
    control=json.loads((run/'journal/control.json').read_text())
    names={c['name'] for c in plan['calls']}
    if set(control['calls'])!=names or not all(v.get('final') for v in control['calls'].values()):
        raise RuntimeError('runtime call set is incomplete')
    if any(c['status']=='in_flight' for c in control['calls'].values()):raise RuntimeError('in-flight attempt cannot be ledgered')
    return {'status':'PART_B_FINAL_RUNTIME_LEDGER','source_seal_commit':binding['seal_commit'],
        'source_seal_sha256':binding['seal_sha256'],'registration_sha256':binding['registration_sha256'],
        'files':[{'path':str(p.relative_to(run)),'sha256':digest(p)} for p in runtime_files(run)]}


def verify_runtime(run,ledger_path,ledger_digest):
    verify_digest(ledger_path,ledger_digest);run=Path(run).resolve()
    ledger=json.loads(Path(ledger_path).read_text());seen=set()
    for entry in ledger['files']:
        path=entry['path']
        if path in seen:raise RuntimeError('duplicate ledger entry')
        seen.add(path);p=safe_path(run,path)
        if digest(p)!=entry['sha256']:raise RuntimeError('runtime hash mismatch: '+path)
    actual={str(p.relative_to(run)) for p in runtime_files(run)}
    if seen!=actual:raise RuntimeError('runtime inventory mismatch')
    return ledger


def verify_published_ledger(repo,branch,registration_path,seal,seal_digest,run,ledger_path,ledger_digest):
    binding=verify_source(repo,branch,registration_path,seal,seal_digest,require_head=False)
    ledger=verify_runtime(run,ledger_path,ledger_digest)
    expected=(binding['seal_commit'],binding['seal_sha256'],binding['registration_sha256'])
    if (ledger['source_seal_commit'],ledger['source_seal_sha256'],ledger['registration_sha256'])!=expected:
        raise RuntimeError('ledger belongs to another source seal/registration')
    if ledger_record(run,binding)['files']!=ledger['files']:raise RuntimeError('terminal runtime ledger differs')
    committed_bytes(repo,ledger_path,binding['head']);committed_bytes(repo,ledger_digest,binding['head'])
    for p in runtime_files(run):committed_bytes(repo,p,binding['head'])
    return binding,ledger


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['verify-source','build-ledger','verify-ledger'])
    p.add_argument('--repo',type=Path,default=Path('.'));p.add_argument('--branch',default='main')
    for name in ['registration','seal','seal-digest']:p.add_argument('--'+name,type=Path,required=True)
    for name in ['run-dir','ledger','ledger-digest']:p.add_argument('--'+name,type=Path)
    args=p.parse_args()
    if args.action=='verify-source':
        binding=verify_source(args.repo,args.branch,args.registration,args.seal,args.seal_digest)
        print(json.dumps({k:binding[k] for k in ['seal_commit','seal_sha256','registration_sha256']},indent=2));return
    if not all([args.run_dir,args.ledger,args.ledger_digest]):raise RuntimeError('run and both ledger paths required')
    if args.action=='build-ledger':
        if args.ledger.resolve().is_relative_to(args.run_dir.resolve()):raise RuntimeError('ledger must be outside runtime folder')
        from .partb_launch import write_json
        binding=verify_source(args.repo,args.branch,args.registration,args.seal,args.seal_digest)
        value=ledger_record(args.run_dir,binding);write_json(args.ledger,value)
        with args.ledger_digest.open('x') as stream:stream.write(digest(args.ledger)+'\n')
        print('ledger built',len(value['files']),digest(args.ledger))
    else:
        _,value=verify_published_ledger(args.repo,args.branch,args.registration,args.seal,args.seal_digest,args.run_dir,args.ledger,args.ledger_digest)
        print('ledger verified',len(value['files']))


if __name__=='__main__':main()
