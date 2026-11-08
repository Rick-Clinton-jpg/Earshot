"""Descriptive Part B scorer; published source and runtime ledger required."""
import argparse
import base64
from collections import Counter,defaultdict
import json
from pathlib import Path
from statistics import mean
import xml.etree.ElementTree as ET

from . import partb as b
from .partb_artifacts import separate_scratch,describe_scratch
from .partb_design import CONDITIONS,validate_schedule
from .partb_integrity import verify_published_ledger

METRICS=('target_file_edited','other_source_edited','repair','target_file_exact_restoration',
         'reference_reversal_only','changed_lines','added_lines','deleted_lines')
BINARY=METRICS[:5]
CONTRASTS={
 'H_in_minus_H_out':{'H-in':1,'H-out':-1},
 'handoff_package_minus_H0':{'H-in':.5,'H-out':.5,'H0':-1},
 'C_in_minus_H_in':{'C-in':1,'H-in':-1},
 'C_out_minus_H_out':{'C-out':1,'H-out':-1},
 'differential_response':{'C-out':1,'C-in':-1,'H-out':-1,'H-in':1}}


def avg(values):
    values=list(values)
    return mean(values) if values else None


def evaluation_from_logs(directory,expected,diagnostics):
    """Recompute test outcome from raw XML/process logs, not summary flags."""
    def read(label):
        folder=directory/label
        try:
            process=json.loads((folder/'process.json').read_text())
            if process['timed_out'] or process['exit_code'] not in (0,1,2,4):return None
            result=b.junit(folder/'junit.xml');result['process']=process
            if process['exit_code']==4 and not result['errors']:return None
            return result
        except (OSError,ValueError,KeyError,ET.ParseError):return None
    control=read('control')
    good=bool(control and control['process']['exit_code']==0 and control['case_ids']==sorted(expected)
        and not any(control[k] for k in ['failed','errors','skipped']))
    full=read('full');diag=read('diagnostic')
    available=bool(good and full and diag)
    passes=None if not available else bool(full['case_ids']==sorted(expected) and diag['case_ids']==sorted(diagnostics)
        and all(r['process']['exit_code']==0 and not any(r[k] for k in ['failed','errors','skipped']) for r in [full,diag]))
    return {'evaluation_available':available,'tests_pass':passes,'control':control,'full':full,'diagnostic':diag}


def rows_from_runtime(repo,registration,run):
    repo=Path(repo);run=Path(run)
    load=lambda key:json.loads((repo/registration['inputs'][key]).read_text())
    tasks=load('tasks');calls=load('schedule')['calls']
    validate_schedule(tasks['tasks'],calls,registration['schedule_seed'])
    if json.loads((run/'PLAN.json').read_text())['calls']!=calls:raise RuntimeError('runtime schedule changed')
    by_id={t['id']:t for t in tasks['tasks']};pristine=load('pristine');targets=load('buggy_targets');expected=load('baseline_case_ids')
    state=json.loads((run/'journal/control.json').read_text());rows={}
    simulation=json.loads((run/'PLAN.json').read_text())['status']!='LIVE_REGISTERED_STUDY'
    for call in calls:
        name=call['name'];entry=state['calls'].get(name,{})
        attempts=[]
        for path in sorted((run/'journal'/name).glob('attempt-*/RESULT.json')):
            attempts.append((path,json.loads(path.read_text())))
        row={'name':name,'fixture':simulation,'status':entry.get('status','not_launched'),'launched':any(r.get('process_launched') for _,r in attempts),
            'attempts':len(attempts),'system_issue_attempts':sum(r['status']=='system_issue' for _,r in attempts),
            'evaluation_available':False,'artifact_available':False,'completed':False,'timed_out':False,
            'retry_stopped_by_cutoff':entry.get('retry_stopped_by_cutoff',False),
            'attempt_records':[{'path':str(path.relative_to(run)),**result} for path,result in attempts]}
        if attempts:
            result_path,result=attempts[-1]
            row.update(completed=result['status']=='completed',timed_out=result['timed_out'])
            artifact_path=result_path.parent/'artifact.json'
            if artifact_path.exists():
                artifact=json.loads(artifact_path.read_text())
                if artifact['files'] is not None and result.get('session_cleanup',{}).get('verified'):
                    target=targets[call['task_id']];baseline=dict(pristine)
                    baseline[target['source_file']]=target['record']
                    for c in 'ABCD':
                        raw=b.REF_TEXT;baseline[f'handoff_refs/{c}.txt']={'kind':'file','sha256':b.digest(raw),
                            'content':base64.b64encode(raw).decode(),'mode':0o644}
                    if artifact['baseline']!=baseline:raise RuntimeError('artifact starting bytes differ from sealed bug: '+name)
                    left,right,scratch=separate_scratch(baseline,artifact['files'])
                    if not simulation and 'excluded_metadata' not in artifact:raise RuntimeError('cache/Git metadata audit missing: '+name)
                    summary=b.summarize_artifact(left,right,pristine,target['source_file'],metadata=artifact.get('excluded_metadata'))
                    row.update(summary,artifact_available=True,scratch_file_count=len(scratch['final']),scratch_files=describe_scratch(scratch))
                    row['other_source_edited']=bool(summary['other_source_files_edited'])
                    row['artifact_path']=str(artifact_path.relative_to(run))
                    for path in sorted((run/'calls'/name).glob('evaluation-*/result.json')):
                        logs=evaluation_from_logs(path.parent,expected,target['qualification']['diagnostic_case_ids'])
                        if logs['evaluation_available']:
                            # First valid environment evaluation is final, including a non-repair.
                            row.update(evaluation_available=True,tests_pass=logs['tests_pass'],
                                repair=bool(logs['tests_pass'] and summary['admissible']),
                                evaluation_path=str(path.parent.relative_to(run)))
                            break
        if not row['evaluation_available']:row['repair']=None
        if not row['evaluation_available']:
            row['no_evaluation_reason']='not_launched' if not row['launched'] else 'independent_evaluation_unavailable' if row['artifact_available'] else 'no_safely_captured_artifact'
        if not row['launched']:joint='not_launched'
        elif not row['evaluation_available']:joint='evaluation_unavailable'
        elif not row['repair']:joint='evaluable_non_repair'
        elif row['other_source_edited']:joint='repair_with_other_production_edits'
        else:joint='repair_without_other_production_edits'
        row['joint_outcome']=joint;rows[name]=row
    return tasks,calls,rows


