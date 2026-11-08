"""Fresh-session launch controls. Importing never authenticates or launches.

Study execution additionally requires a verified published-source permit.
Practice must be explicitly authorized by its caller. Process fixtures exercise
the same journal, cutoff, timeout and pause paths without a model service.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import math
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import tempfile
import uuid
from urllib.parse import urlparse

from .partb import snapshot, digest,excluded_inventory
from .partb_cli import (CLI_VERSION, SETUP_VERSION, cli_prefix, environment, permission_config,
                        verify_initial_configuration_home)


class LaunchPaused(RuntimeError):
    """Another call paused admission before this process was launched."""


def utcnow():
    return datetime.now(timezone.utc)


def stamp(value):
    return value.astimezone(timezone.utc).isoformat().replace('+00:00','Z')


def instant(value):
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None:raise ValueError('cutoff must name a time zone')
    return result.astimezone(timezone.utc)


def write_json(path,value):
    """Exclusive immutable record, flushed before control state points to it."""
    path=Path(path)
    with path.open('x') as stream:
        json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    directory=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(directory)
    finally:os.close(directory)


def atomic_json(path,value):
    """Only mutable control state uses replacement; attempt evidence is exclusive."""
    path=Path(path)
    fd,name=tempfile.mkstemp(prefix='.control-',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as stream:
            json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
        os.replace(name,path)
        directory=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if os.path.exists(name):os.unlink(name)


class CredentialCopy:
    """Explicit source only; disposable secret never enters artifact records."""
    def __init__(self,source,session):
        self.source=Path(source);self.target=session.config/'auth.json'
        self.values=[];self.leak_detected=False

    def __enter__(self):
        # O_NOFOLLOW prevents following a swapped final-component symlink.
        fd=os.open(self.source,os.O_RDONLY|os.O_NOFOLLOW)
        try:
            info=os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o600:
                raise RuntimeError('auth source must be a regular mode-0600 file')
            with os.fdopen(fd,'rb',closefd=False) as stream:data=stream.read()
        finally:os.close(fd)
        parsed=json.loads(data)
        def collect(value):
            if isinstance(value,dict):
                for key,item in value.items():
                    if isinstance(item,str) and len(item)>12 and any(x in key.lower() for x in ['token','key','account_id']):
                        self.values.append(item)
                    else:collect(item)
            elif isinstance(value,list):
                for item in value:collect(item)
        collect(parsed)
        if not self.values:raise RuntimeError('auth file has no recognised credential values')
        fd=os.open(self.target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:
            with os.fdopen(fd,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
        except BaseException:
            self.target.unlink(missing_ok=True);self.values.clear();raise
        return self

    def sanitize(self,text):
        for value in sorted(self.values,key=len,reverse=True):
            if value in text:
                self.leak_detected=True;text=text.replace(value,'[REDACTED_CREDENTIAL]')
        return text

    def __exit__(self,*args):
        self.target.unlink(missing_ok=True)
        self.values.clear()


def prepare_practice(session,cli,python,model='gpt-6.1-sol',effort='low',loopback_url=None):
    """Prepare reviewed native tool permissions, without reading any auth file."""
    if subprocess.check_output([str(cli),'--version'],text=True,timeout=15).strip()!=CLI_VERSION:
        raise RuntimeError('CLI version mismatch')
    if not session.temporary.resolve().is_relative_to(session.workspace.resolve()):
        raise RuntimeError('TMPDIR outside workspace')
    if any(session.config.iterdir()):raise RuntimeError('practice requires an empty initial CODEX_HOME')
    for p in session.workspace.rglob('*'):
        if p.name.lower() in {'agents.md','agents.override.md','claude.md','gemini.md'}:
            raise RuntimeError('unreviewed workspace instruction file')
    base=permission_config(session,python)
    prefix='model = '+json.dumps(model)+'\nmodel_reasoning_effort = '+json.dumps(effort)+'\n'
    if loopback_url is not None:
        url=urlparse(loopback_url)
        if (url.scheme!='http' or url.hostname!='127.0.0.1' or not url.port or url.path!='/v1'
                or url.username or url.password or url.query or url.fragment):
            raise RuntimeError('scripted transport must be an explicit loopback server')
        prefix+='model_provider = "partb_loopback"\n'
        prefix+='[model_providers.partb_loopback]\nname = "Local scripted fixture"\n'
        prefix+='base_url = '+json.dumps(loopback_url)+'\nwire_api = "responses"\nrequires_openai_auth = false\nsupports_websockets = false\n'
        # Provider table must not absorb the following top-level settings.
        top,permissions=base.split('[permissions.partb]',1)
        config=top+prefix+'[permissions.partb]'+permissions
    else:config=prefix+base
    target=session.config/'config.toml'
    with target.open('x') as stream:stream.write(config)
    verify_initial_configuration_home(session)
    env=environment(session)
    # The agent's commands use the same dependency environment as qualification.
    env['PYTHONPATH']=subprocess.check_output([str(python),'-B','-c',
       'import sysconfig;print(sysconfig.get_path("purelib"))'],text=True,timeout=15).strip()
    env['PATH']=str(Path(python).resolve().parent)+':/usr/bin:/bin'
    result={'argv':cli_prefix(cli)+['exec','--strict-config','--ignore-rules','--skip-git-repo-check',
            '-C',str(session.workspace),'--json','-'],
            'env':env,'config_sha256':digest(config.encode()),'cli_sha256':digest(Path(cli).read_bytes()),
            'purpose':'practice','hosted_authorized':False,
            'workspace':str(session.workspace),'codex_home':str(session.config),
            'backend_policy':{'model':model,'effort':effort,'python':str(Path(python).resolve()),
                              'dependency_path':env['PYTHONPATH'],'setup_version':SETUP_VERSION,
                              'pytest_disable_plugin_autoload':env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'],
                              'pytest_plugins':env['PYTEST_PLUGINS']}}
    result['cleanup_timeout']=2.0
    if loopback_url is not None:result['transport']='scripted_loopback'
    result['preparation_sha256']=preparation_digest(result)
    return result


def preparation_digest(prepared):
    return digest(json.dumps({k:v for k,v in prepared.items() if k!='preparation_sha256'},sort_keys=True).encode())


class PracticeControl:
    """Shared launch lock and durable pause state; no background retry loop."""
    def __init__(self,root,cutoff,max_attempts=5,clock=utcnow,scheduled=()):
        if max_attempts<1:raise ValueError('positive attempt limit required')
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.cutoff=instant(cutoff);self.max_attempts=max_attempts;self.clock=clock
        with self.locked() as state:
            if state:
                if (state['cutoff']!=stamp(self.cutoff) or state['max_attempts']!=max_attempts
                        or state['scheduled']!=list(scheduled)):
                    raise RuntimeError('cannot change durable cutoff or attempt limit')
            else:state.update(cutoff=stamp(self.cutoff),max_attempts=max_attempts,paused=False,calls={},scheduled=list(scheduled))

    @contextmanager
    def locked(self):
        with (self.root/'control.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            path=self.root/'control.json'
            state=json.loads(path.read_text()) if path.exists() else {}
            try:
                yield state
            finally:
                atomic_json(path,state)
                fcntl.flock(lock,fcntl.LOCK_UN)

    def pause(self,state,reason,call):
        state.update(paused=True,pause_reason=reason)
        write_json(self.root/('pause-'+uuid.uuid4().hex+'.json'),{
            'time':stamp(self.clock()),'reason':reason,'call':call,
            'finished':[k for k,v in state['calls'].items() if v.get('final')],
            'calls_left':[k for k in state['scheduled'] if not state['calls'].get(k,{}).get('final')],
            'in_flight':[k for k,v in state['calls'].items() if v.get('status')=='in_flight']})

    def resume_rick(self,reason):
        if not reason.strip():raise ValueError('explicit Rick instruction must be recorded')
        self.finish_cutoff()
        with self.locked() as state:
            if self.clock()>=self.cutoff:raise RuntimeError('cutoff passed; cannot resume')
            if any(v.get('status')=='in_flight' for v in state['calls'].values()):
                raise RuntimeError('unreconciled in-flight attempts; preserve and review')
            if any(v.get('partial_artifact') for v in state['calls'].values()):
                raise RuntimeError('partial artifact requires reconciliation; no automatic relaunch')
            if any(v['attempts']>=self.max_attempts and not v.get('final') for v in state['calls'].values()):
                raise RuntimeError('attempt limit reached; counts cannot be reset')
            write_json(self.root/('resume-'+uuid.uuid4().hex+'.json'),{'time':stamp(self.clock()),'instruction':reason})
            state.update(paused=False,pause_reason=None)

    def finish_cutoff(self):
        """Record never-launched cells even while paused; retain old attempts."""
        if self.clock()<self.cutoff:return
        with self.locked() as state:
            for call in state['scheduled']:
                old=state['calls'].get(call)
                if old and (old.get('final') or old['status']=='in_flight'):continue
                path=self.root/('cutoff-'+uuid.uuid4().hex+'.json')
                write_json(path,{'call':call,'time':stamp(self.clock()),'process_launched':False,
                    'status':'retry_stopped_by_cutoff' if old else 'stopped_by_cutoff'})
                if old:old.update(final=True,retry_stopped_by_cutoff=True,cutoff_record=str(path))
                else:state['calls'][call]={'status':'stopped_by_cutoff','final':True,'attempts':0,
                    'prompt_sha256':None,'record':str(path)}


def outcome(exit_code,timed_out,stdout,stderr,patterns):
    events=[]
    for line in stdout.splitlines():
        try:event=json.loads(line)
        except ValueError:continue
        if isinstance(event,dict):events.append(event)
    errors=[stderr]
    for e in events:
        if e.get('type') in {'error','turn.failed'}:errors.append(json.dumps(e))
    text='\n'.join(errors)
    matches=[p['id'] for p in patterns if re.search(p['regex'],text,re.I)]
    if matches:return 'system_issue',matches
    if timed_out:return 'timed_out',[]
    answers=[e.get('item',{}).get('text') for e in events if e.get('type')=='item.completed'
             and e.get('item',{}).get('type')=='agent_message']
    if exit_code==0 and any(isinstance(x,str) and x.strip() for x in answers):return 'completed',[]
    return 'system_issue',['unclassified_no_final_answer']


def kill_group(process,signum):
    try:os.killpg(process.pid,signum)
    except ProcessLookupError:pass


def run_prepared(control,call,session,prepared,prompt,timeout,grace,patterns,
                 authorized=False,fixture=False,sanitize=lambda text:text,study_permit=None,on_launch=None):
    """One attempt only. No automatic resume, retry or implicit study approval.

    fixture=True is permitted only with an explicit scripted transport;
    it cannot bypass authorization on a prepared hosted command.
    """
    if not re.fullmatch(r'[A-Za-z0-9_-]+',call):raise ValueError('unsafe call ID')
    if not all(math.isfinite(x) and x>0 for x in [timeout,grace]):raise ValueError('positive finite limits required')
    is_process_fixture=prepared.get('transport')=='scripted_process'
    is_fixture=prepared.get('transport') in {'scripted_process','scripted_loopback'}
    if fixture!=is_fixture:raise RuntimeError('fixture mode requires a scripted-process preparation')
    if not fixture:
        if not authorized:raise RuntimeError('explicit execution authorization required')
        if prepared.get('purpose')=='study':
            from .partb_integrity import StudyPermit
            if not isinstance(study_permit,StudyPermit):raise RuntimeError('published study permit required')
            study_permit.verify_call(call,prepared,prompt,timeout,grace)
        elif prepared.get('purpose')!='practice':raise RuntimeError('unsupported execution purpose')
    if prepared.get('preparation_sha256')!=preparation_digest(prepared):
        raise RuntimeError('prepared launch changed')
    if prepared.get('workspace')!=str(session.workspace) or prepared.get('codex_home')!=str(session.config):
        raise RuntimeError('prepared session changed')
    if control.root.resolve().is_relative_to(session.workspace.resolve()):
        raise RuntimeError('control journal must be outside the agent workspace')
    control.finish_cutoff()
    prompt_sha=digest(prompt.encode())
    with control.locked() as state:
        if state['scheduled'] and call not in state['scheduled']:raise RuntimeError('unscheduled call')
        existing=state['calls'].get(call)
        if existing and existing['prompt_sha256'] not in (None,prompt_sha):raise RuntimeError('saved prompt changed')
        if existing and existing.get('final'):return {'status':'already_final','record':existing['record']}
    # Setup and version/config checks precede the last-launch cutoff check.
    verify_initial_configuration_home(session)
    if digest((session.config/'config.toml').read_bytes())!=prepared['config_sha256']:
        raise RuntimeError('prepared config changed')
    if not is_process_fixture:
        if digest(Path(prepared['argv'][0]).read_bytes())!=prepared['cli_sha256']:
            raise RuntimeError('prepared CLI changed')
        if subprocess.check_output([prepared['argv'][0],'--version'],text=True,timeout=15,
                env=prepared['env']).strip()!=CLI_VERSION:raise RuntimeError('CLI version mismatch')
        from .partb_processes import SessionProcesses
        cleanup=SessionProcesses(session,prepared['cleanup_timeout'])
    else:cleanup=None
    launch_margin=timeout+grace+(prepared.get('cleanup_timeout',0) if cleanup else 0)
    policy_sha=digest(json.dumps({'timeout':timeout,'grace':grace,'patterns':patterns,
        'backend':prepared.get('backend_policy'), 'cli_sha256':prepared.get('cli_sha256'),
        'purpose':prepared.get('purpose'),'transport':prepared.get('transport','hosted'),
        'cleanup_timeout':prepared.get('cleanup_timeout',0)},sort_keys=True).encode())
    baseline=snapshot(session.workspace)
    baseline_metadata=excluded_inventory(session.workspace)
    runtime_exclusions=[str(cleanup.own.relative_to(session.workspace))] if cleanup else []
    for name in runtime_exclusions:baseline.pop(name,None)
    baseline_sha=digest(json.dumps(baseline,sort_keys=True).encode())
    with control.locked() as state:
        existing=state['calls'].get(call)
        if existing and existing['prompt_sha256']!=prompt_sha:raise RuntimeError('saved prompt changed')
        if existing and existing.get('final'):return {'status':'already_final','record':existing['record']}
        if state['paused']:raise LaunchPaused('paused; Rick must explicitly resume')
        if state.get('policy_sha256',policy_sha)!=policy_sha:raise RuntimeError('durable launch policy changed')
        state['policy_sha256']=policy_sha
        if existing and existing['status']=='in_flight':raise RuntimeError('unreconciled attempt; never relaunch silently')
        if existing and existing.get('workspace')==str(session.workspace):
            raise RuntimeError('retry requires a fresh opaque session')
        if existing and existing.get('baseline_sha256')!=baseline_sha:
            raise RuntimeError('retry baseline changed')
        if existing and existing['attempts']>=control.max_attempts:
            control.pause(state,'attempt_limit',call);return {'status':'paused_attempt_limit'}
        if (control.cutoff-control.clock()).total_seconds()<launch_margin:
            path=control.root/(call+'-stopped-'+uuid.uuid4().hex+'.json')
            value={'status':'stopped_by_cutoff','process_launched':False,'time':stamp(control.clock())}
            write_json(path,value)
            state['calls'][call]={'status':'stopped_by_cutoff','final':True,'attempts':existing['attempts'] if existing else 0,
                'prompt_sha256':prompt_sha,'record':str(path)}
            return value
        if study_permit is not None:study_permit.verify_call(call,prepared,prompt,timeout,grace)
        number=(existing['attempts'] if existing else 0)+1
        directory=control.root/call/f'attempt-{number:02d}';directory.mkdir(parents=True,exist_ok=False)
        write_json(directory/'START.json',{'time':stamp(control.clock()),'prompt_sha256':prompt_sha,
            'attempt':number,'timeout':timeout,'grace':grace,'workspace':str(session.workspace),
            'config_sha256':prepared['config_sha256'],'fixture':fixture})
        state['calls'][call]={'status':'in_flight','attempts':number,'final':False,'prompt_sha256':prompt_sha,
            'workspace':str(session.workspace),'baseline_sha256':baseline_sha}
        state.setdefault('launch_sequence',[]).append({'call':call,'attempt':number,'time':stamp(control.clock())})
        # Persist reservation BEFORE Popen. A crash leaves a reviewable in-flight entry.
        atomic_json(control.root/'control.json',state)
        if (control.cutoff-control.clock()).total_seconds()<launch_margin:
            value={'status':'stopped_by_cutoff','process_launched':False,'time':stamp(control.clock()),'attempt':number}
            write_json(directory/'RESULT.json',value)
            state['calls'][call].update(status='stopped_by_cutoff',final=True,record=str(directory/'RESULT.json'))
            return value
        try:
            process=subprocess.Popen(prepared['argv'],cwd=session.workspace,env=prepared['env'],
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
        except OSError as error:
            process=None;launch_error=type(error).__name__+': '+str(error)
        if on_launch is not None:on_launch()
    timed=False;interrupted=False
    if process is None:stdout='';stderr=launch_error;exit_code=None
    else:
        try:stdout,stderr=process.communicate(prompt,timeout=timeout)
        except subprocess.TimeoutExpired:
            timed=True;kill_group(process,signal.SIGTERM)
            try:stdout,stderr=process.communicate(timeout=grace)
            except subprocess.TimeoutExpired:
                kill_group(process,signal.SIGKILL);stdout,stderr=process.communicate()
        except BaseException:
            interrupted=True;kill_group(process,signal.SIGKILL);stdout,stderr=process.communicate()
        finally:
            # Group cleanup alone does not cover detached processes.
            kill_group(process,signal.SIGKILL)
        exit_code=process.returncode
    raw=(stdout,stderr);stdout=sanitize(stdout);stderr=sanitize(stderr)
    secret_seen=raw!=(stdout,stderr)
    status,matches=outcome(exit_code,timed,stdout,stderr,patterns)
    if secret_seen:status='system_issue';matches=['credential_exposure_redacted']
    if interrupted:status='system_issue';matches=['controller_interrupted']
    if status=='system_issue':
        # Pause before potentially slower snapshot/evaluation I/O. Other workers
        # may finish, but no new process may cross the shared launch lock.
        with control.locked() as state:control.pause(state,','.join(matches),call)
    try:
        cleanup_result=cleanup.finish() if cleanup else {'verified':True,'method':'scripted process group fixture'}
        cleanup_error=None
    except (OSError,RuntimeError,subprocess.SubprocessError) as error:
        cleanup_result={'verified':False};cleanup_error=type(error).__name__+': '+str(error)
        status='system_issue';matches=['session_cleanup_unverified']
        with control.locked() as state:control.pause(state,'session_cleanup_unverified',call)
    (directory/'stdout.log').write_text(stdout);(directory/'stderr.log').write_text(stderr)
    try:
        final=snapshot(session.workspace)
        for name in runtime_exclusions:final.pop(name,None)
        capture_error=None
    except (OSError,ValueError) as error:
        final=None;capture_error=type(error).__name__+': '+str(error)
        status='system_issue';matches=['artifact_capture_error']
        with control.locked() as state:control.pause(state,'artifact_capture_error',call)
    final_metadata=excluded_inventory(session.workspace) if final is not None else {}
    write_json(directory/'artifact.json',{'baseline':baseline,'files':final,'status':'PROCESS_ARTIFACT',
        'fixture':fixture,'capture_error':capture_error,'controller_runtime_exclusions':runtime_exclusions,
        'excluded_metadata':{'baseline':baseline_metadata,'final':final_metadata}})
    partial=status=='system_issue' and (capture_error is not None or cleanup_error is not None or baseline!=final)
    value={'status':status,'exit_code':exit_code,'timed_out':timed,'system_issue_matches':matches,
        'process_launched':process is not None,'attempt':number,'ended_at_utc':stamp(control.clock()),
        'partial_artifact':partial,'fixture':fixture,'credential_output_redacted':secret_seen,
        'session_cleanup':cleanup_result,'cleanup_error':cleanup_error}
    write_json(directory/'RESULT.json',value)
    with control.locked() as state:
        state['calls'][call].update(status=status,final=status in {'completed','timed_out'},
            partial_artifact=partial,record=str(directory/'RESULT.json'))
    return value
