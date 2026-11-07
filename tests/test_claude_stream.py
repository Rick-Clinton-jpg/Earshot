"""Raw pinned fixtures and explicitly synthetic variants; no live CLI calls."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime,timedelta,timezone
import pytest
from jsonschema import validate
from earshot.claude_stream import parse_claude,parse_events,version_number,verify_project_state,project_key
from earshot.reliability import classify,AttemptRunner,Control,error_text
from earshot.gate import gate_handoff

ROOT=Path(__file__).resolve().parents[1]
FIXTURES=ROOT/'tests/fixtures/claude_recon'
CONFIG={'backend':'claude','model':'claude-sonnet-5-5','version':'2.1.319'}
WORKSPACE='/home/user/earshot_check/ws/workspace'
PATTERNS=json.loads((ROOT/'earshot/system_issue_patterns.json').read_text())

def stream(name):return (FIXTURES/(name+'_call.jsonl')).read_text()
def variant(edit):
    events=parse_events(stream('relay'));edit(events)
    return '\n'.join(json.dumps(e) for e in events)
def result(events):return next(e for e in events if e.get('type')=='result')
def init(events):return next(e for e in events if e.get('subtype')=='init')
def rate(events):return next(e for e in events if e.get('type')=='rate_limit_event')['rate_limit_info']

def test_fixture_bytes_and_provenance():
    provenance=json.loads((FIXTURES/'PROVENANCE.json').read_text())
    assert provenance['source_commit']=='c90d5c6411b9bcc035ae4cc2282cc144516e5351'
    for e in provenance['files']:
        data=(ROOT/e['path']).read_bytes();assert len(data)==e['bytes'];assert hashlib.sha256(data).hexdigest()==e['sha256']
    for e in json.loads((FIXTURES/'MANIFEST.json').read_text())['files']:
        data=(FIXTURES/Path(e['path']).name).read_bytes();assert hashlib.sha256(data).hexdigest()==e['sha256']

@pytest.mark.parametrize('name,schema',[('relay','sender.schema.json'),('listener','answer.schema.json')])
def test_real_fixtures_parse_and_validate(name,schema):
    row=parse_claude(stream(name),WORKSPACE,CONFIG)
    assert not row['configuration_fault'] and not row['provider_error']
    validate(row['answer'],json.loads((ROOT/'earshot'/schema).read_text()))
    assert row['cli_version']=='2.1.319' and row['usage_pause_reason'] is None
    if name=='relay':
        handoff,status=gate_handoff(row['answer'],{'public_refs':['A','B']})
        assert status=='accepted' and handoff['required_memory_refs']==['handoff_refs/A.txt','handoff_refs/B.txt']

def test_real_isolation_fixture_rejected_as_relay_init():
    row=parse_claude(stream('isolation'),WORKSPACE,CONFIG)
    assert 'init tools differ from relay allowlist' in row['configuration_fault']
    assert classify(dict(row,exit_code=0),PATTERNS)[0]=='configuration_fault'

@pytest.mark.parametrize('key,value',[('model','other'),('claude_code_version','wrong'),('tools',['Read']),('mcp_servers',['x']),('slash_commands',['x']),('skills',['x']),('additional_directories',['/tmp']),('permissionMode','other'),('cwd','/tmp')])
def test_synthetic_init_drift_is_configuration_fault(key,value):
    row=parse_claude(variant(lambda es:init(es).__setitem__(key,value)),WORKSPACE,CONFIG)
    assert row['configuration_fault']

@pytest.mark.parametrize('key,value',[('is_error',True),('api_error_status',429),('subtype','error_max_turns')])
def test_synthetic_exit_zero_provider_error_never_gate_rejected(key,value):
    row=parse_claude(variant(lambda es:result(es).__setitem__(key,value)),WORKSPACE,CONFIG)
    assert row['answer'] is None and row['provider_error']
    assert classify(dict(row,exit_code=0),PATTERNS)[0]=='system_issue'

def test_synthetic_failed_rate_status_is_usage_limit():
    def edit(es):result(es)['is_error']=True;rate(es)['status']='rejected'
    row=parse_claude(variant(edit),WORKSPACE,CONFIG)
    assert row['usage_pause_reason']=='usage limit'
    assert classify(dict(row,exit_code=0),PATTERNS)==('system_issue',['rate_limit'])

def test_success_missing_structured_answer_is_gate_rejection():
    row=parse_claude(variant(lambda es:result(es).pop('structured_output')),WORKSPACE,CONFIG)
    assert not row['provider_error']
    assert classify(dict(row,exit_code=0),PATTERNS)[0]=='gate_rejected'

def test_synthetic_spawned_subagent_stops_arm(tmp_path):
    row=parse_claude(variant(lambda es:result(es)['subagent_stats'].__setitem__('spawned',1)),WORKSPACE,CONFIG)
    control=Control(tmp_path,datetime.now(timezone.utc)+timedelta(hours=1))
    out=AttemptRunner(tmp_path,PATTERNS,control,lambda *a:dict(row,exit_code=0)).run('call','fixture')
    assert out['administrative_status']=='configuration_fault' and control.blocked
    assert not list((tmp_path/'traces').glob('*.json'))
    assert (tmp_path/'configuration_fault/call-attempt1.json').exists()

def test_synthetic_usage_90_keeps_answer_and_pauses_with_both_resets(tmp_path):
    row=parse_claude(variant(lambda es:rate(es)['unifiedWindows']['five_hour'].__setitem__('utilization',.90)),WORKSPACE,CONFIG)
    control=Control(tmp_path,datetime.now(timezone.utc)+timedelta(hours=1))
    runner=AttemptRunner(tmp_path,PATTERNS,control,lambda *a:dict(row,exit_code=0))
    out=runner.run('call','fixture');assert out['classification']=='accepted'
    assert control.before_launch()=='paused_usage_90'
    pause=json.loads((tmp_path/'pauses.json').read_text())[0]
    assert pause['reason']=='usage at 90%' and set(pause['quota_windows'])=={'five_hour','seven_day'}
    assert all(w['reset_utc'] for w in pause['quota_windows'].values())
    assert runner.run('call','fixture')==out # Never retry this completed answer.

def test_missing_init_during_failure_is_not_configuration_drift():
    text=json.dumps({'type':'result','subtype':'error','is_error':True,'result':'unknown failure'})
    row=parse_claude(text,WORKSPACE,CONFIG)
    assert not row['configuration_fault']
    assert classify(dict(row,exit_code=0),PATTERNS)==('system_issue',['unclassified_no_answer'])

def test_rate_limit_key_names_are_not_error_text():
    row=parse_claude(stream('relay'),WORKSPACE,CONFIG)
    assert 'rateLimitType' not in error_text(row)
    assert classify(dict(row,exit_code=0),PATTERNS)==('accepted',[])

def test_fixed_offset_import_without_timezone_database():
    code="""import sys
