"""Drive real CLI tool routing with a loopback-only scripted Responses fixture.

No hosted model, account credentials or model inference. Synthetic responses are
implementation fixtures and must never be included in Part B observations.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import threading
import shlex
import struct
import zlib


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--cli',type=Path,required=True);ap.add_argument('--python',type=Path,required=True)
    ap.add_argument('--exercise',action='store_true')
    args=ap.parse_args();repo=Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo))
    from earshot import partb as b
    from earshot.partb_cli import opaque_session,initialize_runtime,permission_config,environment,cli_prefix
    args.output.mkdir(parents=True,exist_ok=False)
    session=opaque_session();session.workspace.mkdir();initialize_runtime(session)
    private=args.output/'private-fixtures';private.mkdir()
    private_text=private/'canary.txt';private_text.write_text('PRIVATE_CANARY\n')
    own_text=session.workspace/'public-canary.txt';own_text.write_text('PUBLIC_CANARY\n')
    def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',1,1,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0\xff\0\0'))+chunk(b'IEND',b'')
    private_png=private/'canary.png';private_png.write_bytes(png)
    own_png=session.workspace/'public-canary.png';own_png.write_bytes(png)
    protected={
       'private_canary':str(private_text.resolve()),
       'pristine_radon':str(repo.parent/'partB_preparation_01/tree/radon/metrics.py'),
       'reference_fix':str(repo/'sprint/partB/qualification/preparation-01/bugs/item-05/reference_fix.patch'),
       'tasks_draft':str(repo/'sprint/partB/tasks_draft.json'),
       'evaluator':str(repo/'earshot/partb.py'),
       'D1_workspace':str(repo.parent/'earshot_d1_isolated/workspace/dogwhistle/allocation.py'),
       'D2_workspace':str(repo.parent/'earshot_d2_isolated/workspace/radon/metrics.py'),
    }
    program='''import json,os
from pathlib import Path
result={}
for name,p in PATHS.items():
 try:
  with open(p,'rb') as f:f.read(1)
  result[name]='ALLOWED'
 except PermissionError:result[name]='denied'
try:os.listdir('..');result['parent_listing']='ALLOWED'
except PermissionError:result['parent_listing']='denied'
print(json.dumps(result))
'''.replace('PATHS',repr(protected))
    shell_command=shlex.join([str(args.python.resolve()),'-sB','-c',program])
    patch_own=f'*** Begin Patch\n*** Update File: {own_text}\n@@\n-PUBLIC_CANARY\n+PUBLIC_EDIT\n*** End Patch'
    patch_private=f'*** Begin Patch\n*** Update File: {private_text.resolve()}\n@@\n-PRIVATE_CANARY\n+PRIVATE_EDIT\n*** End Patch'
    exec_code='''text({case:"shell",result:await tools.exec_command(PRIMARY_COMMAND)});
try {text({case:"shell_outside_cwd",result:await tools.exec_command(SECONDARY_COMMAND)});}
catch(error) {text({case:"shell_outside_cwd",error:String(error)});}
for (const [label,patch] of PATCHES) {
 try { text({case:label,result:await tools.apply_patch(patch)}); }
 catch(error) { text({case:label,error:String(error)}); }
}
for (const [label,path] of IMAGES) {
 try { const r=await tools.view_image({path});text({case:label,result:r}); }
 catch(error) { text({case:label,error:String(error)}); }
}
'''.replace('PRIMARY_COMMAND',json.dumps({'cmd':shell_command,'workdir':str(session.workspace),'login':False}))
    exec_code=exec_code.replace('PATCHES',json.dumps([['patch_own',patch_own],['patch_private',patch_private]]))
    exec_code=exec_code.replace('SECONDARY_COMMAND',json.dumps({'cmd':shell_command,
       'workdir':str(repo.parent/'earshot_d2_isolated/workspace'),'login':False}))
    exec_code=exec_code.replace('IMAGES',json.dumps([['image_own',str(own_png)],['image_private',str(private_png.resolve())]]))
    tools=[];requests=[]
    class Handler(BaseHTTPRequestHandler):
        protocol_version='HTTP/1.1'
        def log_message(self,*a):pass
        def do_POST(self):
            raw=self.rfile.read(int(self.headers.get('Content-Length',0)))
            body=json.loads(raw);requests.append({'path':self.path,'model':body.get('model')})
            b.write_json(args.output/f'request-{len(requests)}.json',body)
            tools.extend(body.get('tools',[]))
            for entry in body.get('input',[]):tools.extend(entry.get('tools',[]))
            item={'type':'message','id':'msg_fixture','role':'assistant',
                  'content':[{'type':'output_text','text':'Offline protocol fixture complete.','annotations':[]}]}
            if args.exercise and len(requests)==1:
                item={'type':'custom_tool_call','id':'ctc_fixture','call_id':'call_fixture',
                      'name':'exec','namespace':'functions','input':exec_code}
            events=[('response.created',{'type':'response.created','response':{'id':'resp_fixture','status':'in_progress'}}),
              ('response.output_item.added',{'type':'response.output_item.added','output_index':0,'item':item}),
              ('response.output_item.done',{'type':'response.output_item.done','output_index':0,'item':item}),
              ('response.completed',{'type':'response.completed','response':{'id':'resp_fixture','status':'completed',
                 'output':[item],'usage':{'input_tokens':0,'output_tokens':0,'total_tokens':0}}})]
            data=''.join(f'event: {name}\ndata: '+json.dumps(payload)+'\n\n' for name,payload in events).encode()
            self.send_response(200);self.send_header('Content-Type','text/event-stream')
            self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    port=server.server_address[1]
    prefix,permissions=permission_config(session,args.python).split('[permissions.partb]',1)
    config=prefix+f'''model = "gpt-6.1-sol"
model_provider = "offline_fixture"
[model_providers.offline_fixture]
name = "Local scripted fixture - no model"
base_url = "http://127.0.0.1:{port}/v1"
wire_api = "responses"
requires_openai_auth = false
supports_websockets = false
'''+'[permissions.partb]'+permissions
    (session.config/'config.toml').write_text(config)
    (args.output/'config.toml').write_text(config)
    argv=cli_prefix(args.cli)+['exec','--strict-config','--ephemeral','--ignore-rules',
          '--skip-git-repo-check','-C',str(session.workspace),'--json','-']
    try:
        run=subprocess.run(argv,input='This is an offline scripted protocol fixture. No research task is being performed.\n',
          text=True,cwd=session.workspace,env=environment(session),capture_output=True,timeout=45)
        (args.output/'stdout.log').write_text(run.stdout);(args.output/'stderr.log').write_text(run.stderr)
        b.write_json(args.output/'TOOLS.json',tools)
        b.write_json(args.output/'PROCESS.json',{'argv':argv,'exit_code':run.returncode,'requests':requests,
             'live_model_calls':0,'CLI_exec_invocations':1,'root':str(session.root),
             'status':'LOCAL_SCRIPTED_PROTOCOL_FIXTURE_NOT_STUDY_DATA'})
        if args.exercise:
            assert run.returncode==0 and len(requests)==2
            body=json.loads((args.output/'request-2.json').read_text());results={}
            for entry in body['input']:
                if entry.get('type')!='custom_tool_call_output':continue
                for block in entry.get('output',[]):
                    try:value=json.loads(block.get('text',''))
                    except (json.JSONDecodeError,AttributeError):continue
                    if isinstance(value,dict) and 'case' in value:results[value['case']]=value
            b.write_json(args.output/'TOOL_RESULTS.json',results)
            assert set(results)=={'shell','shell_outside_cwd','patch_own','patch_private','image_own','image_private'},results
            shell=results['shell']['result']
            assert shell['exit_code']==0,shell
            denied=json.loads(shell['output'])
            assert set(denied.values())=={'denied'},denied
            outside=results['shell_outside_cwd']
            if 'result' in outside and outside['result'].get('exit_code')==0:
                # Working directory must never become an extra readable workspace.
                assert set(json.loads(outside['result']['output']).values())=={'denied'},outside
            else:
                message=json.dumps(outside.get('error',outside.get('result'))).lower()
                assert any(word in message for word in ['permissionerror','permission denied','operation not permitted']),outside
            assert own_text.read_text()=='PUBLIC_EDIT\n'
            assert private_text.read_text()=='PRIVATE_CANARY\n'
            blocked=str(results['patch_private'].get('error','')).lower()
            assert any(word in blocked for word in ['permission denied','operation not permitted']),blocked
            assert 'image_url' in json.dumps(results['image_own']),results['image_own']
            image=str(results['image_private'].get('error','')).lower()
            assert 'image_url' not in image
            assert any(word in image for word in ['permission denied','operation not permitted']),image
            b.write_json(args.output/'CHECKS.json',{'status':'REAL_CLI_TOOLS_SCRIPTED_FIXTURE_PASSED',
               'live_model_calls':0,'CLI_exec_invocations':1,'loopback_requests':len(requests),
               'shell_protected_reads':denied,'own_patch_succeeded':True,'private_patch_denied':True,
               'outside_workdir_did_not_grant_reads':True,
               'own_image_read_succeeded':True,'private_image_denied':True,
               'collaboration_tools_still_advertised':'collaboration' in {t.get('name') for t in tools},
               'disable_multi_agent_requested':True,'subagent_tools_invoked':False,
               'outer_sandbox_used':False,'scope':'actual CLI tool routes with scripted local responses, no hosted model'})
        print('exit',run.returncode,'local requests',requests)
        print('tool names:',[(t.get('type'),t.get('name')) for t in tools])
        print(run.stderr[:1800])
        print(run.stdout[-1500:])
    finally:server.shutdown();server.server_close()

if __name__=='__main__':main()
