from datetime import datetime,timedelta,timezone
import hashlib
import json
from pathlib import Path
import pytest
from earshot.reliability import AttemptRunner,Control,classify,reset_time,write_new

ROOT=Path(__file__).resolve().parents[1]
PATTERNS=json.loads((ROOT/'earshot/system_issue_patterns.json').read_text())

class FakeClock:
    def __init__(self):self.value=datetime(2026,11,7,0,0,tzinfo=timezone.utc);self.sleeps=[]
    def now(self):return self.value
    def sleep(self,s):self.sleeps.append(s);self.value+=timedelta(seconds=s)


def good():return {'exit_code':0,'answer':{'required_memory_refs':['handoff_refs/A.txt','handoff_refs/B.txt'],'note':'fake'}}
def issue(message='usage limit'):return {'exit_code':1,'answer':None,'events':[{'type':'error','message':message}]}

def test_usage_pause_requires_rick_then_same_prompt_retry(tmp_path):
    clock=FakeClock();control=Control(tmp_path,clock.now()+timedelta(days=1),clock=clock);seen=[]
    message=PATTERNS['codex_trial_usage_messages'][0]
    def fake(name,prompt,ctrl):
        seen.append((prompt,clock.now()))
        return issue(message) if len(seen)==1 else good()
    runner=AttemptRunner(tmp_path,PATTERNS,control,fake)
    assert runner.run('call','identical prompt')['administrative_status']=='paused_usage_limit'
    assert runner.run('other','other prompt')['administrative_status']=='paused_usage_limit'
    assert len(seen)==1 and not clock.sleeps
    # A plain process restart does not authorize resume.
    restarted=Control(tmp_path,control.cutoff,clock=clock)
    assert restarted.before_launch()=='paused_usage_limit'
    restarted.resume_by_rick()
    out=AttemptRunner(tmp_path,PATTERNS,restarted,fake).run('call','identical prompt')
    assert out['classification']=='accepted' and out['attempt']==2
    assert [x[0] for x in seen]==['identical prompt']*2
    assert (tmp_path/'system_issue/call-attempt1.json').exists()
    events=json.loads((tmp_path/'pauses.json').read_text())
    assert [e['event'] for e in events]==['manual_pause','resume_authorized_by_rick']
    assert 'trial_usage_limit' in json.loads((tmp_path/'system_issue/call-attempt1.json').read_text())['system_issue_matches']


@pytest.mark.parametrize('record,expected',[(good(),'accepted'),({'exit_code':0,'answer':None},'gate_rejected'),({'exit_code':0,'answer':{'required_memory_refs':['bad']}},'gate_rejected'),({'exit_code':None,'answer':None,'timed_out':True},'timed_out'),({'exit_code':1,'answer':good()['answer'],'stderr':'usage limit'},'unclassified_failure')])
def test_final_outcomes_never_retry(tmp_path,record,expected):
    clock=FakeClock();control=Control(tmp_path,clock.now()+timedelta(hours=6),clock=clock);calls=[]
    def fake(*a):calls.append(a);return record.copy()
    r=AttemptRunner(tmp_path,PATTERNS,control,fake)
    out=r.run('call','prompt');before=(tmp_path/'traces/call.json').read_bytes()
    assert out['classification']==expected
    assert r.run('call','prompt')==out
    assert len(calls)==1 and (tmp_path/'traces/call.json').read_bytes()==before


def test_five_system_issues_stop_arm(tmp_path):
    clock=FakeClock();control=Control(tmp_path,clock.now()+timedelta(days=1),clock=clock);calls=[]
    def fake(*args):calls.append(1);return issue('network unreachable')
    result=AttemptRunner(tmp_path,PATTERNS,control,fake).run('call','prompt')
    assert result['administrative_status']=='system_issue_not_run' and len(calls)==5
    assert len(list((tmp_path/'system_issue').glob('*.json')))==5
    again=Control(tmp_path,clock.now()+timedelta(hours=6),clock=clock)
    assert again.blocked and again.before_launch()=='arm_stopped'


def test_attempt_files_exclusive(tmp_path):
    p=tmp_path/'trace.json';write_new(p,{'first':1});before=p.read_bytes()
    with pytest.raises(FileExistsError):write_new(p,{'second':2})
    assert p.read_bytes()==before


def test_counter_survives_restart(tmp_path):
    prompt='prompt';digest=hashlib.sha256(prompt.encode()).hexdigest()
    for n in [1,2]:
        write_new(tmp_path/f'attempt_state/call/attempt{n}.json',{'attempt':n,'prompt_sha256':digest})
        write_new(tmp_path/f'system_issue/call-attempt{n}.json',issue())
    clock=FakeClock();control=Control(tmp_path,clock.now()+timedelta(days=1),clock=clock)
    out=AttemptRunner(tmp_path,PATTERNS,control,lambda *a:good()).run('call',prompt)
    assert out['attempt']==3


