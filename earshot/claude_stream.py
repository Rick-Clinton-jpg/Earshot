"""Interpret pinned Claude Code JSONL fixtures; no process or model calls."""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import re

RESULT_FIELDS = ('subtype', 'is_error', 'api_error_status', 'terminal_reason',
                 'stop_reason', 'safety_stops', 'num_turns', 'duration_ms',
                 'total_cost_usd', 'usage', 'modelUsage', 'permission_denials',
                 'subagent_stats', 'result')


def version_number(raw):
    match = re.fullmatch(r'(\d+\.\d+\.\d+)(?: \(Claude Code\))?', raw.strip())
    return match[1] if match else raw.strip()


def parse_events(stdout):
    events = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            event = {'type': 'unparsed_stdout', 'text': line}
        if isinstance(event, dict):
            events.append(event)
    return events


def utc_reset(value):
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        try:
            return datetime.fromtimestamp(value, timezone.utc).isoformat().replace('+00:00', 'Z')
        except (ValueError, OverflowError, OSError):
            pass
    return None


def parse_claude(stdout, workspace, config, exit_code=0):
    events = parse_events(stdout)
    inits = [e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init']
    results = [e for e in events if e.get('type') == 'result']
    faults = []
    expected = {'model': config['model'], 'claude_code_version': config['version'],
                'permissionMode': 'dontAsk', 'cwd': str(Path(workspace)),
                'mcp_servers': [], 'slash_commands': [], 'skills': [], 'additional_directories': []}
    if len(inits) > 1:
        faults.append('multiple init events')
    for init in inits:
        for key, value in expected.items():
            if key not in init or init[key] != value:
                faults.append(f'init {key}: expected {value!r}, got {init.get(key)!r}')
        tools = init.get('tools')
        if not isinstance(tools, list) or len(tools) != 4 or not all(isinstance(t,str) for t in tools) or set(tools) != {'Glob', 'Grep', 'Read', 'StructuredOutput'}:
            faults.append('init tools differ from relay allowlist')
    result = results[-1] if results else {}
    if len(results) > 1:
        faults.append('multiple terminal result events')
    success = (len(results) == 1 and result.get('subtype') == 'success'
               and result.get('is_error') is False and 'api_error_status' in result
               and result['api_error_status'] is None)
    if success and not inits:
        faults.append('successful result lacks init event')
    if result:
        usage = result.get('modelUsage')
        stats=result.get('subagent_stats')
        spawned=stats.get('spawned') if isinstance(stats,dict) else None
        if isinstance(usage, dict) and set(usage) - {config['model']}:
            faults.append('unexpected modelUsage model')
        if spawned is not None and (type(spawned) is not int or spawned != 0):
            faults.append('spawned subagent')
        if success and (not isinstance(usage, dict) or not usage or spawned is None):
            faults.append('successful result lacks model/subagent evidence')
    windows = {}
    statuses = []
    for event in events:
        if event.get('type') != 'rate_limit_event':
            continue
        info = event.get('rate_limit_info', {})
        if not isinstance(info,dict):continue
        statuses.append(info.get('status'))
        for name in ('five_hour', 'seven_day'):
            unified=info.get('unifiedWindows')
            value=unified.get(name) if isinstance(unified,dict) else None
            if isinstance(value, dict):
                windows[name] = dict(value, reset_utc=utc_reset(value.get('resetsAt')))
    blocked = (not success or exit_code != 0) and any(s is not None and s != 'allowed' for s in statuses)
    high = any(isinstance(v.get('utilization'), (float, int))
               and not isinstance(v.get('utilization'), bool)
               and math.isfinite(v['utilization']) and v['utilization'] >= .90 for v in windows.values())
    reason = 'usage limit' if blocked else ('usage at 90%' if high else None)
    return {'answer': result.get('structured_output') if success else None, 'events': events,
            'claude_result': {k: result.get(k) for k in RESULT_FIELDS},
            'claude_result_fields_present': [k for k in RESULT_FIELDS if k in result],
            'cli_version': inits[0].get('claude_code_version') if inits else None,
            'claude_init': inits[0] if inits else None,
            'configuration_fault': faults or None, 'provider_error': not success,
            'usage_limit_detected': blocked, 'usage_pause_reason': reason,
            'quota_windows': windows, 'rate_limit_statuses': statuses}


def project_key(workspace):
    """Fixture-derived project encoding; observed storage paths are audited separately."""
    return re.sub(r'[^A-Za-z0-9]', '-', str(Path(workspace)))


def verify_project_state(workspace, state_root=None):
    root = Path(state_root) if state_root else Path.home() / '.claude'
    project = root / 'projects' / project_key(workspace)
    if project.is_symlink():
        raise RuntimeError('Claude project state is a symlink')
    if not project.exists():
        return str(project)
    for path in project.rglob('*'):
        parts = path.relative_to(project).parts
        if path.is_symlink():
            raise RuntimeError('symlink in Claude project state')
        if not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}',parts[0]):
            raise RuntimeError('non-session directory in Claude project state: '+str(path))
        allowed_dir = path.is_dir() and (len(parts) == 1 or (len(parts) >= 2 and parts[1] == 'tool-results'))
        allowed_file = path.is_file() and len(parts) >= 3 and parts[1] == 'tool-results'
        if not (allowed_dir or allowed_file):
            raise RuntimeError('unexpected Claude memory/instruction/state path: ' + str(path))
    return str(project)
