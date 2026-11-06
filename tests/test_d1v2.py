"""Offline design fixtures; none are study observations."""
import hashlib
import json
from datetime import datetime,timedelta,timezone
from types import SimpleNamespace
import pytest
from earshot.d1v2 import calls,run_stage,command,main,parse_stream
from earshot.d1v2_score import task_summary,arm_summary,cross_arm,PAIRS
from earshot.reliability import AttemptRunner,Control

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
    config={'backend':'codex','cli':'codex','model':'fixture','effort':'low','output_method':'codex_jsonl'}
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
    backend=Backend({'backend':'codex','cli':'fixture','model':'fixture','effort':'low','output_method':'codex_jsonl'},tmp_path,tmp_path/'schema',lambda:None)
    result=backend('fixture','prompt',control)
    assert result['timed_out'];assert len(killed)==1;assert process.n==2
