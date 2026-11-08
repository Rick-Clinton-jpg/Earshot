"""Scheduling and scoring fixtures. No model calls or real registrations."""
import base64
import copy
import json
from pathlib import Path
import subprocess
import sys
import importlib.util

import pytest

from earshot import partb as b
from earshot.partb_artifacts import separate_scratch
from earshot.partb_design import schedule,prompts,validate_schedule
from earshot.partb_integrity import (ready,source_closure,verify_source,verify_runtime,ledger_record,digest,StudyPermit)
from earshot.partb_study import StudyRunner,ScriptedBackend
from earshot.partb_score import score_rows,render_report,evaluation_from_logs


def rec(text):
    raw=text.encode();return {'kind':'file','sha256':b.digest(raw),'content':base64.b64encode(raw).decode(),'mode':0o644}


@pytest.fixture
def mini(tmp_path):
    repo=tmp_path/'repo';repo.mkdir();inputs=repo/'inputs';inputs.mkdir()
    clean={'radon/__init__.py':rec(''),'radon/calc.py':rec('VALUE = 1\n'),
           'radon/tests/test_calc.py':rec('def test_value():\n    assert True\n'),
           'pyproject.toml':rec('[tool.pytest.ini_options]\n')}
    broken=rec('VALUE = 0\n')
    task={'id':'fixture-task','target':'A','bug_report':'The value is incorrect.'}
    tasks={'tasks':[task],'candidate_files':dict(zip('ABCD',['radon/calc.py','radon/b.py','radon/c.py','radon/d.py']))}
    calls=schedule([task])
    values={'tasks':tasks,'schedule':{'calls':calls},'pristine':clean,
      'buggy_targets':{task['id']:{'source_file':'radon/calc.py','record':broken,
          'qualification':{'source_file':'radon/calc.py','diagnostic_case_ids':['fixture.test::test_value']}}},
      'diagnostics':{task['id']:['radon/tests/test_calc.py::test_value']},
      'baseline_case_ids':['fixture.test::test_value'],'system_issue_patterns':{'patterns':[{'id':'usage','regex':'usage limit'}]},
      'prompts':prompts([task],calls,tasks['candidate_files'])}
    paths={}
    for key,value in values.items():
        path=inputs/(key+'.json');b.write_json(path,value);paths[key]=str(path.relative_to(repo))
    registration={'status':'DRAFT','inputs':paths,'schedule_seed':20261108,'workers':2,'max_attempts':5,
        'timeout_seconds':180,'termination_grace_seconds':5,'cutoff_utc':'2050-01-01T00:00:00Z',
        'backend':{'python':sys.executable}}
    def evaluator(baseline,pristine,final,qualification,python,output,expected,diagnostics,metadata=None):
        summary=b.summarize_artifact(baseline,final,pristine,qualification['source_file'],metadata=metadata)
        good=b.contents(final['radon/calc.py'])==b.contents(pristine['radon/calc.py'])
        summary.update(evaluation_available=True,tests_pass=good,test_verified_admissible_repair=good and summary['admissible'])
        return summary
    return repo,registration,calls,clean,evaluator


def test_existing_180_schedule_and_prompt_contract_are_unchanged():
    repo=Path(__file__).resolve().parents[1];root=repo/'sprint/partB'
    tasks=json.loads((root/'tasks_draft.json').read_text())
    calls=json.loads((root/'schedule_draft.json').read_text())['calls']
    assert schedule(tasks['tasks'])==calls and len(calls)==180
    assert len(validate_schedule(tasks['tasks'],calls))==36
    rendered=prompts(tasks['tasks'],calls,tasks['candidate_files'])
    assert rendered==json.loads((root/'inputs/PROMPTS.json').read_text())
    for call in calls:
        payload=json.loads(rendered[call['name']].split('Trial input:\n')[1])
        assert set(payload)<= {'task_id','bug_report','candidate_files','handoff'}
        assert 'target' not in payload and 'condition' not in payload
        if call['condition']=='H0':assert 'handoff' not in payload
        else:assert payload['handoff']['required_memory_refs']==[f'handoff_refs/{c}.txt' for c in call['incoming_pair']]


