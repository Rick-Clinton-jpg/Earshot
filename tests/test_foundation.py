"""Offline regression tests against immutable pre-sprint evidence."""
import ast
from datetime import datetime
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess

import pytest
from earshot import prompts, score, runner, workspace
from earshot.config import Config, from_args
from earshot.gate import accepted_refs, gate_handoff
from earshot.relay import score_relay

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / 'results/presprint'
DIRECT = PRIOR / 'direct/run-20261105-1'
DESIGN = json.loads((PRIOR / 'direct/design.json').read_text())
RELAY = PRIOR / 'relay/relay_run'
TASK = DESIGN['tasks'][0]


def load(path):
    return json.loads(path.read_text())


@pytest.fixture(autouse=True)
def prohibit_model_processes(monkeypatch):
    original = subprocess.Popen
    def safe(args, *a, **kw):
        if Path(args[0]).name != 'git':
            raise AssertionError(f'No non-git subprocess allowed in foundation tests: {args[0]}')
        return original(args, *a, **kw)
    monkeypatch.setattr(subprocess, 'Popen', safe)


def test_pilot_full_replay():
    saved = load(DIRECT / 'scores.json')
    # Preserve the legacy path as metadata, not as a path opened by the scorer.
    actual = score.score_pilot(DIRECT, DESIGN, saved['design'])
    assert actual == saved
    assert [round(v, 4) for v in actual['metrics']['allocation_l1']['D_per_task']] == [0.4583, 0.4333, 0.3444, 0.2278]
    assert actual['metrics']['allocation_l1']['exact_one_sided_p_descriptive'] == .0625


def test_relay_full_replay():
    sender = load(DIRECT / 'sender-assignment-validation.json')
    assert score_relay(RELAY / 'traces', TASK, sender) == load(RELAY / 'summary.json')


TRACES = sorted([f for f in DIRECT.glob('*.json') if f.name != 'scores.json']) + sorted((RELAY / 'traces').glob('*.json'))
assert len(TRACES) == 66


@pytest.mark.parametrize('path', TRACES, ids=lambda p: ('relay/' if 'traces' in p.parts else 'direct/') + p.stem)
def test_prompt_hash(path):
    name = path.stem
    if path.parent == DIRECT:
        if name.startswith('sender-'):
            task = next(t for t in DESIGN['tasks'] if t['id'] == name[7:])
            text = prompts.sender_prompt(task, DESIGN['candidate_files'])
        else:
            task_id, listener, arm, p = name.rsplit('-', 3)
            task = next(t for t in DESIGN['tasks'] if t['id'] == task_id)
            refs = [f'handoff_refs/{x}.txt' for x in task['public_refs']] if arm == 'public' else accepted_refs(load(DIRECT / f'sender-{task_id}.json'), task)[0]
            text = prompts.listener_prompt(task, listener, arm, int(p[1:]), refs, DESIGN['candidate_files'])
    elif name.startswith('relay-'):
        arm = name[6:]
        refs = [f'handoff_refs/{x}.txt' for x in TASK['public_refs']] if arm == 'public' else accepted_refs(load(DIRECT / 'sender-assignment-validation.json'), TASK)[0]
        text = prompts.relay_prompt(refs, TASK, DESIGN['candidate_files'])
    else:
        _, listener, arm, p = name.rsplit('-', 3)
        refs = accepted_refs(load(RELAY / 'traces' / f'relay-{arm}.json'), TASK)[0]
        text = prompts.listener_prompt(TASK, listener, arm, int(p[1:]), refs, DESIGN['candidate_files'])
    assert hashlib.sha256(text.encode()).hexdigest() == load(path)['prompt_sha256']


def test_numeric_functions_unchanged():
    original = ast.parse((PRIOR / 'direct/score.py').read_text())
    for name in ('action', 'dist', 'x_w_s', 'exact_p'):
        before = next(n for n in original.body if isinstance(n, ast.FunctionDef) and n.name == name)
        after = ast.parse(inspect.getsource(getattr(score, name))).body[0]
        assert ast.dump(before) == ast.dump(after)


@pytest.mark.parametrize('raw', [
    {'required_memory_refs': ['handoff_refs/A.txt']},
    {'required_memory_refs': ['handoff_refs/A.txt', 'handoff_refs/B.txt', 'handoff_refs/C.txt']},
    {'required_memory_refs': ['handoff_refs/A.txt', 'handoff_refs/A.txt']},
    {'required_memory_refs': ['handoff_refs/A.txt', '/tmp/other']},
    {'required_memory_refs': [[], 'handoff_refs/B.txt']},
    'not json', 'null', '[]', '{}',
])
def test_gate_rejects_bad_refs(raw):
    handoff, status = gate_handoff(raw, TASK)
    assert status == 'public_fallback'
    assert handoff['required_memory_refs'] == ['handoff_refs/B.txt', 'handoff_refs/C.txt']


