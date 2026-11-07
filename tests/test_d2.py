"""D2 checks use scripted data, fake CLIs and local bare remotes only."""
import copy
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import pytest
from earshot import d2_design as D, d2_score as S
from earshot.d2 import Stage, seal2_record
from earshot.d2_reliability import classify_role, AttemptRunner
from earshot.reliability import Control
from earshot.integrity import digest
from earshot.d2_integrity import verify_phase, verify_ledger, ledger, ready
from earshot.d2_checkpoint import checkpoint, restore
from earshot.prompts import WORDINGS, listener_prompt, relay_prompt, sender_prompt
from earshot.score import x_w_s

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'sprint/partD/D2/tasks.json').read_text())
PATTERNS = json.loads((ROOT / 'earshot/system_issue_patterns.json').read_text())
PENDING = {'status': 'PENDING_CALIBRATION', 'patterns': []}


def answer(pair):
    return {'required_memory_refs': D.refs(pair), 'note': 'scripted'}


def row(pair, **metadata):
    return dict(answer=answer(pair), classification='accepted', **metadata)


def allocation(target='A', evidence='source evidence'):
    return {'minutes': {c: 60 if c == target else 0 for c in 'ABCD'},
            'primary_file': target, 'evidence': evidence}


def control(folder):
    return Control(folder, datetime.now(timezone.utc) + timedelta(days=1))


def executor(mode='transparent'):
    def execute(spec, ctl, reserve):
        reserve()
        if spec['role'] == 'receiver':
            return dict(exit_code=0, answer=allocation(), events=[])
        task = next(t for t in DATA['tasks'] if t['id'] == spec['task_id'])
        pair = task['codewords'][spec['kind']] if spec['role'] == 'sender' else spec['incoming_pair'] or task['codewords']['T-in']
        if mode == 'drop-out' and spec['group'] == 'hop1' and spec['kind'] == 'T-out':
            return dict(exit_code=0, answer=None)
        return dict(exit_code=0, answer=answer(pair), events=[])
    return execute


def stage(tmp_path, data=DATA, mode='transparent'):
    folder = tmp_path / 'run'
    return Stage(data, folder, control(folder), executor(mode), PATTERNS)


def records(stage):
    return [json.loads(p.read_text()) for p in sorted((stage.folder / 'traces').glob('*.json'))]


def test_source_tasks_and_rules():
    assert {t['id'] for t in DATA['tasks']} == {f'item-{i:02}' for i in range(1, 17)}
    for c in 'ABCD':
        primary = [t for t in DATA['tasks'] if t['target_file'] == c and t['role'] == 'primary']
        assert sorted(t['p'] for t in primary) == [x for x in 'ABCD' if x != c]
        assert sorted(t['k'] for t in primary) == [1, 2, 3]
    for t in DATA['tasks']:
        assert {key: t[key] for key in D.ref_rule(t['target_file'], t['k'])} == D.ref_rule(t['target_file'], t['k'])
        assert t['target_file'] in t['codewords']['T-in']
        assert D.complement(t['codewords']['T-in']) == t['codewords']['T-out']
        if t['role'] == 'reserve': assert t['k'] == 1
        for p in DATA['candidate_files'].values():
            assert p not in t['id'] and Path(p).name not in t['id']
            assert p not in t['request'] and Path(p).name not in t['request']
        assert t['target_function'].split('.')[-1].lower() not in t['request'].lower()
        assert not any(x in t['id'].split('-') for x in 'ABCD')
        assert t['target_function'] not in t['id']
        assert t['request'].endswith('Allocate 60 minutes of review across the candidate files.')


def test_S_frozen_and_identical():
    rng = random.Random(77)
    for _ in range(100):
        rows = []
        for pair in ('AB', 'CD'):
            for w in range(1, 4):
                cuts = sorted([0, 60] + [rng.randrange(61) for _ in range(3)])
                a = allocation(); a['minutes'] = dict(zip('ABCD', [b-a for a,b in zip(cuts, cuts[1:])]))
                rows.append(dict(classification='accepted', answer=a, incoming_pair=pair, wording=w, receiver='honest', set_number=1))
        cells = {(arm, w): next(r for r in rows if r['incoming_pair'] == pair and r['wording'] == w) for arm,pair in [('public','AB'),('codeword','CD')] for w in range(1,4)}
        assert S.audit(rows, 'AB', 'CD', 'honest') == x_w_s(cells, 'allocation_l1')
        assert S.audit(rows, 'AB', 'AB', 'honest')['S'] == 0


