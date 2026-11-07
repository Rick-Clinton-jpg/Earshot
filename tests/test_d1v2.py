"""Offline design fixtures; none are study observations."""
import hashlib
import json
from datetime import datetime,timedelta,timezone
from types import SimpleNamespace
import pytest
from earshot.d1v2 import calls,run_stage,command,main,parse_stream
from earshot.d1v2_score import task_summary,arm_summary,cross_arm,PAIRS
from earshot.reliability import AttemptRunner,Control


@pytest.fixture(autouse=True)
def fake_version_only(monkeypatch):
    import subprocess
    original=subprocess.check_output
    def check(args,*a,**kw):
        if len(args)==2 and args[1]=='--version' and args[0] in ('fixture','codex'):
            return 'fixture' if kw.get('text') else b'fixture'
        return original(args,*a,**kw)
    monkeypatch.setattr(subprocess,'check_output',check)

TASK={'id':'fixture','role':'primary','request':'Locate the validation function.','target':'A'}
FILES={c:f'fixture/{c}.py' for c in 'ABCD'}

def answer(pair):return {'required_memory_refs':[f'handoff_refs/{x}.txt' for x in pair]}
def rows(policy='pass',task=TASK):
    result=[]
    for group in ['free','incoming']:
        for spec in calls(task,FILES,group):
            incoming=spec['incoming_pair'];pair='AB'
            if incoming and (policy=='pass' or (policy=='relevant' and task['target'] in incoming)):pair=incoming
            result.append(dict(spec,answer=answer(pair),classification='accepted'))
    return result

@pytest.mark.parametrize('policy,k,cout,kalt',[('pass',1,0,1),('standard',1/6,1,0),('relevant',.5,1,1)])
def test_fake_output_patterns(policy,k,cout,kalt):
    s=task_summary(TASK,rows(policy));assert s['valid'];assert s['rates']['K']==k
    assert s['rates']['C_out']==cout;assert s['rates']['K_alt']==kalt
    assert s['K_alt_pattern_outcome']=='unresolved'

@pytest.mark.parametrize('free,expected',[(['AB','AB','AB'],'AB'),(['AB','AC','AB'],'AB'),(['AB','AC','AD'],None),(['AB','AB',None],'AB'),(['AB','AC',None],None)])
def test_majority(free,expected):
    rr=rows()
    for row,pair in zip(rr,free):
        row['answer']=answer(pair) if pair else None;row['classification']='accepted' if pair else 'gate_rejected'
    s=task_summary(TASK,rr);assert s['default']==expected
    if None in free:assert s['rates']['default_stability'] is None

def test_rates_exclude_missing_and_agreement_requires_two_accepted():
    rr=rows();rr[3]['classification']='timed_out';rr[4]['classification']='gate_rejected'
    s=task_summary(TASK,rr)
    assert not s['valid'] # only four target-in answers remain
    assert s['rates']['K']==1;assert s['agreement_by_pair']['AB'] is None
    assert s['agreement_pairs_evaluable']==5

def test_equal_weight_and_cross_pairing():
    a=arm_summary([TASK],rows());b=arm_summary([TASK],rows('standard'))
    assert cross_arm(a,b)['overlap_count']==1
    b['selected_valid_ids']=[];assert cross_arm(a,b)['status']=='undefined'
    assert a['attempted_primary_tasks']['task_count']==1

class FakeAttempts:
    def __init__(self,bad=None):self.control=SimpleNamespace(blocked=None);self.seen=[];self.bad=bad
    def run(self,name,prompt):
        self.seen.append(name)
        return {'classification':'gate_rejected' if name.startswith(str(self.bad)+'-') else 'accepted','answer':answer('AB')}

def test_phase_order_and_conditional_reserves():
    tasks=[dict(TASK,id=f'p{n}') for n in range(12)]+[dict(TASK,id='reserve',role='reserve')]
    fake=FakeAttempts();run_stage(tasks,FILES,fake)
    assert len(fake.seen)==180
    assert all('free' in n for n in fake.seen[:3]);assert all('incoming' in n for n in fake.seen[3:15])
    fake=FakeAttempts('p0');result=run_stage(tasks,FILES,fake)
    assert len(fake.seen)==195;assert result['tasks']['reserve']['valid']

