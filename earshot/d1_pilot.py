"""Read-only analysis of the frozen, non-confirmatory D1 pilot."""
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
from statistics import mean,median
import subprocess

from .d1 import D1,ROOT,PAIRS,load_tasks
from .d1_score import analyze,task_summary

STATUS='D1 pilot. Registered in commit `1a6936e` before its first call, but not published before the run. Used to design a later sealed D1. Not confirmatory.'
REG='1a6936ef646e45671768928c5e245a053897d9a7'
FREEZE='424528e7f0ae64cd1204f958aeba08c45edc9aaf'
RUN='101406f54575f155e699ff9adb15b10bc2fe2c70'


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def verify_inventory():
    inv=json.loads(subprocess.check_output(['git','show',FREEZE+':sprint/partD/D1/UNSEALED_RUN.json'],cwd=ROOT))
    expected={r['path'] for r in inv['traces']}
    actual={str(p.relative_to(ROOT)) for p in (D1/'traces').glob('*.json')}
    if expected!=actual:raise ValueError('trace set mismatch')
    for e in inv['traces']:
        data=(ROOT/e['path']).read_bytes()
        if hashlib.sha256(data).hexdigest()!=e['sha256'] or len(data)!=e['bytes']:raise ValueError('trace hash or byte-count mismatch: '+e['path'])
    return inv


def usage(row):
    return next((e['usage'] for e in reversed(row.get('events',[])) if e.get('type')=='turn.completed' and 'usage' in e),None)


def reasons(row):
    messages=[]
    if row.get('error'):messages.append(row['error'])
    for e in row.get('events',[]):
        if e.get('type')=='error' and e.get('message'):messages.append(e['message'])
        if e.get('type')=='turn.failed' and isinstance(e.get('error'),dict):messages.append(e['error'].get('message','turn.failed'))
    if not messages and row.get('exit_code')!=0:messages.append('process exit '+str(row.get('exit_code')))
    if not messages and row['gate_result']=='rejected':messages.append('gate '+row.get('gate_detail','rejected'))
    return sorted(set(messages))


def summary_stats(values,scheduled):
    v=[x for x in values if x is not None]
    return {'recorded':len(v),'missing':scheduled-len(v),'mean':mean(v) if v else None,'median':median(v) if v else None,'p90_nearest_rank':sorted(v)[math.ceil(.9*len(v))-1] if v else None}


def exploratory_group(task_rows):
    details=[];allrows=[];agreement_count=0;comparable_count=0;scheduled_count=0
    for task in task_rows:
        rows=task['rows'];allrows.extend(rows);pairs={};agreement={}
        for pair in PAIRS+['free']:
            rr=sorted([r for r in rows if r['incoming_pair']==pair],key=lambda r:r['replicate'])
            good=[r for r in rr if r['gate_result']=='accepted']
            pairs[pair]={'distribution':dict(Counter(r['output_pair'] for r in good)),'accepted':len(good),'rejected':sum(r['gate_result']=='rejected' for r in rr),'timed_out':sum('timeout' in r.get('error','').lower() or 'timed out' in r.get('error','').lower() for r in rr)}
            comparable=len(good)==2
            agreed=good[0]['output_pair']==good[1]['output_pair'] if comparable else None
            agreement[pair]={'outputs':[r['output_pair'] for r in rr],'both_accepted':comparable,'agree':agreed}
            if pair!='free':
                scheduled_count+=1;comparable_count+=comparable;agreement_count+=bool(agreed)
        shares={}
        for label,contains in [('in',True),('out',False)]:
            rr=[r for r in rows if r['incoming_pair']!='free' and (task['target'] in r['incoming_pair'])==contains and r['gate_result']=='accepted']
            numerator=sum(r['output_pair']==task['free_choice_pair'] for r in rr) if task['free_choice_pair'] else None
            denominator=len(rr) if task['free_choice_pair'] else 0
            shares[label]={'equal_free_pair':numerator,'accepted_denominator':denominator,'share':numerator/denominator if denominator else None}
        bad=[{'name':r['name'],'exit_code':r.get('exit_code'),'gate_detail':r.get('gate_detail'),'timed_out':'timeout' in r.get('error','').lower() or 'timed out' in r.get('error','').lower(),'recorded_reasons':reasons(r)} for r in rows if r['gate_result']=='rejected']
        details.append({'task_id':task['task_id'],'target':task['target'],'valid':task['valid'],'counts':task['counts'],'output_pair_distributions':pairs,'run_to_run_agreement':agreement,'free_choice_pair':task['free_choice_pair'],'free_choice_agree':task['free_choice_agree'],'equal_free_pair_by_input_group':shares,'failures':bad})
    aggshares={}
    for g in ['in','out']:
        ss=[d['equal_free_pair_by_input_group'][g] for d in details];den=sum(s['accepted_denominator'] for s in ss);num=sum(s['equal_free_pair'] or 0 for s in ss)
        defined=[s['share'] for s in ss if s['share'] is not None]
        aggshares[g]={'equal_free_pair':num,'accepted_denominator':den,'pooled_share':num/den if den else None,'equal_task_mean':mean(defined) if defined else None,'defined_tasks':len(defined)}
    calls=[]
    for r in allrows:
        calls.append({'name':r['name'],'gate_result':r['gate_result'],'exit_code':r.get('exit_code'),'wall_seconds':r.get('elapsed_seconds'),'tool_calls':sum(e.get('type')=='item.completed' for e in r.get('tool_calls',[])) if 'tool_calls' in r else None,'usage':usage(r),'recorded_reasons':reasons(r) if r['gate_result']=='rejected' else []})
    tokens=sorted({k for r in calls if r['usage'] for k in r['usage']})
    metrics={'wall_seconds':summary_stats([r['wall_seconds'] for r in calls],len(calls)),'tool_calls':summary_stats([r['tool_calls'] for r in calls],len(calls))}
    for key in tokens:metrics[key]=summary_stats([r['usage'].get(key) if r['usage'] else None for r in calls],len(calls))
    if not tokens:metrics['token_usage']={'recorded':0,'missing':len(calls),'mean':None,'median':None,'p90_nearest_rank':None}
    return {'n_tasks':len(details),'n_calls':len(calls),'agreement_incoming_pairs':{'scheduled_pairs':scheduled_count,'both_accepted_pairs':comparable_count,'agreeing_pairs':agreement_count,'rate_among_comparable':agreement_count/comparable_count if comparable_count else None},'equal_free_pair_by_input_group':aggshares,'runtime_and_usage':metrics,'tasks':details,'per_call_runtime_usage':calls,'rejection_reason_counts':dict(Counter(m for r in calls for m in r['recorded_reasons']))}