def test_scripted_blocks_follow_fixed_actual_launch_order(mini,tmp_path):
    repo,reg,calls,clean,evaluator=mini
    runner=StudyRunner(repo,reg,tmp_path/'run',fixture_backend=ScriptedBackend(),evaluator=evaluator)
    status=runner.run_blocks();assert status['status']=='completed' and status['simulation']
    state=runner.state()
    assert [r['call'] for r in state['launch_sequence']]==[c['name'] for c in calls]
    assert all(v['attempts']==1 for v in state['calls'].values())
    # A restart adds no process attempts or evaluations to finished calls.
    restarted=StudyRunner(repo,reg,tmp_path/'run',fixture_backend=ScriptedBackend(),evaluator=evaluator)
    restarted.run_blocks();assert len(restarted.state()['launch_sequence'])==15
    assert len(list((tmp_path/'run').glob('calls/*/evaluation-*/result.json')))==15


def test_usage_pause_drains_only_admitted_calls_and_resume_preserves_them(mini,tmp_path):
    repo,reg,calls,clean,evaluator=mini;first=calls[0]['name']
    def program(call,session):
        if call['name']==first:return "import sys;sys.stderr.write('usage limit');sys.exit(1)"
        return 'import time,json;time.sleep(.05);print(json.dumps({"type":"item.completed","item":{"type":"agent_message","text":"fixture"}}))'
    runner=StudyRunner(repo,reg,tmp_path/'run',fixture_backend=ScriptedBackend(program),evaluator=evaluator)
    assert runner.run_blocks()['status']=='paused'
    before=runner.state();assert 1<=len(before['launch_sequence'])<=2
    assert all(v['call'] in [c['name'] for c in calls[:2]] for v in before['launch_sequence'])
    old=(tmp_path/'run/journal'/first/'attempt-01/RESULT.json').read_bytes()
    restarted=StudyRunner(repo,reg,tmp_path/'run',fixture_backend=ScriptedBackend(),evaluator=evaluator)
    restarted.control.resume_rick('Rick permits synthetic resume')
    assert restarted.run_blocks()['status']=='completed'
    assert restarted.state()['calls'][first]['attempts']==2
    assert (tmp_path/'run/journal'/first/'attempt-01/RESULT.json').read_bytes()==old


def test_evaluator_outage_retries_evaluation_not_model(mini,tmp_path):
    repo,reg,calls,clean,evaluator=mini;failed=[False]
    def flaky(*args,**kwargs):
        if not failed[0]:failed[0]=True;return {'evaluation_available':False,'reason':'synthetic evaluator outage'}
        return evaluator(*args,**kwargs)
    runner=StudyRunner(repo,reg,tmp_path/'run',fixture_backend=ScriptedBackend(),evaluator=flaky)
    assert runner.run_blocks()['status']=='paused'
    restarted=StudyRunner(repo,reg,tmp_path/'run',fixture_backend=ScriptedBackend(),evaluator=evaluator)
    restarted.control.resume_rick('Rick permits evaluator recovery fixture')
    assert restarted.run_blocks()['status']=='completed'
    assert all(v['attempts']==1 for v in restarted.state()['calls'].values())
    assert len(list((tmp_path/'run').glob('calls/*/evaluation-*/result.json')))==16


def test_live_draft_refuses_before_creating_runtime_or_process(mini,tmp_path,monkeypatch):
    repo,reg,*_=mini
    monkeypatch.setattr(subprocess,'Popen',lambda *a,**k:pytest.fail('model process must not launch'))
    with pytest.raises(RuntimeError,match='REGISTERED'):
        StudyRunner(repo,reg,tmp_path/'not-created',live=True)
    assert not (tmp_path/'not-created').exists()


def test_fixtures_cannot_be_ledgered_as_study_data(mini,tmp_path):
    repo,reg,_,_,evaluator=mini
    runner=StudyRunner(repo,reg,tmp_path/'run',fixture_backend=ScriptedBackend(),evaluator=evaluator);runner.run_blocks()
    binding={'seal_commit':'synthetic','seal_sha256':'synthetic','registration_sha256':'synthetic'}
    with pytest.raises(RuntimeError,match='simulation'):ledger_record(tmp_path/'run',binding)


