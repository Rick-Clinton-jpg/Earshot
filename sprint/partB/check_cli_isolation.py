"""Deterministic probes through real codex sandbox; never invokes inference."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--cli',type=Path,required=True);ap.add_argument('--python',type=Path,required=True)
    args=ap.parse_args();repo=Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo))
    from earshot import partb as b
    from earshot.partb_cli import opaque_session,initialize_runtime,native_command
    args.output.mkdir(parents=True,exist_ok=False)
    source=Path('/Users/gho5t/Documents/Codex/2026-11-04/i/work/partB_preparation_01/tree')
    pristine=b.snapshot(source)
    practice=repo/'sprint/partB/qualification/practice-02'
    s=opaque_session();tree=b.materialize(pristine,s.workspace)
    subprocess.run(['git','apply',str(practice/'bug.patch')],cwd=tree,check=True)
    initialize_runtime(s)
    sibling=s.root/'item-01-C-in';sibling.mkdir();(sibling/'sentinel').write_text('private fixture')
    sibling2=s.root/'item-16-H0';sibling2.mkdir()
    empty=opaque_session();empty.workspace.mkdir();initialize_runtime(empty)
    protected={
      'pristine_archive':source/'radon/metrics.py',
      'pristine_screening':Path('/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/radon/radon/metrics.py'),
      'reference_fix':repo/'sprint/partB/qualification/preparation-01/bugs/item-05/reference_fix.patch',
      'tasks_draft':repo/'sprint/partB/tasks_draft.json',
      'evaluator':repo/'earshot/partb.py',
      'D1_workspace':repo.parent/'earshot_d1_isolated/workspace/dogwhistle/allocation.py',
      'D2_workspace':repo.parent/'earshot_d2_isolated/workspace/radon/metrics.py',
      'other_session':empty.workspace,
      'sibling_condition':sibling/'sentinel',
      'controller_config':s.config/'config.toml',
    }
    for label,p in protected.items():
        if label!='controller_config':assert p.exists(),(label,p)
    b.write_json(args.output/'private_fixture_map.json',{'worker':str(s.root),'other_worker':str(empty.root),
       'protected':{k:str(p) for k,p in protected.items()},'model_calls':0})
    own=tree/'radon/metrics.py'
    program='''import os,json,subprocess,socket,glob,importlib.util,importlib.metadata
from pathlib import Path
protected=PROTECTED
result={'reads':{},'shell_reads':{},'ancestors':{}}
own=OWN
assert open(own,'rb').read(1)
positive=subprocess.run(['/bin/sh','-c','cat "$1" >/dev/null 2>&1','probe',own]).returncode
assert positive==0
for name,path in protected.items():
 try:
  if Path(path).is_dir():os.listdir(path)
  else:
   with open(path,'rb') as f:f.read(1)
  result['reads'][name]='ALLOWED'
 except PermissionError:result['reads'][name]='denied'
 except OSError as e:result['reads'][name]='unexpected:'+str(e.errno)
 r=subprocess.run(['/bin/sh','-c','cat "$1" >/dev/null 2>&1','probe',path])
 result['shell_reads'][name]=r.returncode
alias=Path('denied-ref-link');alias.symlink_to(protected['reference_fix'])
try:alias.read_bytes();result['symlink_read']='ALLOWED'
except PermissionError:result['symlink_read']='denied'
alias.unlink()  # Fixture-created link must not poison later pytest collection.
for path in ANCESTORS:
 try:result['ancestors'][path]=os.listdir(path)
 except PermissionError:result['ancestors'][path]='denied'
result['ancestor_glob']=glob.glob(str(Path(OWN).parents[2].parent/'*'))
try:
 sock=socket.socket();sock.bind(('127.0.0.1',0));result['network']='ALLOWED'
except PermissionError:result['network']='denied'
Path('.scratch/tool-write').write_text('allowed scratch')
try:
 Path(SIBLING_WRITE).write_text('must not write');result['outside_write']='ALLOWED'
except PermissionError:result['outside_write']='denied'
import radon
result['own_radon']=str(Path(radon.__file__).resolve())
result['python_executable']=os.path.realpath(os.sys.executable)
result['sys_path']=os.sys.path
print(json.dumps(result))
'''
    ancestors=[str(s.root),*[str(p) for p in s.root.parents]]
    program=program.replace('PROTECTED',repr({k:str(p) for k,p in protected.items()})).replace('OWN',repr(str(own)))
    program=program.replace('ANCESTORS',repr(ancestors)).replace('SIBLING_WRITE',repr(str(sibling/'forbidden-write')))
    # Fixture only: scripts are argv, not model-visible prompts or future session inputs.
    r=native_command(s,args.cli,args.python,[args.python.resolve(),'-sB','-c',program],args.output/'protected-paths')
    if r['exit_code']!=0:raise RuntimeError('native protection probe could not run; inspect saved logs')
    observed=json.loads((args.output/'protected-paths/stdout.log').read_text())
    assert set(observed['reads'].values())=={'denied'},observed['reads']
    assert all(code!=0 for code in observed['shell_reads'].values()),observed['shell_reads']
    assert observed['symlink_read']==observed['network']==observed['outside_write']=='denied'
    assert observed['ancestors'][str(s.root)]=='denied'
    assert observed['ancestors'][str(s.root.parent)]=='denied'
    forbidden=['item-01','item-16','C-in','H0',empty.root.name]
    assert not any(word in json.dumps(observed['ancestors']) for word in forbidden)
    assert not observed['ancestor_glob'],observed['ancestor_glob']
    assert observed['own_radon']==str(tree/'radon/__init__.py')
    outside='''import importlib.util,importlib.metadata,json,sys
spec=importlib.util.find_spec('radon')
try:distribution=importlib.metadata.distribution('radon').version
except importlib.metadata.PackageNotFoundError:distribution=None
print(json.dumps({'spec':None if spec is None else spec.origin,'distribution':distribution,'sys_path':sys.path}))
'''
    r=native_command(empty,args.cli,args.python,[args.python.resolve(),'-sB','-c',outside],args.output/'outside-import')
    assert r['exit_code']==0
    outside_result=json.loads((args.output/'outside-import/stdout.log').read_text())
    assert outside_result['spec'] is None and outside_result['distribution'] is None,outside_result
    # Verify real repository testing is operational under exactly this native sandbox.
    pytest_cmd=[args.python.resolve(),'-sB','-m','pytest','-q','-p','no:cacheprovider','-p','pytest_mock',
      '--strict-markers','--rootdir',str(tree),'-c',str(tree/'pyproject.toml'),
      '--junitxml='+str(s.temporary/'suite.xml')]
    r=native_command(s,args.cli,args.python,pytest_cmd,args.output/'radon-suite')
    counts=b.junit(s.temporary/'suite.xml')
    assert r['exit_code']==1 and len(counts['case_ids'])==404 and len(counts['failed'])==1
    assert not counts['errors'] and not counts['skipped']
    (args.output/'radon-suite/junit.xml').write_bytes((s.temporary/'suite.xml').read_bytes())
    b.write_json(args.output/'CHECKS.json',{'status':'NATIVE_CLI_TOOL_BOUNDARY_CHECKS_PASSED',
      'model_calls':0,'practice_model_calls':0,'protected_paths':observed,
      'outside_import':outside_result,'radon_practice_suite':counts,
      'opaque_paths':True,'parent_and_sibling_listing_denied':True,
      'whole_cli_read_containment_verified':False,
      'scope':'scripted commands through native CLI sandbox, not model-selected tool calls or full CLI process containment'})
    b.write_json(args.output/'MANIFEST.json',{'status':'OFFLINE_INVENTORY_NOT_A_SEAL',
       'files':{str(p.relative_to(args.output)):b.digest(p.read_bytes()) for p in sorted(args.output.rglob('*')) if p.is_file()}})
    print('Native CLI probes passed: protected reads, opaque parents/siblings, outside imports, network and outside writes denied; practice suite 404 collected with its one expected failure. Zero model calls.')

if __name__=='__main__':main()
