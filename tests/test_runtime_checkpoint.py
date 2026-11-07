"""Lifecycle tests use a local bare remote and a fake relay only."""
from datetime import datetime,timedelta,timezone
import hashlib,json,shutil,subprocess
from pathlib import Path
import pytest
from earshot.runtime_checkpoint import checkpoint,restore,snapshot
from earshot.reliability import AttemptRunner,Control


def git(root,*args):return subprocess.check_output(['git',*args],cwd=root,text=True,stderr=subprocess.PIPE).strip()

@pytest.fixture
def repository(tmp_path):
    remote=tmp_path/'remote.git';repo=tmp_path/'run-checkout';repo.mkdir()
    subprocess.run(['git','init','--bare','-q',str(remote)],check=True)
    git(repo,'init','-q','-b','main');git(repo,'config','user.name','Offline fixture');git(repo,'config','user.email','fixture@example.invalid')
    git(repo,'remote','add','origin',str(remote));(repo/'seal.txt').write_text('fake seal, not a study seal')
    git(repo,'add','.');git(repo,'commit','-qm','fake sealed baseline');git(repo,'push','-q','origin','main')
    return repo,remote,git(repo,'rev-parse','HEAD')


def test_fake_run_pause_checkpoint_delete_restore_resume(repository,tmp_path):
    repo,remote,seal=repository;folder=repo/'run'
    control=Control(folder,datetime.now(timezone.utc)+timedelta(hours=1))
    patterns={'patterns':[{'id':'usage_limit','regex':'usage limit'}],'manual_pause_matches':['usage_limit','unclassified_no_answer']}
    calls=[]
    def fake(name,prompt,ctl):
        calls.append(name)
        return {'exit_code':1,'answer':None,'error':'usage limit'}
    good={'exit_code':0,'answer':{'required_memory_refs':['handoff_refs/A.txt','handoff_refs/B.txt']}}
    AttemptRunner(folder,patterns,control,lambda *a:good).run('finished','finished prompt')
    runner=AttemptRunner(folder,patterns,control,fake)
    assert runner.run('call','same prompt')['administrative_status']=='paused_usage_limit'
    original=snapshot(folder)
    saved=checkpoint(repo,folder,'codex',seal,'fake-seal-digest','fake-registration-digest')
    assert saved['branch']=='d1-codex-runtime' and git(repo,'rev-parse','HEAD')==seal
    shutil.rmtree(folder) # Test-only simulated loss, never applied to real traces.
    clone=tmp_path/'fresh-clone';subprocess.run(['git','clone','-q','--branch','main',str(remote),str(clone)],check=True)
    git(clone,'checkout','-q','--detach',seal)
    destination=clone/'run'
    restore(clone,destination,'codex',seal,'fake-seal-digest','fake-registration-digest')
    assert snapshot(destination)==original
    newcontrol=Control(destination,control.cutoff)
    assert newcontrol.before_launch()=='paused_usage_limit'
    skip=AttemptRunner(destination,patterns,newcontrol,lambda *a:pytest.fail('finished answer must not be repeated'))
    assert skip.run('finished','finished prompt')['classification']=='accepted'
    assert (destination/'traces/finished.json').read_bytes()==original['traces/finished.json']
    newcontrol.resume_by_rick()
    def succeeds(*a):return {'exit_code':0,'answer':{'required_memory_refs':['handoff_refs/A.txt','handoff_refs/B.txt']}}
    row=AttemptRunner(destination,patterns,newcontrol,succeeds).run('call','same prompt')
    assert row['classification']=='accepted' and row['attempt']==2
    assert (destination/'system_issue/call-attempt1.json').read_bytes()==original['system_issue/call-attempt1.json']
    assert (destination/'attempt_state/call/attempt1.json').read_bytes()==original['attempt_state/call/attempt1.json']


def test_checkpoint_cannot_change_earlier_trace(repository):
    repo,remote,seal=repository;folder=repo/'run';(folder/'traces').mkdir(parents=True)
    trace=folder/'traces/fake.json';trace.write_text('test-only first bytes')
    checkpoint(repo,folder,'claude',seal,'seal','registration')
    trace.write_text('test-only altered bytes')
    with pytest.raises(RuntimeError,match='immutable'):checkpoint(repo,folder,'claude',seal,'seal','registration')


def test_restore_rejects_wrong_seal_or_existing_destination(repository,tmp_path):
    repo,remote,seal=repository;folder=repo/'run';folder.mkdir();(folder/'control.json').write_text('{}')
    checkpoint(repo,folder,'codex',seal,'seal','registration')
    with pytest.raises(RuntimeError,match='another seal'):restore(repo,tmp_path/'restore','codex',seal,'wrong','registration')
    with pytest.raises(FileExistsError):restore(repo,folder,'codex',seal,'seal','registration')


def test_rejected_checkpoint_push_is_not_forced(repository):
    repo,remote,seal=repository;folder=repo/'run';folder.mkdir();(folder/'control.json').write_text('{}')
    hook=remote/'hooks/pre-receive';hook.write_text('#!/bin/sh\nexit 1\n');hook.chmod(0o755)
    with pytest.raises(subprocess.CalledProcessError):checkpoint(repo,folder,'codex',seal,'seal','registration')
    assert not git(repo,'ls-remote','origin','refs/heads/d1-codex-runtime')
    assert git(repo,'rev-parse','HEAD')==seal and (folder/'control.json').read_text()=='{}'


@pytest.mark.parametrize('tamper',['changed','extra'])
def test_restore_checks_every_hash_and_exact_inventory(repository,tmp_path,tamper):
    repo,remote,seal=repository;folder=repo/'run';folder.mkdir();(folder/'control.json').write_text('{}')
    checkpoint(repo,folder,'codex',seal,'seal','registration')
    edit=tmp_path/'tamper-clone';subprocess.run(['git','clone','-q','--branch','d1-codex-runtime',str(remote),str(edit)],check=True)
    git(edit,'config','user.name','Offline fixture');git(edit,'config','user.email','fixture@example.invalid')
    path=edit/'runtime/codex/run'/('control.json' if tamper=='changed' else 'extra.json');path.write_text('test-only alteration')
    git(edit,'add','.');git(edit,'commit','-qm','test-only bad snapshot');git(edit,'push','-q','origin','d1-codex-runtime')
    with pytest.raises(RuntimeError,match='mismatch|exact saved file set'):restore(repo,tmp_path/'restored','codex',seal,'seal','registration')
    assert not (tmp_path/'restored').exists()


def test_checkpoint_includes_git_ignored_runtime_bytes(repository,tmp_path):
    repo,remote,seal=repository;folder=repo/'run';(folder/'__pycache__').mkdir(parents=True)
    (folder/'__pycache__/fixture.pyc').write_bytes(b'test-only opaque runtime bytes')
    # This ignored-file rule belongs to the fake sealed repository.
    (repo/'.git/info/exclude').write_text('__pycache__/\n')
    checkpoint(repo,folder,'codex',seal,'seal','registration')
    destination=tmp_path/'restored'
    restore(repo,destination,'codex',seal,'seal','registration')
    assert snapshot(destination)==snapshot(folder)