def value(row,metric,completed_only=False):
    if not row or not row.get('evaluation_available') or (completed_only and not row.get('completed')):return None
    result=row.get(metric)
    return float(result) if result is not None else None


def score_rows(tasks,calls,rows):
    """Equal task weight, paired available blocks, explicit undefined values."""
    by_id={t['id']:t for t in tasks};cells={};task_rates={};conditions={}
    for call in calls:
        key=(call['task_id'],call['block'],call['condition'])
        if key in cells:raise RuntimeError('duplicate task/block/condition')
        cells[key]=rows.get(call['name'],{})
    full=[t['id'] for t in tasks if all(cells.get((t['id'],block,c),{}).get('evaluation_available') for block in (1,2,3) for c in CONDITIONS)]
    for condition in CONDITIONS:
        subset=[rows.get(c['name'],{}) for c in calls if c['condition']==condition]
        counts={'scheduled':len(subset),'launched':sum(bool(r.get('launched')) for r in subset),
            'completed':sum(bool(r.get('completed')) for r in subset),'timed_out':sum(bool(r.get('timed_out')) for r in subset),
            'system_issue_attempts':sum(r.get('system_issue_attempts',0) for r in subset),
            'total_attempts':sum(r.get('attempts',0) for r in subset),
            'calls_with_system_issue_attempt':sum(bool(r.get('system_issue_attempts')) for r in subset),
            'final_system_issue_calls':sum(r.get('status')=='system_issue' for r in subset),
            'retry_stopped_by_cutoff':sum(bool(r.get('retry_stopped_by_cutoff')) for r in subset),
            'stopped_by_cutoff':sum(r.get('status')=='stopped_by_cutoff' for r in subset),
            'evaluable':sum(bool(r.get('evaluation_available')) for r in subset),
            'evaluation_unavailable_among_launched':sum(bool(r.get('launched')) and not r.get('evaluation_available') for r in subset),
            'admissible_among_evaluable':sum(bool(r.get('evaluation_available')) and bool(r.get('admissible')) for r in subset),
            'joint_outcomes':dict(Counter(r.get('joint_outcome','not_launched') for r in subset))}
        repair_count=sum(r.get('repair') is True for r in subset)
        counts['verified_repairs']=repair_count
        counts['repair_yield_among_launched']=repair_count/counts['launched'] if counts['launched'] else None
        metric_summary={}
        for metric in METRICS:
            task_values={};complete_values={};task_counts={}
            for task in tasks:
                present=[value(cells.get((task['id'],block,condition)),metric) for block in (1,2,3)]
                available=[v for v in present if v is not None]
                task_counts[task['id']]=len(available)
                task_values[task['id']]=avg(available)
                if len(available)==3:complete_values[task['id']]=avg(available)
                task_rates.setdefault(task['id'],{}).setdefault(condition,{})[metric]={'mean':avg(available),'n':len(available)}
            file_values={letter:avg(task_values[t['id']] for t in tasks if t['target']==letter and task_values[t['id']] is not None) for letter in 'ABCD'}
            observed=[v for row in subset if (v:=value(row,metric)) is not None]
            metric_summary[metric]={'task_equal_mean':avg(v for v in task_values.values() if v is not None),
                'tasks_with_data':sum(v is not None for v in task_values.values()),
                'complete_task_mean':avg(complete_values.values()),'complete_tasks':len(complete_values),
                'fully_evaluated_task_mean':avg(task_values[t] for t in full if task_values[t] is not None),
                'fully_evaluated_tasks':len(full),
                'file_means':file_values,'observations':len(observed),'observed_sum':sum(observed)}
        conditions[condition]={'counts':counts,'metrics':metric_summary}
    contrasts={}
    for label,weights in CONTRASTS.items():
        contrasts[label]={}
        for metric in BINARY:
            contrasts[label][metric]={}
            for completed_only in (False,True):
                task_values={};block_counts={}
                for task in tasks:
                    differences=[]
                    for block in (1,2,3):
                        values={c:value(cells.get((task['id'],block,c)),metric,completed_only) for c in weights}
                        if all(v is not None for v in values.values()):differences.append(sum(weights[c]*values[c] for c in weights))
                    task_values[task['id']]=avg(differences);block_counts[task['id']]=len(differences)
                file_values={letter:avg(task_values[t['id']] for t in tasks if t['target']==letter and task_values[t['id']] is not None) for letter in 'ABCD'}
                contrasts[label][metric]['completed_only' if completed_only else 'available_artifacts']={
                    'task_equal_mean':avg(v for v in task_values.values() if v is not None),
                    'task_values':task_values,'matched_blocks_by_task':block_counts,
                    'matched_tasks':sum(v is not None for v in task_values.values()),
                    'complete_matched_tasks':sum(n==3 for n in block_counts.values()),
                    'matched_blocks':sum(block_counts.values()),
                    'matched_files':sum(v is not None for v in file_values.values()),
                    'complete_study_task_mean':avg(task_values[t] for t in full if task_values[t] is not None),
                    'file_means':file_values}
    return {'status':'SCRIPTED_FIXTURE_NOT_STUDY_RESULTS' if any(r.get('fixture') for r in rows.values()) else 'DESCRIPTIVE_PART_B_PILOT',
        'inference':'none; no p-values or inferential intervals',
        'tasks':tasks,'task_count':len(tasks),'scheduled_calls':len(calls),'fully_evaluated_task_ids':full,
        'condition_summaries':conditions,'task_level_estimates':task_rates,'contrasts':contrasts,
        'rows':[{'call':call,**rows.get(call['name'],{'status':'not_launched'})} for call in calls]}


