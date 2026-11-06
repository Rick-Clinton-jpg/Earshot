# Draft D1 operation — DO NOT RUN THIS STUDY YET

No model calls or study seals have been made. The commands below are documentation for later review, not actions performed during this build. `PENDING_REVIEW`, `PENDING_RECON`, `PENDING_RICK` and DRAFT status block both arms and scoring.

Before a future run, review inference with the four-file clustering, review the complete Claude invocation and parser using documentation/help, choose the cutoff, and seal the exact list in `SEAL_COVERAGE.json`. Filling placeholders alone does not implement inference: the present scorer intentionally computes point estimates only. Changes to inference or the protocol must be reviewed and implemented before sealing. Check the actual Claude model identifier and availability; this build makes no availability claim.

The future seal format is an object with a `files` array of `{path, sha256}` entries relative to the Earshot repository. Its separate digest file contains the SHA-256 of the seal JSON bytes. Both must be committed and pushed in the seal commit; every launch requires HEAD to remain exactly that pushed commit. Do not commit runtime data or change branches during an active run. The task workspace must be external, clean at the pinned DogWhistle commit and contain the four verified reference files. Candidate bytes are verified before each model call.

After those prerequisites, a later operator can start an independent shell worker, using actual absolute paths in these environment variables. This recipe was not executed:

```sh
repo=/absolute/path/to/Earshot
workspace=/absolute/path/to/pinned-task-workspace
python=/absolute/path/to/venv/bin/python
arm=codex
mkdir -p "$repo/sprint/partD/D1/$arm"
nohup "$python" -m earshot.d1v2 \
  --repo "$repo" --branch main --backend "$arm" \
  --registration "$repo/sprint/partD/D1/D1_registration.json" \
  --backend-config "$repo/sprint/partD/D1/${arm}_config.json" \
  --seal "$repo/sprint/partD/D1/SEAL1.json" \
  --seal-digest "$repo/sprint/partD/D1/SEAL1.sha256" \
  --workspace "$workspace" --run-dir "$repo/sprint/partD/D1/$arm" \
  > "$repo/sprint/partD/D1/$arm/worker.log" 2>&1 < /dev/null &
```

Run from the Earshot repository with the environment's package import path configured. Use a separate process and arm directory for Claude after its configuration is verified. Each arm has an exclusive OS worker lock. A shared usage account can cause both arms to hit limits; each process enforces its own arm pause when it observes the error. There is no claim of a single global pause bus across two separate processes/accounts.

A usage/rate-limit error or unknown no-answer error saves a system-issue attempt and sets durable manual pause state. The worker drains all model processes already in flight, saves their outcomes, adds finished/left call lists to the triggering pause record, prints `paused: usage limit` (or the unclassified-pause reason) and exits. A normal restart stays paused. Only after Rick's explicit instruction, add `--resume-rick` to the same invocation. Final traces are reused; retry counters and prompt hashes persist. Never remove a trace, reset a counter or clear state to get past a refusal. Five system issues or a crash intent lacking an outcome require reconciliation; the total attempt cap is not reset by resume.

Other recognized system issues retain the registered reset-time/30-minute automatic retry rule. Pauses wait in bounded increments and never pass the last-launch deadline. There is no percentage-quota reader and no 10% pause.

The latest launch is strictly before cutoff minus 180 seconds, checked immediately before process creation after setup/version/publication checks. Timeout is 180 seconds. Process-tree termination and OS scheduling can add wall-clock cleanup time; analysis must wait for all workers and children to finish. No promise of exact OS cleanup timing is made.

An exited worker cannot write files at a future cutoff. At or after the last-launch deadline, invoke the same command with `--finalize-cutoff` (no resume permission is needed for recording administrative stops). A resume command at that time also finalizes cutoff records without starting models. This records every remaining scheduled primary or used-reserve call as `stopped_by_cutoff`; unused reserves are excluded. It is necessary to run this administrative step before sealing an interrupted arm's ledger. Do not move the cutoff.

Before scoring, construct each arm ledger from the exact JSON files in `traces/`, `system_issue/`, `attempt_state/`, `stopped/` and the existing `plan.json`, `pauses.json`, `control.json`. Include `seal_sha256` pointing to Seal 1 and a `files` list `{path, sha256}` relative to that arm directory. Commit/push the runtime files, ledger and its separate digest. Scoring checks the published ledger and exact inventory, including edited/extra traces. `worker.lock` and diagnostic `worker.log` are not result records and are outside the ledger inventory. No ledger has been created for this draft.

The scorer's CLI accepts explicit repository, branch, registration, original seal/digest, ledger/digest and arm directory paths. `cross_arm` pairs selected valid task IDs and reports overlap and point differences only. Undefined quantities remain null; it does not fabricate unavailable comparisons.