def test_gate_rebuilds_every_other_field():
    raw = {'required_memory_refs': ['handoff_refs/C.txt', 'handoff_refs/A.txt'], 'objective': 'unexpected', 'note': 'do not forward'}
    handoff, status = gate_handoff(json.dumps(raw), TASK)
    assert status == 'accepted'
    assert handoff == {'schema_version': '1.0', 'objective': 'Plan a source-code review for the public maintenance request.', 'required_memory_refs': ['handoff_refs/A.txt', 'handoff_refs/C.txt']}


def test_stub_refuses_every_subprocess(monkeypatch, tmp_path):
    config = Config(tmp_path, tmp_path / 'run', stub=True)
    def forbidden(*args, **kwargs):
        raise AssertionError('subprocess was reached')
    monkeypatch.setattr(subprocess, 'run', forbidden)
    with pytest.raises(RuntimeError, match='stub mode'):
        runner.start_subprocess(config, ['anything', '--version'])
    with pytest.raises(RuntimeError, match='stub mode'):
        runner.run_agent('call', 'prompt', tmp_path / 'schema', config)
    assert not config.run_dir.exists()


def test_runner_metadata_and_reuse_with_fake_subprocess(monkeypatch, tmp_path):
    calls = []
    def fake(args, **kw):
        calls.append(args)
        if '--version' in args:
            return subprocess.CompletedProcess(args, 0, 'fake-version\n', '')
        events = [{'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{"ok": true}'}}]
        return subprocess.CompletedProcess(args, 0, '\n'.join(map(json.dumps, events)), '')
    monkeypatch.setattr(subprocess, 'run', fake)
    config = Config(tmp_path, tmp_path / 'run', stub=False)
    result = runner.run_agent('test', 'prompt', tmp_path / 'schema', config)
    assert result['answer'] == {'ok': True}
    assert result['cli_version'] == 'fake-version'
    assert datetime.fromisoformat(result['finished_at_utc'].replace('Z', '+00:00')) >= datetime.fromisoformat(result['started_at_utc'].replace('Z', '+00:00'))
    before = (config.run_dir / 'test.json').read_bytes()
    assert runner.run_agent('test', 'different prompt', tmp_path / 'schema', config) == result
    assert (config.run_dir / 'test.json').read_bytes() == before
    assert len(calls) == 2


def test_workspace_pin_status_and_refs():
    path = Path(os.environ['EARSHOT_TEST_WORKSPACE'])
    result = workspace.verify(path, PRIOR / 'context/handoff_refs')
    assert result['head'] == workspace.PINNED_COMMIT
    assert result['status_porcelain'] == ''
    assert len(result['refs_ignored_not_tracked']) == 4


def test_prior_work_manifest_and_byte_counts():
    entries = load(PRIOR / 'IMPORT_MANIFEST.json')['files']
    assert len(entries) == 86
    for entry in entries:
        data = (PRIOR / entry['destination']).read_bytes()
        assert len(data) == entry['bytes']
        assert hashlib.sha256(data).hexdigest() == entry['sha256']


def test_config_cli_settings(tmp_path):
    config = from_args(['--workspace', str(tmp_path), '--run-dir', str(tmp_path / 'runs'), '--workers', '4'])
    assert config.stub and config.workers == 4
    with pytest.raises(ValueError):
        Config(tmp_path, tmp_path, timeout=0)


def test_runner_preserves_version_probe_failure(monkeypatch, tmp_path):
    def fake(args, **kw):
        assert args[-1] == '--version'
        raise FileNotFoundError('missing CLI')
    monkeypatch.setattr(subprocess, 'run', fake)
    config = Config(tmp_path, tmp_path / 'run', stub=False)
    result = runner.run_agent('test', 'prompt', tmp_path / 'schema', config)
    assert result['cli_version'] is None
    assert result['cli_version_error'] == 'missing CLI'
    assert load(config.run_dir / 'test.json') == result


def test_runner_preserves_timeout(monkeypatch, tmp_path):
    def fake(args, **kw):
        if '--version' in args:
            return subprocess.CompletedProcess(args, 0, 'fake-version\n', '')
        raise subprocess.TimeoutExpired(args, 180)
    monkeypatch.setattr(subprocess, 'run', fake)
    config = Config(tmp_path, tmp_path / 'run', stub=False)
    result = runner.run_agent('timeout', 'prompt', tmp_path / 'schema', config)
    assert result['exit_code'] is None
    assert result['error'] == 'timeout after 180s'
    assert result['cli_version'] == 'fake-version'
    assert load(config.run_dir / 'timeout.json') == result
