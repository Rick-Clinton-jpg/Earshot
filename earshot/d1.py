"""Registered honest-relay D1 only. No receivers or codeword instructions."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from itertools import combinations
import argparse
import hashlib
import json
from pathlib import Path

from .config import Config
from .gate import accepted_refs, gate_handoff
from .prompts import relay_prompt
from .runner import run_agent, verify_registration, PINNED_CLI_VERSION

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / 'results/presprint/relay/provenance'
D1 = ROOT / 'sprint/partD/D1'
PAIRS = [''.join(x) for x in combinations('ABCD', 2)]


def load_tasks():
    prior_reg = json.loads((PRIOR / 'registration.json').read_text())
    prior_design = json.loads((PRIOR / 'tasks.json').read_text())
    indexed = {t['id']: {'id':t['id'], 'request':t['request'], 'target':t['target']} for t in prior_design['tasks']}
    # No prior public_refs, codeword_refs or hidden_pair enters D1's tasks/prompts.
    return prior_reg, prior_design['candidate_files'], indexed


def slots(task):
    return [{'name':f"d1-{task['id']}-{pair}-r{r}", 'task_id':task['id'], 'incoming_pair':pair, 'replicate':r} for pair in PAIRS + ['free'] for r in [1,2]]


def incoming_refs(pair):
    return [] if pair == 'free' else [f'handoff_refs/{x}.txt' for x in pair]


def annotate(record, task, slot):
    raw = record.get('answer')
    # Free input never passes the gate; it is an intentionally empty incoming cue.
    fallback_task = {'public_refs':list('AB')}
    delivered, status = gate_handoff(raw, fallback_task)
    accepted = record.get('exit_code') == 0 and status == 'accepted'
    pair = ''.join(sorted(ref.split('/')[1].split('.')[0] for ref in delivered['required_memory_refs'])) if accepted else None
    record.update(task_id=task['id'], target=task['target'], incoming_pair=slot['incoming_pair'], replicate=slot['replicate'], gate_result='accepted' if accepted else 'rejected', gate_detail=status, gated_handoff=delivered, output_pair=pair, kept=(pair == slot['incoming_pair']) if accepted else None, includes_target=(task['target'] in pair) if accepted else None)
    return record


def run_slot(task, files, slot, config):
    info = verify_registration(config.registration)
    registration = json.loads(Path(config.registration).read_text())
    expected = registration['settings']
    if (config.model,config.reasoning_effort,config.workers,config.timeout) != (expected['model'],expected['reasoning_effort'],expected['workers'],expected['timeout']):
        raise RuntimeError('runtime settings differ from registration')
    text = relay_prompt(incoming_refs(slot['incoming_pair']),task,files)
    return run_agent(slot['name'],text,ROOT/'earshot/sender.schema.json',config,finalize=lambda record:annotate(record,task,slot))


def run_task(task, files, config):
    with ThreadPoolExecutor(max_workers=config.workers) as pool:
        pending = {pool.submit(run_slot, task, files, slot, config):slot for slot in slots(task)}
        for future in as_completed(pending):
            result = future.result()
            print(json.dumps({'name':result['name'],'exit_code':result.get('exit_code'),'gate':result['gate_result']}),flush=True)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',type=Path,required=True)
    parser.add_argument('--smoke',action='store_true')
    args=parser.parse_args(argv)
    prior,files,tasks=load_tasks()
    config=Config(args.workspace,D1/'traces',stub=False,registration=D1/'D1_registration.json')
    verify_registration(config.registration)
    if args.smoke:
        task=tasks['study-label-commitment']; slot={'name':'smoke-study-label-commitment-BC-r1','task_id':task['id'],'incoming_pair':'BC','replicate':1}
        result=run_slot(task,files,slot,replace(config,run_dir=ROOT/'sprint/partD/smoke'))
        assert result.get('answer') and result['gate_result']=='accepted'
        assert result.get('started_at_utc') and result.get('finished_at_utc') and result.get('cli_version')==PINNED_CLI_VERSION
        assert result['prompt_sha256']==hashlib.sha256(relay_prompt(incoming_refs('BC'),task,files).encode()).hexdigest()
        print(json.dumps({'smoke':'passed','excluded_from_D1':True,'name':result['name']}),flush=True)
        return
    from .d1_score import task_summary
    for tid in prior['primary_task_ids']:
        run_task(tasks[tid],files,config)
    invalid=[tid for tid in prior['primary_task_ids'] if not task_summary(tasks[tid],config.run_dir)['valid']]
    needed=len(invalid)
    for tid in prior['reserve_task_ids']:
        if needed == 0: break
        run_task(tasks[tid],files,config)
        if task_summary(tasks[tid],config.run_dir)['valid']: needed-=1

if __name__=='__main__': main()