class NoZoneInfo:
    def find_spec(self,fullname,path=None,target=None):
        if fullname in ('zoneinfo','tzdata'):raise ImportError('no timezone database in this test')
sys.meta_path.insert(0,NoZoneInfo())
from earshot.reliability import LOCAL,reset_time
from datetime import datetime,timezone,timedelta
assert LOCAL.utcoffset(None)==timedelta(hours=5,minutes=30)
for name in ('IST','Asia/Calcutta','Asia/Kolkata'):
    dt,_=reset_time('reset at 06:00 '+name,datetime(2026,11,7,tzinfo=timezone.utc))
    assert dt.hour==0 and dt.minute==30
"""
    subprocess.run([sys.executable,'-c',code],cwd=ROOT,check=True)

def test_project_state_allows_only_session_tool_results(tmp_path):
    project=tmp_path/'projects'/project_key(WORKSPACE)
    results=project/'00000000-0000-0000-0000-000000000001'/'tool-results';results.mkdir(parents=True);(results/'result.txt').write_text('fixture')
    assert verify_project_state(WORKSPACE,tmp_path)==str(project)
    (project/'memory').mkdir()
    with pytest.raises(RuntimeError):verify_project_state(WORKSPACE,tmp_path)

def test_claude_cli_version_normalization():
    assert version_number((FIXTURES/'claude_version.txt').read_text())=='2.1.319'
