"""Historical descriptive helpers; command now reports the frozen trial."""
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

REG='1a6936ef646e45671768928c5e245a053897d9a7'
FREEZE='424528e7f0ae64cd1204f958aeba08c45edc9aaf'
RUN='101406f54575f155e699ff9adb15b10bc2fe2c70'


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def verify_inventory():
    inv=json.loads(subprocess.check_output(['git','show',FREEZE+':sprint/partD/D1/UNSEALED_RUN.json'],cwd=ROOT))
    mapping=json.loads((D1/'PATH_MAP.json').read_text())
    by_old={e['old_path']:e for e in mapping['traces']}
    expected={r['path'] for r in inv['traces']}
    if set(by_old)!=expected:raise ValueError('path-map trace set mismatch')
    observed=set()
    for e in inv['traces']:
        mapped=by_old[e['path']]
        if mapped['sha256']!=e['sha256']:raise ValueError('mapped hash disagrees with frozen inventory')
        path=ROOT/mapped['new_path'];data=path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=e['sha256'] or len(data)!=e['bytes']:raise ValueError('trace hash or byte-count mismatch: '+str(path))
        observed.add(path.resolve())
    actual={p.resolve() for folder in [D1/'traces',D1/'system_issue'] for p in folder.glob('*.json')}
    if observed!=actual:raise ValueError('unexpected or missing trace file')
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
    from .trial_run import main as report_trial
    report_trial()

if __name__=='__main__':main()