def test_scratch_is_inventoried_but_symlinks_remain_out_of_policy():
    before={'radon/a.py':rec('x=0\n')};after={**before,'.scratch/report.txt':rec('temporary')}
    left,right,inventory=separate_scratch(before,after)
    assert left==right and '.scratch/report.txt' in inventory['final']
    after['.scratch/link']={'kind':'symlink','destination':'/outside'}
    left,right,_=separate_scratch(before,after)
    assert '.scratch/link' in right
    assert not b.summarize_artifact(left,right,before,'radon/a.py')['admissible']


@pytest.mark.parametrize('name',['repro.py','notes.txt','debug/results.json','image.bin'])
def test_new_regular_nonprotected_files_outside_radon_are_scratch(name):
    pristine={'radon/a.py':rec('VALUE=1\n')};buggy={'radon/a.py':rec('VALUE=0\n')}
    final={**pristine,name:rec('\0binary' if name=='image.bin' else 'print("repro")\n')}
    result=b.summarize_artifact(buggy,final,pristine,'radon/a.py')
    assert result['admissible'] and result['changed_paths']==['radon/a.py']
    assert result['scratch_file_count']==1 and result['scratch_files'][0]['path']==name
    assert result['reference_reversal_only'] and result['target_file_edited']


@pytest.mark.parametrize('name',['test_repro.py','repro_test.py','tests/helper.py','conftest.py','pyproject.toml',
    'pytest.ini','requirements-dev.txt','package.json','config.json','.env','.gitignore','setup.py','.scratch/pytest.ini',
    '.scratch/test_debug.py','radon/new.py','radon/notes.txt'])
def test_test_config_dependency_and_radon_additions_remain_out_of_policy(name):
    pristine={'radon/a.py':rec('VALUE=1\n')};buggy={'radon/a.py':rec('VALUE=0\n')}
    result=b.summarize_artifact(buggy,{**pristine,name:rec('VALUE=2\n')},pristine,'radon/a.py')
    assert not result['admissible'] and name in result['changed_paths']
    assert result['scratch_file_count']==0


def test_python_test_definitions_are_not_hidden_as_root_scratch():
    before={'radon/a.py':rec('VALUE=1\n')}
    for code in ['def test_value():\n    assert True\n','import unittest\n','import pytest\n']:
        result=b.summarize_artifact(before,{**before,'repro.py':rec(code)},before,'radon/a.py')
        assert not result['admissible'] and result['scratch_file_count']==0


def test_existing_nonproduction_changes_remain_out_of_policy():
    before={'radon/a.py':rec('VALUE=1\n'),'README.rst':rec('original')}
    final={**before,'README.rst':rec('changed')}
    assert not b.summarize_artifact(before,final,before,'radon/a.py')['admissible']


def test_symlinks_in_cache_and_git_subtrees_are_captured_and_rejected(tmp_path):
    (tmp_path/'radon').mkdir();(tmp_path/'radon/a.py').write_text('VALUE=1\n')
    (tmp_path/'.git').mkdir();(tmp_path/'.pytest_cache').mkdir()
    baseline=b.snapshot(tmp_path)
    for name in ['.pytest_cache/link','.git/link','repro.py']:(tmp_path/name).symlink_to('/not-followed')
    final=b.snapshot(tmp_path)
    assert all(final[name]['kind']=='symlink' for name in ['.pytest_cache/link','.git/link','repro.py'])
    result=b.summarize_artifact(baseline,final,baseline,'radon/a.py')
    assert not result['admissible'] and len(result['policy_violations'])==3


def test_protected_metadata_changes_cannot_bypass_cache_git_inventory():
    before={'radon/a.py':rec('VALUE=1\n')}
    metadata={'baseline':{},'final':{
        '.pytest_cache/pytest.ini':{'kind':'file','sha256':'fixture','bytes':1},
        '.git/config':{'kind':'file','sha256':'fixture','bytes':1},
        '.pytest_cache/.gitignore':{'kind':'file','sha256':'framework-marker','bytes':1}}}
    result=b.summarize_artifact(before,before,before,'radon/a.py',metadata=metadata)
    assert not result['admissible']
    assert {v['path'] for v in result['policy_violations']}=={'.pytest_cache/pytest.ini','.git/config'}


