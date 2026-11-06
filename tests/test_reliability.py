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

def test_usage_pause_then_same_prompt_retry(tmp_path):
    clock=FakeClock();control=Control(tmp_path,clock.now()+timedelta(days=1),clock=clock);seen=[]
    def fake(name,prompt,ctrl):
        seen.append((prompt,clock.now()))
        return issue('usage limit; try again at 5:32 AM') if len(seen)==1 else good()
    runner=AttemptRunner(tmp_path,PATTERNS,control,fake)
    out=runner.run('call','identical prompt')
    assert out['classification']=='accepted' and out['attempt']==2
    assert [x[0] for x in seen]==['identical prompt']*2
    assert seen[1][1]==datetime(2026,11,7,0,2,tzinfo=timezone.utc)
    assert (tmp_path/'system_issue/call-attempt1.json').exists()
    events=json.loads((tmp_path/'pauses.json').read_text());assert [e['event'] for e in events]==['system_issue_pause','resume']
    assert events[0]['parsed_reset_utc']=='2026-11-07T00:02:00Z'


@pytest.mark.parametrize('record,expected',[(good(),'accepted'),({'exit_code':0,'answer':None},'gate_rejected'),({'exit_code':0,'answer':{'required_memory_refs':['bad']}},'gate_rejected'),({'exit_code':None,'answer':None,'timed_out':True},'timed_out'),({'exit_code':2,'answer':None,'stderr':'unknown local fault'},'unclassified_failure'),({'exit_code':1,'answer':good()['answer'],'stderr':'usage limit'},'unclassified_failure')])
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
    def fake(*args):calls.append(1);return issue()
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
    r=AttemptRunner(tmp_path,PATTERNS,control,lambda *a:issue('usage limit; try again at 11:00 PM')).run('call','prompt')
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
