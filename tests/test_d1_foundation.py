import ast
from pathlib import Path
import subprocess
import pytest
from earshot import runner
from earshot.config import Config

ROOT = Path(__file__).resolve().parents[1]


def test_command_identity():
    source = ast.parse((ROOT / 'results/presprint/direct/run.py').read_text())
    function = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'run_agent')
    assignment = next(n for n in function.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'cmd' for t in n.targets))
    schema = ROOT / 'earshot/sender.schema.json'
    config = Config(ROOT.parent / 'earshot_foundation_workspace', ROOT / 'unused', stub=False)
    old = eval(compile(ast.Expression(assignment.value), '<frozen command>', 'eval'), {'MODEL':config.model, 'DESIGN':{'reasoning_effort':config.reasoning_effort}, 'schema':schema, 'WORKSPACE':config.workspace})
    assert runner.build_command(config, schema) == old
    assert schema.read_bytes() == (ROOT / 'results/presprint/direct/sender.schema.json').read_bytes()


def test_cli_version_mismatch_refuses_exec(monkeypatch, tmp_path):
    calls=[]
    def fake(args, **kwargs):
        calls.append(args)
        assert args[-1] == '--version'
        return subprocess.CompletedProcess(args, 0, 'fake-wrong-version\n', '')
    monkeypatch.setattr(subprocess, 'run', fake)
    monkeypatch.setattr(runner, 'verify_registration', lambda path: {})
    result=runner.run_agent('bad-version','prompt',tmp_path/'schema',Config(tmp_path,tmp_path/'runs',stub=False))
    assert 'CLI version mismatch' in result['error']
    assert result['answer'] is None
    assert len(calls)==1