def row(y,completed=True):
    return {'fixture':True,'launched':True,'completed':completed,'evaluation_available':True,'admissible':True,
        'repair':bool(y),'target_file_edited':bool(y),'other_source_edited':False,
        'target_file_exact_restoration':bool(y),'reference_reversal_only':bool(y),
        'changed_lines':2 if y else 0,'added_lines':1 if y else 0,'deleted_lines':1 if y else 0,
        'joint_outcome':'repair_target_only' if y else 'evaluable_non_repair'}


def test_task_equal_weighting_and_missing_values_are_not_pooled_or_zero_filled():
    tasks=[{'id':'a','target':'A'},{'id':'b','target':'B'}];calls=[];rows={}
    for block in (1,2,3):
        name=f'a{block}';calls.append({'name':name,'task_id':'a','block':block,'condition':'H-in'});rows[name]=row(1)
    calls.append({'name':'b1','task_id':'b','block':1,'condition':'H-in'});rows['b1']=row(0)
    scores=score_rows(tasks,calls,rows);metric=scores['condition_summaries']['H-in']['metrics']['repair']
    assert metric['task_equal_mean']==.5 and metric['observed_sum']==3 and metric['observations']==4
    assert metric['complete_tasks']==1 and metric['complete_task_mean']==1
    assert scores['condition_summaries']['H-out']['metrics']['repair']['task_equal_mean'] is None
    assert scores['contrasts']['H_in_minus_H_out']['repair']['available_artifacts']['task_equal_mean'] is None
    assert scores['status']=='SCRIPTED_FIXTURE_NOT_STUDY_RESULTS'
    assert 'not study results' in render_report(scores)


def test_matched_contrasts_require_all_cells_and_report_completed_only():
    tasks=[{'id':'t','target':'A'}];calls=[];rows={}
    for condition,y in [('H0',0),('H-in',1),('H-out',0),('C-in',0),('C-out',1)]:
        calls.append({'name':condition,'task_id':'t','block':1,'condition':condition})
        rows[condition]=row(y,completed=condition!='C-out')
    scores=score_rows(tasks,calls,rows)
    item=scores['contrasts']['differential_response']['repair']
    assert item['available_artifacts']['task_equal_mean']==2
    assert item['available_artifacts']['matched_blocks']==1
    assert item['completed_only']['task_equal_mean'] is None
    assert scores['contrasts']['handoff_package_minus_H0']['repair']['available_artifacts']['task_equal_mean']==.5


def registered():
    return {'status':'REGISTERED','cutoff_utc':'2050-01-01T00:00:00Z','timeout_seconds':180,
        'primary_calls':180,'task_count':12,'blocks_per_task':3,'conditions':['H0','H-in','H-out','C-in','C-out'],
        'workers':2,'max_attempts':5,'seal_1_files':['registration.json'],'inputs':{}}


@pytest.mark.parametrize('field,value',[('status','DRAFT'),('cutoff_utc','PENDING_RICK'),('timeout_seconds',300),('primary_calls',144)])
def test_readiness_refuses_drafts_pending_and_design_drift(field,value):
    reg=registered();reg[field]=value
    with pytest.raises(RuntimeError):ready(reg)


def test_runtime_ledger_refuses_edited_missing_and_added_files(tmp_path):
    run=tmp_path/'run';run.mkdir();trace=run/'trace.json';trace.write_text('{"fixture":true}\n')
    ledger=tmp_path/'LEDGER.json';b.write_json(ledger,{'files':[{'path':'trace.json','sha256':digest(trace)}]})
    check=tmp_path/'LEDGER.sha256';check.write_text(digest(ledger)+'\n')
    assert verify_runtime(run,ledger,check)
    trace.write_text('{"fixture":"edited"}\n')
    with pytest.raises(RuntimeError,match='hash mismatch'):verify_runtime(run,ledger,check)
    trace.write_text('{"fixture":true}\n');(run/'extra.json').write_text('{}')
    with pytest.raises(RuntimeError,match='inventory'):verify_runtime(run,ledger,check)