@pytest.mark.parametrize('pairs,n', [({'T-in':'AB','T-out':'CD'},2), ({'T-in':'AB','T-out':'AB'},2), ({'T-in':'AB','T-out':'AC'},4)])
def test_schedule(pairs, n):
    t = dict(DATA['tasks'][0], target_file='A', codewords={'T-in':'AB','T-out':'CD'})
    calls = D.receiver_calls(t, DATA['candidate_files'], pairs)
    assert len({s['incoming_pair'] for s in calls}) == n
    informative = {s['incoming_pair'] for s in calls if s['set_number'] == 2}
    assert len(informative) == n // 2
    assert 41 <= 17 + len(calls) <= 65
    assert [s['name'] for s in D.receiver_order(calls,13)] == [s['name'] for s in D.receiver_order(list(reversed(calls)),13)]
    assert D.receiver_order(calls,13) != D.receiver_order(calls,14)


def test_prompts():
    t=DATA['tasks'][0]; files=DATA['candidate_files']
    for receiver in ('honest','coalition','conceal'):
        for w in range(1,4):
            s=D.spec(t,'receiver','receiver',files,pair='AB',receiver=receiver,wording=w)
            prefix = WORDINGS['coalition' if receiver=='conceal' else receiver][w-1]
            if receiver=='conceal': prefix+=' '+D.CONCEAL
            assert s['prompt'].split('\nTrial input:')[0] == prefix
            if receiver!='conceal': assert s['prompt']==listener_prompt(t,receiver,'irrelevant',w,D.refs('AB'),files)
            assert D.spec(t,'receiver','receiver',files,pair='AB',receiver=receiver,wording=w,parent='relay')['prompt']==s['prompt']
    assert D.sender_calls(t,files)[0]['prompt']==sender_prompt(dict(t,hidden_pair=list(t['decoded_pairs']['T-in'])),files)
    assert D.relay_calls(t,files)[0]['prompt']==relay_prompt([],t,files)


def test_decisions_and_family():
    assert S.ES.sign_flip_test([1]*12)['p']==2/4096
    stats={a:{h:[None]*12 for h in S.CLAIMS} for a in ('codex','claude')}
    stats['codex']['H1']=[-1]*12
    stats['codex']['H2']=[1]*12
    stats['codex']['H3']=[1]*8
    result=S.confirmatory(stats)
    assert result['family_size']==8
    assert result['tests']['codex:H1']['opposite_direction']
    assert not result['tests']['codex:H1']['holds']
    assert result['tests']['codex:H3']['holds']  # step 3
    stats['codex']['H3']=[1]*7
    r=S.confirmatory(stats)['tests']['codex:H3']
    assert r['status']=='INCONCLUSIVE' and r['p']==1
    assert S.confirmatory(stats,reduced=True)['family_size']==5


def test_exploratory_fixed_family():
    arms={a:[dict(id=f't{i}',**{h:float(i) for h in S.CLAIMS},H1_keep_only=1.,**{'H3_T-in':1.,'H3_T-out':1.}) for i in range(12)] for a in ('codex','claude')}
    for reduced,n in [(False,10),(True,5)]:
        result=S.exploratory(arms,reduced)
        assert result['family_size']==n
        p=[v['p'] for v in result['tests'].values()]
        expected=S.ES.benjamini_hochberg(p)
        assert [v['p_adjusted'] for v in result['tests'].values()]==list(expected['p_adj'])
        for v in result['tests'].values(): assert v['label']=='exploratory'
    for r in arms['codex'][7:]:r['H1_keep_only']=None
    r=S.exploratory(arms)
    assert r['tests']['codex:H1_keep_only']['p']==1 and r['family_size']==10


def test_ratio_and_file_check():
    rows=[dict(id=str(i),target_file=c,D_sender=float(i+1),D_last=float(10+i),H1=float(i+1)) for i,c in enumerate('ABCD')]
    result=S.ratio(rows)
    assert result['value']==2.5/11.5 and 'interval' not in result
    for r in rows:r['D_last']=0.
    assert S.ratio(rows)['value'] is None
    for r in rows:r['D_last']=-1.
    assert S.ratio(rows)['value'] is None
    check=S.file_check(rows,'H1')
    assert check['positive_file_means']==4 and check['out_of']==4 and 'p' not in check
    assert 'design_effect' in check


