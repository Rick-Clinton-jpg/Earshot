"""Real subprocess fixtures for launch controls; no model/API/auth service."""
from datetime import datetime,timedelta,timezone
import json
import os
import shlex
import signal
from pathlib import Path
import subprocess
import sys
import threading
import time

import pytest

from earshot import partb_launch as launch
from earshot import partb_cli as cli
from earshot.partb import digest

NOW=datetime(2026,11,8,tzinfo=timezone.utc)
PATTERNS=[{'id':'usage_limit','regex':r'usage limit|rate.limit|too many requests'}]
DONE=json.dumps({'type':'item.completed','item':{'type':'agent_message','text':'Finished.'}})


def setup(tmp_path,code):
    session=cli.opaque_session(tmp_path);session.workspace.mkdir();cli.initialize_runtime(session)
    config='fixture = true\n';(session.config/'config.toml').write_text(config)
    (session.workspace/'source.py').write_text('VALUE = 1\n')
    prepared={'argv':[sys.executable,'-u','-B','-c',code],
       'env':{'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1'},
       'config_sha256':digest(config.encode()),'purpose':'practice','transport':'scripted_process',
       'workspace':str(session.workspace),'codex_home':str(session.config)}
    prepared['preparation_sha256']=launch.preparation_digest(prepared)
    return session,prepared


def control(tmp_path,**kwargs):
    return launch.PracticeControl(tmp_path/'journal',launch.stamp(NOW+timedelta(hours=1)),clock=lambda:NOW,**kwargs)


def run(c,s,p,**kwargs):
    return launch.run_prepared(c,'practice',s,p,'public prompt',timeout=3,grace=.2,patterns=PATTERNS,fixture=True,**kwargs)


def test_completed_attempt_is_immutable_and_skipped_after_restart(tmp_path):
    s,p=setup(tmp_path,'print('+repr(DONE)+')');c=control(tmp_path)
    result=run(c,s,p);assert result['status']=='completed'
    path=tmp_path/'journal/practice/attempt-01/RESULT.json';before=path.read_bytes()
    # An already finished call is skipped even though the old home has runtime state.
    (s.config/'history.jsonl').write_text('later runtime file')
    assert run(control(tmp_path),s,p)['status']=='already_final'
    assert path.read_bytes()==before
    assert not (path.parent.parent/'attempt-02').exists()
    with pytest.raises(RuntimeError,match='prompt changed'):
        launch.run_prepared(c,'practice',s,p,'changed',3,.2,PATTERNS,fixture=True)


@pytest.mark.parametrize('code,reason',[
    ("import sys;sys.stderr.write('usage limit reached');sys.exit(1)",'usage_limit'),
    ("import sys;sys.stderr.write('HTTP rate-limit error');sys.exit(1)",'usage_limit'),
    ("import sys;sys.stderr.write('unknown transport fault');sys.exit(1)",'unclassified_no_final_answer'),
    ("print('no final answer event')",'unclassified_no_final_answer')])
def test_limit_and_unknown_no_answer_pause_without_retry(tmp_path,code,reason):
    s,p=setup(tmp_path,code);c=control(tmp_path,scheduled=['practice','next'])
    result=run(c,s,p);assert result['status']=='system_issue'
    assert reason in result['system_issue_matches']
    state=json.loads((c.root/'control.json').read_text());assert state['paused']
    assert state['calls']['practice']['attempts']==1
    pause=json.loads(next(c.root.glob('pause-*.json')).read_text())
    assert pause['calls_left']==['practice','next']
    with pytest.raises(RuntimeError,match='paused'):run(c,s,p)
    assert len(list((c.root/'practice').glob('attempt-*')))==1


