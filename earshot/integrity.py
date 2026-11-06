"""Published-source and immutable-ledger checks. No function launches a model."""
import hashlib
import json
from pathlib import Path
import subprocess

PENDING=('PENDING_RECON','PENDING_RICK','PENDING_REVIEW')


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require_ready(value):
    text=json.dumps(value,sort_keys=True)
    if any(marker in text for marker in PENDING):raise RuntimeError('registration/configuration contains pending review fields')
    if isinstance(value,dict) and value.get('status')=='DRAFT':raise RuntimeError('draft registration cannot run or score')


def git(repo,*args):return subprocess.check_output(['git',*args],cwd=repo,text=True,stderr=subprocess.PIPE).strip()


def safe_path(root,relative):
    root=Path(root).resolve();p=(root/relative).resolve()
    if not p.is_relative_to(root) or '.git' in p.relative_to(root).parts:raise RuntimeError('unsafe manifest path')
    return p


def verify_digest(path,digest_file):
    expected=Path(digest_file).read_text().strip()
    if len(expected)!=64 or any(c not in '0123456789abcdef' for c in expected):raise RuntimeError('invalid digest file')
    if digest(path)!=expected:raise RuntimeError('digest mismatch')
    return expected


def published_head(repo,branch):
    head=git(repo,'rev-parse','HEAD')
    remote=git(repo,'ls-remote','origin','refs/heads/'+branch).split()
    if not remote or remote[0]!=head:raise RuntimeError('HEAD is not the published branch head')
    return head


def committed_bytes(repo,path,head):
    repo=Path(repo).resolve();rel=Path(path).resolve().relative_to(repo).as_posix()
    try:blob=subprocess.check_output(['git','show',head+':'+rel],cwd=repo,stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:raise RuntimeError('file not committed: '+rel) from e
    if blob!=Path(path).read_bytes():raise RuntimeError('file differs from published commit: '+rel)
    return rel


def ensure_published(repo,branch,seal_path,seal_digest):
    repo=Path(repo).resolve();seal_path=Path(seal_path).resolve()
    seal=json.loads(seal_path.read_text());require_ready(seal)
    expected=verify_digest(seal_path,seal_digest)
    head=published_head(repo,branch)
    relative=committed_bytes(repo,seal_path,head);committed_bytes(repo,seal_digest,head)
    seal_commit=git(repo,'log','-1','--format=%H','--',relative)
    if head!=seal_commit:raise RuntimeError('local commit exists after seal')
    for entry in seal['files']:
        p=safe_path(repo,entry['path'])
        if digest(p)!=entry['sha256']:raise RuntimeError('sealed file hash mismatch: '+entry['path'])
        committed_bytes(repo,p,head)
    return {'seal_digest':expected,'seal_commit':seal_commit,'branch':branch}


def runtime_files(folder):
    folder=Path(folder)
    files=set()
    for name in ['traces','system_issue','attempt_state','stopped']:
        files.update(p.resolve() for p in (folder/name).rglob('*.json') if p.is_file())
    for name in ['pauses.json','control.json','plan.json']:
        if (folder/name).is_file():files.add((folder/name).resolve())
    return files


def verify_ledger(repo,branch,ledger_path,ledger_digest,run_dir):
    verify_digest(ledger_path,ledger_digest)
    head=published_head(repo,branch)
    committed_bytes(repo,ledger_path,head);committed_bytes(repo,ledger_digest,head)
    ledger=json.loads(Path(ledger_path).read_text())
    listed=set()
    for entry in ledger['files']:
        p=safe_path(run_dir,entry['path'])
        if p in listed:raise RuntimeError('duplicate ledger path')
        listed.add(p)
        if digest(p)!=entry['sha256']:raise RuntimeError('trace/ledger hash mismatch: '+entry['path'])
        committed_bytes(repo,p,head)
    if listed!=runtime_files(run_dir):raise RuntimeError('ledger runtime file set mismatch')
    return ledger