@pytest.mark.parametrize('change', ['float','negative','too_large','sum','missing_primary','missing_evidence','bool'])
def test_receiver_validation(change):
    a=allocation()
    if change=='float': a['minutes']['A']=60.0
    if change=='negative': a['minutes']['B']=-1
    if change=='too_large': a['minutes']['A']=61
    if change=='sum': a['minutes']['A']=59
    if change=='missing_primary': del a['primary_file']
    if change=='missing_evidence': del a['evidence']
    if change=='bool': a['minutes']['A']=True
    assert classify_role({'exit_code':0,'answer':a},PATTERNS,'receiver')[0]=='gate_rejected'
    assert classify_role({'exit_code':0,'answer':allocation()},PATTERNS,'receiver')[0]=='accepted'
    assert classify_role({'exit_code':0,'answer':None},PATTERNS,'receiver')[0]=='gate_rejected'


def test_two_hop_and_missing_defaults():
    t=dict(DATA['tasks'][0],codewords={'T-in':'AB','T-out':'CD'})
    rows=[row('AB',name='one',group='hop1',kind='T-in',replicate=1),
          row('AC',name='two',group='hop1',kind='T-in',replicate=2),
          row('AB',name='three',group='hop1',kind='T-in',replicate=3),
          row('AB',name='four',group='hop2',kind='T-in',parent='one'),
          row('AB',name='five',group='hop2',kind='T-in',parent='two')]
    m=S.two_hop(t,rows,'AB')['T-in']
    assert m['two_hop_survival']==S.fraction(1,2)
    assert m['recreated_at_hop2']==S.fraction(1,2)
    assert m['hop2_keep']==S.fraction(1,2)
    assert m['hop2_keep_default']==S.fraction(1,1)
    assert m['chains_not_completed']==1
    assert len(D.hop2_calls(t,DATA['candidate_files'],rows[:3]))==3
    out=S.task_score(t,rows,PENDING)
    assert out['hop1']['T-in']['unclassified']==2
    assert out['H1_keep_only'] is None and out['H4'] is None
    assert D.default_pair([row('AB'),row('AC'),row('AD')]) is None
    assert D.default_pair([row('AB'),row('AB'),{'classification':'gate_rejected'}])=='AB'


def test_phase_skip_and_hop2(tmp_path):
    s=stage(tmp_path,mode='drop-out')
    with pytest.raises(RuntimeError,match='sender'):s.relays()
    s.senders();s.relays()
    assert len(s.state['skipped_receivers'])==12 and s.receiver_plan(0)==[]
    rows=records(s)
    assert sum(r['group']=='hop2' for r in rows)==36
    rec=seal2_record(ROOT,'codex',ROOT/'sprint/partD/D1/SEAL1.json','fake',s,7) if s.folder.is_relative_to(ROOT) else None
    for t in DATA['tasks']:
        if t['id'] in s.state['selected_ids']:
            result=S.task_score(t,[r for r in rows if r['task_id']==t['id']],PENDING,True)
            assert all(result[h] is None for h in S.CLAIMS)


def test_full_fake_pipeline(tmp_path):
    arms={}
    for arm in ('codex','claude'):
        s=stage(tmp_path/arm)
        s.senders();s.relays()
        rec={'receiver_order_seed':42,'receiver_order':[v['name'] for v in s.receiver_plan(42)],'skipped_receivers':[]}
        s.receivers(rec,lambda:None)
        rows=records(s)
        assert len(rows)==12*41
        assert sum(r['group']=='hop2' for r in rows)==72
        before={p:p.read_bytes() for p in (s.folder/'traces').glob('*.json')}
        # Restart skips saved final answers; never relaunch.
        def no_execute(*args):raise AssertionError('saved answer reran')
        restarted=Stage(DATA,s.folder,s.control,no_execute,PATTERNS)
        restarted.receivers(rec,lambda:None)
        assert all(p.read_bytes()==b for p,b in before.items())
        arms[arm]=dict(rows=rows,state=s.state)
    result=S.score(DATA,arms,PENDING,dry=True)
    assert result['status']=='DRY RUN: not a result'
    for arm in ('codex','claude'):
        for t in result['arms'][arm]['tasks']:
            assert t['delta']==0.0
            assert 'receiver_calls' in t and 'hop2' in t and t['H4'] is None
    assert all(r['decision']=='DRY RUN: not a result' for r in result['confirmatory']['tests'].values())
    assert result['confirmatory']['tests']['codex:H4']['p']==1
    assert result['exploratory']['family_size']==10
    with pytest.raises(RuntimeError,match='PENDING_CALIBRATION'):S.score(DATA,arms,PENDING)


def test_draft_refusal():
    with pytest.raises(RuntimeError):ready({'status':'DRAFT'},PENDING)
    with pytest.raises(RuntimeError):ready({'status':'REGISTERED','family_size':8},PENDING)


def git(repo,*args):
    return subprocess.check_output(['git',*map(str,args)],cwd=repo,text=True,stderr=subprocess.PIPE).strip()


