"""Durable call outcomes and bounded system retries; importing never launches work."""
from datetime import datetime,timedelta,timezone
import json
import os
from pathlib import Path
import re
import threading
import time
from zoneinfo import ZoneInfo
from .gate import gate_handoff

UTC=timezone.utc
LOCAL=ZoneInfo('Asia/Calcutta')
FINAL={'accepted','gate_rejected','timed_out','unclassified_failure'}


def stamp(dt):return dt.astimezone(UTC).isoformat().replace('+00:00','Z')


def write_new(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())


def replace_state(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)


def error_text(record):
    strings=[str(record.get('error') or ''),str(record.get('stderr') or '')]
    for event in record.get('events',[]):
        if event.get('type')=='error':strings.append(str(event.get('message') or ''))
        if event.get('type')=='turn.failed':strings.append(str(event.get('error') or ''))
    return '\n'.join(strings)


def classify(record,patterns):
    text=error_text(record)
    if record.get('timed_out') is True:return 'timed_out',[]
    if record.get('exit_code')==0:
        _,status=gate_handoff(record.get('answer'),{'public_refs':['A','B']})
        return ('accepted' if status=='accepted' else 'gate_rejected'),[]
    matches=[p['id'] for p in patterns['patterns'] if re.search(p['regex'],text,re.I)]
    if record.get('exit_code') not in (None,0) and record.get('answer') is None and matches:
        return 'system_issue',matches
    return 'unclassified_failure',[]


def reset_time(text,now):
    """Parse explicit ISO or time-of-day resets; otherwise use 30 minutes."""
    raw=text;now=now.astimezone(UTC)
    iso=re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})',text)
    if iso:
        dt=datetime.fromisoformat(iso.group().replace('Z','+00:00'))
        return max(dt,now),{'raw_text':raw,'method':'explicit ISO timestamp','parsed_reset_utc':stamp(dt)}
    match=re.search(r'(?:try again|reset(?:s)?|available again).*?(?:at\s+)(\d{1,2}):(\d{2})(?:\s*(AM|PM))?(?:\s+(UTC|GMT|IST|Asia/Calcutta|Asia/Kolkata|[A-Z]{2,5}))?',text,re.I)
    if match:
        hour,minute=int(match[1]),int(match[2]);ampm=(match[3] or '').upper();zone=match[4]
        if minute<60 and ((ampm and 1<=hour<=12) or (not ampm and 0<=hour<24)):
            zones={'UTC':UTC,'GMT':UTC,'IST':LOCAL,'ASIA/CALCUTTA':LOCAL,'ASIA/KOLKATA':LOCAL}
            tz=LOCAL if not zone else zones.get(zone.upper())
            if tz is not None:
                if ampm:hour=hour%12+(12 if ampm=='PM' else 0)
                dt=now.astimezone(tz).replace(hour=hour,minute=minute,second=0,microsecond=0)
                if dt<=now.astimezone(tz):dt+=timedelta(days=1)
                return dt.astimezone(UTC),{'raw_text':raw,'method':'next future local time-of-day' if not zone else 'next future named time-of-day','timezone':str(tz),'parsed_reset_utc':stamp(dt)}
    dt=now+timedelta(minutes=30)
    return dt,{'raw_text':raw,'method':'no unambiguous supported reset; 30-minute fallback','parsed_reset_utc':None,'retry_at_utc':stamp(dt)}


class Clock:
    def now(self):return datetime.now(UTC)
    def sleep(self,seconds):time.sleep(seconds)


class Control:
    """One shared control per backend arm; workers publish pauses before returning."""
    def __init__(self,folder,cutoff,timeout=180,clock=None):
        self.folder=Path(folder);self.clock=clock or Clock();self.cutoff=cutoff.astimezone(UTC)
        self.latest_launch=self.cutoff-timedelta(seconds=timeout)
        self.lock=threading.RLock();self.pause_until=None;self.blocked=None
        self.folder.mkdir(parents=True,exist_ok=True)
        path=self.folder/'control.json'
        if path.exists():
            old=json.loads(path.read_text());self.blocked=old.get('blocked')
            if old.get('pause_until'):self.pause_until=datetime.fromisoformat(old['pause_until'].replace('Z','+00:00'))
    def persist(self):
        replace_state(self.folder/'control.json',{'blocked':self.blocked,'pause_until':stamp(self.pause_until) if self.pause_until else None})
    def event(self,event):
        path=self.folder/'pauses.json'
        entries=json.loads(path.read_text()) if path.exists() else []
        entries.append(event);replace_state(path,entries)
    def pause(self,text,call):
        with self.lock:
            until,details=reset_time(text,self.clock.now())
            self.pause_until=max(until,self.pause_until) if self.pause_until else until
            self.event({'event':'system_issue_pause','at_utc':stamp(self.clock.now()),'call':call,'resume_at_utc':stamp(self.pause_until),**details});self.persist()
    def stop(self,reason):
        with self.lock:
            self.blocked=reason;self.event({'event':'arm_stopped','reason':reason,'at_utc':stamp(self.clock.now())});self.persist()
    def before_launch(self):
        while True:
            with self.lock:
                if self.blocked:return 'arm_stopped'
                now=self.clock.now()
                if now>=self.latest_launch:return 'stopped_by_cutoff'
                if not self.pause_until:return None
                if now>=self.pause_until:
                    self.pause_until=None;self.event({'event':'resume','at_utc':stamp(now)});self.persist();return None
                seconds=min(30,(self.pause_until-now).total_seconds(),(self.latest_launch-now).total_seconds())
            self.clock.sleep(max(0,seconds))


class AttemptRunner:
    def __init__(self,folder,patterns,control,execute):
        self.folder=Path(folder);self.patterns=patterns;self.control=control;self.execute=execute
    def run(self,name,prompt):
        if Path(name).name!=name:raise ValueError('invalid call name')
        import hashlib
        digest=hashlib.sha256(prompt.encode()).hexdigest()
        final=self.folder/'traces'/f'{name}.json'
        if final.exists():
            row=json.loads(final.read_text())
            if row['prompt_sha256']!=digest:raise ValueError('saved final prompt mismatch')
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
                path=self.folder/'stopped'/f'{name}.json'
                row={'call':name,'administrative_status':stop,'at_utc':stamp(self.control.clock.now()),'attempts':n}
                if not path.exists():write_new(path,row)
                return row
            n+=1
            write_new(call/f'attempt{n}.json',{'attempt':n,'prompt_sha256':digest,'at_utc':stamp(self.control.clock.now())})
            row=self.execute(name,prompt,self.control)
            # execute checks cutoff again after preflight; an unlaunched call is administrative.
            if row.get('administrative_status'):
                write_new(self.folder/'stopped'/f'{name}.json',dict(row,prompt_sha256=digest))
                return row
            kind,matches=classify(row,self.patterns)
            row.update(name=name,attempt=n,prompt_sha256=digest,classification=kind,system_issue_matches=matches)
            if kind=='system_issue':
                write_new(self.folder/'system_issue'/f'{name}-attempt{n}.json',row)
                self.control.pause(error_text(row),name)
                continue
            write_new(final,row)
            return row
