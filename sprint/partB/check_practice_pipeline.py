"""End-to-end practice wiring, scripted loopback only; no live entry point."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cli',type=Path,required=True)
    parser.add_argument('--python',type=Path,required=True)
    args=parser.parse_args()
    repo=Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo))
    from earshot import partb as b
    from earshot.partb_cli import opaque_session,initialize_runtime,CLI_VERSION
    from earshot.partb_protocol import LocalResponses,message,javascript,run_fixture,case_outputs
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    b.write_json(output/'PREFLIGHT.json',{'initial_folder_empty':not any(output.iterdir()),
       'mode':'SCRIPTED_LOCAL_ONLY','hosted_model_calls':0,'auth_copied':False})
    assert subprocess.check_output([str(args.cli),'--version'],text=True).strip()==CLI_VERSION
    private=repo.parent/'partB_preparation_01/tree'
    pristine=b.snapshot(private)
    qualification=repo/'sprint/partB/qualification/preparation-01'
    assert {p:r['sha256'] for p,r in pristine.items()}==json.loads((qualification/'SOURCE_MANIFEST.json').read_text())
    practice=repo/'sprint/partB/qualification/practice-02'
    for path,sha in json.loads((practice/'MANIFEST.json').read_text())['files'].items():
        assert b.digest((practice/path).read_bytes())==sha,path
    task=json.loads((practice/'QUALIFICATION.json').read_text())
    candidates=json.loads((repo/'sprint/partB/tasks_draft.json').read_text())['candidate_files']
    expected=task['repeated_runs']['clean-1']['case_ids']
    dependencies=subprocess.check_output([str(args.python),'-B','-c',
        'import sysconfig;print(sysconfig.get_path("purelib"))'],text=True).strip()
    results={}
    for variant in ['no_edit','reference','new_file','root_repro']:
        directory=output/variant;directory.mkdir()
        session=opaque_session()
        assert not list(session.root.iterdir())
        source=b.materialize(pristine,directory/'controller-source')
        subprocess.run(['git','apply',str(practice/'bug.patch')],cwd=source,check=True)
        baseline=b.make_workspace(pristine,b.snapshot(source),session.workspace)
        initialize_runtime(session)
        baseline_metadata=b.excluded_inventory(session.workspace)
        b.write_json(directory/'SESSION_PREFLIGHT.json',{'root':str(session.root),
           'root_initially_empty':True,'CODEX_HOME_initially_empty':not any(session.config.iterdir()),
           'instruction_files_in_workspace':[str(p.relative_to(session.workspace)) for p in session.workspace.rglob('*')
             if p.is_file() and p.name.lower() in {'agents.md','agents.override.md','claude.md','gemini.md'}],
           'git_commits':subprocess.check_output(['git','rev-list','--count','HEAD'],cwd=session.workspace,text=True).strip(),
           'git_remotes':subprocess.check_output(['git','remote'],cwd=session.workspace,text=True).splitlines()})
        assert not json.loads((directory/'SESSION_PREFLIGHT.json').read_text())['instruction_files_in_workspace']
        call={'condition':'C-in' if variant=='reference' else 'H-in',
              'receiver':'coalition' if variant=='reference' else 'honest','incoming_pair':'AC'}
        prompt=b.render_prompt(task,call,candidates)
        (directory/'prompt.txt').write_text(prompt)
        # Known repair is injected by the controller into a scripted fixture.
        # It must never be described as a discovered/model-generated repair.
        patch=f'*** Begin Patch\n*** Update File: {session.workspace}/radon/metrics.py\n@@\n-    comments_lines = raw.comments\n+    comments_lines = raw.comments + (raw.multi if count_multi else 0)\n'
        if variant=='new_file':patch+=f'*** Add File: {session.workspace}/radon/fixture_added.py\n+VALUE = 1\n'
        if variant=='root_repro':patch+=f'*** Add File: {session.workspace}/repro.py\n+from radon.metrics import mi_parameters\n+print(mi_parameters("pass"))\n'
        patch+='*** End Patch'
        command=shlex.join(['/usr/bin/env','PYTHONPATH='+dependencies,str(args.python.resolve()),'-sB',
           '-m','pytest','-q','-p','no:cacheprovider','-p','pytest_mock','--strict-markers'])
        code=''
        if variant!='no_edit':code+='text({case:"edit",result:await tools.apply_patch('+json.dumps(patch)+')});\n'
        code+='text({case:"agent_tests",result:await tools.exec_command('+json.dumps({
            'cmd':command,'workdir':str(session.workspace),'login':False,'max_output_tokens':1200,'yield_time_ms':10000})+')});'
        with LocalResponses(directory/'requests',lambda body,n:javascript(code,'pipeline') if n==1 else message('Scripted fixture finished.')) as server:
            run=run_fixture(session,args.cli,args.python,server,directory/'cli',prompt,timeout=90)
        assert run.returncode==0 and len(server.requests)==2
        tool_results=case_outputs(server.requests[-1]);b.write_json(directory/'TOOL_RESULTS.json',tool_results)
        tests=tool_results['agent_tests']['result']
        assert tests.get('exit_code')==(1 if variant=='no_edit' else 0),tests
        final=b.snapshot(session.workspace)
        b.write_json(directory/'artifact.json',{'status':'SCRIPTED_CLI_FIXTURE_NOT_MODEL_RESULT',
           'baseline_sha256':b.digest(json.dumps(baseline,sort_keys=True).encode()),'files':final,
           'excluded_metadata_inventory':b.excluded_inventory(session.workspace)})
        result=b.evaluate(baseline,pristine,final,task,args.python,directory/'evaluation',expected,task['diagnostic_node_ids'],
            metadata={'baseline':baseline_metadata,'final':b.excluded_inventory(session.workspace)})
        assert result['evaluation_available']
        assert result['test_verified_admissible_repair']==(variant in {'reference','root_repro'}),variant
        assert result['tests_pass']==(variant!='no_edit'),variant
        assert result['reference_reversal_only']==(variant in {'reference','root_repro'}),variant
        if variant=='new_file':
            assert not result['admissible'] and any(p.get('change_type')=='created' for p in result['policy_violations'])
        if variant=='root_repro':
            assert result['admissible'] and result['scratch_file_count']==1
            assert result['scratch_files'][0]['path']=='repro.py'
            assert 'repro.py' not in result['changed_paths']
        results[variant]={key:result[key] for key in ['evaluation_available','admissible','tests_pass',
            'test_verified_admissible_repair','reference_reversal_only','target_file_exact_restoration']}
        results[variant]['scratch_files']=result['scratch_files']
        results[variant]['agent_tool_test_exit_code']=tests['exit_code']
        print(variant,results[variant],flush=True)
    assert b.snapshot(private)==pristine
    b.write_json(output/'CHECKS.json',{'status':'SCRIPTED_PRACTICE_PIPELINE_PASSED_NOT_EMPIRICAL_RESULTS',
       'hosted_model_calls':0,'practice_calls':0,'study_calls':0,'CLI_exec_invocations':len(results),
       'local_protocol_requests':2*len(results),'cases':results,'private_archive_unchanged':True,
       'live_auth_or_provider_validated':False,'practice_target':task['id']})
    b.write_json(output/'MANIFEST.json',{'status':'LOCAL_FIXTURE_INVENTORY_NOT_A_SEAL','files':{
       str(p.relative_to(output)):b.digest(p.read_bytes()) for p in sorted(output.rglob('*')) if p.is_file()}})


if __name__=='__main__':main()
