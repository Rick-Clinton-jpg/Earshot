"""D2 phase-aware integrity; Seal 1 sources remain immutable after Seal 2."""
import json
from pathlib import Path
import subprocess
from .integrity import (digest, git, safe_path, verify_digest, committed_bytes,
                        published_head, require_ready)
from .reliability import write_new
from .d1v2 import verify_workspace


def ready(registration, patterns):
    require_ready(registration)
    if registration.get('status') != 'REGISTERED':
        raise RuntimeError('D2 must be REGISTERED before a real run')
    if patterns.get('status') != 'CALIBRATED':
        raise RuntimeError('text-check patterns are not CALIBRATED')
    if type(registration.get('family_size')) is not int or registration['family_size'] != 8:
        raise RuntimeError('D2 addendum 3 requires a family of exactly 8')
    outcome = registration.get('claude_coalition_role_check')
    reason = registration.get('family_size_reason', {})
    amendment = (isinstance(reason, dict) and
                 reason.get('path') == 'sprint/partD/D2/D2_ADDENDUM_3.md' and
                 reason.get('sha256') == 'bcb1c7a249385238c7017c5b5fa5c6ba0a7c00168e7d3da46542c3c12b3f37ca')
    if outcome != 'passed' and not (outcome == 'failed' and amendment):
        raise RuntimeError('failed role check requires the approved addendum-3 family reason')


def files_match(repo, seal, revision):
    seen = set()
    for entry in seal['files']:
        path = safe_path(repo, entry['path'])
        if entry['path'] in seen:
            raise RuntimeError('duplicate seal path')
        seen.add(entry['path'])
        if digest(path) != entry['sha256']:
            raise RuntimeError('sealed hash mismatch: ' + entry['path'])
        committed_bytes(repo, path, revision)
    return seen


def require_sealed_input(repo, path, seal1):
    """Bind an explicitly selected runtime input to the source seal."""
    relative = Path(path).resolve().relative_to(Path(repo).resolve()).as_posix()
    entries = {e['path']: e['sha256'] for e in json.loads(Path(seal1).read_text())['files']}
    if entries.get(relative) != digest(path):
        raise RuntimeError('runtime input is not covered by Seal 1: ' + relative)


def verify_phase(repo, branch, seal1, digest1, registration, phase,
                 seal2=None, digest2=None, arm=None, require_head=True):
    repo = Path(repo).resolve()
    head = published_head(repo, branch)
    verify_digest(seal1, digest1)
    relative = Path(seal1).resolve().relative_to(repo).as_posix()
    seal1_commit = git(repo, 'log', '-1', '--format=%H', head, '--', relative)
    if not seal1_commit:
        raise RuntimeError('Seal 1 not committed')
    committed_bytes(repo, seal1, head); committed_bytes(repo, digest1, head)
    s1 = json.loads(Path(seal1).read_text())
    paths = files_match(repo, s1, head)
    if paths != set(registration['seal_1_files']):
        raise RuntimeError('Seal 1 coverage mismatch')
    # Compare with Seal 1 itself, not just a later commit's working bytes.
    for entry in s1['files']:
        committed_bytes(repo, safe_path(repo, entry['path']), seal1_commit)
    phase_commit = seal1_commit
    s2 = None
    if phase == 'receiver':
        if not seal2 or not digest2:
            raise RuntimeError('receiver phase needs published Seal 2')
        verify_digest(seal2, digest2)
        rel2 = committed_bytes(repo, seal2, head)
        committed_bytes(repo, digest2, head)
        phase_commit = git(repo, 'log', '-1', '--format=%H', head, '--', rel2)
        s2 = json.loads(Path(seal2).read_text())
        if s2['arm'] != arm or s2['seal_1_commit'] != seal1_commit or s2['seal_1_sha256'] != digest(seal1):
            raise RuntimeError('Seal 2 belongs to another arm or Seal 1')
        if subprocess.run(['git', 'merge-base', '--is-ancestor', seal1_commit, phase_commit], cwd=repo).returncode:
            raise RuntimeError('Seal 1 is not an ancestor of Seal 2')
        files_match(repo, s2, head)
    if require_head and head != phase_commit:
        raise RuntimeError('HEAD must be at the published phase seal commit')
    return dict(seal_1_commit=seal1_commit, phase_commit=phase_commit, seal_2=s2)


def runtime_files(folder):
    root = Path(folder).resolve()
    paths = sorted(root.rglob('*.json'))
    for p in paths:
        if p.is_symlink() or not p.resolve().is_relative_to(root):
            raise RuntimeError('unsafe runtime path')
    return paths


def ledger(run, arm, seal1_commit, seal1):
    run = Path(run).resolve()
    return dict(arm=arm, seal_commit=seal1_commit, seal_sha256=digest(seal1),
                files=[dict(path=p.relative_to(run).as_posix(), sha256=digest(p))
                       for p in runtime_files(run)])


def verify_ledger(repo, branch, path, digest_path, run):
    verify_digest(path, digest_path)
    head = published_head(repo, branch)
    committed_bytes(repo, path, head); committed_bytes(repo, digest_path, head)
    data = json.loads(Path(path).read_text())
    listed = set()
    for entry in data['files']:
        p = safe_path(run, entry['path'])
        if p in listed or digest(p) != entry['sha256']:
            raise RuntimeError('ledger mismatch or duplicate path')
        listed.add(p)
        committed_bytes(repo, p, head)
    if listed != {p.resolve() for p in runtime_files(run)}:
        raise RuntimeError('ledger inventory mismatch')
    return data
