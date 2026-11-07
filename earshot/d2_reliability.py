"""D2 role validation with D1 durable retry/pause behavior, in a new module."""
from pathlib import Path
import json
import re
from .reliability import classify, write_new, stamp, error_text
from .score import action
import jsonschema

SCHEMA = json.loads((Path(__file__).parent / 'answer.schema.json').read_text())


def classify_role(row, patterns, role):
    if role != 'receiver' or row.get('exit_code') != 0 or row.get('provider_error') or row.get('timed_out') or row.get('configuration_fault'):
        return classify(row, patterns)
    try:
        jsonschema.validate(row.get('answer'), SCHEMA)
    except jsonschema.ValidationError:
        return 'gate_rejected', []
    return ('accepted' if action(row) is not None else 'gate_rejected'), []


class AttemptRunner:
    def __init__(self,folder,patterns,control,execute,reserve_at_launch=False, role="relay"):
        self.role=role;self.folder=Path(folder);self.patterns=patterns;self.control=control;self.execute=execute;self.reserve_at_launch=reserve_at_launch
    def run(self,name,prompt):
        if Path(name).name!=name:raise ValueError('invalid call name')
        import hashlib
        digest=hashlib.sha256(prompt.encode()).hexdigest()
        final=self.folder/'traces'/f'{name}.json'
        if final.exists():
            row=json.loads(final.read_text())
            if row['prompt_sha256']!=digest:raise ValueError('saved final prompt mismatch')
            return row
        stopped=self.folder/'stopped'/f'{name}.json'
        if stopped.exists():
            row=json.loads(stopped.read_text())
            if row.get('prompt_sha256',digest)!=digest:raise ValueError('saved stopped prompt mismatch')
            return row
        call=self.folder/'attempt_state'/name;call.mkdir(parents=True,exist_ok=True)
        pending=sorted(call.glob('attempt*.json'))
        n=len(pending)
        for path in pending:
            state=json.loads(path.read_text());index=state['attempt']
            if state['prompt_sha256']!=digest:raise ValueError('saved attempt prompt mismatch')
            if not (self.folder/'system_issue'/f'{name}-attempt{index}.json').exists():
                self.control.stop('interrupted attempt without durable outcome: '+name)
                return {'call':name,'administrative_status':'arm_stopped'}
        while True:
            if n>=5:
                self.control.stop('five system issues exhausted call: '+name)
                return {'call':name,'administrative_status':'system_issue_not_run','attempts':n}
            stop=self.control.before_launch()
            if stop:
                if stop.startswith('paused_'):return {'call':name,'administrative_status':stop,'attempts':n}
                path=self.folder/'stopped'/f'{name}.json'
                row={'call':name,'administrative_status':stop,'at_utc':stamp(self.control.clock.now()),'attempts':n,'prompt_sha256':digest}
                if not path.exists():write_new(path,row)
                return row
            n+=1
            def reserve():write_new(call/f'attempt{n}.json',{'attempt':n,'prompt_sha256':digest,'at_utc':stamp(self.control.clock.now())})
            if self.reserve_at_launch:row=self.execute(name,prompt,self.control,reserve)
            else:
                reserve();row=self.execute(name,prompt,self.control)
            # execute checks cutoff again after preflight; an unlaunched call is administrative.
            if row.get('administrative_status'):
                if row['administrative_status'].startswith('paused_'):return dict(row,attempts=n-1)
                write_new(self.folder/'stopped'/f'{name}.json',dict(row,prompt_sha256=digest))
                return row
            with self.control.lock:
                kind,matches=classify_role(row,self.patterns,self.role)
                row.update(name=name,attempt=n,prompt_sha256=digest,classification=kind,system_issue_matches=matches)
                if kind=='configuration_fault':
                    write_new(self.folder/'configuration_fault'/f'{name}-attempt{n}.json',row)
                    self.control.stop('configuration fault: '+name)
                    return {'call':name,'administrative_status':'configuration_fault','attempts':n}
                if kind=='system_issue':
                    write_new(self.folder/'system_issue'/f'{name}-attempt{n}.json',row)
                    manual=set(matches)&set(self.patterns.get('manual_pause_matches',[]))
                    if manual or row.get('usage_pause_reason'):
                        reason=row.get('usage_pause_reason') or ('unclassified no answer' if 'unclassified_no_answer' in manual else 'usage limit')
                        self.control.manual_pause(error_text(row),name,reason,{'quota_windows':row.get('quota_windows',{})})
                        return {'call':name,'administrative_status':self.control.before_launch(),'attempts':n}
                    self.control.pause(error_text(row),name)
                    continue
                # Even a failed process with an answer is final, but a limit still pauses the arm.
                limits=[p['id'] for p in self.patterns['patterns'] if p['id'] in self.patterns.get('manual_pause_matches',[]) and re.search(p['regex'],error_text(row),re.I)]
                write_new(final,row)
                if row.get('usage_pause_reason') or (row.get('exit_code')!=0 and limits):
                    self.control.manual_pause(error_text(row),name,row.get('usage_pause_reason') or 'usage limit',{'quota_windows':row.get('quota_windows',{})})
                return row