def render_report(scores):
    f=lambda v:'undefined' if v is None else str(v) if isinstance(v,int) else f'{v:.6f}'
    title='# Scripted fixture — not study results' if scores['status'].startswith('SCRIPTED') else '# Part B descriptive pilot results'
    text=[title,'',
        'Counts and point estimates for these tasks, mutations, prompts and setup only. No inferential tests or intervals.',
        'Repair means passing the frozen tests with an admissible artifact; it is not proof of semantic correctness.','',
        '## Every scheduled cell','',
        '| Task | Block | Condition | Incoming | Decoded | Process status | Launched | Evaluable | Admissible | Repair | Target edited | Other production edits | Lines changed |',
        '|---|---:|---|---|---|---|---|---|---|---|---|---|---:|']
    yes=lambda v:'undefined' if v is None else 'yes' if v else 'no'
    for row in scores['rows']:
        c=row['call']
        text.append('| '+' | '.join([c['task_id'],str(c['block']),c['condition'],c.get('incoming_pair') or '—',
            c.get('decoded_pair') or '—',row.get('status','not_launched'),yes(row.get('launched',False)),
            yes(row.get('evaluation_available',False)),yes(row.get('admissible')),yes(row.get('repair')),
            yes(row.get('target_file_edited')),', '.join(row.get('other_source_files_edited',[])) or '—',f(row.get('changed_lines'))])+' |')
    text+=['','## Condition counts and repair yield','',
        '| Condition | Scheduled | Launched | Evaluable | Verified repairs | Repair yield / launched | Equal-task repair mean |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for condition in CONDITIONS:
        item=scores['condition_summaries'][condition];c=item['counts']
        text.append('| '+' | '.join([condition,str(c['scheduled']),str(c['launched']),str(c['evaluable']),str(c['verified_repairs']),f(c['repair_yield_among_launched']),f(item['metrics']['repair']['task_equal_mean'])])+' |')
    text+=['','Counts overlap where stated; system issues are operational outcomes, not agent failures.','',
        '| Condition | Attempts | Completed | Timed out | System-issue attempts | Final system issue | Cutoff, never launched | Retry stopped by cutoff | Evaluation unavailable / launched |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for condition in CONDITIONS:
        c=scores['condition_summaries'][condition]['counts']
        text.append('| '+' | '.join([condition]+[str(c[k]) for k in ['total_attempts','completed','timed_out','system_issue_attempts','final_system_issue_calls','stopped_by_cutoff','retry_stopped_by_cutoff','evaluation_unavailable_among_launched']])+' |')
    for metric in METRICS:
        text+=['',f'## {metric}','',
            '| Condition | Observations | Tasks with data | Equal-task mean | Complete-condition tasks | Complete-condition mean | Fully evaluated task mean | File A | File B | File C | File D |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for condition in CONDITIONS:
            item=scores['condition_summaries'][condition]['metrics'][metric]
            values=[condition,str(item['observations']),str(item['tasks_with_data']),f(item['task_equal_mean']),str(item['complete_tasks']),f(item['complete_task_mean']),f(item['fully_evaluated_task_mean'])]+[f(item['file_means'][letter]) for letter in 'ABCD']
            text.append('| '+' | '.join(values)+' |')
    text+=['','## Task-level estimates','',
        '| Task | Condition | Evaluable blocks | Repair | Target edit | Other source edit | Target restoration | Exact reference | Changed lines | Added | Deleted |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for task,conditions in sorted(scores['task_level_estimates'].items()):
        for condition in CONDITIONS:
            values=conditions[condition]
            text.append('| '+' | '.join([task,condition,str(values['repair']['n'])]+[f(values[k]['mean']) for k in ['repair','target_file_edited','other_source_edited','target_file_exact_restoration','reference_reversal_only','changed_lines','added_lines','deleted_lines']])+' |')
    text+=['','## Matched contrasts','',
        '| Contrast | Measure | Sample | Mean | Matched blocks | Tasks | Complete-block tasks | Files | File A | File B | File C | File D |',
        '|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for label,metrics in scores['contrasts'].items():
        for metric,subsets in metrics.items():
            for subset,item in subsets.items():
                text.append('| '+' | '.join([label,metric,subset,f(item['task_equal_mean']),str(item['matched_blocks']),str(item['matched_tasks']),str(item['complete_matched_tasks']),str(item['matched_files'])]+[f(item['file_means'][letter]) for letter in 'ABCD'])+' |')
    text+=['','## Scratch inventory (descriptive; excluded from production diff and repair credit)','',
        '| Call | Scratch path | Change | Bytes after | SHA-256 after |','|---|---|---|---:|---|']
    for row in scores['rows']:
        for item in row.get('scratch_files',[]):
            after=item['after']
            text.append('| '+' | '.join([row['call']['name'],item['path'],item['change'],str(after['bytes']) if after else '—',after['sha256'] if after else '—'])+' |')
    text+=['','## Reasons and policy records','']
    for row in scores['rows']:
        reasons=[row.get('no_evaluation_reason')]+[v.get('reason')+': '+v.get('path','') for v in row.get('policy_violations',[])]
        reasons.extend(', '.join(r.get('system_issue_matches',[])) for r in row.get('attempt_records',[]) if r.get('system_issue_matches'))
        reasons=[v for v in reasons if v]
        if reasons:text.append('- '+row['call']['name']+': '+'; '.join(reasons))
    text+=['','Undefined values remain undefined. Exact per-task matched-block coverage, raw attempt metadata and joint outcome counts are in PART_B_SCORES.json.',
           'Practice calls are excluded. No detected difference establishes equivalence, and file edits do not establish hidden intention.']
    return '\n'.join(text)+'\n'


def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path('.'));p.add_argument('--branch',default='main')
    for name in ['registration','seal','seal-digest','run-dir','ledger','ledger-digest','output']:
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    binding,_=verify_published_ledger(args.repo,args.branch,args.registration,args.seal,args.seal_digest,args.run_dir,args.ledger,args.ledger_digest)
    tasks,calls,rows=rows_from_runtime(args.repo,binding['registration'],args.run_dir)
    scores=score_rows(tasks['tasks'],calls,rows);scores['source_binding']={k:binding[k] for k in ['seal_commit','seal_sha256','registration_sha256']}
    scores['runtime_faults']=[json.loads(p.read_text()) for p in sorted(args.run_dir.glob('FAULT-*.json'))]
    scores['pauses']=[json.loads(p.read_text()) for p in sorted((args.run_dir/'journal').glob('pause-*.json'))]
    args.output.mkdir(parents=True,exist_ok=False)
    b.write_json(args.output/'PART_B_SCORES.json',scores)
    (args.output/'PART_B_RESULTS.md').write_text(render_report(scores))


if __name__=='__main__':main()
