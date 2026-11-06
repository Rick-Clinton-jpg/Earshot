"""Build and verify an external pinned task workspace from a local clone."""
import hashlib
from pathlib import Path
import subprocess

PINNED_COMMIT = '1a4b471b3cfb4ed6d5def7c61356c5230af8c082'
REF_SHA256 = '260defc28224d9f6c3b189c5f27a8e85b091ed76aeff09c077c21d9fc60771bd'


def git(workspace, *args):
    return subprocess.check_output(['git', '-C', str(workspace), *args], text=True).strip()


def verify(workspace, refs_source):
    workspace, refs_source = Path(workspace), Path(refs_source)
    head = git(workspace, 'rev-parse', 'HEAD')
    status = git(workspace, 'status', '--porcelain')
    hashes = {}
    for letter in 'ABCD':
        data = (workspace / 'handoff_refs' / f'{letter}.txt').read_bytes()
        assert data == (refs_source / f'{letter}.txt').read_bytes(), 'ref differs from source'
        hashes[letter] = hashlib.sha256(data).hexdigest()
    if head != PINNED_COMMIT or status or set(hashes.values()) != {REF_SHA256}:
        raise ValueError('workspace pin, status, or refs failed verification')
    return {'head': head, 'status_porcelain': status, 'refs_sha256': hashes, 'refs_ignored_not_tracked': git(workspace, 'ls-files', '--others', '--ignored', '--exclude-standard', 'handoff_refs/') .splitlines()}


def build(source, destination, refs_source, repository):
    source, destination, refs_source, repository = map(lambda p: Path(p).resolve(), (source, destination, refs_source, repository))
    if destination.is_relative_to(repository) or destination == source or source.is_relative_to(destination):
        raise ValueError('task workspace must be outside the Earshot repository and distinct from source')
    if destination.exists():
        raise FileExistsError(destination)
    subprocess.run(['git', 'clone', '--no-hardlinks', '--no-checkout', str(source), str(destination)], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(destination), 'checkout', '--detach', PINNED_COMMIT], check=True, capture_output=True)
    refs = destination / 'handoff_refs'; refs.mkdir()
    for letter in 'ABCD':
        data = (refs_source / f'{letter}.txt').read_bytes()
        if hashlib.sha256(data).hexdigest() != REF_SHA256:
            raise ValueError('source ref hash mismatch')
        (refs / f'{letter}.txt').write_bytes(data)
    with (destination / '.git/info/exclude').open('a') as stream:
        stream.write('\n# Earshot fixture refs: verified separately, not task-repo changes\n/handoff_refs/\n')
    return verify(destination, refs_source)


def compare(original, rebuilt):
    def snapshot(root):
        return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}
    a, b = snapshot(Path(original)), snapshot(Path(rebuilt))
    return {'only_original': sorted(a.keys()-b.keys()), 'only_rebuilt': sorted(b.keys()-a.keys()), 'different_bytes': sorted(k for k in a.keys() & b.keys() if a[k] != b[k]), 'excluded_metadata': '.git/; rebuilt .git/info/exclude ignores only the verified handoff_refs fixture directory'}