def test_explicit_resume_keeps_counts_and_requires_fresh_same_baseline(tmp_path):
    s,p=setup(tmp_path,"import sys;sys.stderr.write('usage limit');sys.exit(1)");c=control(tmp_path)
    run(c,s,p);c=control(tmp_path)
    with pytest.raises(ValueError,match='instruction'):c.resume_rick('')
    c.resume_rick('Rick explicitly authorized retry in this fixture')
    with pytest.raises(RuntimeError,match='fresh opaque'):run(c,s,p)
    second,prepared=setup(tmp_path,'print('+repr(DONE)+')')
    (second.workspace/'source.py').write_text('DIFFERENT = 1')
    with pytest.raises(RuntimeError,match='baseline changed'):run(c,second,prepared)
    (second.workspace/'source.py').write_text('VALUE = 1\n')
    result=run(c,second,prepared);assert result['attempt']==2 and result['status']=='completed'
    assert (c.root/'practice/attempt-01/RESULT.json').exists()


def test_partial_artifact_is_preserved_and_blocks_relaunch(tmp_path):
    s,p=setup(tmp_path,"from pathlib import Path;import sys;Path('source.py').write_text('changed');sys.exit(1)")
    c=control(tmp_path);result=run(c,s,p)
    assert result['partial_artifact']
    artifact=json.loads((c.root/'practice/attempt-01/artifact.json').read_text())
    assert artifact['baseline']!=artifact['files']
    with pytest.raises(RuntimeError,match='partial artifact'):c.resume_rick('Rick asks to resume')


def test_interrupted_attempt_requires_reconciliation(tmp_path):
    s,p=setup(tmp_path,'print('+repr(DONE)+')');c=control(tmp_path)
    with c.locked() as state:
        state['calls']['practice']={'status':'in_flight','final':False,'attempts':1,
            'prompt_sha256':digest(b'public prompt')}
    with pytest.raises(RuntimeError,match='unreconciled'):run(control(tmp_path),s,p)
    with pytest.raises(RuntimeError,match='in-flight'):c.resume_rick('Rick asks to resume')


def test_attempt_limit_cannot_be_reset(tmp_path):
    c=control(tmp_path,max_attempts=2)
    for number in [1,2]:
        s,p=setup(tmp_path,"import sys;sys.stderr.write('usage limit');sys.exit(1)")
        assert run(c,s,p)['attempt']==number
        if number==1:c.resume_rick('Rick permits next attempt')
    with pytest.raises(RuntimeError,match='attempt limit'):c.resume_rick('Rick asks again')
    with pytest.raises(RuntimeError,match='cannot change'):control(tmp_path,max_attempts=5)


def test_cutoff_does_not_launch_or_call_it_a_timeout(tmp_path,monkeypatch):
    s,p=setup(tmp_path,'raise RuntimeError("must never start")')
    c=launch.PracticeControl(tmp_path/'journal',launch.stamp(NOW+timedelta(seconds=3)),clock=lambda:NOW)
    monkeypatch.setattr(launch.subprocess,'Popen',lambda *a,**k:pytest.fail('launched past margin'))
    result=run(c,s,p)
    assert result['status']=='stopped_by_cutoff' and not result['process_launched']
    assert json.loads((c.root/'control.json').read_text())['calls']['practice']['attempts']==0


def test_cutoff_is_rechecked_immediately_before_popen(tmp_path,monkeypatch):
    s,p=setup(tmp_path,'raise RuntimeError("must never start")');c=control(tmp_path)
    current=[NOW];c.clock=lambda:current[0]
    original_write=launch.atomic_json
    def slow_reservation(path,state):
        original_write(path,state)
        if state['calls'].get('practice',{}).get('status')=='in_flight':
            current[0]=NOW+timedelta(hours=1)
    monkeypatch.setattr(launch,'atomic_json',slow_reservation)
    monkeypatch.setattr(launch.subprocess,'Popen',lambda *a,**k:pytest.fail('late launch'))
    result=run(c,s,p);assert result['status']=='stopped_by_cutoff' and not result['process_launched']
    assert (c.root/'practice/attempt-01/START.json').exists()


