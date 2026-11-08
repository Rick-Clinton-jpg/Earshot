"""Plain agent-side pytest under setup v2, driven by a local scripted server."""
import argparse
from datetime import timedelta
import json
from pathlib import Path
import re
import sys
import subprocess


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cli',type=Path,required=True);parser.add_argument('--python',type=Path,required=True)
    args=parser.parse_args();repo=Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo))
    from earshot import partb as b
    from earshot.partb_cli import opaque_session,initialize_runtime,SETUP_VERSION
    from earshot.partb_launch import prepare_practice,PracticeControl,run_prepared,stamp,utcnow
    from earshot.partb_protocol import LocalResponses,javascript,message,case_outputs
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    pristine=b.snapshot(repo.parent/'partB_preparation_01/tree')
    manifest=json.loads((repo/'sprint/partB/qualification/preparation-01/SOURCE_MANIFEST.json').read_text())
    assert {p:r['sha256'] for p,r in pristine.items()}==manifest
    practice=repo/'sprint/partB/qualification/practice-02'
    task=json.loads((practice/'QUALIFICATION.json').read_text());results={}
    for variant in ['pristine','practice_bug']:
        directory=output/variant;directory.mkdir()
        session=opaque_session();assert not list(session.root.iterdir())
        b.materialize(pristine,session.workspace);initialize_runtime(session)
        if variant=='practice_bug':
            subprocess.run(['git','apply',str(practice/'bug.patch')],cwd=session.workspace,check=True)
        command='python -m pytest -q radon/tests'
        code='text({case:"plain_tests",result:await tools.exec_command('+json.dumps({
            'cmd':command,'workdir':str(session.workspace),'login':True,
            'max_output_tokens':4000,'yield_time_ms':10000})+')});'
        with LocalResponses(directory/'requests',lambda body,n:javascript(code) if n==1 else message('Offline setup check complete.')) as server:
            prepared=prepare_practice(session,args.cli,args.python,loopback_url=server.url)
            assert prepared['env']['PYTEST_DISABLE_PLUGIN_AUTOLOAD']=='1'
            assert prepared['env']['PYTEST_PLUGINS']=='pytest_mock'
            b.write_json(directory/'PREPARED.json',prepared)
            control=PracticeControl(directory/'journal',stamp(utcnow()+timedelta(minutes=3)))
            result=run_prepared(control,'offline',session,prepared,'Local scripted test setup check; no hosted model.',60,5,[],fixture=True)
        assert result['status']=='completed' and len(server.requests)==2,result
        tool=case_outputs(server.requests[-1])['plain_tests']['result']
        b.write_json(directory/'TOOL_RESULT.json',tool)
        text=tool['output'];failures=re.findall(r'^FAILED (\S+)(?:\s+-.*)?$',text,re.M)
        assert not re.search(r'\b[1-9]\d* errors?\b',text),text
        assert 'fixture \'mocker\' not found' not in text
        if variant=='pristine':
            assert tool['exit_code']==0 and re.search(r'\b404 passed\b',text) and not failures,text
            passed=404
        else:
            assert tool['exit_code']==1 and re.search(r'\b1 failed, 403 passed\b',text),text
            assert failures==task['diagnostic_node_ids'],failures
            passed=403
        results[variant]={'passed':passed,'failed':failures,'setup_errors':0,'exit_code':tool['exit_code']}
        print(variant,results[variant],flush=True)
    b.write_json(output/'CHECKS.json',{'setup_version':SETUP_VERSION,'command':'python -m pytest -q radon/tests',
        'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','PYTEST_PLUGINS':'pytest_mock','cases':results,
        'hosted_model_calls':0,'practice_calls':0,'local_protocol_requests':4})


if __name__=='__main__':main()
