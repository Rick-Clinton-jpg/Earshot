"""Read-boundary integration checks. The CLI is used only in sandbox mode."""
import json
from pathlib import Path
import subprocess
import sys
import tomllib

import pytest

from earshot import partb_cli as c

CLI=Path('/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex')
PYTHON=Path('/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/env-radon/bin/python')


def test_opaque_session_contains_no_task_or_condition_names(tmp_path):
    first=c.opaque_session(tmp_path);second=c.opaque_session(tmp_path)
    assert first.root!=second.root
    assert first.root.parent==second.root.parent==tmp_path
    assert first.workspace.name==second.workspace.name=='w'
    assert first.temporary.is_relative_to(first.workspace)
    for session in [first,second]:
        assert not any(label in str(session.root) for label in ['item-01','H-in','C-out','coalition'])
        assert session.root.stat().st_mode&0o777==0o700


def test_native_profile_denies_root_and_disallows_legacy_override(tmp_path,monkeypatch):
    session=c.opaque_session(tmp_path)
    monkeypatch.setattr(c,'interpreter_roots',lambda _: [tmp_path/'trusted-python'])
    cfg=tomllib.loads(c.permission_config(session,PYTHON))
    fs=cfg['permissions']['partb']['filesystem']
    assert fs[':root']=='deny' and fs[':slash_tmp']=='deny'
    assert fs[str(session.home)]=='deny'
    assert cfg['permissions']['partb']['network']['enabled'] is False
    assert 'sandbox_mode' not in cfg
    assert cfg['agents']['enabled'] is False
    assert cfg['project_doc_max_bytes']==0
    argv=c.native_argv(CLI,session.workspace,['/bin/true'])
    assert 'sandbox' in argv and 'exec' not in argv
    assert '--no-daemon' in argv and '-P' in argv and 'partb' in argv
    assert '--dangerously-bypass-approvals-and-sandbox' not in argv


def test_native_launcher_refuses_external_temp_or_changed_config(tmp_path,monkeypatch):
    monkeypatch.setattr(c.subprocess,'check_output',lambda *a,**k:c.CLI_VERSION+'\n')
    session=c.Session(tmp_path,tmp_path/'w',tmp_path/'h',tmp_path/'h/c',tmp_path/'outside')
    with pytest.raises(RuntimeError,match='TMPDIR'):
        c.native_command(session,CLI,PYTHON,['/bin/true'],tmp_path/'out')
    session=c.opaque_session(tmp_path);session.workspace.mkdir();c.initialize_runtime(session)
    (session.config/'config.toml').write_text('changed configuration')
    monkeypatch.setattr(c,'interpreter_roots',lambda _:[tmp_path/'runtime'])
    with pytest.raises(RuntimeError,match='config changed'):
        c.native_command(session,CLI,PYTHON,['/bin/true'],tmp_path/'out2')


@pytest.mark.skipif(not CLI.exists() or not PYTHON.exists(),reason='pinned local macOS CLI runtime required')
def test_real_cli_sandbox_denies_study_material_and_cross_session_reads(tmp_path):
    repo=Path(__file__).resolve().parents[1]
    script=repo/'sprint/partB/check_cli_isolation.py'
    output=tmp_path/'checks'
    result=subprocess.run([sys.executable,'-B',str(script),'--output',str(output),
           '--cli',str(CLI),'--python',str(PYTHON)],cwd=repo,capture_output=True,text=True,timeout=120)
    assert result.returncode==0,result.stdout+result.stderr
    checks=json.loads((output/'CHECKS.json').read_text())
    assert checks['model_calls']==checks['practice_model_calls']==0
    assert checks['parent_and_sibling_listing_denied']
    assert set(checks['protected_paths']['reads'].values())=={'denied'}
    assert checks['outside_import']['spec'] is None
    assert checks['outside_import']['distribution'] is None
    # Do not promote a tool-command fixture to a whole-worker isolation claim.
    assert checks['whole_cli_read_containment_verified'] is False


@pytest.mark.skipif(not CLI.exists() or not PYTHON.exists(),reason='pinned local macOS CLI runtime required')
def test_actual_cli_file_tools_use_permission_profile_with_scripted_responses(tmp_path):
    repo=Path(__file__).resolve().parents[1]
    output=tmp_path/'protocol'
    result=subprocess.run([sys.executable,'-B',str(repo/'sprint/partB/probe_cli_tools.py'),
       '--exercise','--output',str(output),'--cli',str(CLI),'--python',str(PYTHON)],
       cwd=repo,capture_output=True,text=True,timeout=120)
    assert result.returncode==0,result.stdout+result.stderr
    checks=json.loads((output/'CHECKS.json').read_text())
    assert checks['live_model_calls']==0 and checks['CLI_exec_invocations']==1
    assert checks['loopback_requests']==2
    assert checks['own_patch_succeeded'] and checks['private_patch_denied']
    assert checks['own_image_read_succeeded'] and checks['private_image_denied']
    assert checks['outside_workdir_did_not_grant_reads']
    assert set(checks['shell_protected_reads'].values())=={'denied'}
    assert not checks['subagent_tools_invoked']