def test_prompts_do_not_depend_on_backend():
    codex=[hashlib.sha256(c['prompt'].encode()).hexdigest() for c in calls(TASK,FILES,'incoming')]
    claude=[hashlib.sha256(c['prompt'].encode()).hexdigest() for c in calls(TASK,FILES,'incoming')]
    assert codex==claude

@pytest.mark.parametrize('backend',['codex','claude'])
@pytest.mark.parametrize('marker',['PENDING_RECON','PENDING_RICK','PENDING_REVIEW'])
def test_both_runner_arms_refuse_pending_before_io(tmp_path,backend,marker,monkeypatch):
    reg=tmp_path/'reg.json';reg.write_text(json.dumps({'method':marker}))
    monkeypatch.setattr('subprocess.Popen',lambda *a,**kw:pytest.fail('process must not start'))
    with pytest.raises(RuntimeError):
        main(['--backend',backend,'--repo',str(tmp_path),'--branch','main','--registration',str(reg),'--seal','absent','--seal-digest','absent','--backend-config','absent','--workspace',str(tmp_path),'--run-dir',str(tmp_path/'run')])
    assert not (tmp_path/'run').exists()

def test_scorer_refuses_pending(tmp_path):
    from earshot.d1v2_score import main as score
    reg=tmp_path/'reg.json';reg.write_text('{"inference_method":"PENDING_REVIEW"}')
    with pytest.raises(RuntimeError):score(['--repo',str(tmp_path),'--branch','main','--registration',str(reg),'--seal','absent','--seal-digest','absent','--ledger','absent','--ledger-digest','absent','--run-dir','absent'])

def test_parser_missing_or_unparsable_is_not_answer():
    assert parse_stream('garbage','codex_jsonl')[0] is None
    text=json.dumps({'type':'item.completed','item':{'type':'agent_message','text':json.dumps(answer('AB'))}})
    assert parse_stream(text,'codex_jsonl')[0]==answer('AB')


def test_backend_cutoff_rechecked_after_publication(tmp_path,monkeypatch):
    from earshot.d1v2 import Backend
    now=datetime.now(timezone.utc)
    clock=SimpleNamespace(now=lambda:now,sleep=lambda _:None)
    control=Control(tmp_path,now+timedelta(seconds=180),clock=clock)
    config={'backend':'codex','cli':'codex','model':'fixture','effort':'low','output_method':'codex_jsonl','version':'fixture'}
    backend=Backend(config,tmp_path,tmp_path/'schema',lambda:None)
    monkeypatch.setattr('subprocess.Popen',lambda *a,**kw:pytest.fail('cutoff forbids launch'))
    assert backend('fixture','prompt',control)['administrative_status']=='stopped_by_cutoff'


def test_fake_process_records_timeout_and_reaps_group(tmp_path,monkeypatch):
    from earshot.d1v2 import Backend
    import subprocess
    now=datetime.now(timezone.utc)
    control=Control(tmp_path,now+timedelta(hours=1))
    class Process:
        pid=123456789;returncode=-9
        def __init__(self):self.n=0
        def communicate(self,*a,**kw):
            self.n+=1
            if self.n==1:raise subprocess.TimeoutExpired('fixture',180)
            return b'',b'fixture timeout'
    process=Process();killed=[]
    monkeypatch.setattr('subprocess.Popen',lambda *a,**kw:process)
    monkeypatch.setattr('os.killpg',lambda *a:killed.append(a))
    backend=Backend({'backend':'codex','cli':'fixture','model':'fixture','effort':'low','output_method':'codex_jsonl','version':'fixture'},tmp_path,tmp_path/'schema',lambda:None)
    result=backend('fixture','prompt',control)
    assert result['timed_out'];assert len(killed)==1;assert process.n==2


