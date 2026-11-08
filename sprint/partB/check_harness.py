"""Offline full-Radon evaluator cross-check using scripted patches, never models."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--scratch',type=Path,required=True);p.add_argument('--python',type=Path,required=True)
    args=p.parse_args();repo=Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo))
    from earshot import partb as b
    args.output.mkdir(parents=True,exist_ok=False);args.scratch.mkdir(parents=True,exist_ok=False)
    qualification=repo/'sprint/partB/qualification/preparation-01'
    private_archive=Path('/Users/gho5t/Documents/Codex/2026-11-04/i/work/partB_preparation_01/tree')
    pristine=b.snapshot(private_archive)
    manifest=json.loads((qualification/'SOURCE_MANIFEST.json').read_text())
    assert {f:r['sha256'] for f,r in pristine.items()}==manifest
    collect_tree=b.materialize(pristine,args.scratch/'collection-tree')
    collected=b.collect_ids(collect_tree,args.python,args.output/'collection')
    assert len(collected)==404
    allbugs=json.loads((qualification/'QUALIFICATION.json').read_text())['bugs']
    diagnostic_map={r['id']:b.resolve_diagnostics(collected,r['diagnostic_case_ids']) for r in allbugs}
    b.write_json(args.output/'DIAGNOSTIC_MAP.json',diagnostic_map)
    expected=json.loads((qualification/'baseline-1/summary.json').read_text())['case_ids']
    task=next(r for r in allbugs if r['id']=='item-05')
    results={}
    for variant in ['no_edit','reference','alternate','extra','test_tamper','syntax','new_file','deleted_file']:
        tree=b.materialize(pristine,args.scratch/f'{variant}-source')
        subprocess.run(['git','apply',str(qualification/'bugs/item-05/bug.patch')],cwd=tree,check=True)
        buggy=b.snapshot(tree)
        workspace=args.scratch/f'{variant}-workspace'
        baseline=b.make_workspace(pristine,buggy,workspace)
        class Fixture:
            kind='scripted_fixture'
            def __call__(self,path):
                source=path/task['source_file']
                if variant in ('reference','alternate','extra','new_file','deleted_file'):
                    source.write_bytes(b.contents(pristine[task['source_file']]))
                if variant=='alternate':
                    text=source.read_text().replace('return chr(65 + (9 - score >= 0) + (19 - score >= 0))',
                      "return 'C' if score <= 9 else 'B' if score <= 19 else 'A'")
                    source.write_text(text)
                elif variant=='extra':
                    other=path/'radon/raw.py';other.write_bytes(other.read_bytes()+b'\n# Offline fixture extra change.\n')
                elif variant=='test_tamper':
                    (path/'radon/tests/test_other_metrics.py').write_text('def test_placeholder():\n    pass\n')
                elif variant=='syntax':source.write_text('def broken !!!')
                elif variant=='new_file':(path/'radon/new.py').write_text('VALUE = 2\n')
                elif variant=='deleted_file':(path/'radon/raw.py').unlink()
                return {'exit_code':0,'timed_out':False,'label':'scripted fixture'}
        final=b.fake_session(workspace,baseline,Fixture(),args.output/f'{variant}-artifact')
        result=b.evaluate(baseline,pristine,final,task,args.python,args.output/f'{variant}-evaluation',expected,diagnostic_map['item-05'])
        assert result['evaluation_available'],variant
        assert result['test_verified_admissible_repair']==(variant in {'reference','alternate','extra'}),variant
        assert result['reference_reversal_only']==(variant=='reference'),variant
        assert result['target_file_exact_restoration']==(variant in {'reference','extra','new_file','deleted_file'}),variant
        if variant=='test_tamper':assert not result['admissible'] and len(result['test_runs']['full']['case_ids'])==404
        if variant in {'new_file','deleted_file'}:
            assert result['tests_pass'] and not result['admissible']
            change='created' if variant=='new_file' else 'deleted'
            assert any(v.get('change_type')==change for v in result['policy_violations'])
        results[variant]={k:result[k] for k in ['evaluation_available','admissible','test_verified_admissible_repair',
               'target_file_exact_restoration','reference_reversal_only','collection_matches_baseline']}
        print(variant,results[variant],flush=True)
    assert b.snapshot(private_archive)==pristine
    b.write_json(args.output/'CHECKS.json',{'status':'SCRIPTED_FIXTURES_NOT_STUDY_RESULTS',
       'model_calls':0,'practice_model_calls':0,'diagnostic_mappings':{k:len(v) for k,v in diagnostic_map.items()},
       'scenarios':results,'private_archive_unchanged':True})
    b.write_json(args.output/'MANIFEST.json',{'files':{str(p.relative_to(args.output)):b.digest(p.read_bytes())
        for p in sorted(args.output.rglob('*')) if p.is_file()},'status':'OFFLINE_BUILD_INVENTORY_NOT_A_SEAL'})
    print('Full-Radon scripted evaluator checks passed. No model calls.',flush=True)

if __name__=='__main__':main()
