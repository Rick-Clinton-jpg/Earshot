"""Read-restricted Codex sandbox integration, with no inference entry point.

Deterministic commands exercise the pinned real `codex sandbox` binary. An
outer/nested Seatbelt probe is retained as a diagnostic: this Mac refused it.
That failed probe is not a production containment mechanism or readiness pass.
This module never calls `codex exec`, any model service or an authentication flow.
"""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

from .partb import digest, write_json

CLI_VERSION='codex-cli 0.165.0-alpha.1.2'
SETUP_VERSION='partb-agent-env-v2-pytest-mock'


@dataclass(frozen=True)
class Session:
    root: Path
    workspace: Path
    home: Path
    config: Path
    temporary: Path


def opaque_session(parent='/private/tmp'):
    root=Path(tempfile.mkdtemp(prefix='esb_',dir=parent)).resolve()
    root.chmod(0o700)
    return Session(root,root/'w',root/'h',root/'h'/'c',root/'w'/'.scratch')


def initialize_runtime(session):
    for p in [session.home,session.config,session.temporary]:p.mkdir(mode=0o700)


def verify_initial_configuration_home(session):
    """Before CLI startup, accept only the reviewed config and optional auth.

    CLI-created runtime files are never copied to another session. This guard
    is for initial launch, not an attempted allowlist of all later runtime state.
    """
    allowed={'config.toml','auth.json'}
    found=[]
    for p in session.config.iterdir():
        if p.is_symlink() or not p.is_file() or p.name not in allowed:found.append(p.name)
        elif p.name=='auth.json' and p.stat().st_mode&0o777!=0o600:found.append('auth.json:bad-mode')
    if found:raise RuntimeError('unapproved initial CODEX_HOME entries: '+', '.join(sorted(found)))
    if not (session.config/'config.toml').is_file():raise RuntimeError('initial config missing')
    return {'allowed_initial_entries':sorted(p.name for p in session.config.iterdir())}


def interpreter_roots(python):
    text=subprocess.check_output([str(python),'-B','-c',
         'import sys,json;print(json.dumps([sys.prefix,sys.base_prefix]))'],text=True)
    return [Path(p).resolve() for p in json.loads(text)]


def permission_config(session, python):
    # No legacy --sandbox/sandbox_mode override: those bypass named profiles.
    lines=['default_permissions = "partb"','approval_policy = "never"','web_search = "disabled"',
      'project_doc_max_bytes = 0','cli_auth_credentials_store = "file"',
      'agents = { enabled = false }',
      '[permissions.partb]','extends = ":workspace"',
      '[permissions.partb.filesystem]', '":root" = "deny"','":minimal" = "read"',
      '":tmpdir" = "write"','":slash_tmp" = "deny"',
      json.dumps(str(session.home))+' = "deny"']
    for p in interpreter_roots(python):lines.append(json.dumps(str(p))+' = "read"')
    lines += ['[permissions.partb.filesystem.":workspace_roots"]','"." = "write"',
              '[permissions.partb.network]','enabled = false']
    return '\n'.join(lines)+'\n'


def outer_profile(session, python, cli):
    """Interpreter/runtime ancestors only; never grant session-parent listing."""
    runtime=[*interpreter_roots(python),Path(cli).resolve().parent,
       Path('/System/Library'),Path('/System/Volumes/Preboot/Cryptexes/OS'),
       Path('/usr/bin'),Path('/usr/lib'),Path('/usr/libexec'),Path('/usr/share'),
       Path('/bin'),Path('/Library/Apple'),Path('/private/etc'),Path('/dev')]
    quote=lambda p:json.dumps(str(Path(p).resolve()))
    ancestors={p for r in runtime for p in Path(r).resolve().parents}
    # HOME/runtime state is readable to the trusted CLI controller. The native
    # child profile explicitly denies this HOME to the agent's commands.
    read_roots=[session.workspace,session.home,session.temporary,*runtime]
    reads=' '.join('(subpath '+quote(p)+')' for p in read_roots)
    reads+=' '+' '.join('(literal '+quote(p)+')' for p in sorted(ancestors))
    writes=' '.join('(subpath '+quote(p)+')' for p in [session.workspace,session.home,session.temporary])
    return ('(version 1)(allow default)(deny network*)(deny file-read*)(deny file-write*)'
      '(allow file-read-metadata)(allow file-read* '+reads+')'
      '(allow file-write* '+writes+' (literal "/dev/null"))')