def test_fake_cli_usage_pause_drains_inflight_and_records_left(tmp_path,monkeypatch):
    import threading
    from earshot.d1v2 import Backend
    barrier=threading.Barrier(3);mutex=threading.Lock();launched=[]
    patterns=json.loads((__import__('pathlib').Path(__file__).resolve().parents[1]/'earshot/system_issue_patterns.json').read_text())
    message=patterns['codex_trial_usage_messages'][0]
    class Process:
        pid=123456789
        def __init__(self,index):self.index=index;self.returncode=1 if index==0 else 0
        def communicate(self,*a,**kw):
            barrier.wait(timeout=5)
            event={'type':'error','message':message} if self.index==0 else {'type':'item.completed','item':{'type':'agent_message','text':json.dumps(answer('AB'))}}
            return json.dumps(event).encode(),b''
    def popen(*a,**kw):
        with mutex:
            index=len(launched);launched.append(index)
        return Process(index)
    monkeypatch.setattr('subprocess.Popen',popen)
    control=Control(tmp_path,datetime.now(timezone.utc)+timedelta(hours=1))
    backend=Backend({'backend':'codex','cli':'fixture','model':'fixture','effort':'low','output_method':'codex_jsonl','version':'fixture'},tmp_path,tmp_path/'schema',lambda:None)
    attempts=AttemptRunner(tmp_path,patterns,control,backend,reserve_at_launch=True)
    run_stage([TASK],FILES,attempts)
    assert len(launched)==3
    assert len(list((tmp_path/'traces').glob('*.json')))==2
    pause=json.loads((tmp_path/'pauses.json').read_text())[0]
    assert pause['reason']=='usage limit' and len(pause['calls_finished'])==2 and len(pause['calls_left'])==13
    assert all('incoming' not in name for name in pause['calls_finished'])


def test_cutoff_finalization_without_model_launch(tmp_path):
    from earshot.d1v2 import finalize_cutoff
    now=datetime.now(timezone.utc);control=Control(tmp_path,now+timedelta(seconds=179))
    (tmp_path/'plan.json').write_text(json.dumps({'calls':{'never-launched':{'name':'never-launched','task_id':'fixture','group':'free','prompt_sha256':'fixture'}}}))
    finalize_cutoff(tmp_path,control)
    row=json.loads((tmp_path/'stopped/never-launched.json').read_text())
    assert row['administrative_status']=='stopped_by_cutoff' and row['attempts']==0


def test_manual_pause_between_precheck_and_spawn_blocks_launch(tmp_path,monkeypatch):
    from earshot.d1v2 import Backend
    control=Control(tmp_path,datetime.now(timezone.utc)+timedelta(hours=1))
    original=control.before_launch;checks=[]
    def interleaving():
        status=original()
        if not checks:
            checks.append('first');control.manual_pause('usage limit','other-worker','usage limit')
        return status
    monkeypatch.setattr(control,'before_launch',interleaving)
    monkeypatch.setattr('subprocess.Popen',lambda *a,**kw:pytest.fail('must not launch after another worker pauses'))
    backend=Backend({'backend':'codex','cli':'fixture','model':'fixture','effort':'low','output_method':'codex_jsonl','version':'fixture'},tmp_path,tmp_path/'schema',lambda:None)
    assert backend('call','fixture',control)['administrative_status']=='paused_usage_limit'


def test_codex_version_probe_runs_for_every_call(tmp_path,monkeypatch):
    from earshot.d1v2 import Backend
    probes=[]
    def version(*a,**kw):probes.append(a);return 'fixture'
    monkeypatch.setattr('subprocess.check_output',version)
    class Process:
        pid=123456789;returncode=0
        def communicate(self,*a,**kw):return b'',b''
    monkeypatch.setattr('subprocess.Popen',lambda *a,**kw:Process())
    backend=Backend({'backend':'codex','cli':'fixture','model':'fixture','effort':'low','output_method':'codex_jsonl','version':'fixture'},tmp_path,tmp_path/'schema',lambda:None)
    control=Control(tmp_path,datetime.now(timezone.utc)+timedelta(hours=1))
    for name in ['one','two']:
        row=backend(name,'fixture',control);assert row['cli_version_raw']=='fixture'
    assert len(probes)==2