def test_timeout_kills_descendants_and_retains_partial_edit(tmp_path):
    sentinel=tmp_path/'late-child'
    child="import time;from pathlib import Path;time.sleep(1);Path("+repr(str(sentinel))+").write_text('escaped')"
    code="import subprocess,sys,time;from pathlib import Path;Path('source.py').write_text('partial');subprocess.Popen([sys.executable,'-c',"+repr(child)+"]);time.sleep(10)"
    s,p=setup(tmp_path,code);c=control(tmp_path)
    result=launch.run_prepared(c,'practice',s,p,'public prompt',.2,.1,PATTERNS,fixture=True)
    assert result['status']=='timed_out' and result['timed_out']
    assert (c.root/'practice/attempt-01/artifact.json').exists()
    time.sleep(1.1);assert not sentinel.exists()
    assert run(c,s,p)['status']=='already_final'


def test_pause_blocks_next_launch_while_inflight_call_finishes(tmp_path):
    c=control(tmp_path,scheduled=['practice','second','third'])
    slow,p=setup(tmp_path,"import time;time.sleep(.4);print("+repr(DONE)+")")
    fast,q=setup(tmp_path,"import sys;sys.stderr.write('usage limit');sys.exit(1)")
    results=[];errors=[]
    def worker():
        try:results.append(run(c,slow,p))
        except Exception as error:errors.append(error)
    thread=threading.Thread(target=worker);thread.start()
    deadline=time.monotonic()+3
    while time.monotonic()<deadline:
        with c.locked() as state:
            if state['calls'].get('practice',{}).get('status')=='in_flight':break
        time.sleep(.01)
    result=launch.run_prepared(c,'second',fast,q,'second prompt',3,.2,PATTERNS,fixture=True)
    assert result['status']=='system_issue'
    third,r=setup(tmp_path,'print('+repr(DONE)+')')
    with pytest.raises(RuntimeError,match='paused'):
        launch.run_prepared(c,'third',third,r,'third prompt',3,.2,PATTERNS,fixture=True)
    thread.join(4);assert not thread.is_alive() and not errors
    assert results[0]['status']=='completed'
    assert json.loads((c.root/'control.json').read_text())['paused']


def test_credential_copy_is_private_redacted_and_removed(tmp_path):
    s,p=setup(tmp_path,'pass');source=tmp_path/'auth.json'
    token='synthetic-fixture-credential-never-real'
    source.write_text(json.dumps({'tokens':{'access_token':token}}));source.chmod(0o600)
    before=source.read_bytes()
    with launch.CredentialCopy(source,s) as credentials:
        assert (s.config/'auth.json').stat().st_mode&0o777==0o600
        assert credentials.sanitize('prefix '+token)=='prefix [REDACTED_CREDENTIAL]'
        result=run(control(tmp_path),s,p,sanitize=credentials.sanitize)
        assert result['status']=='system_issue'  # No final-answer event from pass.
    assert not (s.config/'auth.json').exists() and source.read_bytes()==before
    source.chmod(0o644)
    with pytest.raises(RuntimeError,match='mode-0600'):
        with launch.CredentialCopy(source,s):pass


def test_secret_in_process_output_is_redacted_and_pauses(tmp_path):
    token='synthetic-fixture-credential-never-real';s,p=setup(tmp_path,'print('+repr(DONE+token)+')')
    source=tmp_path/'auth.json';source.write_text(json.dumps({'OPENAI_API_KEY':token}));source.chmod(0o600)
    c=control(tmp_path)
    with launch.CredentialCopy(source,s) as credentials:result=run(c,s,p,sanitize=credentials.sanitize)
    assert result['credential_output_redacted'] and result['status']=='system_issue'
    for file in c.root.rglob('*'):
        if file.is_file():assert token.encode() not in file.read_bytes()
    assert '[REDACTED_CREDENTIAL]' in (c.root/'practice/attempt-01/stdout.log').read_text()


