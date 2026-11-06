import ast,hashlib,json,os,re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def data():return json.loads((ROOT/'sprint/partD/D1/tasks.json').read_text())

def test_fresh_targets_balanced_and_prompt_free_candidates():
    d=data();tasks=d['tasks'];assert len(tasks)==16 and len({t['id'] for t in tasks})==16
    for role,n in [('primary',3),('reserve',1)]:assert Counter(t['target'] for t in tasks if t['role']==role)==dict.fromkeys('ABCD',n)
    old={'A':{'label_commitment','checkpoint','ensure_published','parse_assignment'},'B':{'codeword','receiver_input','decoded_correct','summarize'},'C':{'public_decoded_pair','eligible_targets','validate_registration','_summary'},'D':{'trial_input','_assignment','equivalence','summarize'}}
    for t in tasks:
        assert t['target_function'] not in old[t['target']]
        assert 'hidden_pair' not in t
        for path in d['candidate_files'].values():assert Path(path).name not in t['request']
    assert not set(d['candidate_files'].values()) & set(d['excluded_prompt_files'])

def test_target_lines_hashes_and_complete_mention_audit():
    d=data();workspace=Path(os.environ['EARSHOT_TEST_WORKSPACE'])
    for path,expected in d['candidate_sha256'].items():
        source=(workspace/path).read_text();assert hashlib.sha256((workspace/path).read_bytes()).hexdigest()==expected
        functions={n.name:n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
        assert len(functions)>=4
        for t in d['tasks']:
            if d['candidate_files'][t['target']]==path:assert functions[t['target_function']].lineno==t['target_line']
        mentions=[{'line':i,'text':line} for i,line in enumerate(source.splitlines(),1) if re.search(r'coalition|codeword|decod|required_memory_refs',line,re.I)]
        assert mentions==d['remaining_mentions'][path]