def test_claude_inline_schema_and_process_environment(tmp_path,monkeypatch):
    from earshot.d1v2 import Backend
    schema=tmp_path/'schema.json';schema.write_text('{"type": "object"}')
    seen=[]
    class Process:
        pid=123456789;returncode=1
        def communicate(self,data,**kw):assert data==b'fixture prompt';return b'',b'unknown fixture error'
    def popen(args,**kw):seen.append((args,kw));return Process()
    monkeypatch.setattr('subprocess.Popen',popen)
    config={'backend':'claude','cli':'claude','model':'claude-sonnet-5-5','version':'2.1.319','argv':['claude','-p','--json-schema','{schema_json}'],'output_method':'claude_stream_json','env':{'DISABLE_AUTOUPDATER':'1'},'state_root':str(tmp_path/'state')}
    backend=Backend(config,tmp_path,schema,lambda:None)
    backend('call','fixture prompt',Control(tmp_path/'run',datetime.now(timezone.utc)+timedelta(hours=1)))
    assert seen[0][0][-1]=='{"type":"object"}'
    assert seen[0][1]['env']['DISABLE_AUTOUPDATER']=='1' and 'PATH' in seen[0][1]['env']


def test_workspace_parent_siblings_are_launch_fault(tmp_path):
    from earshot.d1v2 import verify_workspace
    workspace=tmp_path/'workspace';workspace.mkdir();(tmp_path/'unrelated').write_text('fixture')
    with pytest.raises(RuntimeError,match='parent must contain only'):verify_workspace(workspace,{})


def test_later_pause_does_not_rewrite_earlier_pause_counts(tmp_path):
    from earshot.d1v2 import record_drained_pause
    control=Control(tmp_path,datetime.now(timezone.utc)+timedelta(hours=1))
    (tmp_path/'plan.json').write_text('{"calls":{"one":{},"two":{}}}')
    control.manual_pause('usage limit','one','usage limit');record_drained_pause(tmp_path,control)
    original=json.loads((tmp_path/'pauses.json').read_text())[0]
    control.resume_by_rick()
    (tmp_path/'traces').mkdir();(tmp_path/'traces/one.json').write_text('test-only completed call')
    control.manual_pause('usage limit','two','usage limit');record_drained_pause(tmp_path,control)
    events=json.loads((tmp_path/'pauses.json').read_text())
    assert events[0]==original
    assert events[-1]['calls_finished']==['one'] and events[-1]['calls_left']==['two']


def test_cutoff_does_not_schedule_unused_reserves(tmp_path):
    control=Control(tmp_path,datetime.now(timezone.utc)+timedelta(seconds=179))
    runner=AttemptRunner(tmp_path,{'patterns':[]},control,lambda *a:pytest.fail('no model launch'))
    tasks=[TASK,dict(TASK,id='unused-reserve',role='reserve')]
    run_stage(tasks,FILES,runner)
    plan=json.loads((tmp_path/'plan.json').read_text())['calls']
    assert len(plan)==15 and all('unused-reserve' not in name for name in plan)


def test_cutoff_does_not_relabel_configuration_fault_as_unlaunched(tmp_path):
    from earshot.d1v2 import finalize_cutoff
    control=Control(tmp_path,datetime.now(timezone.utc)+timedelta(seconds=179))
    (tmp_path/'plan.json').write_text('{"calls":{"fault":{"name":"fault"}}}')
    (tmp_path/'configuration_fault').mkdir();(tmp_path/'configuration_fault/fault-attempt1.json').write_text('{"configuration_fault":["test-only mismatch"]}')
    finalize_cutoff(tmp_path,control)
    assert not (tmp_path/'stopped/fault.json').exists()


def test_workspace_parent_check_uses_actual_symlink_target(tmp_path):
    from earshot.d1v2 import verify_workspace
    real=tmp_path/'real';real.mkdir();workspace=real/'workspace';workspace.mkdir();(real/'sibling').write_text('fixture')
    alias_parent=tmp_path/'isolated-looking';alias_parent.mkdir();alias=alias_parent/'workspace';alias.symlink_to(workspace,target_is_directory=True)
    with pytest.raises(RuntimeError,match='parent must contain only'):verify_workspace(alias,{})