def test_missing_executable_is_paused_with_attempt_record(tmp_path):
    s,p=setup(tmp_path,'pass');p['argv']=['/does-not-exist']
    p['preparation_sha256']=launch.preparation_digest(p)
    c=control(tmp_path);result=run(c,s,p)
    assert result['status']=='system_issue' and not result['process_launched']
    assert (c.root/'practice/attempt-01/RESULT.json').exists()


def test_changed_preparation_and_unauthorized_hosted_commands_refuse(tmp_path):
    s,p=setup(tmp_path,'pass');c=control(tmp_path)
    p['env']['UNREVIEWED']='value'
    with pytest.raises(RuntimeError,match='launch changed'):run(c,s,p)
    p.pop('transport');p['preparation_sha256']=launch.preparation_digest(p)
    with pytest.raises(RuntimeError,match='authorization'):
        launch.run_prepared(c,'practice',s,p,'public prompt',3,.2,PATTERNS)
    with pytest.raises(RuntimeError,match='fixture mode'):run(c,s,p)


def test_error_word_in_normal_answer_does_not_trigger_usage_pause():
    event=json.dumps({'type':'item.completed','item':{'type':'agent_message','text':'Added a usage limit test.'}})
    assert launch.outcome(0,False,event,'',PATTERNS)==('completed',[])


def test_artifact_capture_fault_is_retained_and_pauses(tmp_path,monkeypatch):
    s,p=setup(tmp_path,'print('+repr(DONE)+')');c=control(tmp_path)
    original=launch.snapshot;calls=[]
    def capture(path):
        calls.append(path)
        if len(calls)==2:raise ValueError('artifact exceeds per-file size cap')
        return original(path)
    monkeypatch.setattr(launch,'snapshot',capture)
    result=run(c,s,p)
    assert result['status']=='system_issue' and result['partial_artifact']
    assert result['system_issue_matches']==['artifact_capture_error']
    assert (c.root/'practice/attempt-01/stdout.log').exists()
    artifact=json.loads((c.root/'practice/attempt-01/artifact.json').read_text())
    assert artifact['files'] is None and 'size cap' in artifact['capture_error']
    with pytest.raises(RuntimeError,match='partial artifact'):c.resume_rick('Rick asks to resume')


CLI=Path('/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex')
PYTHON=Path('/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/env-radon/bin/python')


@pytest.mark.skipif(not CLI.exists() or not PYTHON.exists(),reason='pinned local CLI required')
def test_real_cli_loopback_uses_prepared_launcher_and_native_patch(tmp_path):
    from earshot.partb_protocol import LocalResponses,javascript,message
    session=cli.opaque_session();session.workspace.mkdir();cli.initialize_runtime(session)
    source=session.workspace/'source.py';source.write_text('VALUE = 1\n')
    patch=f'*** Begin Patch\n*** Update File: {source}\n@@\n-VALUE = 1\n+VALUE = 2\n*** End Patch'
    code='text(await tools.apply_patch('+json.dumps(patch)+'));'
    with LocalResponses(tmp_path/'requests',lambda body,n:javascript(code) if n==1 else message('Scripted edit finished.')) as server:
        prepared=launch.prepare_practice(session,CLI,PYTHON,loopback_url=server.url)
        c=launch.PracticeControl(tmp_path/'journal',launch.stamp(launch.utcnow()+timedelta(minutes=2)),scheduled=['practice'])
        result=launch.run_prepared(c,'practice',session,prepared,'Local scripted fixture. No hosted model.',30,1,PATTERNS,fixture=True)
    assert result['status']=='completed' and source.read_text()=='VALUE = 2\n'
    assert len(server.requests)==2
    assert json.loads((c.root/'practice/attempt-01/artifact.json').read_text())['fixture']
    assert prepared['env']['CODEX_HOME']==str(session.config)
    assert '--sandbox' not in prepared['argv'] and '--ignore-user-config' not in prepared['argv']


