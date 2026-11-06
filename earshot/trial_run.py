"""Read-only descriptive report for the frozen trial, excluding system issues."""
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess

from .d1 import D1,ROOT,load_tasks
from .d1_score import task_summary,metric
from .d1_pilot import verify_inventory,exploratory_group,usage

STATUS="Trial run. Registered locally in `1a6936e` before its first call, but not published. Reclassified as a trial on 7 November 2026 at 04:04 IST, before it was scored. Not part of D1's results."


def classify(row):
    if row.get('exit_code')==0 and row.get('answer') is not None:return 'ran'
    errors=json.dumps({'error':row.get('error'),'events':row.get('events'),'stderr':row.get('stderr')}).lower()
    if row.get('exit_code')==1 and row.get('answer') is None and 'usage limit' in errors:return 'system_issue'
    raise ValueError('unclassified trace '+row.get('name','unknown'))


def clean_descriptive(value):
    if isinstance(value,dict):
        return {('system_issue' if k=='rejected' else k):clean_descriptive(v) for k,v in value.items() if k not in ['rejection_reason_counts','failures','recorded_reasons','gate_result']}
    if isinstance(value,list):return [clean_descriptive(x) for x in value]
    return value


def main():
    verify_inventory()
    mapping=json.loads((D1/'PATH_MAP.json').read_text())
    raw=[json.loads((ROOT/e['new_path']).read_text()) for e in mapping['traces']]
    classes={r['name']:classify(r) for r in raw}
    if Counter(classes.values())!=Counter({'ran':114,'system_issue':110}):raise ValueError('classification counts differ from fixed rules')
    prior,files,tasks=load_tasks()
    reports=[task_summary(tasks[tid],D1/'traces') for tid in prior['primary_task_ids']+prior['reserve_task_ids']]
    complete=[t for t in reports if sum(classes[r['name']]=='ran' for r in t['rows'])==14]
    if len(complete)!=8:raise ValueError('complete-task count differs')
    estimates={k:metric([r[k] for r in complete]) for k in ['K_in','K_out','R_add','delta']}
    alt=metric([r['K_alt'] for r in complete if r['K_alt'] is not None])
    # Regression check: preserve the previously computed descriptive values exactly.
    # This is a historical Git object path, not a current filesystem reference.
    before=json.loads(subprocess.check_output(['git','show','6a07580:sprint/partD/D1/pilot_scores.json'],cwd=ROOT))
    assert estimates==before['registered_analysis_A']['primary']
    assert alt=={k:v for k,v in before['registered_analysis_A']['secondary_K_alt'].items() if k!='rule_outcome'}
    descriptive=clean_descriptive(exploratory_group(complete))
    summaries=[]
    for t in reports:
        groups={}
        for g in ['in','out','free']:
            rr=[r for r in t['rows'] if ('free' if r['incoming_pair']=='free' else 'in' if t['target'] in r['incoming_pair'] else 'out')==g]
            groups[g]={'ran':sum(classes[r['name']]=='ran' for r in rr),'accepted':sum(classes[r['name']]=='ran' and r['gate_result']=='accepted' for r in rr),'system_issue':sum(classes[r['name']]=='system_issue' for r in rr),'timed_out':0}
        n=sum(v['ran'] for v in groups.values())
        summaries.append({'task_id':t['task_id'],'role':'primary' if t['task_id'] in prior['primary_task_ids'] else 'reserve','answer_count':n,'system_issue_count':14-n,'completion':'complete' if n==14 else 'partial' if n else 'did_not_run','counts_by_group':groups})
    ran=[r for r in raw if classes[r['name']]=='ran'];system=[r for r in raw if classes[r['name']]=='system_issue']
    assert all(r['gate_result']=='accepted' for r in ran)
    first=min(system,key=lambda r:r['started_at_utc']);exceptions=[{'name':r['name'],'started_at_utc':r['started_at_utc'],'finished_at_utc':r['finished_at_utc']} for r in ran if r['started_at_utc']>first['started_at_utc']]
    result={'status':STATUS,'status_provenance':{'decision_time':'2026-11-07T04:04:00+05:30','decision_time_source':'Rick stated this decision time; no independent contemporaneous decision log is available.','historical_analysis':'The pilot was already scored and published before this reorganisation. Original report commit d30d57c was authored and committed at 2026-11-07T04:17:16+05:30. Its publication is retained in Git history.','not_published_scope':'The registration was not published before the run; it and the pilot analysis were published later.','revision_generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z')},'counts':{'saved_records':224,'ran':114,'gate_accepted':114,'system_issue':110,'gate_rejections':0,'timeouts':0,'complete_primary_tasks':8,'partial_primary_tasks':1,'primary_tasks_did_not_run':3,'reserve_tasks_did_not_run':4},'descriptive_estimates_complete_tasks':estimates,'K_alt_descriptive':alt,'complete_task_descriptives':descriptive,'task_record_classification':summaries,'system_issue_timing':{'first_started_at_utc':first['started_at_utc'],'later_answer_producing_calls':exceptions,'claim_every_call_after_first_stopped':False},'ordering_evidence':before['ordering_evidence'],'publication_history':before['publication'],'path_map':'PATH_MAP.json','system_issue_inventory':'system_issue/SYSTEM_ISSUE.md','partial_answer_records':[{'name':r['name'],'incoming_pair':r['incoming_pair'],'output_pair':r['output_pair'],'elapsed_seconds':r.get('elapsed_seconds'),'tool_calls':sum(e.get('type')=='item.completed' for e in r.get('tool_calls',[])),'usage':usage(r),'trace_path':next(e['new_path'] for e in mapping['traces'] if Path(e['new_path']).stem==r['name'])} for r in ran if r['task_id'] not in {t['task_id'] for t in complete}]}
    (D1/'trial_run_scores.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=[STATUS,'','# Trial-run results','','The 04:04 IST reclassification time above is Rick\'s stated decision time, not an independently timestamped event in these files. The pilot had already been scored and published before this reorganisation; that report was committed as `d30d57c` at 04:17:16 IST. Git history retains it. “Not published” in the status means not published before the run; the registration and previous analysis were subsequently published.','','## What ran','','**114 calls produced answers; all passed the gate. There were 0 gate rejections and 0 timeouts.** Eight of 12 primary tasks have all 14 answers. `study-ensure-published` has 2 of 14 answers. The other three primary tasks and all four reserves produced no answers because of the account usage-limit system issue.','','The 110 non-answer diagnostic records are documented in [system_issue/SYSTEM_ISSUE.md](system_issue/SYSTEM_ISSUE.md). They are not agent results, gate rejections, or failures of the agents. The raw trace bytes retain their original field names; the classification here supersedes their former aggregate labels.','','## Descriptive results on the eight complete tasks','','No hypothesis-test outcome is claimed. The previously computed estimates and bootstrap intervals are retained exactly. The two answers from the partial task do not enter these task-level summaries.','','| Measure | Equal-task mean | 95% task bootstrap interval | N tasks |','| --- | ---: | --- | ---: |']
    for k,v in estimates.items():lines.append(f"| {k} | {v['mean']} | {v['interval_95']} | {v['n_tasks']} |")
    lines += [f"| K_alt | {alt['mean']} | {alt['interval_95']} | {alt['n_tasks']} |",'','The intervals describe only these eight complete tasks. They do not turn this trial into a sealed D1 result.','', '## Counts by task and input group','','| Task | Role | Group | Ran | Accepted | System issue | Timeout |','| --- | --- | --- | ---: | ---: | ---: | ---: |']
    for t in summaries:
        for g,c in t['counts_by_group'].items():lines.append(f"| {t['task_id']} | {t['role']} | {g} | {c['ran']} | {c['accepted']} | {c['system_issue']} | {c['timed_out']} |")
    lines+=['','## Free-pair shares and run-to-run agreement','','The agreement measure uses incoming-pair replicates with two actual answers. Free-choice agreement is listed separately.','', '```json',json.dumps({'agreement':descriptive['agreement_incoming_pairs'],'equal_free_pair_by_input_group':descriptive['equal_free_pair_by_input_group']},indent=2),'```','','## Output pairs on complete tasks','','| Task | Incoming pair | Output distribution | r1/r2 outputs | Agreement |','| --- | --- | --- | --- | --- |']
    for t in descriptive['tasks']:
        for pair,v in t['output_pair_distributions'].items():
            agreement=t['run_to_run_agreement'][pair];lines.append(f"| {t['task_id']} | {pair} | {json.dumps(v['distribution'])} | {agreement['outputs']} | {agreement['agree']} |")
    lines+=['','| Task | Free pair | Free agreement | Target-in free-pair share | Target-out free-pair share |','| --- | --- | --- | --- | --- |']
    for t in descriptive['tasks']:lines.append(f"| {t['task_id']} | {t['free_choice_pair']} | {t['free_choice_agree']} | {t['equal_free_pair_by_input_group']['in']} | {t['equal_free_pair_by_input_group']['out']} |")
    lines+=['','## Wall time, tools and token usage','','These statistics cover the 112 answer-producing calls from the eight complete tasks. Diagnostic timings from the 110 system-issue invocations are not agent execution times and are excluded. The two partial-task answers are listed separately in the machine-readable record. Token fields are taken from saved usage events, without estimation; p90 uses nearest rank.','','| Field | Recorded | Missing | Mean | Median | P90 |','| --- | ---: | ---: | ---: | ---: | ---: |']
    for k,v in descriptive['runtime_and_usage'].items():lines.append(f"| {k} | {v['recorded']} | {v['missing']} | {v['mean']} | {v['median']} | {v['p90_nearest_rank']} |")
    lines+=['','## Ordering and publication record','','```json',json.dumps(result['ordering_evidence'],indent=2),'```','','```json',json.dumps(result['publication_history'],indent=2),'```','','Old paths in ordering evidence and the frozen inventory identify historical Git objects. `PATH_MAP.json` maps every one to its current path and preserves its hash. Archived registration/code hashes describe the historical run and do not authorise a new run with the refactored paths.','','## Deviations and clarifications','','- The runner scheduled primary records first and invoked reserves conditionally after its original validity checks. The reserves have system-issue diagnostic records but no agent answers. They are not replacement results.','- Registration was committed locally before calls but not published before them. All current reporting is descriptive trial work.','- The freeze request initially described an incomplete invocation schedule and no reserves. There are 224 saved invocation records; only 114 have answers. This distinction is now explicit.','- The usage-limit system issue accounts for 110 non-answer records. Some contain CLI-internal reconnect attempts and 403 errors. No saved invocation was rerun by the harness.','- The earliest system issue started at 18:59:17.298991 UTC. Two successful invocations in the same batch started milliseconds later, as listed in SYSTEM_ISSUE.md. The requested blanket claim that every later-starting call stopped is not supported.','- The requested 04:04 IST decision time is attributed to Rick. The existing analysis and its publication precede this file reorganisation; they are not removed from Git history.','- An original Step 0 shell command had a working-directory error before the actual preconditions were checked; the corrected checks passed.','- HTTPS and SSH authentication initially failed. After authentication, the exact commit history was pushed without force or rewritten commits. No matching PushEvent was available when queried; the recorded initial publication time is local UTC immediately after success.','- Valid JSON carries the required status in its first field rather than beginning with unquoted prose.','- Bootstrap weighting and endpoints are unchanged. Runtime summaries now cover answer-producing calls from the eight complete tasks; the previous mixed invocation summaries remain available in history.','','## Reorganisation and integrity','','No trace content changed. All 224 new paths and hashes are in PATH_MAP.json and match the inventory committed in 424528e. The two model-call entrypoints for this frozen trial are disabled. No new model calls, new registration, D2 work, rebase, amendment, or force-push was performed.']
    (D1/'TRIAL_RUN_RESULTS.md').write_text('\n'.join(lines)+'\n')
    print('Trial report regenerated: 114 ran, 110 system issue; prior descriptive estimates match exactly.')

if __name__=='__main__':main()
