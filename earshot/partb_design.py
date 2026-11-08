"""Frozen Part B schedule and prompts; no model or filesystem side effects."""
from itertools import groupby
import random

from .partb import render_prompt

CONDITIONS=('H0','H-in','H-out','C-in','C-out')


def schedule(tasks,seed=20261108):
    blocks=[]
    for task in sorted(tasks,key=lambda x:x['id']):
        target=task['target']
        for number,partner in enumerate(c for c in 'ABCD' if c!=target):
            inside=''.join(sorted(target+partner))
            outside=''.join(c for c in 'ABCD' if c not in inside)
            calls=[]
            for condition in CONDITIONS:
                pair=None if condition=='H0' else inside if condition.endswith('-in') else outside
                decoded=None if pair is None else ''.join(c for c in 'ABCD' if c not in pair)
                calls.append({'name':f"{task['id']}-block{number+1}-{condition}",
                    'task_id':task['id'],'block':number+1,'condition':condition,
                    'receiver':'coalition' if condition.startswith('C') else 'honest',
                    'incoming_pair':pair,'incoming_includes_target':None if pair is None else target in pair,
                    'decoded_pair':decoded,'decoded_includes_target':None if decoded is None else target in decoded})
            blocks.append(calls)
    rng=random.Random(seed);rng.shuffle(blocks)
    for calls in blocks:rng.shuffle(calls)
    return [call for calls in blocks for call in calls]


def validate_schedule(tasks,calls,seed=20261108):
    if len({t['id'] for t in tasks})!=len(tasks):raise RuntimeError('duplicate task IDs')
    expected=schedule(tasks,seed)
    if calls!=expected:raise RuntimeError('schedule differs from the frozen allocation/order')
    if len({c['name'] for c in calls})!=len(calls):raise RuntimeError('duplicate call IDs')
    return list(blocks(calls))


def blocks(calls):
    for _,group in groupby(calls,key=lambda c:(c['task_id'],c['block'])):
        group=list(group)
        if len(group)!=5 or {c['condition'] for c in group}!=set(CONDITIONS):
            raise RuntimeError('incomplete or interleaved five-condition block')
        yield group


def prompts(tasks,calls,candidates):
    by_id={t['id']:t for t in tasks}
    return {c['name']:render_prompt(by_id[c['task_id']],c,candidates) for c in calls}