@pytest.mark.skipif(not CLI.exists() or not PYTHON.exists(),reason='pinned local CLI required')
def test_prepare_rejects_nonlocal_fixture_and_workspace_instructions(tmp_path):
    session=cli.opaque_session(tmp_path);session.workspace.mkdir();cli.initialize_runtime(session)
    with pytest.raises(RuntimeError,match='loopback'):
        launch.prepare_practice(session,CLI,PYTHON,loopback_url='https://example.com/v1')
    (session.workspace/'AGENTS.md').write_text('unreviewed')
    with pytest.raises(RuntimeError,match='instruction file'):
        launch.prepare_practice(session,CLI,PYTHON)


@pytest.mark.skipif(not CLI.exists() or not PYTHON.exists(),reason='pinned local CLI required')
def test_real_cli_detached_worker_is_stopped_without_killing_other_session(tmp_path):
    from earshot.partb_protocol import LocalResponses,javascript,message
    peer=cli.opaque_session();peer.workspace.mkdir();cli.initialize_runtime(peer)
    peer_code='import subprocess,sys; p=subprocess.Popen([sys.executable,"-B","-c","import time;time.sleep(15)"],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);print(p.pid)'
    cli.native_command(peer,CLI,PYTHON,[str(PYTHON.resolve()),'-sB','-c',peer_code],tmp_path/'peer')
    peer_pid=int((tmp_path/'peer/stdout.log').read_text())
    try:
        session=cli.opaque_session();session.workspace.mkdir();cli.initialize_runtime(session)
        late=session.workspace/'late-edit'
        child='import time;from pathlib import Path;time.sleep(2);Path('+repr(str(late))+').write_text("late")'
        parent='import subprocess,sys;from pathlib import Path;p=subprocess.Popen([sys.executable,"-B","-c",'+repr(child)+'],start_new_session=True,cwd="/usr/bin",env={},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);Path("child-pid.txt").write_text(str(p.pid));print("parent finished")'
        cmd=shlex.join([str(PYTHON.resolve()),'-sB','-c',parent])
        code='text(await tools.exec_command('+json.dumps({'cmd':cmd,'workdir':str(session.workspace),'login':False})+'));'
        with LocalResponses(tmp_path/'requests',lambda body,n:javascript(code) if n==1 else message('Scripted fixture complete.')) as server:
            prepared=launch.prepare_practice(session,CLI,PYTHON,loopback_url=server.url)
            c=launch.PracticeControl(tmp_path/'journal',launch.stamp(launch.utcnow()+timedelta(minutes=2)))
            result=launch.run_prepared(c,'practice',session,prepared,'Scripted local fixture.',30,1,PATTERNS,fixture=True)
        child_pid=int((session.workspace/'child-pid.txt').read_text())
        assert result['status']=='completed' and result['session_cleanup']['verified']
        assert child_pid in result['session_cleanup']['killed_pids']
        os.kill(peer_pid,0)  # A different sandbox session was not stopped.
        time.sleep(2.2);assert not late.exists()
    finally:
        try:os.kill(peer_pid,signal.SIGKILL)
        except ProcessLookupError:pass


@pytest.mark.skipif(not CLI.exists() or not PYTHON.exists(),reason='pinned local CLI required')
def test_unverified_session_cleanup_pauses_and_holds_artifact(tmp_path,monkeypatch):
    from earshot.partb_protocol import LocalResponses,message
    from earshot.partb_processes import SessionProcesses
    session=cli.opaque_session();session.workspace.mkdir();cli.initialize_runtime(session)
    def unavailable(self):raise RuntimeError('scripted cleanup check failed')
    monkeypatch.setattr(SessionProcesses,'finish',unavailable)
    with LocalResponses(tmp_path/'requests',lambda body,n:message('Scripted fixture complete.')) as server:
        prepared=launch.prepare_practice(session,CLI,PYTHON,loopback_url=server.url)
        c=launch.PracticeControl(tmp_path/'journal',launch.stamp(launch.utcnow()+timedelta(minutes=2)))
        result=launch.run_prepared(c,'practice',session,prepared,'Scripted local fixture.',30,1,PATTERNS,fixture=True)
    assert result['status']=='system_issue' and result['partial_artifact']
    assert result['system_issue_matches']==['session_cleanup_unverified']
    with pytest.raises(RuntimeError,match='partial artifact'):c.resume_rick('Rick asks to resume')


