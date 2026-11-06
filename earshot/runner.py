"""One trace per fresh CLI call, with explicit config and subprocess safety."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
from .config import Config

PINNED_CLI_VERSION = "codex-cli 0.165.0-alpha.1.2"

def build_command(config, schema):
    return [config.cli, "exec", "--json", "--ephemeral", "--ignore-user-config", "--sandbox", "read-only", "--model", config.model, "--config", f"model_reasoning_effort={config.reasoning_effort}", "--output-schema", str(schema.resolve()), "--cd", str(config.workspace.resolve()), "-"]


def start_subprocess(config: Config, args, **kwargs):
    if config.stub:
        raise RuntimeError("stub mode refuses to start any subprocess")
    return subprocess.run(args, **kwargs)


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def run_agent(name: str, prompt: str, schema: Path, config: Config) -> dict:
    if config.stub:
        raise RuntimeError("stub mode refuses to start any subprocess")
    if not name or Path(name).name != name or name in ('.', '..'):
        raise ValueError('call name must be a single filename component')
    config.run_dir.mkdir(parents=True, exist_ok=True)
    path = config.run_dir / f'{name}.json'
    if path.exists():
        return json.loads(path.read_text())
    # Exclusive reservation also prevents concurrent invocations overwriting a trace.
    lock = config.run_dir / f'{name}.lock'
    with lock.open('x'):
        pass
    try:
        if path.exists():
            return json.loads(path.read_text())
        started_at = utc_now()
        started = time.time()
        try:
            version = start_subprocess(config, [config.cli, '--version'], capture_output=True, text=True, timeout=10)
            if version.returncode:
                raise RuntimeError(f'CLI version probe failed: {version.stderr.strip()}')
            if version.stdout.strip() != PINNED_CLI_VERSION:
                raise RuntimeError(f'CLI version mismatch: {version.stdout.strip()!r}; required {PINNED_CLI_VERSION!r}')
        except (OSError, subprocess.SubprocessError, RuntimeError) as error:
            result = {'name': name, 'exit_code': None, 'error': str(error), 'answer': None,
                      'elapsed_seconds': round(time.time() - started, 2),
                      'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                      'started_at_utc': started_at, 'finished_at_utc': utc_now(),
                      'cli_version': None, 'cli_version_error': str(error)}
            with path.open('x') as stream:
                stream.write(json.dumps(result, indent=2) + '\n')
            return result
        args = build_command(config, schema)
        try:
            proc = start_subprocess(config, args, input=prompt, text=True, capture_output=True, timeout=config.timeout)
            events = []
            for line in proc.stdout.splitlines():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    events.append({'unparsed_stdout': line})
            messages = [e['item'].get('text', '') for e in events if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message']
            answer_text = messages[-1] if messages else None
            try:
                answer = json.loads(answer_text) if answer_text else None
            except json.JSONDecodeError:
                answer = None
            result = {'name': name, 'exit_code': proc.returncode, 'answer': answer, 'answer_text': answer_text, 'tool_calls': [e for e in events if e.get('type') in ('item.started', 'item.completed') and e.get('item', {}).get('type') == 'command_execution'], 'events': events, 'stderr': proc.stderr}
        except subprocess.TimeoutExpired as error:
            result = {'name': name, 'exit_code': None, 'error': f'timeout after {error.timeout}s', 'answer': None}
        result.update(elapsed_seconds=round(time.time() - started, 2), prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(), started_at_utc=started_at, finished_at_utc=utc_now(), cli_version=version.stdout.strip())
        with path.open('x') as stream:
            stream.write(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
        return result
    finally:
        lock.unlink(missing_ok=True)
