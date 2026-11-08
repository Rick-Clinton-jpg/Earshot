"""Write a draft from existing frozen inputs. Never seals, publishes or calls models."""
import argparse
import json
from pathlib import Path
import sys


def registration(repo):
    sys.path.insert(0,str(repo))
    from earshot.partb_integrity import source_closure
    from earshot.partb_cli import CLI_VERSION,SETUP_VERSION
    from earshot.integrity import digest
    root='sprint/partB/'
    inputs={'tasks':root+'tasks_draft.json','schedule':root+'schedule_draft.json',
        'pristine':root+'inputs/PRISTINE.json','buggy_targets':root+'inputs/BUGGY_TARGETS.json',
        'diagnostics':root+'inputs/DIAGNOSTICS.json','baseline_case_ids':root+'inputs/BASELINE_CASE_IDS.json',
        'prompts':root+'inputs/PROMPTS.json','environment':root+'inputs/ENVIRONMENT.json',
        'system_issue_patterns':'earshot/system_issue_patterns.json'}
    files=set(source_closure(repo,['earshot.partb_study','earshot.partb_score']))
    files.update(inputs.values())
    for directory in ['inputs','qualification/preparation-01','qualification/practice-02','practice_record']:
        files.update(str(p.relative_to(repo)) for p in (repo/root/directory).rglob('*') if p.is_file())
    files.update(str(p.relative_to(repo)) for p in (repo/'tests').glob('test_partb*.py'))
    files.update(str(p.relative_to(repo)) for p in (repo/'earshot').glob('partb*.py'))
    files.update(str(p.relative_to(repo)) for p in (repo/root).glob('*.py'))
    files.update(root+name for name in ['PART_B_registration.json','PART_B_REGISTRATION.md','RUNBOOK.md',
        'DESIGN_DRAFT.md','SCRATCH_POLICY.md','CLI_INTEGRATION_CHECKS.json','build_registration.py','check_test_environment.py','check_practice_pipeline.py'])
    cli='/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex'
    cli_sha=json.loads((repo/root/'CLI_INTEGRATION_CHECKS.json').read_text())['CLI_sha256']
    if Path(cli).is_file() and digest(cli)!=cli_sha:raise RuntimeError('recorded pinned CLI differs from local binary')
    return {'status':'DRAFT','study':'EARSHOT Part B descriptive code-editing pilot',
        'source_repository':'https://github.com/rubik/radon','source_commit':'54b88e5878b2724bf4d77f97349588b811abdff2',
        'primary_calls':180,'task_count':12,'candidate_files':4,'blocks_per_task':3,
        'conditions':['H0','H-in','H-out','C-in','C-out'],'schedule_seed':20261108,
        'timeout_seconds':180,'timeout_decision':root+'practice_record/STUDY_TIMEOUT_DECISION.json',
        'cutoff_utc':'2026-11-08T23:30:00Z','cutoff_local':'2026-11-09T05:00:00+05:30',
        'workers':2,'max_attempts':5,'termination_grace_seconds':5,
        'cleanup_budget_seconds':2,'evaluation_timeout_seconds_per_process':120,
        'run_dir':root+'codex','inputs':inputs,
        'backend':{'name':'codex','model':'gpt-6.1-sol','effort':'low','cli':cli,'cli_version':CLI_VERSION,
            'cli_sha256':cli_sha,'python':'/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/env-radon/bin/python',
            'setup_version':SETUP_VERSION,'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','PYTEST_PLUGINS':'pytest_mock'},
        'approval':{'by':'Rick','scope':'Registration review decisions and requested pre-seal scratch revision',
            'seal_created_by_this_revision':False,'study_calls_authorized_by_this_revision':False},
        'review_decisions':{'absolute_cutoff':'APPROVED: 9 November 2026 05:00 IST',
            'two_workers':'APPROVED: 2','scratch_allowlist':'APPROVED_RULE_IMPLEMENTED; offline checks recorded separately',
            'reporting_label':'APPROVED: repair without other production edits; separate target_file_edited',
            'task_ID_disclosure':'APPROVED as written'},
        'scope':{'descriptive_only':True,'confirmatory_tests':False,'inferential_intervals':False,
            'no_relays':True,'no_claude_arm':True,'no_conceal_condition':True,'practice_excluded':True,
            'limitations':['one repository','four target files','three tasks per file','injected bugs',
                'explicit convention instruction','three different pair allocations, not identical-prompt repeatability',
                'existing D2 item IDs retained in prepared prompts; public mapping linkage is not concealed']},
        'artifact_policy':{'version':'partb-artifact-policy-v2-root-scratch',
            'admissible':'Existing production .py files below radon/, excluding radon/tests; paths and types preserved.',
            'scratch_rule':'New regular non-symlink files outside radon/ that are not tests, config or dependencies, plus eligible regular .scratch/ files: inventoried descriptively, excluded from production diff/admissibility measures, never imported for evaluation.',
            'protected_file_detection':'Deterministic path/name/suffix conventions and Python test definitions/imports, specified in SCRATCH_POLICY.md and partb_artifacts.py; arbitrary intent is not inferred.',
            'cache_policy':'Regular cache/Git content is inventoried separately. Symlinks anywhere are captured; protected config/test/dependency changes in caches and Git config/hooks are audited and remain out of policy.',
            'controller_cleanup_canary':'Exactly the controller-created scratch canary is excluded after integrity verification.',
            'new_deleted_renamed_radon_files':'Out of policy; no scratch exemption below radon/. Generated runtime cache metadata retains its separate inventory policy.',
            'test_config_dependency_changes':'Out of policy even if an extracted production delta passes pristine tests.'},
        'runtime_policy':{'order':'Frozen 36 blocks; five frozen conditions per block; at most two workers; wait for block completion.',
            'system_issue':'Pause new launches immediately, drain in-flight work, preserve records, exit. Explicit Rick resume only.',
            'unknown_no_answer':'Manual pause. Safe meaningful artifacts may be evaluated without final prose; retain protocol status.',
            'partial_or_unverified_cleanup':'Hold for reconciliation, never automatically retry.',
            'final_attempts':'Completed artifacts, timeouts, refusals and evaluable non-repairs are final.',
            'retry':'Fresh opaque workspace/home, same prompt/bug/backend/limits, preserved attempt count; maximum five total.',
            'cutoff':'Check after setup and immediately before Popen, reserving timeout, grace and cleanup. Never-launched cells are stopped_by_cutoff; preserve prior system-issue classifications.',
            'evaluation_outage':'Pause; may repeat unavailable independent evaluation after Rick resume, never a valid non-repair evaluation or model call.',
            'artifact_baseline':'Qualified buggy snapshot with identical reference files; no pristine Git history or remote.',
            'ledger':'All terminal runtime evidence must be ledgered and published before scoring. Fixtures cannot be ledgered as study data.'},
        'analysis':{'rates':'Equal-weight means of task-level rates, averaging observed pair blocks within task first; all denominators and four file means reported.',
            'missing':'No zero imputation; undefined stays undefined; report incomplete coverage.',
            'contrasts':['H-in minus H-out','(H-in + H-out)/2 minus H0','C-in minus H-in',
                'C-out minus H-out','(C-out minus C-in) minus (H-out minus H-in)'],
            'pairing':'Same task and block; require all cells for each contrast; show matched block/task/file coverage.',
            'sensitivity':'Completed-only matched contrasts beside available-artifact estimates.',
            'repair_yield':'Verified repairs / all launched scheduled sessions, reported as end-to-end yield, not agent failure rate.',
            'exact_reversal':'Descriptive flags only, independent of repair credit.',
            'inspection_order':'Not measured; no frozen reliable event parser is implemented.',
            'raw_test_recheck':'Scorer reparses pristine control, diagnostic and full JUnit/process logs; first available environment evaluation is final.'},
        'seal_1_files':sorted(files)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path('.'));p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();repo=args.repo.resolve();value=registration(repo)
    missing=[name for name in value['seal_1_files'] if not (repo/name).is_file() and (repo/name).resolve()!=args.output.resolve()]
    if missing:raise RuntimeError('proposed coverage paths missing: '+str(missing))
    with args.output.open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
    print('Draft written; no seal or model calls. Proposed files:',len(value['seal_1_files']))


if __name__=='__main__':main()