def test_cutoff_does_not_wait_for_late_reset(tmp_path):
    clock=FakeClock();control=Control(tmp_path,clock.now()+timedelta(minutes=10),clock=clock)
    r=AttemptRunner(tmp_path,PATTERNS,control,lambda *a:issue('network unreachable; try again at 11:00 PM')).run('call','prompt')
    assert r['administrative_status']=='stopped_by_cutoff'
    assert clock.now()==control.latest_launch
    assert not (tmp_path/'traces/call.json').exists()


def test_cutoff_no_call_launched(tmp_path):
    clock=FakeClock();control=Control(tmp_path,clock.now()+timedelta(seconds=179),clock=clock)
    def forbidden(*a):raise AssertionError('must not execute')
    out=AttemptRunner(tmp_path,PATTERNS,control,forbidden).run('call','prompt')
    assert out['administrative_status']=='stopped_by_cutoff'


@pytest.mark.parametrize('text',['HTTP 401','HTTP 403','status 429','HTTP 503','reconnecting... 2/5','network is unreachable','rate limit'])
def test_sealed_pattern_categories(text):assert classify(issue(text),PATTERNS)[0]=='system_issue'


def test_reset_timezone_and_fallback():
    now=datetime(2026,11,7,0,0,tzinfo=timezone.utc)
    dt,info=reset_time('try again at 3:34 AM',now)
    assert dt==datetime(2026,11,7,22,4,tzinfo=timezone.utc)
    dt,info=reset_time('reset at 01:00 UTC',now);assert dt.hour==1
    dt,info=reset_time('usage limit without a time',now);assert dt==now+timedelta(minutes=30) and info['parsed_reset_utc'] is None


def test_stopped_before_spawn_is_reusable_without_resampling(tmp_path):
    from datetime import datetime,timedelta,timezone
    from earshot.reliability import AttemptRunner,Control
    control=Control(tmp_path,datetime.now(timezone.utc)+timedelta(hours=1))
    runner=AttemptRunner(tmp_path,{'patterns':[]},control,lambda *a:{'administrative_status':'stopped_by_cutoff'})
    assert runner.run('stopped','same bytes')['administrative_status']=='stopped_by_cutoff'
    runner.execute=lambda *a:pytest.fail('administratively stopped call must not launch')
    assert runner.run('stopped','same bytes')['administrative_status']=='stopped_by_cutoff'
    assert control.blocked is None


def test_unknown_no_answer_pauses_not_agent_failure(tmp_path):
    clock=FakeClock();control=Control(tmp_path,clock.now()+timedelta(days=1),clock=clock)
    out=AttemptRunner(tmp_path,PATTERNS,control,lambda *a:issue('unrecognised fixture error')).run('unknown','same')
    assert out['administrative_status']=='paused_unclassified'
    trace=json.loads((tmp_path/'system_issue/unknown-attempt1.json').read_text())
    assert trace['classification']=='system_issue' and trace['system_issue_matches']==['unclassified_no_answer']
    assert not (tmp_path/'traces/unknown.json').exists()


def test_manual_pause_cutoff_overrides_resume(tmp_path):
    clock=FakeClock();control=Control(tmp_path,clock.now()+timedelta(minutes=10),clock=clock)
    control.manual_pause('usage limit','fixture','usage limit')
    clock.value+=timedelta(hours=1)
    assert control.resume_by_rick()=='stopped_by_cutoff'
    assert control.before_launch()=='stopped_by_cutoff'


def test_pause_before_actual_launch_does_not_consume_attempt(tmp_path):
    clock=FakeClock();control=Control(tmp_path,clock.now()+timedelta(days=1),clock=clock)
    def prelaunch(name,prompt,ctrl,reserve):
        ctrl.manual_pause('usage limit','another-call','usage limit')
        return {'administrative_status':'paused_usage_limit'}
    runner=AttemptRunner(tmp_path,PATTERNS,control,prelaunch,reserve_at_launch=True)
    assert runner.run('call','same')['administrative_status']=='paused_usage_limit'
    assert not list((tmp_path/'attempt_state/call').glob('attempt*.json'))
    control.resume_by_rick()
    def success(name,prompt,ctrl,reserve):reserve();return good()
    runner.execute=success
    assert runner.run('call','same')['attempt']==1


def test_failed_process_with_answer_is_final_but_limit_still_pauses(tmp_path):
    clock=FakeClock();control=Control(tmp_path,clock.now()+timedelta(days=1),clock=clock)
    record=dict(good(),exit_code=1,stderr='rate limit')
    runner=AttemptRunner(tmp_path,PATTERNS,control,lambda *a:record)
    out=runner.run('call','same')
    assert out['classification']=='unclassified_failure' and control.before_launch()=='paused_usage_limit'
    runner.execute=lambda *a:pytest.fail('answer must never be rerun')
    control.resume_by_rick();assert runner.run('call','same')==out
