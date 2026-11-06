import hashlib,json,subprocess
from pathlib import Path
import pytest
from earshot.integrity import ensure_published,verify_ledger,require_ready


def git(root,*args):return subprocess.check_output(['git',*args],cwd=root,text=True,stderr=subprocess.PIPE).strip()


@pytest.fixture
def published(tmp_path):
    remote=tmp_path/'remote.git';repo=tmp_path/'repo';repo.mkdir()
    subprocess.run(['git','init','--bare','-q',str(remote)],check=True)
    git(repo,'init','-q','-b','main');git(repo,'config','user.name','Offline Fixture');git(repo,'config','user.email','fixture@example.invalid')
    git(repo,'remote','add','origin',str(remote))
    (repo/'code.py').write_text('fixture = True\n')
    seal={'stage':'D1','files':[{'path':'code.py','sha256':hashlib.sha256((repo/'code.py').read_bytes()).hexdigest()}]}
    (repo/'seal.json').write_text(json.dumps(seal));(repo/'seal.sha256').write_text(hashlib.sha256((repo/'seal.json').read_bytes()).hexdigest()+'\n')
    git(repo,'add','.');git(repo,'commit','-qm','fixture seal');git(repo,'push','-q','origin','main')
    return repo,remote


def test_published_passes(published):
    repo,_=published;assert ensure_published(repo,'main',repo/'seal.json',repo/'seal.sha256')['seal_commit']==git(repo,'rev-parse','HEAD')


@pytest.mark.parametrize('case',['unpushed','pushed_after_seal','edited_code','seal_digest'])
def test_publication_refusals(published,case):
    repo,_=published
    if case in ['unpushed','pushed_after_seal']:
        (repo/'other').write_text('another commit');git(repo,'add','.');git(repo,'commit','-qm','after seal')
        if case=='pushed_after_seal':git(repo,'push','-q','origin','main')
    elif case=='edited_code':(repo/'code.py').write_text('fixture = Truf\n')
    else:(repo/'seal.sha256').write_text('0'*64+'\n')
    with pytest.raises(RuntimeError):ensure_published(repo,'main',repo/'seal.json',repo/'seal.sha256')


def setup_ledger(repo):
    run=repo/'arm';(run/'traces').mkdir(parents=True);p=run/'traces/call.json';p.write_text('{"fixture":true}')
    ledger=repo/'ledger.json';ledger.write_text(json.dumps({'files':[{'path':'traces/call.json','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}]}))
    stamp=repo/'ledger.sha256';stamp.write_text(hashlib.sha256(ledger.read_bytes()).hexdigest()+'\n')
    git(repo,'add','.');git(repo,'commit','-qm','fixture ledger');git(repo,'push','-q','origin','main')
    return run,ledger,stamp


def test_ledger_passes(published):
    repo,_=published;run,ledger,stamp=setup_ledger(repo);assert verify_ledger(repo,'main',ledger,stamp,run)


@pytest.mark.parametrize('case',['digest','edited_trace','extra_trace'])
def test_ledger_refusals(published,case):
    repo,_=published;run,ledger,stamp=setup_ledger(repo)
    if case=='digest':stamp.write_text('0'*64+'\n')
    elif case=='edited_trace':(run/'traces/call.json').write_text('{"fixture":fals}')
    else:(run/'traces/extra.json').write_text('{}')
    with pytest.raises(RuntimeError):verify_ledger(repo,'main',ledger,stamp,run)


@pytest.mark.parametrize('marker',['PENDING_RECON','PENDING_RICK','PENDING_REVIEW'])
def test_pending_always_refused(marker):
    with pytest.raises(RuntimeError):require_ready({'nested':{'method':marker}})
