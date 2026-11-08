"""Pinned macOS session cleanup, including detached native-sandbox processes.

Identify the session by its kernel-checked permissions on three existing
canaries, rather than parent PID or inherited environment. Do not signal a PID
unless its permissions still match immediately before the signal. Missing or
unusable platform APIs cause refusal, not a weaker cleanup claim.
"""
import ctypes
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import time
import uuid


class SessionProcesses:
    def __init__(self,session,timeout=2):
        if sys.platform!='darwin':raise RuntimeError('macOS session cleanup required')
        self.timeout=timeout;self.own=session.temporary/('.stop-'+uuid.uuid4().hex)
        self.private=session.root/('.controller-stop-'+uuid.uuid4().hex)
        self.config=session.config/'config.toml';self.value=uuid.uuid4().hex
        for p in [self.own,self.private]:
            with p.open('x') as stream:stream.write(self.value)
        self.library=ctypes.CDLL('/usr/lib/libsandbox.1.dylib',use_errno=True)
        self.check=self.library.sandbox_check
        # Fixed arguments must be declared for Apple ARM64 variadic ABI.
        self.check.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int]
        self.check.restype=ctypes.c_int
        self.flags=1|ctypes.c_int.in_dll(self.library,'SANDBOX_CHECK_NO_REPORT').value
        if self.signature(os.getpid())!=(0,0,0):
            raise RuntimeError('controller cannot independently check cleanup canaries')

    def signature(self,pid):
        result=[]
        for operation,path in [('file-write-data',self.own),('file-read-data',self.private),('file-read-data',self.config)]:
            ctypes.set_errno(0)
            value=self.check(pid,operation.encode(),self.flags,ctypes.c_char_p(os.fsencode(path)))
            if value not in (0,1):raise RuntimeError('sandbox query failed; cleanup unverified')
            result.append(value)
        return tuple(result)

    def validate(self):
        for p in [self.own,self.private]:
            if not stat.S_ISREG(p.lstat().st_mode) or p.read_text()!=self.value:
                raise RuntimeError('cleanup canary changed; workspace must be held for review')

    def candidates(self):
        self.validate()
        rows=subprocess.check_output(['/bin/ps','-axo','uid=,pid='],text=True,timeout=self.timeout)
        result=[]
        for line in rows.splitlines():
            uid,pid=map(int,line.split())
            if uid!=os.getuid() or pid==os.getpid():continue
            try:
                if self.signature(pid)==(0,1,1):result.append(pid)
            except ProcessLookupError:continue
        return result

    def finish(self):
        deadline=time.monotonic()+self.timeout;killed=set()
        # Stop matching processes before killing them, preventing new forks
        # from already identified parents. Rescan for reparented descendants.
        while True:
            pids=self.candidates()
            if not pids:return {'verified':True,'killed_pids':sorted(killed),
                'method':'native sandbox permission signature on session canaries'}
            for sig in [signal.SIGSTOP,signal.SIGKILL]:
                for pid in pids:
                    try:
                        if self.signature(pid)==(0,1,1):os.kill(pid,sig);killed.add(pid)
                    except ProcessLookupError:pass
            if time.monotonic()>=deadline:raise RuntimeError('session processes still present; cleanup unverified')
            time.sleep(.02)