@pytest.mark.skipif(not CLI.exists() or not PYTHON.exists(),reason='pinned local CLI required')
def test_real_cli_retry_ignores_only_unchanged_controller_cleanup_canary(tmp_path):
    from earshot.partb_protocol import LocalResponses,message
    c=launch.PracticeControl(tmp_path/'journal',launch.stamp(launch.utcnow()+timedelta(minutes=3)))
    for number,text in [(1,''),(2,'Scripted fixture finished.')]:
        session=cli.opaque_session();session.workspace.mkdir();cli.initialize_runtime(session)
        (session.workspace/'source.py').write_text('VALUE = 1\n')
        with LocalResponses(tmp_path/f'requests-{number}',lambda body,n:message(text)) as server:
            prepared=launch.prepare_practice(session,CLI,PYTHON,loopback_url=server.url)
            result=launch.run_prepared(c,'practice',session,prepared,'Same public prompt.',30,1,PATTERNS,fixture=True)
        assert result['attempt']==number
        if number==1:
            assert result['status']=='system_issue' and not result['partial_artifact']
            c.resume_rick('Rick explicitly authorizes fixture resume')
        else:assert result['status']=='completed'


def test_journal_inside_workspace_is_refused(tmp_path):
    session,prepared=setup(tmp_path,'pass')
    c=launch.PracticeControl(session.workspace/'journal',launch.stamp(NOW+timedelta(hours=1)),clock=lambda:NOW)
    with pytest.raises(RuntimeError,match='outside the agent workspace'):run(c,session,prepared)


def test_cutoff_while_paused_marks_unlaunched_and_preserves_system_issue(tmp_path):
    c=control(tmp_path,scheduled=['practice','unlaunched'])
    session,prepared=setup(tmp_path,"import sys;sys.stderr.write('usage limit');sys.exit(1)")
    run(c,session,prepared)
    trace=c.root/'practice/attempt-01/RESULT.json';before=trace.read_bytes()
    c.clock=lambda:NOW+timedelta(hours=2)
    with pytest.raises(RuntimeError,match='cutoff'):c.resume_rick('Rick asks after cutoff')
    state=json.loads((c.root/'control.json').read_text())
    assert state['calls']['unlaunched']['status']=='stopped_by_cutoff'
    assert state['calls']['unlaunched']['attempts']==0
    assert state['calls']['practice']['status']=='system_issue'
    assert state['calls']['practice']['retry_stopped_by_cutoff']
    assert trace.read_bytes()==before


def test_cutoff_finalization_is_idempotent_and_does_not_close_inflight(tmp_path):
    c=control(tmp_path,scheduled=['active','unlaunched'])
    with c.locked() as state:
        state['calls']['active']={'status':'in_flight','final':False,'attempts':1,'prompt_sha256':'example'}
    c.clock=lambda:NOW+timedelta(hours=2)
    c.finish_cutoff();records=list(c.root.glob('cutoff-*.json'));assert len(records)==1
    c.finish_cutoff();assert list(c.root.glob('cutoff-*.json'))==records
    state=json.loads((c.root/'control.json').read_text())
    assert not state['calls']['active']['final']


def test_retry_cannot_change_model_or_limits(tmp_path):
    c=control(tmp_path)
    session,prepared=setup(tmp_path,"import sys;sys.stderr.write('usage limit');sys.exit(1)")
    run(c,session,prepared);c.resume_rick('Rick authorizes same-policy retry')
    fresh,changed=setup(tmp_path,'print('+repr(DONE)+')')
    changed['backend_policy']={'model':'different-model'}
    changed['preparation_sha256']=launch.preparation_digest(changed)
    with pytest.raises(RuntimeError,match='launch policy changed'):run(c,fresh,changed)
