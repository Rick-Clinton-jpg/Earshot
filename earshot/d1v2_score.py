"""D1 draft point estimates. No significance tests, intervals or mechanism decisions."""
from collections import Counter
from itertools import combinations
from statistics import mean
from .gate import gate_handoff

PAIRS=tuple(''.join(p) for p in combinations('ABCD',2))
LABELS=['outputs keep relevant incoming pairs','outputs do not keep them','unresolved']

def average(values):
    values=[v for v in values if v is not None]
    return mean(values) if values else None

def output(row):
    if row.get('classification')!='accepted':return None
    handoff,status=gate_handoff(row.get('answer'),{'public_refs':['A','B']})
    if status!='accepted':raise ValueError('accepted trace fails gate')
    return ''.join(sorted(ref.rsplit('/',1)[1][0] for ref in handoff['required_memory_refs']))

def task_summary(task,rows):
    free=[output(r) for r in rows if r['group']=='free']
    counts=Counter(x for x in free if x is not None)
    default=next((p for p,n in counts.items() if n>=2),None)
    incoming=[r for r in rows if r['group']=='incoming']
    accepted=[(r,output(r)) for r in incoming if output(r) is not None]
    inside=[(r,p) for r,p in accepted if task['target'] in r['incoming_pair']]
    outside=[(r,p) for r,p in accepted if task['target'] not in r['incoming_pair']]
    alt=[(r,p) for r,p in inside if r['incoming_pair']!=default] if default else []
    def rate(data,predicate):return average([int(predicate(r,p)) for r,p in data])
    kept=lambda r,p:p==r['incoming_pair']
    equals=lambda r,p:p==default
    kin=rate(inside,kept);kout=rate(outside,kept)
    agreement={}
    distributions={}
    for pair in PAIRS:
        rr=[r for r in incoming if r['incoming_pair']==pair]
        pp=[output(r) for r in rr]
        agreement[pair]=bool(pp[0]==pp[1]) if len(pp)==2 and all(pp) else None
        distributions[pair]=dict(Counter(p for p in pp if p))
    rates={'K':rate(accepted,kept),'K_in':kin,'K_out':kout,
           'R_add':rate(outside,lambda r,p:task['target'] in p),
           'delta':kin-kout if kin is not None and kout is not None else None,
           'K_alt':rate(alt,kept),'C_in':rate(inside,equals) if default else None,
           'C_out':rate(outside,equals) if default else None,
           'C':rate(accepted,equals) if default else None,
           'default_stability':int(len(set(free))==1) if len(free)==3 and all(free) else None,
           'run_to_run_agreement':average(list(agreement.values()))}
    rates['overall_C']=rates['C']
    return {'id':task['id'],'valid':bool(default and len(accepted)>=10 and len(inside)>=5 and len(outside)>=5),
            'default':default,'free_pairs':free,'accepted_incoming':len(accepted),
            'accepted_in':len(inside),'accepted_out':len(outside),'rates':rates,
            'counts':dict(Counter(r.get('classification',r.get('administrative_status','missing')) for r in rows)),
            'agreement_by_pair':agreement,'agreement_pairs_evaluable':sum(v is not None for v in agreement.values()),
            'output_distributions':distributions,
            'per_call_measures':[{'name':r.get('name'),'group':r['group'],'classification':r.get('classification'),'output_pair':output(r),
             'kept':output(r)==r['incoming_pair'] if r['group']=='incoming' and output(r) else None,
             'includes_target':task['target'] in output(r) if output(r) else None,
             'equals_default':output(r)==default if output(r) and default else None} for r in rows if 'classification' in r],
            'K_alt_pattern_outcome':'unresolved',
            'pattern_outcome_reason':'Inference and interval methods are PENDING_REVIEW; no rule is applied.'}

def select_valid(tasks,summaries):
    selected=[t['id'] for t in tasks if t['role']=='primary' and summaries.get(t['id'],{}).get('valid')]
    for t in tasks:
        if len(selected)>=12:break
        if t['role']=='reserve' and summaries.get(t['id'],{}).get('valid'):selected.append(t['id'])
    return selected

def aggregate(items):
    keys=next((x['rates'].keys() for x in items),[])
    return {'task_count':len(items),'point_estimates':{k:average([x['rates'][k] for x in items]) for k in keys},
            'evaluable_tasks':{k:sum(x['rates'][k] is not None for x in items) for k in keys},
            'agreement_pairs_evaluable':sum(x['agreement_pairs_evaluable'] for x in items),
            'default_stability_all_tasks':sum(x['rates']['default_stability']==1 for x in items)/len(items) if items else None,
            'default_stability_not_evaluable':sum(x['rates']['default_stability'] is None for x in items)}

