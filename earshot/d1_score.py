"""D1's pre-specified accepted-output rates and task-level inference."""
from collections import Counter
from datetime import datetime
from fractions import Fraction
import hashlib
import json
from math import lcm
from pathlib import Path
import random
from statistics import mean

from .d1 import D1, ROOT, PAIRS, incoming_refs, load_tasks, slots, annotate
from .runner import verify_registration


def exact_p(values):
    rational=[Fraction(v) for v in values]
    scale=lcm(*(v.denominator for v in rational)) if rational else 1
    integers=[int(v*scale) for v in rational]
    distribution=Counter({0:1})
    for v in integers:
        nxt=Counter()
        for total,count in distribution.items():
            nxt[total+v]+=count; nxt[total-v]+=count
        distribution=nxt
    observed=sum(integers)
    return sum(n for total,n in distribution.items() if total>=observed)/(2**len(integers))


def interval(values):
    if not values: return None
    rng=random.Random(20261107); n=len(values)
    estimates=sorted(sum(values[rng.randrange(n)] for _ in range(n))/n for _ in range(10000))
    return [estimates[250],estimates[9750]]


def metric(values):
    return {'mean':mean(values) if values else None,'interval_95':interval(values),'n_tasks':len(values)}


def task_summary(task,folder):
    rows=[]
    for slot in slots(task):
        path=Path(folder)/(slot['name']+'.json')
        if not path.exists() and (Path(folder).parent / 'PATH_MAP.json').exists():
            diagnostic = Path(folder).parent / 'system_issue' / path.name
            if diagnostic.exists(): path = diagnostic
        if not path.exists():
            rows.append({'name':slot['name'],'incoming_pair':slot['incoming_pair'],'gate_result':'missing','output_pair':None,'kept':None,'includes_target':None,'task_id':task['id'],'target':task['target'],'elapsed_seconds':None})
            continue
        raw=json.loads(path.read_text())
        # Recompute measurements from raw answer; never trust stored gate labels alone.
        recalculated=annotate(dict(raw),task,slot)
        for key in ['gate_result','output_pair','kept','includes_target']:
            if key in raw and raw[key]!=recalculated[key]:
                raise ValueError(f'saved {key} disagrees with raw answer: {path}')
        error_text=json.dumps({'error':raw.get('error'),'events':raw.get('events'),'stderr':raw.get('stderr')}).lower()
        if raw.get('exit_code')==1 and raw.get('answer') is None and 'usage limit' in error_text:
            # Preserve original bytes/labels; distinguish infrastructure records in derived data.
            recalculated['gate_result']='system_issue'
        rows.append(recalculated)
    def group(row):
        return 'free' if row['incoming_pair']=='free' else ('in' if task['target'] in row['incoming_pair'] else 'out')
    counts={}
    for g in ['in','out','free']:
        rr=[r for r in rows if group(r)==g]
        counts[g]={'scheduled':len(rr),'run':sum(r['gate_result'] not in ('missing','system_issue') for r in rr),'system_issue':sum(r['gate_result']=='system_issue' for r in rr),'accepted':sum(r['gate_result']=='accepted' for r in rr),'rejected':sum(r['gate_result']=='rejected' for r in rr),'timed_out':sum('timeout' in r.get('error','').lower() or 'timed out' in r.get('error','').lower() for r in rr),'missing':sum(r['gate_result']=='missing' for r in rr)}
    valid=counts['in']['accepted']>=5 and counts['out']['accepted']>=5
    accepted=[r for r in rows if r['gate_result']=='accepted']
    in_rows=[r for r in accepted if group(r)=='in'];out_rows=[r for r in accepted if group(r)=='out']
    kin=Fraction(sum(r['kept'] for r in in_rows),len(in_rows)) if in_rows else None
    kout=Fraction(sum(r['kept'] for r in out_rows),len(out_rows)) if out_rows else None
    radd=Fraction(sum(r['includes_target'] for r in out_rows),len(out_rows)) if out_rows else None
    free=[r for r in rows if group(r)=='free']
    free_pair=free[0]['output_pair'] if all(r['gate_result']=='accepted' for r in free) and free[0]['output_pair']==free[1]['output_pair'] else None
    alt=[r for r in in_rows if r['incoming_pair']!=free_pair] if free_pair else []
    kalt=Fraction(sum(r['kept'] for r in alt),len(alt)) if alt else None
    overall=[r for r in accepted if group(r)!='free']
    return {'task_id':task['id'],'target':task['target'],'valid':valid,'invalid_reason':None if valid else 'fewer than 5 accepted incoming-pair calls in at least one input group','counts':counts,'K_in':float(kin) if kin is not None else None,'K_out':float(kout) if kout is not None else None,'R_add':float(radd) if radd is not None else None,'delta':float(kin-kout) if kin is not None and kout is not None else None,'delta_fraction':str(kin-kout) if kin is not None and kout is not None else None,'K_alt':float(kalt) if kalt is not None else None,'K_alt_n_calls':len(alt),'free_choice_outputs':[r['output_pair'] for r in free],'free_choice_agree':free_pair is not None,'free_choice_pair':free_pair,'overall_keep_rate':sum(r['kept'] for r in overall)/len(overall) if overall else None,'output_distributions':{pair:dict(Counter(r['output_pair'] for r in accepted if r['incoming_pair']==pair)) for pair in PAIRS+['free']},'free_pair_share_all_accepted':sum(r['output_pair']==free_pair for r in accepted)/len(accepted) if free_pair and accepted else None,'free_pair_share_denominator':len(accepted) if free_pair else 0,'rows':rows}


