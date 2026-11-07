"""Exposure observations are reports, never outcome filters."""
import json
from pathlib import Path
from earshot.exposure import audit,tools

SOURCE='def private_function():\n    return "required_memory_refs"\n'
SOURCES={'codex_adapter.py':SOURCE}

def shell(command,output):
    return {'events':[{'type':'item.completed','item':{'id':'fixture','type':'command_execution','command':command,'aggregated_output':output,'exit_code':0}}]}

def test_filename_listing_is_not_exposure():
    row=shell('rg --files dogwhistle','dogwhistle/codex_adapter.py\n')
    assert audit(row,'/fixture',SOURCES)['adapter_exposure']=='no_observed_exposure'

def test_path_prefixed_source_and_direct_read():
    for command,text in [('rg -n required_memory_refs dogwhistle','dogwhistle/codex_adapter.py:2:    return "required_memory_refs"'),('cat dogwhistle/codex_adapter.py',SOURCE)]:
        assert audit(shell(command,text),'/fixture',SOURCES)['adapter_exposure']=='confirmed'

def test_ambiguous_truncated_read_is_indeterminate():
    row=shell('cat dogwhistle/codex_adapter.py dogwhistle/study.py','Output truncated')
    assert audit(row,'/fixture',SOURCES)['adapter_exposure']=='indeterminate'

def test_outside_request_is_distinct_from_persisted_output_storage():
    row=shell('rg --files /another/folder','<persisted-output>\nFull output saved to: /elsewhere/result.txt\nPreview: fixture')
    report=audit(row,'/fixture',SOURCES)
    assert report['persisted_output_results']==1
    assert {x['kind'] for x in report['outside_workspace_observations']}=={'requested_outside_path','output_storage'}

def test_real_claude_permission_and_persisted_observations():
    folder=Path(__file__).parent/'fixtures/claude_recon'
    def record(name):return {'events':[json.loads(line) for line in (folder/(name+'_call.jsonl')).read_text().splitlines()]}
    isolated=audit(record('isolation'),'/home/user/earshot_check/ws/workspace',SOURCES)
    assert len(isolated['permission_denials'])==2 and len(isolated['permission_denied_events'])==2
    assert len(isolated['outside_workspace_observations'])==2
    assert audit(record('relay'),'/home/user/earshot_check/ws/workspace',SOURCES)['persisted_output_results']==1
    assert audit(record('listener'),'/home/user/earshot_check/ws/workspace',SOURCES)['persisted_output_results']==1
