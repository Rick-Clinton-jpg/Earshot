"""Loopback scripted protocol transport for CLI integration checks, never inference."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import threading

from .partb import write_json
from .partb_cli import permission_config,environment,cli_prefix,verify_initial_configuration_home


def message(text):
    return {'type':'message','id':'msg_fixture','role':'assistant',
          'content':[{'type':'output_text','text':text,'annotations':[]}]}


def javascript(code,tag='fixture'):
    return {'type':'custom_tool_call','id':'ctc_'+tag,'call_id':'call_'+tag,
            'name':'exec','namespace':'functions','input':code}


def function(name,arguments,tag='fixture'):
    return {'type':'function_call','id':'fc_'+tag,'call_id':'call_'+tag,
            'name':name,'namespace':'collaboration','arguments':json.dumps(arguments)}


def tool_outputs(body):
    out=[]
    for entry in body.get('input',[]):
        if not entry.get('type','').endswith('call_output'):continue
        value=entry.get('output',[])
        if isinstance(value,str):out.append(value)
        else:out.extend(v.get('text','') for v in value if isinstance(v,dict))
    return out


def case_outputs(body):
    results={}
    for value in tool_outputs(body):
        try:item=json.loads(value)
        except json.JSONDecodeError:continue
        if isinstance(item,dict) and 'case' in item:results[item['case']]=item
    return results


class LocalResponses:
    def __init__(self,output,callback,secrets=()):
        self.output=Path(output);self.output.mkdir(parents=True,exist_ok=False)
        self.callback=callback;self.secrets=[v for v in secrets if v];self.requests=[]
        self.leak_detected=False;self.lock=threading.RLock()
        parent=self
        class Handler(BaseHTTPRequestHandler):
            protocol_version='HTTP/1.1'
            def log_message(self,*args):pass
            def do_POST(self):
                raw=self.rfile.read(int(self.headers.get('Content-Length',0)))
                body=json.loads(raw)
                with parent.lock:
                    parent.requests.append(body);number=len(parent.requests)
                    text=json.dumps(body)
                    if any(secret in text for secret in parent.secrets):
                        parent.leak_detected=True
                        write_json(parent.output/f'request-{number}.json',{'credential_leak_detected':True,'body_not_saved':True})
                        item=message('Fixture stopped: sensitive content would have entered a request.')
                    else:
                        write_json(parent.output/f'request-{number}.json',body)
                        item=parent.callback(body,number)
                events=[('response.created',{'type':'response.created','response':{'id':f'resp_{number}','status':'in_progress'}}),
                  ('response.output_item.added',{'type':'response.output_item.added','output_index':0,'item':item}),
                  ('response.output_item.done',{'type':'response.output_item.done','output_index':0,'item':item}),
                  ('response.completed',{'type':'response.completed','response':{'id':f'resp_{number}','status':'completed',
                    'output':[item],'usage':{'input_tokens':0,'output_tokens':0,'total_tokens':0}}})]
                data=''.join('event: '+name+'\ndata: '+json.dumps(payload)+'\n\n' for name,payload in events).encode()
                self.send_response(200);self.send_header('Content-Type','text/event-stream')
                self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
    def __enter__(self):self.thread.start();return self
    def __exit__(self,*args):self.server.shutdown();self.server.server_close()
    @property
    def url(self):return f'http://127.0.0.1:{self.server.server_address[1]}/v1'
    def safe_text(self,text):
        for secret in self.secrets:
            if secret in text:self.leak_detected=True;text=text.replace(secret,'[REDACTED_CREDENTIAL]')
        return text


def fixture_config(session,python,url,approved_marker=None):
    prefix,permissions=permission_config(session,python).split('[permissions.partb]',1)
    if approved_marker:prefix+='developer_instructions = '+json.dumps(approved_marker)+'\n'
    return prefix+f'''model = "gpt-6.1-sol"
model_provider = "offline_fixture"
[model_providers.offline_fixture]
name = "Local scripted fixture - no model"
base_url = "{url}"
wire_api = "responses"
requires_openai_auth = false
supports_websockets = false
'''+'[permissions.partb]'+permissions


def run_fixture(session,cli,python,server,output,prompt,ephemeral=True,approved_marker=None,timeout=60,test_only_seeded_home=False):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    config=fixture_config(session,python,server.url,approved_marker)
    target=session.config/'config.toml'
    with target.open('x') as f:f.write(config)
    if not test_only_seeded_home:verify_initial_configuration_home(session)
    (output/'config.toml').write_text(config)
    argv=cli_prefix(cli)+['exec','--strict-config','--ignore-rules','--skip-git-repo-check',
      '-C',str(session.workspace),'--json']+(['--ephemeral'] if ephemeral else [])+['-']
    run=subprocess.run(argv,input=prompt,text=True,cwd=session.workspace,env=environment(session),
       stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    (output/'stdout.log').write_text(server.safe_text(run.stdout))
    (output/'stderr.log').write_text(server.safe_text(run.stderr))
    write_json(output/'PROCESS.json',{'status':'SCRIPTED_LOOPBACK_NOT_STUDY_DATA','argv':argv,
       'exit_code':run.returncode,'hosted_model_calls':0,'local_protocol_requests':len(server.requests),
       'credential_leak_detected':server.leak_detected,'ephemeral':ephemeral})
    return run