def analyze(folder,primary,reserves,tasks):
    reports=[task_summary(tasks[tid],folder) for tid in primary]
    missing=[r for r in reports if not r['valid']]
    selected=[r for r in reports if r['valid']]; replacements=[]
    reserve_index=0
    for bad in missing:
        while reserve_index<len(reserves):
            tid=reserves[reserve_index]; reserve_index+=1
            if not any((Path(folder)/(s['name']+'.json')).exists() for s in slots(tasks[tid])):
                continue
            reserve=task_summary(tasks[tid],folder);reports.append(reserve)
            replacements.append({'invalid_primary':bad['task_id'],'reason':bad['invalid_reason'],'reserve':tid,'reserve_valid':reserve['valid']})
            if reserve['valid']:
                selected.append(reserve);break
    estimates={key:metric([r[key] for r in selected]) for key in ['K_in','K_out','R_add','delta']}
    p=exact_p([Fraction(r['delta_fraction']) for r in selected]) if selected else None
    alt=metric([r['K_alt'] for r in selected if r['K_alt'] is not None])
    ci=alt['interval_95']
    alt['rule_outcome']='keep relevant refs' if ci and ci[0]>.5 else ('rewrite to their own choice' if ci and ci[1]<.5 else 'unresolved')
    rows=[r for task in reports for r in task['rows'] if r['gate_result']!='missing']
    return {'valid_tasks':len(selected),'selected_task_ids':[r['task_id'] for r in selected],'outcome':'INCONCLUSIVE' if len(selected)<10 else ('mean delta > 0 supported' if p<=.05 else 'mean delta > 0 not shown'),'primary':estimates,'exact_one_sided_p':p,'secondary_K_alt':alt,'replacements':replacements,'descriptive':{'overall_keep_rate_task_mean':metric([r['overall_keep_rate'] for r in selected]),'free_pair_share_task_mean':metric([r['free_pair_share_all_accepted'] for r in selected if r['free_pair_share_all_accepted'] is not None]),'by_target':{letter:{key:mean([r[key] for r in selected if r['target']==letter]) if any(r['target']==letter for r in selected) else None for key in ['K_in','K_out','R_add','delta']} for letter in 'ABCD'}},'tasks':reports,'total_records':len(rows),'total_run':sum(r['gate_result']!='system_issue' for r in rows),'total_system_issue':sum(r['gate_result']=='system_issue' for r in rows),'total_gate_accepted':sum(r['gate_result']=='accepted' for r in rows),'total_rejected':sum(r['gate_result']=='rejected' for r in rows),'per_call_runtime_usage':[{'name':r['name'],'elapsed_seconds':r.get('elapsed_seconds'),'usage':next((e['usage'] for e in reversed(r.get('events',[])) if e.get('type')=='turn.completed' and 'usage' in e),None),'error':r.get('error'),'exit_code':r.get('exit_code')} for r in rows]}


def main():
    from .trial_run import main as report_trial
    report_trial()

if __name__=='__main__':main()
