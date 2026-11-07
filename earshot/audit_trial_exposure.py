"""Read-only baseline audit of the frozen 114 answered trial calls."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from .exposure import ADAPTERS,RULE,audit
from .integrity import git


def baseline(repo, source, workspace):
    repo,source=Path(repo),Path(source)
    source_commit=git(source,'rev-parse','HEAD')
    if source_commit!='1a4b471b3cfb4ed6d5def7c61356c5230af8c082':raise RuntimeError('wrong source pin')
    sources={name:(source/'dogwhistle'/name).read_text() for name in ADAPTERS}
    inventory=json.loads((repo/'sprint/trial_run/PATH_MAP.json').read_text())
    rows=[]
    for entry in inventory['traces']:
        if entry['classification']!='ran':continue
        path=repo/entry['new_path'];data=path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=entry['sha256']:raise RuntimeError('trial trace differs from frozen path map')
        record=json.loads(data)
        if record['exit_code']!=0 or record['answer'] is None:raise RuntimeError('not an answered trial trace')
        rows.append({'path':entry['new_path'],'sha256':entry['sha256'],**audit(record,workspace,sources)})
    if len(rows)!=114:raise RuntimeError('answered trace count differs from 114')
    return {'status':'Retrospective descriptive audit of existing trial logs; not D1 results.',
            'source_commit':source_commit,'frozen_inventory_commit':inventory['frozen_inventory_commit'],
            'adapter_source_sha256':{name:hashlib.sha256((source/'dogwhistle'/name).read_bytes()).hexdigest() for name in ADAPTERS},
            'rule':RULE,'calls':len(rows),'adapter_exposure_counts':dict(Counter(r['adapter_exposure'] for r in rows)),
            'calls_with_explicit_outside_observations':sum(bool(r['outside_workspace_observations']) for r in rows),
            'outside_observation_count':sum(len(r['outside_workspace_observations']) for r in rows),'per_call':rows}


def main(argv=None):
    parser=argparse.ArgumentParser()
    for name in ['repo','source','workspace','output']:parser.add_argument('--'+name,required=True)
    args=parser.parse_args(argv)
    result=baseline(args.repo,args.source,args.workspace)
    path=Path(args.output)
    if path.resolve().is_relative_to((Path(args.repo)/'sprint/trial_run').resolve()):raise RuntimeError('trial files are protected')
    with path.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='per_call'},indent=2))

if __name__=='__main__':main()
