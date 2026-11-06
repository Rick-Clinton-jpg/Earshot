import hashlib
import json
from pathlib import Path
import subprocess
import pytest
from earshot.d1 import D1,ROOT,main as run_trial
from earshot.d1_pilot import verify_inventory
from earshot.trial_run import classify,STATUS


def test_all_trace_hashes_match_frozen_inventory():
    verify_inventory()
    mapping=json.loads((D1/'PATH_MAP.json').read_text())
    frozen=json.loads(subprocess.check_output(['git','show','424528e:sprint/partD/D1/UNSEALED_RUN.json'],cwd=ROOT))
    expected={e['path']:e for e in frozen['traces']}
    assert len(mapping['traces'])==224
    assert len({e['new_path'] for e in mapping['traces']})==224
    for e in mapping['traces']:
        raw=(ROOT/e['new_path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==e['sha256']==expected[e['old_path']]['sha256']
        assert len(raw)==expected[e['old_path']]['bytes']


def test_fixed_classification_and_directory_counts():
    ran=list((D1/'traces').glob('*.json'));system=list((D1/'system_issue').glob('*.json'))
    assert len(ran)==114 and len(system)==110
    assert all(classify(json.loads(p.read_text()))=='ran' for p in ran)
    assert all(classify(json.loads(p.read_text()))=='system_issue' for p in system)
    assert not (ROOT/'sprint/partD/D1/traces').exists()  # a new draft D1 folder is allowed


def test_descriptive_values_preserved_and_no_hypothesis_outcome():
    data=json.loads((D1/'trial_run_scores.json').read_text())
    old=json.loads(subprocess.check_output(['git','show','6a07580:sprint/partD/D1/pilot_scores.json'],cwd=ROOT))
    assert data['status']==STATUS
    assert data['descriptive_estimates_complete_tasks']==old['registered_analysis_A']['primary']
    assert data['K_alt_descriptive']=={k:v for k,v in old['registered_analysis_A']['secondary_K_alt'].items() if k!='rule_outcome'}
    assert data['counts']['ran']==data['counts']['gate_accepted']==114
    assert data['counts']['gate_rejections']==data['counts']['timeouts']==0
    def check(obj):
        if isinstance(obj,dict):
            assert not {'rejected','exact_one_sided_p','rule_outcome','outcome'} & obj.keys()
            for v in obj.values():check(v)
        elif isinstance(obj,list):
            for v in obj:check(v)
    check(data)


def test_timing_exception_not_removed():
    data=json.loads((D1/'trial_run_scores.json').read_text())
    assert data['system_issue_timing']['first_started_at_utc']=='2026-11-06T18:59:17.298991Z'
    assert len(data['system_issue_timing']['later_answer_producing_calls'])==2
    assert data['system_issue_timing']['claim_every_call_after_first_stopped'] is False


def test_frozen_trial_cannot_launch(monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('subprocess reached')
    monkeypatch.setattr(subprocess,'run',forbidden)
    with pytest.raises(RuntimeError,match='frozen'):run_trial([])


def test_readme_only_two_requested_insertions():
    before=subprocess.check_output(['git','show','6a07580:README.md'],cwd=ROOT,text=True)
    line='A D1 trial run was completed and is reported in `sprint/trial_run/`. The sealed D1 has not been run yet.'
    for heading in ['## Results','## Progress']:before=before.replace(heading+'\n',heading+'\n\n'+line+'\n',1)
    assert (ROOT/'README.md').read_text()==before


def test_legacy_reader_classifies_system_records_separately():
    from earshot.d1 import load_tasks
    from earshot.d1_score import task_summary
    _,_,tasks=load_tasks()
    row=task_summary(tasks['reserve-honest-summarize'],D1/'traces')
    assert all(c['run']==0 and c['rejected']==0 for c in row['counts'].values())
    assert sum(c['system_issue'] for c in row['counts'].values())==14
