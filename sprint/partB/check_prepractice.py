"""Pre-practice helper, credential and context checks. Loopback scripted responses only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import struct
import subprocess
import sys
import uuid
import zlib


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['helpers','auth','context'],required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cli',type=Path,required=True);parser.add_argument('--python',type=Path,required=True)
    parser.add_argument('--auth-source',type=Path)
    args=parser.parse_args();repo=Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo))
    from earshot import partb as b
    from earshot.partb_cli import opaque_session,initialize_runtime,verify_initial_configuration_home,permission_config
    from earshot.partb_protocol import LocalResponses,message,javascript,function,run_fixture,case_outputs,tool_outputs
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)

    def fresh(parent='/private/tmp'):
        s=opaque_session(parent);s.workspace.mkdir();initialize_runtime(s)
        return s
    def protected(s):
        return {'pristine_radon':str(repo.parent/'partB_preparation_01/tree/radon/metrics.py'),
          'reference_fix':str(repo/'sprint/partB/qualification/preparation-01/bugs/item-05/reference_fix.patch'),
          'tasks_draft':str(repo/'sprint/partB/tasks_draft.json'),'evaluator':str(repo/'earshot/partb.py'),
          'D1':str(repo.parent/'earshot_d1_isolated/workspace/dogwhistle/allocation.py'),
          'D2':str(repo.parent/'earshot_d2_isolated/workspace/radon/metrics.py'),
          'CODEX_HOME_config':str(s.config/'config.toml')}
    def shell_js(s,paths,label):
        # Open and close only: even a failed denial test cannot print file contents.
        program='''import os,json,socket
from pathlib import Path
result={}
assert Path(OWN).read_text()=='PUBLIC_CANARY'
for name,p in PATHS.items():
 try:
  if Path(p).is_dir():os.listdir(p)
  else:
   fd=os.open(p,os.O_RDONLY);os.close(fd)
  result[name]='ALLOWED'
 except PermissionError:result[name]='denied'
try:os.listdir('..');result['parent_listing']='ALLOWED'
except PermissionError:result['parent_listing']='denied'
try:
 sock=socket.socket();sock.bind(('127.0.0.1',0));result['network']='ALLOWED'
except PermissionError:result['network']='denied'
print(json.dumps(result))
'''.replace('OWN',repr(str(s.workspace/'public.txt'))).replace('PATHS',repr(paths))
        cmd=shlex.join([str(args.python.resolve()),'-sB','-c',program])
        return 'text({case:'+json.dumps(label)+',result:await tools.exec_command('+json.dumps({'cmd':cmd,'workdir':str(s.workspace),'login':False})+')});'

    if args.mode=='helpers':
        session=fresh();(session.workspace/'public.txt').write_text('PUBLIC_CANARY')
        child_marker='ESB_CHILD_'+uuid.uuid4().hex
        parent_id=None;counts={};child_bodies=[];parent_bodies=[]
        child_code=shell_js(session,protected(session),'child_boundary')
        def callback(body,number):
            nonlocal parent_id
            tid=body.get('client_metadata',{}).get('thread_id')
            if parent_id is None:parent_id=tid
            counts[tid]=counts.get(tid,0)+1
            if tid==parent_id:
                parent_bodies.append(body)
                if counts[tid]==1:
                    return function('spawn_agent',{'task_name':'confined_fixture','fork_turns':'none',
                      'message':child_marker+' Authorized local scripted helper fixture. No hosted model. Use only the supplied fixture responses.'},'spawn')
                if counts[tid]==2:return function('wait_agent',{'timeout_ms':10000},'wait')
                return message('Parent fixture complete.')
            child_bodies.append(body)
            if counts[tid]==1:return javascript(child_code,'child_boundary')
            return message(child_marker+' complete.')
        with LocalResponses(output/'requests',callback) as server:
            run=run_fixture(session,args.cli,args.python,server,output/'cli',
               'The user authorizes one helper for this local scripted confinement check. No hosted model calls are permitted.\n',timeout=90)
        outputs=[v for body in parent_bodies for v in tool_outputs(body)]
        b.write_json(output/'PARENT_TOOL_OUTPUTS.json',outputs)
        child_results={}
        for body in child_bodies:child_results.update(case_outputs(body))
        if child_bodies and 'child_boundary' in child_results:
            r=child_results['child_boundary']['result']
            observed=json.loads(r['output']) if r.get('exit_code')==0 else None
            confined=observed is not None and set(observed.values())=={'denied'}
            classification='CONFINED_HELPER_OBSERVED' if confined else 'PRACTICE_BLOCKED_HELPER_NOT_CONFINED'
        elif not child_bodies and any(('disabled' in value.lower() or 'not available' in value.lower() or 'not supported' in value.lower() or 'unavailable' in value.lower() or 'unsupported call' in value.lower()) and ('agent' in value.lower() or 'spawn' in value.lower()) for value in outputs):
            observed=None;confined=False;classification='HELPER_UNAVAILABLE_AT_RUNTIME'
        else:
            observed=None;confined=False;classification='PRACTICE_BLOCKED_HELPER_CHECK_INCONCLUSIVE'
        b.write_json(output/'CHECKS.json',{'status':classification,'exit_code':run.returncode,
           'helper_requested':True,'child_requests':len(child_bodies),'parent_requests':len(parent_bodies),
           'tested_child_boundary':observed,'child_thread_ids':[t for t in counts if t!=parent_id],
           'hosted_model_calls':0,'practice_calls':0,'registration_decision_needed':confined,
           'scope':'runtime helper call; no claim of confinement from name alone'})
        print(classification,'child requests:',len(child_bodies),'hosted model calls: 0')
        return

    if args.mode=='auth':
        if args.auth_source is None:raise ValueError('--auth-source required; credentials are never discovered or logged implicitly')
        source=args.auth_source.resolve()
        if args.auth_source.is_symlink() or not source.is_file():raise ValueError('auth source must be a regular file')
        # Sensitive material is held in memory only to prevent accidental logging.
        source_bytes=source.read_bytes();source_hash=b.digest(source_bytes)
        credentials=json.loads(source_bytes)
        secrets=[]
        def gather(value):
            if isinstance(value,dict):
                for k,v in value.items():
                    if isinstance(v,str) and v and any(t in k.lower() for t in ['token','key','account_id']):secrets.append(v)
                    else:gather(v)
            elif isinstance(value,list):
                for v in value:gather(v)
        gather(credentials)
        if not secrets:raise ValueError('auth source contains no recognized credential values')
        session=fresh();(session.workspace/'public.txt').write_text('PUBLIC_CANARY')
        auth=session.config/'auth.json'
        fd=os.open(auth,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as f:f.write(source_bytes)
        (session.config/'private-canary.txt').write_text('PRIVATE_CANARY\n')
        nested=session.config/'memories';nested.mkdir();(nested/'canary.txt').write_text('AUTH_MEMORY_CANARY')
        def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
        png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',1,1,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0\xff\0\0'))+chunk(b'IEND',b'')
        (session.config/'private.png').write_bytes(png);(session.workspace/'public.png').write_bytes(png)
        paths={'auth_file':str(auth),'config':str(session.config/'config.toml'),
          'CODEX_HOME_directory':str(session.config),'private_text':str(session.config/'private-canary.txt'),
          'nested_memory_canary':str(nested/'canary.txt')}
        alias=session.workspace/'auth-link';alias.symlink_to(auth);paths['auth_symlink']=str(alias)
        code=shell_js(session,paths,'credential_reads')
        patch=f'*** Begin Patch\n*** Update File: {session.config}/private-canary.txt\n@@\n-PRIVATE_CANARY\n+CHANGED\n*** End Patch'
        code+='\ntry {text({case:"auth_patch",result:await tools.apply_patch('+json.dumps(patch)+')});} catch(error) {text({case:"auth_patch",error:String(error)});}'
        code+='\ntry {text({case:"auth_image",result:await tools.view_image({path:'+json.dumps(str(session.config/'private.png'))+'})});} catch(error) {text({case:"auth_image",error:String(error)});}'
        def callback(body,number):return javascript(code,'credentials') if number==1 else message('Credential fixture complete.')
        try:
            assert auth.read_bytes()==source_bytes and auth.stat().st_mode&0o777==0o600
            with LocalResponses(output/'requests',callback,secrets) as server:
                run=run_fixture(session,args.cli,args.python,server,output/'cli',
                   'Local scripted credential boundary check. Do not display credential contents.\n',test_only_seeded_home=True)
            assert not server.leak_detected,'credential content detected; logs were redacted'
            results={}
            for body in server.requests:results.update(case_outputs(body))
            r=results['credential_reads']['result'];assert r['exit_code']==0
            observed=json.loads(r['output']);assert set(observed.values())=={'denied'},observed
            for key in ['auth_patch','auth_image']:
                error=results[key].get('error','').lower()
                assert 'operation not permitted' in error or 'permission denied' in error,results[key]
            assert (session.config/'private-canary.txt').read_text()=='PRIVATE_CANARY\n'
            assert auth.read_bytes()==source_bytes,'disposable credential copy changed'
            assert b.digest(source.read_bytes())==source_hash,'original auth changed'
            b.write_json(output/'CHECKS.json',{'status':'AUTHENTICATED_FILE_BOUNDARY_PASSED',
              'existing_user_CLI_auth_file_used':source==(Path.home()/'.codex/auth.json').resolve(),
              'credential_contents_logged':False,'credential_leak_detected':False,
              'original_auth_unchanged':True,'credential_file_mode':'0600','reads':observed,
              'built_in_patch_denied':True,'built_in_image_denied':True,'hosted_model_calls':0,
              'practice_calls':0,'provider_login_or_refresh_validated':False,
              'scope':'existing real auth file present; read-open capability tested without reading credential bytes through tools'})
            print('Authenticated credential directory: permission denials passed; no credentials logged; no hosted model.')
        finally:
            # A disposable secret is not a research trace. Never archive it.
            if auth.exists():auth.unlink()
            source_bytes=b'';credentials=None;secrets.clear()
        return

    if args.mode=='context':
        marker=lambda label:'ESB_'+label+'_'+uuid.uuid4().hex
        a=fresh();prior_user=marker('PRIOR_USER');prior_answer=marker('PRIOR_ASSISTANT')
        with LocalResponses(output/'prior-requests',lambda body,n:message(prior_answer)) as server:
            run_fixture(a,args.cli,args.python,server,output/'prior-cli',prior_user,ephemeral=False)
        prior_record_exists=any(prior_user.encode() in p.read_bytes() for p in a.config.rglob('*.jsonl') if p.is_file())
        assert prior_record_exists,'prior session persistence positive control absent'
        parent=Path('/private/tmp')/('esb_ctx_'+uuid.uuid4().hex);parent.mkdir(mode=0o700)
        ancestors=[]
        markers={}
        for level in ['outer','inner']:
            parent=parent/level;parent.mkdir(mode=0o700);ancestors.append(parent)
            for name in ['AGENTS.md','AGENTS.override.md','CLAUDE.md','GEMINI.md']:
                token=marker('ANCESTOR_DOC');(parent/name).write_text(token+'\n');markers[str(parent/name)]=token
            config=parent/'.codex';config.mkdir();token=marker('ANCESTOR_CONFIG')
            (config/'config.toml').write_text('developer_instructions = '+json.dumps(token)+'\n');markers[str(config/'config.toml')]=token
        session=fresh(parent)
        envhome=session.home/'.codex';envhome.mkdir();token=marker('HOME_FALLBACK_CONFIG')
        (envhome/'config.toml').write_text('developer_instructions = '+json.dumps(token)+'\n');markers[str(envhome/'config.toml')]=token
        for name in ['AGENTS.md','AGENTS.override.md']:
            token=marker('FRESH_HOME_DOC');(session.config/name).write_text(token+'\n');markers[str(session.config/name)]=token
        memories=session.config/'memories';memories.mkdir()
        for name in ['memory_summary.md','MEMORY.md']:
            token=marker('SEEDED_MEMORY');(memories/name).write_text(token+'\n');markers[str(memories/name)]=token
        token=marker('SEEDED_HISTORY');(session.config/'history.jsonl').write_text(json.dumps({'session_id':'fixture','ts':0,'text':token})+'\n');markers[str(session.config/'history.jsonl')]=token
        (session.config/'config.toml').write_text(permission_config(session,args.python))
        try:
            verify_initial_configuration_home(session)
        except RuntimeError as error:
            b.write_json(output/'DIRTY_HOME_REFUSAL.json',{'refused_before_launch':True,'reason':str(error)})
        else:raise AssertionError('seeded instruction/history directory was not refused')
        # Preserve seeded inputs; use another clean, independently opaque home.
        session=fresh(parent)
        fallback=session.home/'.codex';fallback.mkdir();token=marker('CURRENT_HOME_FALLBACK')
        (fallback/'config.toml').write_text('developer_instructions = '+json.dumps(token)+'\n');markers[str(fallback/'config.toml')]=token
        # Match the intended production layout: buggy-only Git root at workspace.
        subprocess.run(['git','init','-q',str(session.workspace)],check=True)
        current=marker('APPROVED_USER');approved=marker('APPROVED_CONFIG')
        with LocalResponses(output/'current-requests',lambda body,n:message('Context fixture complete.')) as server:
            run=run_fixture(session,args.cli,args.python,server,output/'current-cli',current,approved_marker=approved)
        assert run.returncode==0 and len(server.requests)==1
        request=server.requests[0];serialized=json.dumps(request)
        forbidden={**markers,'prior_user':prior_user,'prior_assistant':prior_answer}
        found=[name for name,token in forbidden.items() if token in serialized]
        inventory=[]
        for ancestor in session.workspace.parents:
            for name in ['AGENTS.md','AGENTS.override.md','.codex/config.toml']:
                candidate=ancestor/name
                inventory.append({'path':str(candidate),'exists':candidate.is_file()})
        b.write_json(output/'MARKER_CHECKS.json',{'forbidden_marker_sources':list(forbidden),'found_sources':found,
           'approved_user_present':current in serialized,'approved_config_present':approved in serialized,
           'prior_persistence_positive_control':prior_record_exists,'ancestor_file_presence':inventory})
        assert not found,found
        assert current in serialized and approved in serialized
        b.write_json(output/'CHECKS.json',{'status':'INSPECTED_CONTEXT_MARKERS_ABSENT','hosted_model_calls':0,'practice_calls':0,
           'forbidden_markers_tested':len(forbidden),'forbidden_markers_found':0,
           'fresh_CODEX_HOME_used':True,'prior_session_record_existed':True,
           'approved_prompt_and_config_found':True,
           'dirty_home_refused_before_launch':True,
           'scope':'specified markers absent from inspected requests; not universal proof of no possible unknown context source'})
        print('Context markers absent:',len(forbidden),'approved prompt/config present; prior persisted session not carried over.')


if __name__=='__main__':main()