def main():
    inv=verify_inventory();prior,files,tasks=load_tasks()
    registered=analyze(D1/'traces',prior['primary_task_ids'],prior['reserve_task_ids'],tasks)
    reports=[task_summary(tasks[tid],D1/'traces') for tid in prior['primary_task_ids']+prior['reserve_task_ids']]
    raw=[r for t in reports for r in t['rows']]
    subprocess.run(['git','merge-base','--is-ancestor',REG,FREEZE],cwd=ROOT,check=True)
    regfiles=['sprint/partD/D1/D1_registration.json','sprint/partD/D1/D1_REGISTRATION.md']
    identical=all(subprocess.check_output(['git','show',REG+':'+f],cwd=ROOT)==subprocess.check_output(['git','show',FREEZE+':'+f],cwd=ROOT) for f in regfiles)
    sourcefiles=['earshot/d1.py','earshot/d1_score.py','earshot/prompts.py','earshot/gate.py','earshot/runner.py','earshot/config.py']
    changed=git('diff','--name-only',REG,RUN,'--',*sourcefiles).splitlines()
    commit_time=git('show','-s','--format=%cI',REG)
    stamps=[r['started_at_utc'] for r in raw]
    order={'registration_commit':REG,'registration_author_time':git('show','-s','--format=%aI',REG),'registration_committer_time':commit_time,'run_code_commit':RUN,'freeze_commit':FREEZE,'registration_ancestor_of_freeze':True,'registration_files_byte_identical':identical,'specified_source_changes_registration_to_run':changed,'first_started_at_utc':min(stamps),'last_started_at_utc':max(stamps),'all_starts_after_registration_commit':all(datetime.fromisoformat(t.replace('Z','+00:00'))>datetime.fromisoformat(commit_time) for t in stamps),'verified_trace_hashes':len(inv['traces'])}
    compact={k:v for k,v in registered.items() if k not in ['tasks','per_call_runtime_usage']}
    compact['tasks']=[{k:v for k,v in t.items() if k!='rows'} for t in registered['tasks']]
    result={'status':STATUS,'ordering_evidence':order,'publication':json.loads((D1/'PILOT_PUSH_HISTORY.json').read_text()),'reserve_scheduling_from_code':'Conditional on primary invalidity, in listed order; an invalid reserve does not fill a replacement slot.','registered_analysis_A':compact,'exploratory_not_registered_B':{'primaries':exploratory_group(reports[:12]),'reserves':exploratory_group(reports[12:])}}
    (D1/'pilot_scores.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=[STATUS,'','# D1 pilot results','','## Ordering and publication evidence','','```json',json.dumps(order,indent=2),'```','','The runner first scheduled all primary tasks, computed their validity, and scheduled reserves conditionally in listed order while valid replacement slots remained. This statement is from the code at the run commit, not inferred from the answers. The excluded smoke trace was already committed in the run commit.','','```json',json.dumps(result['publication'],indent=2),'```','','## Call counts by task and input group','','| Task | Group | Run | Accepted | Rejected | Timed out |','| --- | --- | ---: | ---: | ---: | ---: |']
    for t in reports:
        for g,c in t['counts'].items():lines.append(f"| {t['task_id']} | {g} | {c['run']} | {c['accepted']} | {c['rejected']} | {c['timed_out']} |")
    lines+=['','## A. Registered analysis applied to the pilot','',f"Selected valid tasks: {registered['valid_tasks']}. Registered outcome: **{registered['outcome']}**. The registration requires at least 10 valid tasks. These pilot estimates and p-value are not confirmatory.",'','| Measure | Equal-task mean | 95% task bootstrap interval | N tasks |','| --- | ---: | --- | ---: |']
    for k,v in registered['primary'].items():lines.append(f"| {k} | {v['mean']} | {v['interval_95']} | {v['n_tasks']} |")
    alt=registered['secondary_K_alt'];lines+=['',f"Exact one-sided sign-flip p: {registered['exact_one_sided_p']}.",f"K_alt: {alt['mean']}; interval {alt['interval_95']}; N = {alt['n_tasks']}; fixed-rule outcome: **{alt['rule_outcome']}**.",'','All four reserves were attempted in order. None was valid. The registered selection therefore retained the eight valid primaries, without including unused or invalid reserves in the estimates.','', '```json',json.dumps(registered['replacements'],indent=2),'```','','### Registered descriptives','','```json',json.dumps(registered['descriptive'],indent=2),'```','','Per-task rates, output distributions, free-choice agreement, free-pair shares and their denominators are retained in section A of `pilot_scores.json`. The notes are saved in raw traces and were not scored.','','## B. exploratory, not registered','','Agreement below requires both replicates to be gate-accepted; two missing answers do not count as agreement. Output distributions count accepted pairs only; rejections are counted separately. Free-choice shares are undefined when the two free-choice calls do not both produce the same accepted pair. P90 uses nearest rank over recorded values. Missing usage is reported, never imputed.']
    for label,g in result['exploratory_not_registered_B'].items():
        lines+=['',f'### {label.title()}','',f"{g['n_tasks']} tasks; {g['n_calls']} calls.",'','```json',json.dumps({'agreement':g['agreement_incoming_pairs'],'equal_free_pair_by_input_group':g['equal_free_pair_by_input_group'],'rejection_reason_counts':g['rejection_reason_counts']},indent=2),'```','','| Runtime or usage field | Recorded | Missing | Mean | Median | P90 |','| --- | ---: | ---: | ---: | ---: | ---: |']
        for k,v in g['runtime_and_usage'].items():lines.append(f"| {k} | {v['recorded']} | {v['missing']} | {v['mean']} | {v['median']} | {v['p90_nearest_rank']} |")
        lines+=['','| Task | Input | Accepted output distribution | Rejected | Timeout | r1, r2 outputs | Agreement |','| --- | --- | --- | ---: | ---: | --- | --- |']
        for t in g['tasks']:
            for pair,dist in t['output_pair_distributions'].items():
                agreement=t['run_to_run_agreement'][pair]
                lines.append(f"| {t['task_id']} | {pair} | {json.dumps(dist['distribution'])} | {dist['rejected']} | {dist['timed_out']} | {agreement['outputs']} | {agreement['agree']} |")
        lines+=['','| Task | Free pair | Free agreement | Target-in free-pair share | Target-out free-pair share |','| --- | --- | --- | --- | --- |']
        for t in g['tasks']:lines.append(f"| {t['task_id']} | {t['free_choice_pair']} | {t['free_choice_agree']} | {t['equal_free_pair_by_input_group']['in']} | {t['equal_free_pair_by_input_group']['out']} |")
    lines+=['','## Failures and deviations','','- Reserve scheduling was conditional on task invalidity, not unconditional. All four reserves have saved calls, but none qualified as a valid replacement.','- The registration was committed before the calls but was not published before the run. All analyses here are of a pilot, not a confirmatory experiment.','- The earlier freeze request described an incomplete schedule and no reserves. Its inventory showed all 224 scheduled trace filenames. Those requested statements were not adopted.','- The original runner kept the 110 rejected calls and continued through the registered primary/reserve schedule. Their saved terminal error events report a usage-limit failure. Some traces also contain CLI-internal reconnect attempts and 403 errors, listed verbatim in the exploratory reason records. The harness did not launch replacement attempts for a saved call; it used only the registered reserve rule.','- The original Step 0 command had a working-directory error before its actual checks; the corrected preconditions passed. No failed pytest test was recorded.','- Earlier HTTPS authentication and an SSH authentication check failed. After the user authenticated, the exact history was pushed without force or rewritten commits. No matching repository PushEvent was available when queried; the first push time is local UTC captured immediately after success.','- JSON cannot begin with an unquoted prose status line and remain valid. `pilot_scores.json` therefore carries the required status as its first `status` field; this Markdown file starts with the literal required line.','- Bootstrap denominator and percentile conventions were fixed in the original registration/execution record before calls. K_alt uses eligible task-level rates. No scoring formula was changed for this pilot report.','','No new model calls, overwritten traces, new registration, or D2 work occurred. The smoke test remains excluded.']
    (D1/'D1_PILOT_RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'outcome':registered['outcome'],'valid_tasks':registered['valid_tasks'],'counts':{'run':registered['total_run'],'accepted':registered['total_gate_accepted'],'rejected':registered['total_rejected']},'groups':{k:{'agreement':v['agreement_incoming_pairs'],'reasons':v['rejection_reason_counts']} for k,v in result['exploratory_not_registered_B'].items()}},indent=2))

if __name__=='__main__':main()
