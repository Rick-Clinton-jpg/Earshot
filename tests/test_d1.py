import json
from pathlib import Path
import subprocess
import pytest
from earshot import d1,d1_score,runner
from earshot.config import Config


def fake_run(folder,style,include_reserve=False):
    prior,files,tasks=d1.load_tasks()
    ids=prior['primary_task_ids'] + (prior['reserve_task_ids'][:1] if include_reserve else [])
    folder.mkdir(exist_ok=True)
    for tid in ids:
        task=tasks[tid]; chosen=task['target']+next(x for x in 'ABCD' if x!=task['target']); chosen=''.join(sorted(chosen))
        for slot in d1.slots(task):
            pair=chosen if style=='fixed' or slot['incoming_pair']=='free' else slot['incoming_pair']
            r={'name':slot['name'],'exit_code':0,'answer':{'required_memory_refs':d1.incoming_refs(pair),'note':'fake'},'elapsed_seconds':0}
            r=d1.annotate(r,task,slot)
            (folder/(slot['name']+'.json')).write_text(json.dumps(r))
    return prior,tasks


def test_always_keep(tmp_path):
    prior,tasks=fake_run(tmp_path,'keep')
    result=d1_score.analyze(tmp_path,prior['primary_task_ids'],prior['reserve_task_ids'],tasks)
    assert result['total_run']==168
    assert result['primary']['K_in']['mean']==result['primary']['K_out']['mean']==1
    assert result['primary']['delta']['mean']==0
    assert result['exact_one_sided_p']==1
    assert result['secondary_K_alt']['rule_outcome']=='keep relevant refs'


def test_fixed_target_partner(tmp_path):
    prior,tasks=fake_run(tmp_path,'fixed')
    result=d1_score.analyze(tmp_path,prior['primary_task_ids'],prior['reserve_task_ids'],tasks)
    assert all(t['delta']>0 for t in result['tasks'])
    assert result['primary']['R_add']['mean']==1
    assert result['exact_one_sided_p']==1/4096
    assert result['secondary_K_alt']['rule_outcome']=='rewrite to their own choice'


def test_invalid_and_reserve(tmp_path):
    prior,tasks=fake_run(tmp_path,'keep',True)
    tid=prior['primary_task_ids'][0]
    target=tasks[tid]['target']
    bad=[s for s in d1.slots(tasks[tid]) if s['incoming_pair']!='free' and target in s['incoming_pair']][:2]
    for slot in bad:
        r={'name':slot['name'],'exit_code':0,'answer':{'required_memory_refs':['bad','bad']},'elapsed_seconds':0}
        (tmp_path/(slot['name']+'.json')).write_text(json.dumps(d1.annotate(r,tasks[tid],slot)))
    result=d1_score.analyze(tmp_path,prior['primary_task_ids'],prior['reserve_task_ids'],tasks)
    assert result['total_rejected']==2
    assert result['valid_tasks']==12
    assert result['tasks'][0]['counts']['in']['accepted']==4
    assert result['replacements'][0]['reserve']==prior['reserve_task_ids'][0]
    assert result['replacements'][0]['invalid_primary']==tid


def test_free_disagreement_unresolved(tmp_path):
    prior,tasks=fake_run(tmp_path,'keep')
    for tid in prior['primary_task_ids']:
        slot=d1.slots(tasks[tid])[-1]
        r={'name':slot['name'],'exit_code':0,'answer':{'required_memory_refs':d1.incoming_refs('CD'),'note':'fake'},'elapsed_seconds':0}
        first=tmp_path/f'd1-{tid}-free-r1.json'
        original=json.loads(first.read_text())['output_pair']
        pair='AB' if original=='CD' else 'CD'
        r['answer']['required_memory_refs']=d1.incoming_refs(pair)
        (tmp_path/(slot['name']+'.json')).write_text(json.dumps(d1.annotate(r,tasks[tid],slot)))
    result=d1_score.analyze(tmp_path,prior['primary_task_ids'],prior['reserve_task_ids'],tasks)
    assert result['secondary_K_alt']['mean'] is None
    assert result['secondary_K_alt']['rule_outcome']=='unresolved'


def test_registration_lock(tmp_path):
    path=tmp_path/'registration.json'
    with pytest.raises(RuntimeError):runner.verify_registration(path)
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    path.write_text('{}')
    with pytest.raises(RuntimeError):runner.verify_registration(path)
    subprocess.run(['git','add','registration.json'],cwd=tmp_path,check=True)
    subprocess.run(['git','-c','user.name=Test Fixture','-c','user.email=fixture@example.invalid','commit','-qm','test registration'],cwd=tmp_path,check=True)
    result=runner.verify_registration(path)
    assert result['registration_commit_sha']
    path.write_text('{"edited":true}')
    with pytest.raises(RuntimeError,match='edited'):runner.verify_registration(path)


def test_runner_lock_precedes_cli(monkeypatch,tmp_path):
    def forbidden(*args,**kwargs):raise AssertionError('CLI reached')
    monkeypatch.setattr(subprocess,'run',forbidden)
    with pytest.raises(RuntimeError,match='registration'):
        runner.run_agent('test','prompt',tmp_path/'schema',Config(tmp_path,tmp_path/'run',stub=False,registration=tmp_path/'missing'))
    assert not (tmp_path/'run').exists()


def test_no_old_hidden_fields():
    _,_,tasks=d1.load_tasks()
    assert all(set(t)=={'id','request','target'} for t in tasks.values())
    assert len(d1.slots(next(iter(tasks.values()))))==14
