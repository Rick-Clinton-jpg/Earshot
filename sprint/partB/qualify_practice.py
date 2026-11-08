"""Qualify D2 reserve item-04 offline; this script makes no model calls."""
import argparse
import difflib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--scratch',type=Path,required=True)
    parser.add_argument('--python',type=Path,required=True);args=parser.parse_args()
    repo=Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo))
    from earshot.partb import snapshot,materialize,collect_ids,resolve_diagnostics,run_sandboxed,junit,write_json,digest
    spec=importlib.util.spec_from_file_location('partb_qualifier',Path(__file__).with_name('qualify_bugs.py'))
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    q=repo/'sprint/partB/qualification/preparation-01'
    source=Path('/Users/gho5t/Documents/Codex/2026-11-04/i/work/partB_preparation_01/tree')
    # Source is the existing clean private archive; verify every byte against its recorded inventory.
    manifest=json.loads((q/'SOURCE_MANIFEST.json').read_text())
    assert helper.tree_hashes(source)==manifest
    tasks=json.loads((repo/'sprint/partD/D2/tasks.json').read_text())
    task=next(t for t in tasks['tasks'] if t['id']=='item-04')
    assert task['role']=='reserve' and task['target_function']=='mi_parameters'
    args.output.mkdir(parents=True,exist_ok=False)
    pristine=snapshot(source);tree=materialize(pristine,args.scratch)
    rel='radon/metrics.py';path=tree/rel;before=path.read_text()
    old='raw.comments + (raw.multi if count_multi else 0)'
    altered=helper.mutate(before,'mi_parameters',old,'raw.comments')
    patch=''.join(difflib.unified_diff(before.splitlines(keepends=True),altered.splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel))
    fix=''.join(difflib.unified_diff(altered.splitlines(keepends=True),before.splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel))
    (args.output/'bug.patch').write_text(patch);(args.output/'reference_fix.patch').write_text(fix)
    collected=collect_ids(tree,args.python,args.output/'collection')
    assert len(collected)==404
    write_json(args.output/'collected_node_ids.json',collected)
    records={}
    for phase,content in [('clean',before),('buggy',altered),('restored',before)]:
        path.write_text(content)
        for rep in (1,2):
            label=f'{phase}-{rep}';directory=args.output/label
            command=[args.python,'-B','-m','pytest','-q','-p','no:cacheprovider','-p','pytest_mock','--strict-markers',f'--junitxml={directory.resolve()/"junit.xml"}']
            process=run_sandboxed(command,tree,directory,args.python)
            result=junit(directory/'junit.xml');result['process']=process;records[label]=result
            assert not result['errors'] and not result['skipped']
            assert len(result['case_ids'])==404
            if phase=='buggy':assert process['exit_code']==1 and result['failed']
            else:assert process['exit_code']==0 and result['passed']==404
    assert records['buggy-1']['failed']==records['buggy-2']['failed']
    assert helper.tree_hashes(tree)==manifest
    for name,expected in [('bug.patch',digest(altered.encode())),('reference_fix.patch',digest(before.encode()))]:
        subprocess.run(['git','apply',str((args.output/name).resolve())],cwd=tree,check=True)
        assert digest(path.read_bytes())==expected
    ids=resolve_diagnostics(collected,records['buggy-1']['failed'])
    result={'status':'PRACTICE_QUALIFIED_OFFLINE_NO_MODEL_CALLS','id':'practice-item-04',
       'd2_source_id':'item-04','source_commit':tasks['source_commit'],
       'source_file':rel,'target_function':'mi_parameters',
       'bug_report':'When multiline strings are included as comments, the reported comment percentage and resulting maintainability score are too low. Restore the optional inclusion of multiline strings while preserving the behaviour when that option is disabled.',
       'diagnostic_case_ids':records['buggy-1']['failed'],'diagnostic_node_ids':ids,
       'repeated_runs':records,'bug_patch_sha256':digest(patch.encode()),'reference_fix_sha256':digest(fix.encode()),
       'practice_model_calls':0,'included_in_study_schedule':False}
    write_json(args.output/'QUALIFICATION.json',result)
    write_json(args.output/'MANIFEST.json',{'status':'OFFLINE_PRACTICE_INVENTORY_NOT_A_SEAL',
       'files':{str(p.relative_to(args.output)):digest(p.read_bytes()) for p in sorted(args.output.rglob('*')) if p.is_file()}})
    print('Practice reserve item-04:',len(ids),'reproducible failing diagnostic(s); clean/restored 404 passed twice; zero model calls.')

if __name__=='__main__':main()
