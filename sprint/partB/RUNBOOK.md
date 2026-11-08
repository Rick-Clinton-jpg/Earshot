# Part B runbook — REGISTERED source, no execution authorized

Study timeout: **180 seconds**. Backend: setup v2, Codex gpt-6.1-sol low.
Rick approved the source sealing/publication step after review. The registration
is REGISTERED; its source seal must be published and verified before any later
execution instruction. Cutoff: **9 November 2026, 05:00 IST / 8 November,
23:30 UTC**. No study call is authorized by this runbook. The live commands below
are for a separately authorized run, not instructions to launch now.

Use `/Users/gho5t/Documents/Codex/2026-11-04/i/work/Earshot_foundation`
as the repository root and
`/Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3`
for the trusted controller. Always set `PYTHONDONTWRITEBYTECODE=1`; pytest uses
`-p no:cacheprovider`. New checks/simulations belong in fresh inspected folders
outside the repository. No D1/D2 or presprint file may be edited.

## Before sealing

Review `PART_B_REGISTRATION.md`, `PART_B_registration.json` and
`SCRATCH_POLICY.md`, including the recorded cutoff, two workers, revised
scratch allowance and approved labels. Verify the correct-fix-plus-`repro.py`
fixture and all retained exclusions. Keep agent-facing prompts, instruction
wording, bugs, conditions and allocation unchanged. Practice selected only the
180-second timeout; the approved pytest-mock setup repair is separately recorded.

Run all tests, including `tests` and `sprint/partD/D2/sim/test_sim_c.py`, with
`EARSHOT_TEST_WORKSPACE` set to the existing D1 isolated workspace. Check every
proposed seal file exists; no runtime evidence is included. Verify internal
import/data coverage, baseline/bug bindings, prompt bytes and the full schedule.
Inspect fresh session/home and native boundary fixtures before a live run.

Source publication approval is recorded in the registration. Create
`sprint/partB/SEAL1.json` with exactly the sorted `seal_1_files` as
`{"files":[{"path":"...","sha256":"..."},...]}`. Write the SHA-256 of its
actual bytes plus one newline to `SEAL1.sha256`. Commit source/registration/seal
as one source-seal commit, push without force, and verify published HEAD equals
that commit. Do not start study calls as part of source publication.

## Source guard (future, after publication)

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3 -m earshot.partb_integrity verify-source --repo /Users/gho5t/Documents/Codex/2026-11-04/i/work/Earshot_foundation --branch main --registration sprint/partB/PART_B_registration.json --seal sprint/partB/SEAL1.json --seal-digest sprint/partB/SEAL1.sha256
```

All relative command paths below resolve from the repository root. Live source
checks require no local commit after the seal and exact HEAD/origin agreement.
They are repeated before launches, including call/prompt and backend binding.

## Study launch (requires separate explicit authorization)

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3 -m earshot.partb_study --repo /Users/gho5t/Documents/Codex/2026-11-04/i/work/Earshot_foundation --branch main --registration sprint/partB/PART_B_registration.json --seal sprint/partB/SEAL1.json --seal-digest sprint/partB/SEAL1.sha256 --run-dir sprint/partB/codex --auth-file /Users/gho5t/.codex/auth.json --live
```

Do not commit/push or modify source while the worker runs. Do not restart it
automatically. It holds a worker lease, records actual launch order, completes
one frozen block at a time, pauses on system/evaluation faults and drains active
calls. Raw records use exclusive writes. Only mutable control/status files are
replaced. Credentials live only in private temporary homes and are removed.

Resume only on Rick's explicit instruction, with the same command plus
`--resume-rick "Rick's actual resume instruction and date"`. Never fabricate
authorization. A partial/unverified or in-flight attempt requires reconciliation;
it cannot be silently relaunched. Completed model artifacts are reused for
unavailable-evaluation recovery, with new evaluation records and no model rerun.

If the worker is paused and the absolute cutoff has passed, the same source
guarded command can use `--finalize-cutoff` instead of `--live`, with no auth file.
It launches no model. It refuses an active worker or unreconciled in-flight
attempt, marks never-launched cells stopped by cutoff, and preserves earlier
system-issue classifications with expired-retry notices.

## Ledger before scoring

After terminal status and shutdown, build the ledger outside the run folder:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3 -m earshot.partb_integrity build-ledger --repo /Users/gho5t/Documents/Codex/2026-11-04/i/work/Earshot_foundation --branch main --registration sprint/partB/PART_B_registration.json --seal sprint/partB/SEAL1.json --seal-digest sprint/partB/SEAL1.sha256 --run-dir sprint/partB/codex --ledger sprint/partB/codex_LEDGER.json --ledger-digest sprint/partB/codex_LEDGER.sha256
```

Ledger covers every runtime file except the two empty lease/lock filenames;
it includes mutable control/status at their terminal bytes, all attempts,
artifacts, setup receipts, evaluation trees/logs and faults. Filesystem symlinks
or credentials cause refusal. Simulations cannot be ledgered as study data.
Publish runtime and ledger together only when authorized, then run the same
utility with `verify-ledger`. Never force-push or alter a saved attempt.

## Score and cross-check

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3 -m earshot.partb_score --repo /Users/gho5t/Documents/Codex/2026-11-04/i/work/Earshot_foundation --branch main --registration sprint/partB/PART_B_registration.json --seal sprint/partB/SEAL1.json --seal-digest sprint/partB/SEAL1.sha256 --run-dir sprint/partB/codex --ledger sprint/partB/codex_LEDGER.json --ledger-digest sprint/partB/codex_LEDGER.sha256 --output /tmp/earshot_partb_scored_NEW
```

Choose a new empty output path every time. Scorer requires the published final
ledger, rechecks the original source seal, recomputes artifact metrics and
reparses raw test XML/process logs. It writes JSON and a report from that JSON.
Cross-check computation on a second machine from the same sealed inputs before
publishing results. Preserve each output separately and report all differences;
never change a number to match. No inferential tests or intervals are planned.
