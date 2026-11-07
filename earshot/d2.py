"""D2 phased runner. No backend is invoked by imports, builds or scoring."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess
from .d1v2 import Backend, verify_workspace, record_drained_pause, finalize_cutoff
from .d2_design import (KINDS, sender_calls, relay_calls, hop2_calls, receiver_calls,
                        receiver_order, output_pair, delivered)
from .d2_integrity import ready, verify_phase, require_sealed_input
from .d2_reliability import AttemptRunner
from .d2_checkpoint import checkpoint
from .exposure import audit, tools
from .integrity import digest
from .reliability import Control, write_new, replace_state


def exposure(record, workspace):
    # Reuse outside-path/permission observation logic, but no DogWhistle adapter claims.
    result = audit(record, workspace, {})
    result = {k: v for k, v in result.items() if not k.startswith('adapter_')}
    result['phrase_observations'] = [
        dict(tool_id=t['id'], line=n, text=line)
        for t in tools(record) for n, line in enumerate(t['output'].splitlines(), 1)
        if re.search(r'required_memory_refs|handoff|coalition|preferred pair|decoded|memory ref', line, re.I)]
    result['report_only'] = True
    result['audit_scope'] = ('Visible saved tool inputs/results and explicit outside paths only; '
                             'phrase matches are observations, not attributed source exposure. '
                             'No DogWhistle adapter criterion; no universal read-boundary claim.')
    return result


class D2Backend(Backend):
    def __call__(self, name, prompt, control, reserve=None):
        row = super().__call__(name, prompt, control, reserve)
        row['exposure_audit'] = exposure(row, self.workspace)
        return row


class Stage:
    def __init__(self, data, folder, control, execute, patterns, workers=4):
        if workers != 4:
            raise RuntimeError('D2 carries over the D1 worker limit of 4')
        self.data = data; self.folder = Path(folder); self.control = control
        self.execute = execute; self.patterns = patterns; self.workers = workers
        self.plan = self.folder / 'plan.json'
        if not self.plan.exists():
            write_new(self.plan, {'calls': {}})
        self.state_path = self.folder / 'phase.json'
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {'phase': 'sender'}

    def save(self):
        replace_state(self.state_path, self.state)

    def batch(self, specs):
        plan = json.loads(self.plan.read_text())
        for s in specs:
            metadata = {k: v for k, v in s.items() if k != 'prompt'}
            metadata['prompt_sha256'] = hashlib.sha256(s['prompt'].encode()).hexdigest()
            if s['name'] in plan['calls'] and plan['calls'][s['name']] != metadata:
                raise RuntimeError('immutable call plan changed')
            plan['calls'][s['name']] = metadata
        replace_state(self.plan, plan)
        def one(s):
            def execute(name, prompt, ctl, reserve):
                return dict(self.execute(s, ctl, reserve), **{k: v for k, v in s.items() if k != 'prompt'})
            return AttemptRunner(self.folder, self.patterns, self.control, execute,
                                 reserve_at_launch=True, role=s['role']).run(s['name'], s['prompt'])
        rows = []
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            for start in range(0, len(specs), self.workers):
                if self.control.blocked:
                    break
                rows.extend(pool.map(one, specs[start:start + self.workers]))
        if self.control.blocked:
            record_drained_pause(self.folder, self.control)
            raise RuntimeError('paused: ' + self.control.blocked)
        if any(r.get('administrative_status') for r in rows):
            self.state['stopped_by_cutoff'] = True; self.save()
            raise RuntimeError('stopped by the cutoff')
        return rows

    def senders(self):
        if self.state['phase'] != 'sender':
            return self.state['selected_ids']
        selected = []; used_reserves = []; invalid = []
        tasks = self.data['tasks']; files = self.data['candidate_files']
        # Exhaust all primaries first. A file has exactly one reserve, never reused.
        primaries = sorted((t for t in tasks if t['role'] == 'primary'), key=lambda t: t['id'])
        def valid(t):
            rows = self.batch(sender_calls(t, files))
            return all(output_pair(r) == t['codewords'][r['kind']] for r in rows)
        for t in primaries:
            if valid(t): selected.append(t['id'])
            else: invalid.append(t['id'])
        for letter in 'ABCD':
            if any(t['id'] in invalid and t['target_file'] == letter for t in primaries):
                reserve = next(t for t in tasks if t['role'] == 'reserve' and t['target_file'] == letter)
                used_reserves.append(reserve['id'])
                if valid(reserve): selected.append(reserve['id'])
                else: invalid.append(reserve['id'])
        self.state.update(phase='relay', selected_ids=sorted(selected), invalid_sender_tasks=invalid,
                          reserves_attempted=used_reserves)
        self.save()
        return self.state['selected_ids']

    def relays(self):
        if self.state['phase'] == 'sender':
            raise RuntimeError('sender phase is not final')
        if self.state['phase'] != 'relay':
            return self.state
        deliveries = {}; skipped = []
        for t in sorted(self.data['tasks'], key=lambda t: t['id']):
            if t['id'] not in self.state['selected_ids']: continue
            base = relay_calls(t, self.data['candidate_files'])
            # Default calls finish before incoming calls; every hop 1 finishes before hop 2.
            self.batch([s for s in base if s['group'] == 'free'])
            h1 = self.batch([s for s in base if s['group'] == 'hop1'])
            self.batch(hop2_calls(t, self.data['candidate_files'], h1))
            deliveries[t['id']] = delivered(h1)
            if deliveries[t['id']] is None: skipped.append(t['id'])
        self.state.update(phase='awaiting_seal_2', delivered=deliveries, skipped_receivers=skipped)
        self.save()
        return self.state

    def receiver_plan(self, seed):
        if self.state['phase'] not in ('awaiting_seal_2', 'receiver', 'done'):
            raise RuntimeError('relay phase is not final')
        specs = [s for t in self.data['tasks'] if t['id'] in self.state['selected_ids']
                 for s in receiver_calls(t, self.data['candidate_files'], self.state['delivered'][t['id']])]
        return receiver_order(specs, seed)

    def receivers(self, seal2, publication_check):
        publication_check()
        specs = self.receiver_plan(seal2['receiver_order_seed'])
        if [s['name'] for s in specs] != seal2['receiver_order'] or self.state['skipped_receivers'] != seal2['skipped_receivers']:
            raise RuntimeError('Seal 2 receiver plan mismatch')
        self.state['phase'] = 'receiver'; self.save()
        self.batch(specs)
        self.state['phase'] = 'done'; self.save()


def seal2_record(repo, arm, seal1, seal1_commit, stage, seed):
    """Return a seal record for a later authorized sealing operation; writes nothing."""
    if stage.state['phase'] != 'awaiting_seal_2':
        raise RuntimeError('relay phase incomplete')
    root = Path(repo).resolve()
    immutable = [p for part in ('traces', 'attempt_state', 'system_issue', 'configuration_fault', 'stopped')
                 for p in (stage.folder / part).rglob('*.json')]
    specs = stage.receiver_plan(seed)
    return dict(arm=arm, seal_1_commit=seal1_commit, seal_1_sha256=digest(seal1),
                selected_ids=stage.state['selected_ids'], delivered=stage.state['delivered'],
                skipped_receivers=stage.state['skipped_receivers'], receiver_order_seed=seed,
                receiver_order=[s['name'] for s in specs],
                files=[dict(path=p.resolve().relative_to(root).as_posix(), sha256=digest(p))
                       for p in sorted(immutable)])


def main(argv=None):
    parser = argparse.ArgumentParser()
    for k in ('repo', 'branch', 'registration', 'seal', 'seal-digest', 'workspace', 'run-dir'):
        parser.add_argument('--' + k, required=True)
    parser.add_argument('--backend', choices=('codex', 'claude'), required=True)
    parser.add_argument('--phase', choices=('sender-relay', 'receiver'), required=True)
    parser.add_argument('--seal2'); parser.add_argument('--seal2-digest')
    parser.add_argument('--resume-rick', action='store_true')
    parser.add_argument('--finalize-cutoff', action='store_true')
    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()
    registration = json.loads(Path(args.registration).read_text())
    patterns = json.loads((repo / registration['text_patterns_path']).read_text())
    ready(registration, patterns)
    data = json.loads((repo / registration['tasks_path']).read_text())
    config = registration['arm_configs'][args.backend]
    phase = 'receiver' if args.phase == 'receiver' else 'relay'
    def check():
        info = verify_phase(repo, args.branch, args.seal, args.seal_digest, registration,
                            phase, args.seal2, args.seal2_digest, args.backend)
        verify_workspace(args.workspace, data)
        return info
    info = check()
    for path in (Path(args.registration), repo / registration['tasks_path'],
                 repo / registration['text_patterns_path']):
        require_sealed_input(repo, path, args.seal)
    schemas = {'receiver': repo / 'earshot/answer.schema.json',
               'sender': repo / 'earshot/sender.schema.json', 'relay': repo / 'earshot/sender.schema.json'}
    backends = {role: D2Backend(config, args.workspace, schema, check) for role, schema in schemas.items()}
    folder = Path(args.run_dir).resolve(); folder.mkdir(parents=True, exist_ok=True)
    with (folder / 'worker.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        control = Control(folder, datetime.fromisoformat(registration['cutoff_utc'].replace('Z', '+00:00')))
        if not (folder / 'pauses.json').exists(): write_new(folder / 'pauses.json', [])
        if not (folder / 'control.json').exists(): control.persist()
        def execute(s, ctl, reserve):
            return backends[s['role']](s['name'], s['prompt'], ctl, reserve)
        stage = Stage(data, folder, control, execute,
                      json.loads((repo / 'earshot/system_issue_patterns.json').read_text()), config['workers'])
        try:
            if args.finalize_cutoff or control.clock.now() >= control.latest_launch:
                finalize_cutoff(folder, control)
                stage.state['stopped_by_cutoff'] = True; stage.save()
                print('stopped by the cutoff'); return
            if args.resume_rick: control.resume_by_rick()
            if control.blocked: raise RuntimeError('paused: ' + control.blocked)
            # Local CLI/environment checks only; no model invocation.
            try:
                for backend in backends.values(): backend.preflight()
            except (RuntimeError, OSError, subprocess.SubprocessError) as error:
                fault = folder / 'configuration_fault' / 'preflight.json'
                if not fault.exists():
                    write_new(fault, {'scope': 'arm', 'configuration_fault': [str(error)]})
                control.stop('configuration fault: preflight')
                raise
            if phase == 'receiver': stage.receivers(info['seal_2'], check)
            else: stage.senders(); stage.relays()
            print(stage.state['phase'])
        finally:
            checkpoint(repo, folder, args.backend, info['phase_commit'], digest(args.seal), digest(args.registration))


if __name__ == '__main__':
    main()