@pytest.fixture
def published(tmp_path):
    root=tmp_path/'source';root.mkdir();actual=Path(__file__).resolve().parents[1]
    paths=source_closure(actual,['earshot.partb_study','earshot.partb_score'])
    for name in paths:
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((actual/name).read_bytes())
    reg=registered();reg['seal_1_files']=sorted(paths+['registration.json'])
    b.write_json(root/'registration.json',reg)
    b.write_json(root/'SEAL.json',{'files':[{'path':name,'sha256':digest(root/name)} for name in reg['seal_1_files']]})
    (root/'SEAL.sha256').write_text(digest(root/'SEAL.json')+'\n')
    def git(*args,cwd=root):return subprocess.check_output(['git',*args],cwd=cwd,text=True,stderr=subprocess.PIPE).strip()
    git('init','-q','--initial-branch=main');git('config','user.name','Synthetic integrity fixture');git('config','user.email','fixture@example.invalid')
    git('config','core.hooksPath','/dev/null');git('add','.');git('commit','-qm','Synthetic source seal')
    remote=tmp_path/'bare';git('init','-q','--bare',str(remote));git('remote','add','origin',str(remote));git('push','-q','origin','main')
    return root,git


def test_published_source_checks_exact_files_and_refuses_unpushed_head(published):
    root,git=published
    args=(root,'main',root/'registration.json',root/'SEAL.json',root/'SEAL.sha256')
    assert verify_source(*args)['seal_commit']==git('rev-parse','HEAD')
    source=root/'earshot/partb_study.py';original=source.read_bytes();source.write_bytes(original+b'\n')
    with pytest.raises(RuntimeError,match='sealed file changed'):verify_source(*args)
    source.write_bytes(original);(root/'unsealed-note.txt').write_text('synthetic change')
    git('add','.');git('commit','-qm','Synthetic later commit')
    with pytest.raises(RuntimeError,match='published branch head'):verify_source(*args)
    git('push','-q','origin','main')
    with pytest.raises(RuntimeError,match='after source seal'):verify_source(*args)


def test_source_closure_includes_nested_imports_and_package_init(tmp_path):
    pkg=tmp_path/'earshot';pkg.mkdir()
    (pkg/'__init__.py').write_text('from . import extra\n')
    (pkg/'a.py').write_text('def f():\n    from . import b\n')
    (pkg/'b.py').write_text('VALUE=1\n');(pkg/'extra.py').write_text('VALUE=2\n')
    assert source_closure(tmp_path,['earshot.a'])==['earshot/__init__.py','earshot/a.py','earshot/b.py','earshot/extra.py']


def reseal(root,git,reg):
    (root/'registration.json').write_text(json.dumps(reg,indent=2)+'\n')
    (root/'SEAL.json').write_text(json.dumps({'files':[{'path':p,'sha256':digest(root/p)} for p in reg['seal_1_files']]},indent=2)+'\n')
    (root/'SEAL.sha256').write_text(digest(root/'SEAL.json')+'\n')
    git('add','.');git('commit','-qm','Synthetic revised source seal');git('push','-q','origin','main')


def test_published_source_refuses_missing_import_coverage(published):
    root,git=published;reg=json.loads((root/'registration.json').read_text())
    reg['seal_1_files'].remove('earshot/partb_score.py');reseal(root,git,reg)
    with pytest.raises(RuntimeError,match='import closure'):
        verify_source(root,'main',root/'registration.json',root/'SEAL.json',root/'SEAL.sha256')


def test_published_source_refuses_unsealed_data_input(published):
    root,git=published;reg=json.loads((root/'registration.json').read_text())
    (root/'unsealed.json').write_text('{}');reg['inputs']={'fixture_data':'unsealed.json'};reseal(root,git,reg)
    with pytest.raises(RuntimeError,match='data input'):
        verify_source(root,'main',root/'registration.json',root/'SEAL.json',root/'SEAL.sha256')


def test_seal_digest_mismatch_is_refused(published):
    root,git=published
    with (root/'SEAL.json').open('a') as stream:stream.write(' ')
    with pytest.raises(RuntimeError,match='digest mismatch'):
        verify_source(root,'main',root/'registration.json',root/'SEAL.json',root/'SEAL.sha256')