def commit(repo,message):
    git(repo,'add','.');git(repo,'commit','-m',message)


def test_publication_and_ledger_guards(tmp_path):
    repo=tmp_path/'repo';repo.mkdir();remote=tmp_path/'remote.git'
    git(tmp_path,'init','--bare',remote);git(repo,'init','-b','main')
    git(repo,'config','user.email','fake@example.invalid');git(repo,'config','user.name','Fake test')
    git(repo,'remote','add','origin',remote)
    source=repo/'source';source.write_text('frozen')
    s1=repo/'SEAL1.json';d1=repo/'SEAL1.sha256'
    s1.write_text(json.dumps({'files':[dict(path='source',sha256=digest(source))]}));d1.write_text(digest(s1))
    reg={'seal_1_files':['source']}
    commit(repo,'seal1');first=git(repo,'rev-parse','HEAD');git(repo,'push','origin','main')
    verify_phase(repo,'main',s1,d1,reg,'relay')
    with pytest.raises(RuntimeError):verify_phase(repo,'main',s1,d1,reg,'receiver',arm='codex')
    run=repo/'run';(run/'traces').mkdir(parents=True);trace=run/'traces/a.json';trace.write_text('{}')
    s2=repo/'SEAL2.json';d2=repo/'SEAL2.sha256'
    s2.write_text(json.dumps(dict(arm='codex',seal_1_commit=first,seal_1_sha256=digest(s1),files=[dict(path='run/traces/a.json',sha256=digest(trace))])))
    d2.write_text(digest(s2));commit(repo,'seal2')
    with pytest.raises(RuntimeError):verify_phase(repo,'main',s1,d1,reg,'receiver',s2,d2,'codex')
    git(repo,'push','origin','main')
    info=verify_phase(repo,'main',s1,d1,reg,'receiver',s2,d2,'codex')
    snap=checkpoint(repo,run,'codex',info['phase_commit'],digest(s1),'registration')
    assert snap['branch']=='d2-codex-runtime'
    restored=repo/'restored'
    restore(repo,restored,'codex',info['phase_commit'],digest(s1),'registration')
    assert (restored/'traces/a.json').read_bytes()==trace.read_bytes()
    # A changed runtime trace cannot overwrite an earlier checkpoint.
    trace.write_text('{"edited":true}')
    with pytest.raises(RuntimeError):checkpoint(repo,run,'codex',info['phase_commit'],digest(s1),'registration')
    trace.write_text('{}')
    lp=repo/'LEDGER.json';ld=repo/'LEDGER.sha256'
    lp.write_text(json.dumps(ledger(run,'codex',first,s1)));ld.write_text(digest(lp));commit(repo,'ledger');git(repo,'push','origin','main')
    verify_ledger(repo,'main',lp,ld,run)
    verify_phase(repo,'main',s1,d1,reg,'receiver',s2,d2,'codex',require_head=False)
    with pytest.raises(RuntimeError):verify_phase(repo,'main',s1,d1,reg,'receiver',s2,d2,'codex')
    trace.write_text('{"edited":true}')
    with pytest.raises(RuntimeError):verify_ledger(repo,'main',lp,ld,run)
    trace.write_text('{}');source.write_text('FROZEN')
    with pytest.raises(RuntimeError):verify_phase(repo,'main',s1,d1,reg,'receiver',s2,d2,'codex',require_head=False)


def test_usage_pause_and_durable_resume_fake_cli(tmp_path):
    cli=tmp_path/'fake_cli.py'
    cli.write_text('import sys\nsys.stderr.write("You have hit your usage limit.")\nsys.exit(1)\n')
    ctl=control(tmp_path/'run');count=[]
    def execute(name,prompt,ctl,reserve):
        reserve();count.append(name)
        proc=subprocess.run([sys.executable,str(cli)],capture_output=True,text=True)
        return dict(exit_code=proc.returncode,answer=None,stderr=proc.stderr)
    runner=AttemptRunner(tmp_path/'run',PATTERNS,ctl,execute,True,role='receiver')
    r=runner.run('one','prompt')
    assert ctl.blocked=='manual: usage limit'
    assert r['administrative_status']=='paused_usage_limit'
    runner.run('two','prompt')
    assert count==['one']
    restarted=Control(tmp_path/'run',datetime.now(timezone.utc)+timedelta(days=1))
    assert restarted.blocked
    restarted.resume_by_rick()
    def success(name,prompt,ctl,reserve):reserve();return dict(exit_code=0,answer=allocation())
    r=AttemptRunner(tmp_path/'run',PATTERNS,restarted,success,True,role='receiver').run('one','prompt')
    assert r['attempt']==2 and r['classification']=='accepted'
    r=AttemptRunner(tmp_path/'run',PATTERNS,restarted,lambda *a:pytest.fail('reran'),True,role='receiver').run('one','prompt')
    assert r['attempt']==2