@pytest.mark.parametrize('entry',['AGENTS.md','AGENTS.override.md','history.jsonl','memories','symlink','bad-auth-mode'])
def test_initial_home_refuses_unreviewed_entries(tmp_path,entry):
    session=c.opaque_session(tmp_path);session.workspace.mkdir();c.initialize_runtime(session)
    (session.config/'config.toml').write_text('approved fixture config')
    auth=session.config/'auth.json';auth.write_text('synthetic');auth.chmod(0o600)
    assert c.verify_initial_configuration_home(session)['allowed_initial_entries']==['auth.json','config.toml']
    if entry=='memories':(session.config/entry).mkdir()
    elif entry=='symlink':
        auth.unlink();auth.symlink_to(session.config/'config.toml')
    elif entry=='bad-auth-mode':auth.chmod(0o644)
    else:(session.config/entry).write_text('unreviewed')
    with pytest.raises(RuntimeError,match='unapproved initial CODEX_HOME'):
        c.verify_initial_configuration_home(session)


@pytest.mark.skipif(not CLI.exists() or not PYTHON.exists(),reason='pinned local macOS CLI runtime required')
@pytest.mark.parametrize('mode',['helpers','auth','context'])
def test_prepractice_boundaries_through_scripted_real_cli(tmp_path,mode):
    repo=Path(__file__).resolve().parents[1];output=tmp_path/mode
    argv=[sys.executable,'-B',str(repo/'sprint/partB/check_prepractice.py'),'--mode',mode,
          '--output',str(output),'--cli',str(CLI),'--python',str(PYTHON)]
    if mode=='auth':
        auth=tmp_path/'synthetic-auth.json'
        auth.write_text(json.dumps({'OPENAI_API_KEY':'synthetic-fixture-key-not-a-credential'}));auth.chmod(0o600)
        argv+=['--auth-source',str(auth)]
    run=subprocess.run(argv,cwd=repo,capture_output=True,text=True,timeout=150)
    assert run.returncode==0,run.stdout+run.stderr
    checks=json.loads((output/'CHECKS.json').read_text())
    assert checks['hosted_model_calls']==checks['practice_calls']==0
    if mode=='helpers':
        assert checks['status']=='HELPER_UNAVAILABLE_AT_RUNTIME'
        assert checks['child_requests']==0
    elif mode=='auth':
        assert checks['original_auth_unchanged'] and not checks['credential_leak_detected']
        assert checks['existing_user_CLI_auth_file_used'] is False
    else:
        assert checks['dirty_home_refused_before_launch']
        assert checks['forbidden_markers_found']==0
        assert checks['approved_prompt_and_config_found']


@pytest.mark.skipif(not CLI.exists() or not PYTHON.exists(),reason='pinned local macOS CLI runtime required')
def test_scripted_cli_edit_to_independent_practice_evaluation(tmp_path):
    repo=Path(__file__).resolve().parents[1];output=tmp_path/'practice-pipeline'
    run=subprocess.run([sys.executable,'-B',str(repo/'sprint/partB/check_practice_pipeline.py'),
       '--output',str(output),'--cli',str(CLI),'--python',str(PYTHON)],
       cwd=repo,capture_output=True,text=True,timeout=180)
    assert run.returncode==0,run.stdout+run.stderr
    checks=json.loads((output/'CHECKS.json').read_text())
    assert checks['hosted_model_calls']==checks['practice_calls']==checks['study_calls']==0
    assert checks['local_protocol_requests']==8
    assert checks['cases']['reference']['test_verified_admissible_repair']
    assert not checks['cases']['no_edit']['tests_pass']
    added=checks['cases']['new_file']
    assert added['tests_pass'] and not added['test_verified_admissible_repair']
    assert not added['admissible']
    repro=checks['cases']['root_repro']
    assert repro['test_verified_admissible_repair'] and repro['admissible']
    assert repro['scratch_files'][0]['path']=='repro.py'


@pytest.mark.skipif(not CLI.exists() or not PYTHON.exists(),reason='pinned local macOS CLI runtime required')
def test_plain_agent_pytest_explicitly_loads_mock_with_autoload_disabled(tmp_path):
    repo=Path(__file__).resolve().parents[1];output=tmp_path/'test-environment-v2'
    run=subprocess.run([sys.executable,'-B',str(repo/'sprint/partB/check_test_environment.py'),
        '--output',str(output),'--cli',str(CLI),'--python',str(PYTHON)],
        cwd=repo,capture_output=True,text=True,timeout=180)
    assert run.returncode==0,run.stdout+run.stderr
    checks=json.loads((output/'CHECKS.json').read_text())
    assert checks['hosted_model_calls']==0
    assert checks['cases']['pristine']['passed']==404
    assert checks['cases']['practice_bug']['passed']==403
    assert len(checks['cases']['practice_bug']['failed'])==1
    assert checks['PYTEST_DISABLE_PLUGIN_AUTOLOAD']=='1'
    assert checks['PYTEST_PLUGINS']=='pytest_mock'
