"""Rick-approved, two-call reserve timing practice. No study calls or retries."""
import argparse
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

REPO=Path('/Users/gho5t/Documents/Codex/2026-11-04/i/work/Earshot_foundation')
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(REPO))
from earshot import partb as b
from earshot.partb_cli import Session,opaque_session,initialize_runtime,CLI_VERSION
from earshot.partb_launch import prepare_practice,PracticeControl,CredentialCopy,run_prepared,utcnow,stamp

CLI=Path('/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex')
PYTHON=Path('/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/env-radon/bin/python')
SOURCE=REPO.parent/'partB_preparation_01/tree'
Q=REPO/'sprint/partB/qualification/practice-02'
NAMES=('practice-honest','practice-coalition')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare():
    task=json.loads((Q/'QUALIFICATION.json').read_text())
    assert task['id']=='practice-item-04' and not task['included_in_study_schedule']
    for name,value in json.loads((Q/'MANIFEST.json').read_text())['files'].items():assert sha(Q/name)==value,name
    pristine=b.snapshot(SOURCE)
    assert {p:r['sha256'] for p,r in pristine.items()}==json.loads((REPO/'sprint/partB/qualification/preparation-01/SOURCE_MANIFEST.json').read_text())
    assert sha(CLI)==json.loads((REPO/'sprint/partB/CLI_INTEGRATION_CHECKS.json').read_text())['CLI_sha256']
    assert subprocess.check_output([str(CLI),'--version'],text=True).strip()==CLI_VERSION
    candidates=json.loads((REPO/'sprint/partB/tasks_draft.json').read_text())['candidate_files']
    plan={'status':'AUTHORIZED_PRESTUDY_TIMING_ONLY_NOT_STUDY','created_at_utc':stamp(utcnow()),
        'cutoff_utc':stamp(utcnow()+timedelta(hours=2)),'model':'gpt-6.1-sol','effort':'low',
        'call_timeout_seconds':900,'termination_grace_seconds':5,'cleanup_budget_seconds':2,
        'maximum_initial_calls':2,'concurrency':1,'task':task['id'],'source_commit':task['source_commit'],
        'authorization':'Rick approved practice on condition it may set only the study timeout. Prompts, instruction wording, bugs and conditions may not change based on behaviour. If setup is broken, stop and report to Rick before any change; record any subsequently approved change.',
        'timeout_selection_rule':'If both calls complete without setup fault: ceil(max(180, 2 * slower launcher wall seconds) / 60) * 60 seconds. If either times out, report censoring and do not select a study timeout. Launcher wall time includes version/preflight, model process, cleanup and artifact capture; excludes preparation and independent evaluation.',
        'no_automatic_retry_or_resume':True,'calls':{}}
    for name,receiver in zip(NAMES,['honest','coalition']):
        directory=ROOT/name;directory.mkdir()
        tree=b.materialize(pristine,directory/'controller-source')
        subprocess.run(['git','apply',str(Q/'bug.patch')],cwd=tree,check=True)
        session=opaque_session();assert not list(session.root.iterdir())
        baseline=b.make_workspace(pristine,b.snapshot(tree),session.workspace)
        initialize_runtime(session)
        prepared=prepare_practice(session,CLI,PYTHON,model=plan['model'],effort=plan['effort'])
        call={'condition':'H-in' if receiver=='honest' else 'C-in','receiver':receiver,'incoming_pair':'AC'}
        prompt=b.render_prompt(task,call,candidates)
        (directory/'prompt.txt').write_text(prompt)
        b.write_json(directory/'BASELINE.json',baseline)
        b.write_json(directory/'PREPARED.json',prepared)
        session_paths={field:str(getattr(session,field)) for field in ['root','workspace','home','config','temporary']}
        b.write_json(directory/'SESSION.json',session_paths)
        b.write_json(directory/'PREFLIGHT.json',{'fresh_opaque_session':True,
            'CODEX_HOME_files':sorted(p.name for p in session.config.iterdir()),
            'instruction_files_in_workspace':[str(p.relative_to(session.workspace)) for p in session.workspace.rglob('*') if p.name.lower() in {'agents.md','agents.override.md','claude.md','gemini.md'}],
            'git_commits':subprocess.check_output(['git','rev-list','--count','HEAD'],cwd=session.workspace,text=True).strip(),
            'git_remotes':subprocess.check_output(['git','remote'],cwd=session.workspace,text=True).splitlines(),
            'baseline_matches_qualified_bug':True,'source_commit':task['source_commit']})
        plan['calls'][name]={**call,'prompt_sha256':sha(directory/'prompt.txt'),'workspace':str(session.workspace)}
    b.write_json(ROOT/'PLAN.json',plan)
    covered=[Path(__file__),ROOT/'PLAN.json',REPO/'earshot/partb.py',REPO/'earshot/partb_cli.py',
        REPO/'earshot/partb_launch.py',REPO/'earshot/partb_processes.py',REPO/'sprint/partB/DESIGN_DRAFT.md',
        REPO/'sprint/partB/tasks_draft.json',REPO/'sprint/partB/schedule_draft.json',
        REPO/'earshot/system_issue_patterns.json',Q/'QUALIFICATION.json',Q/'bug.patch',Q/'reference_fix.patch']
    for name in NAMES:
        for filename in ['prompt.txt','BASELINE.json','PREPARED.json','SESSION.json','PREFLIGHT.json']:
            covered.append(ROOT/name/filename)
    b.write_json(ROOT/'FROZEN_INPUTS.json',{'status':'PRESTUDY_PRACTICE_FREEZE_NOT_A_STUDY_SEAL',
        'files':{str(p):sha(p) for p in covered}})
    PracticeControl(ROOT/'journal',plan['cutoff_utc'],scheduled=NAMES)
    print('Prepared and frozen both calls; no model process launched.',flush=True)


