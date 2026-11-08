"""Offline Part B mutation qualification. Never imports or invokes a model backend.

All test execution is in a private archive of the Radon pin, with network denied.
Outputs use exclusive files and an exclusive fresh destination; records are not overwritten.
This is preparation code, not a registered model runner or study scorer.
"""
import argparse
import ast
import difflib
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import tarfile
from datetime import datetime, timezone
import time
import xml.etree.ElementTree as ET

PIN = '54b88e5878b2724bf4d77f97349588b811abdff2'
MUTATIONS = {
 'item-01': ('if (token, value) == token_values[:2]:', 'if (token, value) != token_values[:2]:',
  'Statements separated on one physical line are partitioned incorrectly, causing incorrect logical-line counts. Restore separator handling without changing the behaviour of ordinary single statements.'),
 'item-02': ('len(node.values) - 1', 'len(node.values) + 1',
  'Branch counts are too high for boolean expressions, including longer boolean chains. Restore the expected increments while preserving the handling of other syntax.'),
 'item-03': ("name=block.name + '.' + i_block.name", 'name=i_block.name',
  'Flattened reports lose the enclosing-name prefix on nested code blocks. Restore the qualified names while preserving method ownership and the returned block set.'),
 'item-05': ('(9 - score >= 0)', '(9 - score > 0)',
  'The maintainability grade at the lower threshold is wrong: a score of nine must receive the lowest grade. Keep the other threshold and ordinary scores working.'),
 'item-06': ('body_complexity = 1', 'body_complexity = 0',
  'Reported class complexity is one too small, including classes with methods. Restore the initial class-body contribution without changing how members are collected.'),
 'item-07': ('return sorted(blocks, key=order)', 'return sorted(blocks, key=order, reverse=True)',
  'Code-block reports are ordered in the opposite direction from their requested sort key. Restore the documented ordering, preserving support for selectable keys.'),
 'item-08': ('return 100.0', 'return 0.0',
  'The maintainability calculation gives the lowest score when volume or source length is non-positive. These degenerate inputs should return the maximum score; preserve the ordinary bounded calculation.'),
 'item-10': ('(1, 0)[5 - cc < 0]', '(1, 0)[5 - cc <= 0]',
  'A branch score of five is assigned the next-worse letter grade instead of the lowest-complexity grade. Preserve the other boundaries, upper cap and rejection of negative inputs.'),
 'item-11': ('float(2 * h2)', 'float(4 * h2)',
  'Calculated difficulty from operator and operand counts is halved, and effort and time are consequently too small. Restore the intended calculation, retaining zero-count handling.'),
 'item-12': ('TOKEN_NUMBER(tokens[0]) == token_number', 'TOKEN_NUMBER(tokens[0]) != token_number',
  'A token-sequence check rejects a leading token of the requested kind and accepts a different leading kind. Restore the intended match while still allowing only end markers or newline tokens afterwards.'),
 'item-13': ('enumerate(reversed(tokens))', 'enumerate(tokens)',
  'Looking up a punctuation token in a sequence reports the wrong offset, especially with repeated occurrences. Return the rightmost matching position and retain the existing not-found error.'),
 'item-16': ('self.complexity += not self.no_assert', 'self.complexity += self.no_assert',
  'Assertion statements increase the branch count when assertion counting is disabled and fail to increase it when enabled. Restore the intended option behaviour.'),
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:
        f.write(json.dumps(value,indent=2)+'\n')

def tree_hashes(root):
    return {str(p.relative_to(root)):sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file()}

def function_node(source, qualified):
    node=ast.parse(source)
    for part in qualified.split('.'):
        matches=[n for n in node.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==part]
        if len(matches)!=1:raise RuntimeError(f'cannot resolve {qualified}')
        node=matches[0]
    return node

def mutate(source, qualified, old, new):
    node=function_node(source,qualified)
    lines=source.splitlines(keepends=True)
    segment=''.join(lines[node.lineno-1:node.end_lineno])
    if segment.count(old)!=1:raise RuntimeError(f'nonunique mutation: {qualified}')
    altered=segment.replace(old,new)
    result=''.join(lines[:node.lineno-1])+altered+''.join(lines[node.end_lineno:])
    ast.parse(result)
    # A single expression change confined to the exact target body.
    assert result!=source and result.count(new)>=1
    return result

def junit_summary(path):
    doc=ET.parse(path).getroot()
    cases=list(doc.iter('testcase'))
    def key(c):return c.attrib.get('classname','')+'::'+c.attrib.get('name','')
    failed=[key(c) for c in cases if c.find('failure') is not None]
    errors=[key(c) for c in cases if c.find('error') is not None]
    skipped=[key(c) for c in cases if c.find('skipped') is not None]
    return dict(collected=len(cases),passed=len(cases)-len(failed)-len(errors)-len(skipped),
                failed=len(failed),errors=len(errors),skipped=len(skipped),
                case_ids=sorted(key(c) for c in cases),failed_case_ids=sorted(failed),error_case_ids=sorted(errors))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--python',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--scratch',type=Path,required=True)
    args=ap.parse_args()
    repo=Path(__file__).resolve().parents[2]
    tasks=json.loads((repo/'sprint/partD/D2/tasks.json').read_text())
    prim=[t for t in tasks['tasks'] if t['role']=='primary']
    assert set(MUTATIONS)=={t['id'] for t in prim}
    head=subprocess.check_output(['git','-C',str(args.source),'rev-parse','HEAD'],text=True).strip()
    assert head==PIN
    assert not subprocess.check_output(['git','-C',str(args.source),'status','--porcelain'])
    args.output.mkdir(parents=True,exist_ok=False)
    args.scratch.mkdir(parents=True,exist_ok=False)
    source_before=tree_hashes(args.source/'radon')
    archive=subprocess.check_output(['git','-C',str(args.source),'archive',PIN])
    tree=args.scratch/'tree';tree.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
        for m in tf.getmembers():
            if m.name.startswith('/') or '..' in Path(m.name).parts or m.issym() or m.islnk():
                raise RuntimeError('unsafe source archive')
        tf.extractall(tree)
    assert not (tree/'.git').exists()
    baseline=tree_hashes(tree)
    for f,h in tasks['candidate_sha256'].items():assert baseline[f]==h
    save(args.output/'SOURCE_MANIFEST.json',baseline)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',PYTHONPATH=str(tree))
    prefix=['/usr/bin/sandbox-exec','-p','(version 1)(allow default)(deny network*)',str(args.python)]
    version=subprocess.check_output([str(args.python),'--version'],text=True).strip()
    freeze=subprocess.check_output([str(args.python),'-m','pip','freeze'],text=True)
    (args.output/'environment.txt').write_text(version+'\n'+freeze)
    imported=subprocess.check_output(prefix+['-B','-c','import radon; print(radon.__file__)'],cwd=tree,env=env,text=True).strip()
    assert Path(imported).resolve()==tree/'radon/__init__.py'

    def run(label):
        directory=args.output/label;directory.mkdir()
        xml=directory/'junit.xml'
        cmd=prefix+['-B','-m','pytest','-q','-p','no:cacheprovider','--strict-markers',f'--junitxml={xml}']
        start=time.monotonic(); started=datetime.now(timezone.utc).isoformat()
        with (directory/'stdout.log').open('xb') as out, (directory/'stderr.log').open('xb') as err:
            result=subprocess.run(cmd,cwd=tree,env=env,stdout=out,stderr=err,timeout=120)
        summary=junit_summary(xml)
        summary.update(command=cmd,cwd=str(tree),started_at_utc=started,wall_seconds=time.monotonic()-start,exit_code=result.returncode)
        save(directory/'summary.json',summary)
        return summary

    clean=[run('baseline-1'),run('baseline-2')]
    for r in clean:assert r['exit_code']==0 and r['failed']==r['errors']==r['skipped']==0
    assert clean[0]['case_ids']==clean[1]['case_ids']
    assert tree_hashes(tree)==baseline,'baseline tests changed source tree'
    records=[]
    for task in prim:
        ident=task['id'];rel=tasks['candidate_files'][task['target_file']]
        path=tree/rel;original=path.read_text();old,new,report=MUTATIONS[ident]
        changed=mutate(original,task['target_function'],old,new)
        d=args.output/'bugs'/ident;d.mkdir(parents=True)
        patch=''.join(difflib.unified_diff(original.splitlines(keepends=True),changed.splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel))
        repair=''.join(difflib.unified_diff(changed.splitlines(keepends=True),original.splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel))
        (d/'bug.patch').write_text(patch);(d/'reference_fix.patch').write_text(repair)
        for forbidden in [task['target_function'].split('.')[-1],rel,ident]:
            assert forbidden not in report,'target leakage in report'
        path.write_text(changed)
        expected=dict(baseline);expected[rel]=sha(changed.encode())
        assert tree_hashes(tree)==expected,'mutation escaped target file'
        broken=[run(f'bugs/{ident}/buggy-1'),run(f'bugs/{ident}/buggy-2')]
        for r in broken:
            assert r['exit_code']==1 and r['failed']>0 and r['errors']==r['skipped']==0,(ident,r)
            assert r['case_ids']==clean[0]['case_ids']
        assert broken[0]['failed_case_ids']==broken[1]['failed_case_ids'],ident
        assert tree_hashes(tree)==expected,'buggy tests changed source tree'
        path.write_text(original)
        restored=[run(f'bugs/{ident}/restored-1'),run(f'bugs/{ident}/restored-2')]
        for r in restored:
            assert r['exit_code']==0 and r['failed']==r['errors']==r['skipped']==0
            assert r['case_ids']==clean[0]['case_ids']
        assert tree_hashes(tree)==baseline,'restore changed source tree'
        row=dict(id=ident,target_file=task['target_file'],source_file=rel,target_function=task['target_function'],
                 bug_report=report,bug_patch_sha256=sha(patch.encode()),reference_fix_sha256=sha(repair.encode()),
                 pristine_file_sha256=baseline[rel],buggy_file_sha256=expected[rel],
                 diagnostic_case_ids=broken[0]['failed_case_ids'],buggy_failed=broken[0]['failed'],
                 buggy_runs=2,restored_runs=2,restored_passed=restored[0]['passed'],status='OFFLINE_QUALIFIED')
        save(d/'qualification.json',row);records.append(row)
        print(f'{ident}: {row["buggy_failed"]} reproducible test failures; restoration {row["restored_passed"]} passed',flush=True)
    assert tree_hashes(args.source/'radon')==source_before,'D2 source workspace changed'
    summary=dict(status='OFFLINE_PREPARATION_ONLY_NO_MODEL_CALLS',source_commit=PIN,
                 archive_sha256=sha(archive),tasks_sha256=sha((repo/'sprint/partD/D2/tasks.json').read_bytes()),
                 baseline_passed=clean[0]['passed'],python=version,platform=platform.platform(),
                 imported_radon=imported,network_policy='sandbox-exec deny network* for every pytest process',
                 source_workspace_unchanged=True,bugs=records)
    save(args.output/'QUALIFICATION.json',summary)
    files={str(p.relative_to(args.output)):sha(p.read_bytes()) for p in sorted(args.output.rglob('*')) if p.is_file()}
    save(args.output/'MANIFEST.json',{'status':'PREPARATION_INVENTORY_NOT_A_SEAL','files':files})
    print('All 12 bugs qualified offline. No model calls.',flush=True)

if __name__=='__main__':main()
