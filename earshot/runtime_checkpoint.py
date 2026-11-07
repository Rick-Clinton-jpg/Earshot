"""Append-only runtime-branch snapshots, separate from the sealed run checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from .integrity import git, safe_path

IMMUTABLE = {'traces', 'system_issue', 'attempt_state', 'stopped', 'configuration_fault'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(folder):
    files = {}
    for path in sorted(Path(folder).rglob('*')):
        if path.is_symlink():
            raise RuntimeError('symlink in runtime snapshot')
        if path.is_file():
            files[path.relative_to(folder).as_posix()] = path.read_bytes()
    return files


def checkpoint(repo, run_dir, arm, seal_commit, seal_sha256, registration_sha256):
    if arm not in ('codex', 'claude'):
        raise ValueError('invalid arm')
    repo, run_dir = Path(repo).resolve(), Path(run_dir).resolve()
    if git(repo, 'rev-parse', 'HEAD') != seal_commit:
        raise RuntimeError('run checkout left seal commit')
    files = snapshot(run_dir)
    branch = f'd1-{arm}-runtime'
    remote = git(repo, 'ls-remote', 'origin', 'refs/heads/' + branch).split()
    base = seal_commit
    if remote:
        git(repo, 'fetch', '--no-tags', 'origin', branch)
        base = git(repo, 'rev-parse', 'FETCH_HEAD')
    parent = Path(tempfile.mkdtemp(prefix='earshot-runtime-'))
    worktree = parent / 'checkout'
    # The runtime branch is never checked out in the sealed worker directory.
    local = subprocess.run(['git', 'show-ref', '--verify', '--quiet', 'refs/heads/' + branch], cwd=repo).returncode == 0
    if local:
        git(repo, 'worktree', 'add', str(worktree), branch)
        git(worktree, 'merge', '--ff-only', base)
    else:
        git(repo, 'worktree', 'add', '-b', branch, str(worktree), base)
    target = worktree / 'runtime' / arm / 'run'
    old = snapshot(target) if target.exists() else {}
    if set(old) - set(files):
        raise RuntimeError('runtime checkpoint would lose earlier files: ' + str(worktree))
    for relative, data in files.items():
        if relative in old and old[relative] != data and Path(relative).parts[0] in IMMUTABLE:
            raise RuntimeError('runtime checkpoint would alter an immutable record: ' + relative)
        path = safe_path(target, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with path.open('xb') as stream:
                stream.write(data)
        elif path.read_bytes() != data:
            path.write_bytes(data)  # Mutable control/log state only.
    manifest = {'backend': arm, 'seal_commit': seal_commit, 'seal_sha256': seal_sha256,
                'registration_sha256': registration_sha256,
                'files': [{'path': p, 'bytes': len(b), 'sha256': sha(b)} for p, b in files.items()]}
    manifest_path = worktree / 'runtime' / arm / 'MANIFEST.json'
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    git(worktree, 'add', '--force', '--', 'runtime/' + arm)
    if git(worktree, 'diff', '--cached', '--name-only'):
        git(worktree, 'commit', '-m', f'D1 {arm} runtime checkpoint')
    revision = git(worktree, 'rev-parse', 'HEAD')
    committed_paths=git(worktree,'ls-tree','-r','--name-only',revision,f'runtime/{arm}/run/').splitlines()
    if set(committed_paths)!={f'runtime/{arm}/run/'+p for p in files}:
        raise RuntimeError('checkpoint commit does not cover exact file inventory')
    for relative,data in files.items():
        committed=subprocess.check_output(['git','show',revision+f':runtime/{arm}/run/'+relative],cwd=worktree)
        if committed!=data:raise RuntimeError('checkpoint commit bytes differ: '+relative)
    # A rejected push raises; there is no force or automatic history repair.
    git(worktree, 'push', 'origin', 'HEAD:refs/heads/' + branch)
    published = git(repo, 'ls-remote', 'origin', 'refs/heads/' + branch).split()
    if not published or published[0] != revision:
        raise RuntimeError('runtime checkpoint publication not verified: ' + str(worktree))
    if snapshot(target) != files:
        raise RuntimeError('runtime checkpoint copy changed')
    git(repo, 'worktree', 'remove', str(worktree))
    parent.rmdir()
    return {'branch': branch, 'commit': revision, 'file_count': len(files), 'manifest': manifest}


def restore(repo, run_dir, arm, seal_commit, seal_sha256, registration_sha256):
    repo, run_dir = Path(repo).resolve(), Path(run_dir).resolve()
    if arm not in ('codex', 'claude'):
        raise ValueError('invalid arm')
    if git(repo, 'rev-parse', 'HEAD') != seal_commit:
        raise RuntimeError('restore checkout must be at the seal commit')
    if run_dir.exists():
        raise FileExistsError('restore requires an absent destination; never overwrite runtime files')
    branch = f'd1-{arm}-runtime'
    git(repo, 'fetch', '--no-tags', 'origin', branch)
    revision = git(repo, 'rev-parse', 'FETCH_HEAD')
    prefix = f'runtime/{arm}/'
    def blob(path):
        return subprocess.check_output(['git', 'show', revision + ':' + prefix + path], cwd=repo)
    manifest = json.loads(blob('MANIFEST.json'))
    expected = {'backend': arm, 'seal_commit': seal_commit, 'seal_sha256': seal_sha256,
                'registration_sha256': registration_sha256}
    if any(manifest.get(k) != v for k, v in expected.items()):
        raise RuntimeError('checkpoint belongs to another seal, registration or backend')
    listed = {}
    for entry in manifest['files']:
        relative = entry['path']
        safe_path(run_dir, relative)
        if relative in listed:
            raise RuntimeError('duplicate runtime manifest entry')
        data = blob('run/' + relative)
        if sha(data) != entry['sha256'] or len(data) != entry['bytes']:
            raise RuntimeError('runtime manifest mismatch: ' + relative)
        listed[relative] = data
    tree = git(repo, 'ls-tree', '-r', '--name-only', revision, prefix + 'run/').splitlines()
    if set(tree) != {prefix + 'run/' + p for p in listed}:
        raise RuntimeError('runtime manifest does not cover exact saved file set')
    run_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.restore-', dir=run_dir.parent))
    try:
        for relative, data in listed.items():
            path = safe_path(temporary, relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(data)
        if snapshot(temporary) != listed:
            raise RuntimeError('restored runtime bytes differ')
        temporary.rename(run_dir)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return {'branch': branch, 'commit': revision, 'file_count': len(listed), 'resume_requires_rick': True}


def main(argv=None):
    from .integrity import require_ready, digest, ensure_published
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['restore'])
    for name in ['repo', 'run-dir', 'registration', 'seal', 'seal-digest', 'branch']:
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--arm', choices=['codex', 'claude'], required=True)
    args = parser.parse_args(argv)
    require_ready(json.loads(Path(args.registration).read_text()))
    info = ensure_published(args.repo, args.branch, args.seal, args.seal_digest)
    result = restore(args.repo, args.run_dir, args.arm, info['seal_commit'], digest(Path(args.seal)), digest(Path(args.registration)))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
