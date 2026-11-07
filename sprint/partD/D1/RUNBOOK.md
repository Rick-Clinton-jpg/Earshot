# Draft D1 operation — NOT SEALED, DO NOT RUN MODELS YET

Inference and intervals remain `PENDING_REVIEW`; cutoff remains `PENDING_RICK`; status is DRAFT. Both runners and scoring refuse these fields. There were no model calls during this build. The three Claude environment checks imported from `claude-recon` are existing fixtures, not D1 observations. Their source is pinned in `tests/fixtures/claude_recon/PROVENANCE.json`.

The Claude configuration now specifies the command verified by those fixtures, inline compact schema JSON, environment `DISABLE_AUTOUPDATER=1`, model `claude-sonnet-5-5`, effort low and version 2.1.319. The CLI's raw `2.1.319 (Claude Code)` is normalized only for its version comparison. Each Claude call must match its init configuration and result model/subagent evidence. The Codex version is probed before every model call and stored in each trace. This does not establish that Claude is installed in every future execution environment.

Before a future seal, review and implement inference with four-file clustering and any directional output rule, choose the cutoff, and review the exact 46-file list in `SEAL_COVERAGE.json`. Filling placeholders alone does not implement inference. No actual seal or arm ledger has been created.

## Task workspace and environment

Use an external clean clone at DogWhistle commit `1a4b471b3cfb4ed6d5def7c61356c5230af8c082`, with the verified four reference files. Its parent must contain only the workspace. This is an enforced setup requirement, not a post-hoc outcome exclusion. The isolated local workspace prepared without model calls is `/Users/gho5t/Documents/Codex/2026-11-04/i/work/earshot_d1_isolated/workspace`; rebuild the same pinned layout on another machine. The former workspace remains unchanged but its parent contains siblings and no longer qualifies for D1 launches.

Claude's fixture-derived project key replaces non-alphanumeric characters in the absolute workspace path with hyphens. Before every Claude model call, check that key under the effective `CLAUDE_CONFIG_DIR/projects/` or `~/.claude/projects/`. Only UUID session directories and their `tool-results/` contents are allowed. Memory, instruction, transcript or other files, non-session directories and symlinks stop the arm. Full init events, including built-in plugins, are retained; these checks do not establish absence of all ambient instructions.

The two isolation requests in the saved Claude check were denied. This is evidence about those requests, not a universal security proof. Codex's read-only sandbox does not fence reads to the workspace. All explicit outside-path requests and adapter exposure observations are report-only and never exclude a call. See the registration for the exact detection rule and the retrospective 114-call baseline. Large Claude tool outputs may be previews; persisted storage paths are recorded separately from read requests and denials.

## Future sealed worker

A future Seal 1 JSON has a `files` array `{path, sha256}` relative to Earshot. A separate digest file contains the SHA-256 of the seal JSON bytes. Commit and push both in the seal commit. HEAD must remain exactly that commit and equal the specified remote branch throughout either arm's calls. Do not push ledger/report changes to that branch while either arm is active. Runtime snapshots use separate branches.

After prerequisites are complete, an operator can use this documented recipe. It was not executed:

```sh
repo=/absolute/path/to/sealed-Earshot
workspace=/absolute/path/to/isolated-parent/workspace
python=/absolute/path/to/venv/bin/python
arm=codex
cd "$repo"
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

Use a separate process and arm directory for Claude. Each arm has an exclusive worker lock and independent pause state; their accounts differ. The final cutoff and pause check share the same lock with model-process launch, preventing a worker from launching after another worker has set a pause.

## Outcomes and pauses

Accepted answers, gate rejections and timeouts are final and are never re-attempted. Non-zero exits with answers remain final and unaccepted. Claude provider errors are system issues even at exit zero; their structured payload is not treated as a successful answer. Conflicting configuration evidence is saved under `configuration_fault/`, stops the arm and never becomes an agent outcome. An incomplete error stream without an init/result does not silently become a gate rejection. Successful configuration-valid results lacking a valid structured answer remain gate rejections.

A usage/rate-limit error or unknown no-answer error saves an attempt and manually pauses. After each Claude call, either quota utilization at or above 0.90 also manually pauses, with distinct reason `usage at 90%`, retaining that call's outcome and both available reset times. Quota decisions use values, not key-name text matching. Missing readings are unavailable; there is no invented quota estimate. Codex has no percentage reader.

Workers launch no new calls after a pause, drain in-flight processes and save their outcomes. Pause records include the triggering call, time, finished and left call lists, and raw/parsed reset information. Time-based resets do not authorize resumption of a manual pause. A plain restart stays paused. Only after Rick authorizes it, add `--resume-rick` to the same invocation. Final traces, prompt hashes and counters survive. Other recognized system issues retain the bounded reset-time/30-minute retry rule; five attempts stop the arm. Never reset counters or delete outcomes to bypass a refusal.

Check cutoff after setup/version/publication work and immediately before model-process creation. Do not launch at or after cutoff minus 180 seconds. Timeout is 180 seconds; OS scheduling and process cleanup may add wall time. Await and reap all launched processes before analysis. An exited paused worker cannot write at a future cutoff: its next resume, or the same invocation with `--finalize-cutoff`, records remaining scheduled calls without launching models. Unused reserves are excluded. Never extend the cutoff.

## Runtime checkpoints and restore

At orderly pause, finish or cutoff, after draining workers and flushing output, the runner snapshots every regular file in its arm folder. It creates a separate Git worktree on `d1-codex-runtime` or `d1-claude-runtime`, with a manifest binding the snapshot to its backend, seal commit, seal digest and registration digest. The manifest records each path, byte count and SHA-256. Earlier immutable records may neither disappear nor change. Mutable control/log files can advance. Symlinks are refused. Snapshot commits are pushed without force and the published branch head is verified before success is reported. A rejected push stops; the local run folder and checkpoint worktree are preserved. The sealed run checkout's HEAD never changes.

The snapshot covers file bytes at capture time; the worker log can subsequently receive the checkpoint-publication or exit message. Those diagnostic additions do not change saved outcomes. Checkpoints at orderly exits do not guarantee recovery of a call lost during a sudden container wipe or before a successful push. If any call's completion is uncertain, stop for reconciliation rather than silently sampling it again.

For restore, make a fresh clone and detach at the original seal commit. Rebuild/verify the task workspace. In that clone, use the existing original seal files and an absent arm destination:

```sh
"$python" -m earshot.runtime_checkpoint restore \
  --repo "$repo" --branch main --arm "$arm" \
  --registration "$repo/sprint/partD/D1/D1_registration.json" \
  --seal "$repo/sprint/partD/D1/SEAL1.json" \
  --seal-digest "$repo/sprint/partD/D1/SEAL1.sha256" \
  --run-dir "$repo/sprint/partD/D1/$arm"
```

Restore verifies every hash, exact saved file inventory and seal/backend binding before copying into the absent destination. It never overwrites earlier local traces. Only resume with `--resume-rick` on Rick's instruction; final answers are reused, and system-issue retries retain the earlier attempt count. Restoring a completed or cutoff run does not authorize more calls.

## Final ledgers and scoring

After both arms stop, create each ledger over the exact JSON runtime inventory: `traces/`, `system_issue/`, `configuration_fault/`, `attempt_state/`, `stopped/`, plus existing `plan.json`, `pauses.json` and `control.json`. Include `seal_sha256` and the `{path, sha256}` list relative to the arm directory. Commit/push the runtime files, ledger and separate digest. The checkpoint manifest covers the entire captured folder; the scoring ledger intentionally covers the result/control JSON inventory, as before. Diagnostic `worker.lock` and `worker.log` are outside that ledger.

The scorer accepts explicit repository, branch, registration, original seal/digest, ledger/digest and arm-directory arguments. It checks all hashes and exact ledger inventory and reports configuration faults and exposure observations separately. `cross_arm` pairs selected valid task IDs and reports overlap and point differences only. No inferential method or interval is implemented pending review.