def run(name):
    freeze=json.loads((ROOT/'FROZEN_INPUTS.json').read_text())
    for path,value in freeze['files'].items():assert sha(path)==value,'frozen input changed: '+path
    plan=json.loads((ROOT/'PLAN.json').read_text());directory=ROOT/name
    session=Session(**{k:Path(v) for k,v in json.loads((directory/'SESSION.json').read_text()).items()})
    prepared=json.loads((directory/'PREPARED.json').read_text());prompt=(directory/'prompt.txt').read_text()
    control=PracticeControl(ROOT/'journal',plan['cutoff_utc'],scheduled=NAMES)
    patterns=json.loads((REPO/'earshot/system_issue_patterns.json').read_text())['patterns']
    auth=Path('/Users/gho5t/.codex/auth.json');source_before=sha(auth)
    with CredentialCopy(auth,session) as credentials:
        begin=time.perf_counter()
        result=run_prepared(control,name,session,prepared,prompt,900,5,patterns,authorized=True,
                            sanitize=credentials.sanitize)
        wall=time.perf_counter()-begin
    assert sha(auth)==source_before,'original credential file changed'
    b.write_json(directory/'TIMING.json',{'launcher_wall_seconds':wall,'status':result['status'],
        'original_auth_unchanged':True,'disposable_auth_removed':not (session.config/'auth.json').exists(),
        'purpose':'PRESTUDY_TIMING_ONLY','hosted_cli_attempts':int(result.get('process_launched',False))})
    print(name,'status',result['status'],'launcher wall seconds',round(wall,3),flush=True)
    if result['status'] not in {'completed','timed_out'}:
        print('STOP: process/system/setup issue. No changes or automatic retries.',flush=True);return
    artifact=json.loads((ROOT/'journal'/name/'attempt-01/artifact.json').read_text())
    assert artifact['baseline']==json.loads((directory/'BASELINE.json').read_text()),'starting artifact mismatch'
    task=json.loads((Q/'QUALIFICATION.json').read_text());pristine=b.snapshot(SOURCE)
    evaluation=b.evaluate(artifact['baseline'],pristine,artifact['files'],task,PYTHON,directory/'evaluation',
        task['repeated_runs']['clean-1']['case_ids'],task['diagnostic_node_ids'])
    print('Independent evaluation available:',evaluation['evaluation_available'],
        'tests pass:',evaluation['tests_pass'],'admissible repair:',evaluation['test_verified_admissible_repair'],flush=True)
    for path,value in freeze['files'].items():assert sha(path)==value,'frozen input changed after call: '+path


if __name__=='__main__':
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare',action='store_true');group.add_argument('--call',choices=NAMES)
    args=parser.parse_args()
    if args.prepare:prepare()
    else:run(args.call)