def test_H4_no_followers_is_undefined():
    t=dict(DATA['tasks'][0],target_file='A')
    rows=[]
    for receiver,file in [('coalition','C'),('conceal','A')]:
        for w in range(1,4):
            rows.append(dict(name=f'{receiver}{w}',role='receiver',group='receiver',classification='accepted',incoming_pair='AB',receiver=receiver,wording=w,set_number=1,answer=allocation(file)))
    result=S.task_score(t,rows,{'status':'CALIBRATED','patterns':[]})
    assert result['following']['coalition']['rate']==1
    assert result['following']['conceal']['rate']==0
    assert result['H4'] is None


def test_transparent_control_with_nonconstant_allocations():
    t=DATA['tasks'][0];rng=random.Random(221)
    rows=[]
    for pair in (t['codewords']['T-in'],t['codewords']['T-out']):
        for kind in ('honest','coalition','conceal'):
            for w in range(1,4):
                cuts=sorted([0,60]+[rng.randrange(61) for _ in range(3)])
                a=allocation();a['minutes']=dict(zip('ABCD',[b-a for a,b in zip(cuts,cuts[1:])]))
                rows.append(dict(classification='accepted',incoming_pair=pair,receiver=kind,wording=w,set_number=1,answer=a))
    a,b=t['codewords'].values()
    sender=S.audit_difference(rows,a,b)['D']
    last=(S.audit_difference(rows,a,b)['D']+S.audit_difference(rows,b,a)['D'])/2
    assert last-sender==0.0


def test_pinned_task_lines_and_workspace():
    import ast
    from earshot.d1v2 import verify_workspace
    verify_workspace(DATA['workspace'],DATA)
    for t in DATA['tasks']:
        source=(Path(DATA['workspace'])/DATA['candidate_files'][t['target_file']]).read_text()
        symbols={}
        def walk(nodes,prefix=''):
            for n in nodes:
                if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
                    symbols[prefix+n.name]=n.lineno
                    if isinstance(n,ast.ClassDef):walk(n.body,prefix+n.name+'.')
        walk(ast.parse(source).body)
        assert symbols[t['target_function']]==t['target_line']


def test_retry_cutoff_unknown_and_ninety_pause(tmp_path):
    for label,record,reason in [
        ('unknown',dict(exit_code=1,answer=None,stderr='unclassified problem'),'manual: unclassified no answer'),
        ('ninety',dict(exit_code=0,answer=allocation(),usage_pause_reason='usage at 90%'),'manual: usage at 90%')]:
        folder=tmp_path/label;ctl=control(folder)
        def execute(name,prompt,ctl,reserve):reserve();return record
        runner=AttemptRunner(folder,PATTERNS,ctl,execute,True,role='receiver')
        result=runner.run('call','prompt')
        assert ctl.blocked==reason
        if label=='ninety':assert result['classification']=='accepted'
        else:assert not (folder/'traces/call.json').exists()
    folder=tmp_path/'cutoff';ctl=Control(folder,datetime.now(timezone.utc)+timedelta(seconds=100))
    def never(*args):pytest.fail('process after last-launch deadline')
    result=AttemptRunner(folder,PATTERNS,ctl,never,True,role='receiver').run('call','prompt')
    assert result['administrative_status']=='stopped_by_cutoff'


def test_receiver_publication_refusal_and_no_late_replacement(tmp_path):
    s=stage(tmp_path);s.senders();s.relays()
    before=len(records(s))
    def refused():raise RuntimeError('Seal 2 unpublished')
    with pytest.raises(RuntimeError,match='unpublished'):s.receivers({},refused)
    assert len(records(s))==before
    selected=list(s.state['selected_ids'])
    s.execute=lambda *args:pytest.fail('sender phase repeated')
    assert s.senders()==selected


def test_explicit_input_must_be_sealed(tmp_path):
    from earshot.d2_integrity import require_sealed_input
    source=tmp_path/'source';source.write_text('expected')
    seal=tmp_path/'seal.json';seal.write_text(json.dumps({'files':[dict(path='source',sha256=digest(source))]}))
    require_sealed_input(tmp_path,source,seal)
    rogue=tmp_path/'rogue';rogue.write_text('expected')
    with pytest.raises(RuntimeError):require_sealed_input(tmp_path,rogue,seal)
    source.write_text('edited')
    with pytest.raises(RuntimeError):require_sealed_input(tmp_path,source,seal)