def environment(session):
    # Scoped child environment only; no inherited account credentials, model
    # keys, parent PYTHONPATH, prompt/condition labels or shared daemon state.
    return {'PATH':'/usr/bin:/bin','HOME':str(session.home),
       'CODEX_HOME':str(session.config),'TMPDIR':str(session.temporary),
       'LC_ALL':'en_US.UTF-8','PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'0',
       'PYTHONNOUSERSITE':'1','PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1',
       'PYTEST_PLUGINS':'pytest_mock','PYTHONPATH':''}


def native_argv(cli, cwd, command):
    return cli_prefix(cli)+['sandbox','-P','partb','-C',str(cwd),'--',*map(str,command)]


def cli_prefix(cli):
    return [str(Path(cli).resolve()),'--no-daemon','--disable','multi_agent',
            '--disable','image_generation','--disable','shell_snapshot',
            '--disable','memories','--disable','external_agent_memory_import',
            '--disable','guardian_conversation_history_tools']


def sandbox_command(session, cli, python, command, output, cwd=None, timeout=30):
    """No model call. Exact real sandbox command, nested under outer profile."""
    actual=subprocess.check_output([str(cli),'--version'],text=True).strip()
    if actual!=CLI_VERSION:raise RuntimeError('CLI version mismatch')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    config=permission_config(session,python)
    config_path=session.config/'config.toml'
    if config_path.exists():
        if config_path.read_text()!=config:raise RuntimeError('session configuration changed')
    else:
        with config_path.open('x') as f:f.write(config)
    profile=outer_profile(session,python,cli)
    (output/'outer.sb').write_text(profile);(output/'permissions.toml').write_text(config)
    native=native_argv(cli,cwd or session.workspace,command)
    argv=['/usr/bin/sandbox-exec','-p',profile,*native]
    start=time.monotonic()
    with (output/'stdout.log').open('xb') as out,(output/'stderr.log').open('xb') as err:
        process=subprocess.Popen(argv,cwd=cwd or session.workspace,env=environment(session),
                 stdout=out,stderr=err,start_new_session=True)
        timed=False
        try:process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed=True;os.killpg(process.pid,signal.SIGKILL);process.wait()
    result={'status':'REAL_CLI_SANDBOX_COMMAND_NO_INFERENCE','argv':native,
      'cli_version':actual,'cli_sha256':digest(Path(cli).read_bytes()),
      'outer_profile_sha256':digest(profile.encode()),'permissions_sha256':digest(config.encode()),
      'exit_code':process.returncode,'timed_out':timed,'wall_seconds':time.monotonic()-start,'model_calls':0}
    write_json(output/'process.json',result)
    return result


def native_command(session, cli, python, command, output, cwd=None, timeout=120):
    """Real CLI native tool sandbox only, no nested sandbox and no inference."""
    actual=subprocess.check_output([str(cli),'--version'],text=True).strip()
    if actual!=CLI_VERSION:raise RuntimeError('CLI version mismatch')
    if not session.temporary.resolve().is_relative_to(session.workspace.resolve()):
        raise RuntimeError('TMPDIR must be inside own workspace')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    config=permission_config(session,python);cfg=session.config/'config.toml'
    if cfg.exists():
        if cfg.read_text()!=config:raise RuntimeError('session config changed')
    else:
        with cfg.open('x') as f:f.write(config)
    env=environment(session)
    # Launch the canonical binary: native deny-by-default refused the venv
    # executable symlink. Keep the same recorded venv dependencies explicitly.
    dependencies=subprocess.check_output([str(python),'-B','-c',
       'import sysconfig;print(sysconfig.get_path("purelib"))'],text=True).strip()
    env['PYTHONPATH']=dependencies
    argv=native_argv(cli,cwd or session.workspace,command)
    start=time.monotonic()
    # Pipes keep private controller log files out of the child's descriptor set.
    process=subprocess.Popen(argv,cwd=cwd or session.workspace,env=env,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
    timed=False
    try:stdout,stderr=process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed=True;os.killpg(process.pid,signal.SIGKILL);stdout,stderr=process.communicate()
    with (output/'stdout.log').open('xb') as f:f.write(stdout)
    with (output/'stderr.log').open('xb') as f:f.write(stderr)
    (output/'permissions.toml').write_text(config)
    result={'status':'NATIVE_CLI_TOOL_SANDBOX_FIXTURE_NO_INFERENCE','argv':argv,
      'cli_version':actual,'cli_sha256':digest(Path(cli).read_bytes()),
      'permissions_sha256':digest(config.encode()),'canonical_python':str(Path(python).resolve()),
      'dependency_root':dependencies,'exit_code':process.returncode,'timed_out':timed,
      'wall_seconds':time.monotonic()-start,'model_calls':0,
      'outer_profile_used':False,'whole_cli_read_containment_verified':False}
    write_json(output/'process.json',result)
    return result