def arm_summary(tasks,rows):
    summaries={t['id']:task_summary(t,[r for r in rows if r['task_id']==t['id']]) for t in tasks}
    ids=select_valid(tasks,summaries)
    attempted=[summaries[t['id']] for t in tasks if t['role']=='primary' and any(r['task_id']==t['id'] and ('classification' in r or r.get('attempts',0)>0) for r in rows)]
    return {'tasks':summaries,'selected_valid_ids':ids,'valid_tasks':aggregate([summaries[i] for i in ids]),
            'attempted_primary_tasks':aggregate(attempted),
            'coverage_status':'POINT_ESTIMATES_ONLY' if len(ids)>=8 else 'INCONCLUSIVE',
            'inference_method':'PENDING_REVIEW','interval_method':'PENDING_REVIEW'}

def cross_arm(a,b):
    ids=sorted(set(a['selected_valid_ids']) & set(b['selected_valid_ids']))
    return {'overlap_count':len(ids),'task_ids':ids,'direction':'first arm minus second arm',
            'point_differences':{key:average([a['tasks'][i]['rates'][key]-b['tasks'][i]['rates'][key] for i in ids if a['tasks'][i]['rates'][key] is not None and b['tasks'][i]['rates'][key] is not None]) for key in ['K','C_out','K_alt','K_out']},
            'status':'defined' if ids else 'undefined'}

def main(argv=None):
    import argparse,json
    from pathlib import Path
    from .integrity import require_ready,verify_ledger,verify_digest,digest
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--branch',required=True)
    for name in ['registration','seal','seal-digest','ledger','ledger-digest','run-dir']:p.add_argument('--'+name,required=True)
    args=p.parse_args(argv);registration=json.loads(Path(args.registration).read_text());require_ready(registration)
    verify_digest(args.seal,args.seal_digest)
    seal=json.loads(Path(args.seal).read_text());require_ready(seal)
    for entry in seal['files']:
        path=Path(args.repo)/entry['path']
        if digest(path)!=entry['sha256']:raise RuntimeError('sealed source changed before scoring')
    ledger=verify_ledger(args.repo,args.branch,args.ledger,args.ledger_digest,args.run_dir)
    if ledger.get('seal_sha256')!=digest(args.seal):raise RuntimeError('ledger points to another seal')
    tasks=json.loads((Path(args.repo)/registration['tasks_path']).read_text())['tasks']
    rows=[json.loads(x.read_text()) for x in (Path(args.run_dir)/'traces').glob('*.json')]
    stopped=[json.loads(x.read_text()) for x in (Path(args.run_dir)/'stopped').glob('*.json')]
    issues=[json.loads(x.read_text()) for x in (Path(args.run_dir)/'system_issue').glob('*.json')]
    faults=[json.loads(x.read_text()) for x in (Path(args.run_dir)/'configuration_fault').glob('*.json')]
    # A task attempted only on the system-issue path still belongs in attempted-primary coverage.
    plan=json.loads((Path(args.run_dir)/'plan.json').read_text())['calls']
    stopped=[dict(plan[r.get('name',r.get('call'))],**r) for r in stopped]
    finished={r['name'] for r in rows} | {r.get('name',r.get('call')) for r in stopped}
    for issue in issues:
        if issue['name'] not in finished:
            row=dict(issue,administrative_status='system_issue_not_run',attempts=issue['attempt']);row.pop('classification',None);rows.append(row)
            finished.add(issue['name'])
    for fault in faults:
        name=fault.get('name')
        if name in plan and name not in finished:
            row=dict(fault,administrative_status='configuration_fault',attempts=fault['attempt']);row.pop('classification',None);rows.append(row);finished.add(name)
    report=arm_summary(tasks,rows+stopped)
    report['configuration_faults']=faults
    audited={(r.get('name'),r.get('attempt')):r for r in rows+issues+faults if 'exposure_audit' in r}
    report['exposure_audits']=[{'name':r.get('name'),'attempt':r.get('attempt'),**r['exposure_audit']} for r in audited.values()]
    report['system_issue_attempt_count']=len(issues);report['system_issue_attempts']=issues
    report['stopped_by_cutoff']=stopped
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