def test_scorer_uses_raw_test_logs_and_does_not_trust_summary_flags(tmp_path):
    for label in ['control','diagnostic','full']:
        folder=tmp_path/label;folder.mkdir()
        (folder/'process.json').write_text(json.dumps({'exit_code':0,'timed_out':False}))
        (folder/'junit.xml').write_text('<testsuite><testcase classname="fixture" name="test"/></testsuite>')
    (tmp_path/'result.json').write_text(json.dumps({'tests_pass':False,'evaluation_available':False}))
    good=evaluation_from_logs(tmp_path,['fixture::test'],['fixture::test'])
    assert good['evaluation_available'] and good['tests_pass']
    (tmp_path/'result.json').write_text(json.dumps({'tests_pass':True,'evaluation_available':True}))
    (tmp_path/'full/junit.xml').write_text('<testsuite><testcase classname="fixture" name="test"><failure/></testcase></testsuite>')
    bad=evaluation_from_logs(tmp_path,['fixture::test'],['fixture::test'])
    assert bad['evaluation_available'] and not bad['tests_pass']
    (tmp_path/'control/process.json').write_text(json.dumps({'exit_code':1,'timed_out':False}))
    unavailable=evaluation_from_logs(tmp_path,['fixture::test'],['fixture::test'])
    assert not unavailable['evaluation_available'] and unavailable['tests_pass'] is None


def test_study_permit_binds_exact_call_prompt_backend_and_limits(mini,tmp_path,monkeypatch):
    repo,reg,calls,*_=mini
    reg['backend'].update(model='fixture-model',effort='low',setup_version='fixture-setup',cli_sha256='fixture-cli')
    permit=StudyPermit(repo,'main',repo/'registration.json',repo/'SEAL.json',repo/'SEAL.sha256')
    monkeypatch.setattr(StudyPermit,'verify',lambda self:{'registration':reg})
    prepared={'backend_policy':{'model':'fixture-model','effort':'low','setup_version':'fixture-setup'},
        'cli_sha256':'fixture-cli','env':{'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','PYTEST_PLUGINS':'pytest_mock'}}
    prompt=json.loads((repo/reg['inputs']['prompts']).read_text())[calls[0]['name']]
    assert permit.verify_call(calls[0]['name'],prepared,prompt,180,5)
    with pytest.raises(RuntimeError,match='call/prompt'):permit.verify_call(calls[0]['name'],prepared,prompt+' changed',180,5)
    with pytest.raises(RuntimeError,match='limits'):permit.verify_call(calls[0]['name'],prepared,prompt,181,5)
    prepared['env']['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='0'
    with pytest.raises(RuntimeError,match='test environment'):permit.verify_call(calls[0]['name'],prepared,prompt,180,5)


def test_actual_draft_is_reproducible_covers_imports_data_and_practice_provenance():
    repo=Path(__file__).resolve().parents[1];root=repo/'sprint/partB'
    spec=importlib.util.spec_from_file_location('fixture_draft_builder',root/'build_registration.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    reg=json.loads((root/'PART_B_registration.json').read_text())
    draft=module.registration(repo)
    # Registration/publication approval changes lifecycle metadata, not the
    # prepared intervention. Draft refusal is tested on explicit draft copies.
    assert {k:v for k,v in reg.items() if k not in {'status','approval'}}=={k:v for k,v in draft.items() if k not in {'status','approval'}}
    assert reg['status'] in {'DRAFT','REGISTERED'} and reg['timeout_seconds']==180
    paths=set(reg['seal_1_files'])
    assert set(source_closure(repo,['earshot.partb_study','earshot.partb_score']))<=paths
    assert set(reg['inputs'].values())<=paths
    assert all((repo/p).is_file() for p in paths)
    for manifest in ['IMPORT_MANIFEST.json','PROVENANCE_EXTENSION_MANIFEST.json']:
        imported=json.loads((root/'practice_record'/manifest).read_text())
        assert all(digest(root/'practice_record'/p)==sha for p,sha in imported['files'].items())
    practice=json.loads((root/'qualification/practice-02/QUALIFICATION.json').read_text())
    candidates=json.loads((root/'tasks_draft.json').read_text())['candidate_files']
    for receiver,condition in [('honest','H-in'),('coalition','C-in')]:
        rendered=b.render_prompt(practice,{'receiver':receiver,'condition':condition,'incoming_pair':'AC'},candidates)
        assert rendered==(root/'practice_record'/('practice-'+receiver)/'prompt.txt').read_text()
