# D1 draft build report — no model calls, no seal

Historical report for commit 84a1f6a. Addendum 2 changes and current checks are reported in `ADDENDUM2_REPORT.md`.

This builds a reviewable draft of the next D1. It does not produce experimental observations or establish a D1 result. Synthetic relay and CLI responses occur only in offline tests, not in study traces.

## Changes

- Shared durable call control handles accepted answers, gate rejections, final timeouts, final non-zero exits with answers, and separate system-issue attempts. Final answers are never retried. Attempt files use exclusive creation; interrupted intents block rather than silently repeat a possibly answered call.
- Both backend implementations manually pause on usage/rate limits and unknown no-answer errors. They drain in-flight processes, save their outcomes, record finished/left call lists and exit with a pause message. A plain restart stays paused. Explicit `--resume-rick` preserves counters and prompt hashes. The Codex detector includes the exact usage-limit message from the trial. Fake CLI tests exercise it. Claude messages and its real output method remain unverified.
- Other recognized system issues retain the bounded automatic retry rule. Five attempts stop the arm. Reset interpretation records raw text and UTC, using Asia/Calcutta when no zone is named. No account-percentage field was established from saved streams, pinned CLI help and documentation, so no percentage reader or 10% pause was invented. See `USAGE_RECON.md`.
- New runner/scorer and publication/seal/ledger checks are separate from the frozen trial code. Tests use local bare Git remotes, fake clocks and fake subprocesses. Calls require a published seal commit and exact sealed bytes; scoring requires a published ledger and exact runtime-file inventory. Edited, extra and mismatched traces are refused.
- Incoming point estimates use accepted answers only and equal task weights. Defaults use the accepted two-of-three majority. Validity, conditional reserves and cross-arm intersection pairing are implemented. Default stability and agreement report task and pair coverage; unavailable values are null. There are no sign-flip tests, bootstrap intervals, p-values or claimed hypothesis outcomes in the new scorer.
- `K_alt` labels are “outputs keep relevant incoming pairs”, “outputs do not keep them” and “unresolved”. The draft does not apply a directional rule while inference is pending. Return-to-default statements require the measured equals-default shares.

## Fresh tasks and candidate exposure

The authorized fallback uses `dogwhistle/study.py`, `dogwhistle/heldout.py`, `dogwhistle/visibility.py` and `dogwhistle/honest.py` at pinned commit `1a4b471b3cfb4ed6d5def7c61356c5230af8c082`. There are 12 primary and four reserve tasks, three plus one per candidate. All 16 function targets differ from the trial targets. This is new-task validation on reused files, not unseen-file validation.

`TASK_AUDIT.md` lists every target function/line and all 100 candidate-source lines matching `coalition|codeword|decod|required_memory_refs`. `tasks.json` includes the exact `rg` matches, hashes and module inventory. Prompt-bearing adapters are excluded as candidates. Descriptive and implementation mentions remain, and repository-wide read access can still expose other adapter files. Neither candidate exclusion nor the word “honest” establishes that a relay never encounters prior prompt text.

## Checks

The final full offline suite passed: **164 passed**, zero failed, zero skipped (`BUILD_TESTS.txt`). Earlier test outputs are retained under their step names; they describe earlier versions, including the now-superseded automatic usage-limit retry policy. Step 1's initial two failing tests and their corrected run remain recorded; no failure output was changed to make it pass.

A separate check verified all **86** prior-work manifest entries and all **224** trial trace hashes against the inventory in `424528e`. There are no changes under `results/presprint/` or `sprint/trial_run/` relative to `64a9d93`. DogWhistle and the external pinned task workspace are clean. See `BUILD_CHECKS.json`. No study seal, arm ledger or new model trace was created.

## Review items before sealing

1. Inference and intervals are `PENDING_REVIEW`. Twelve primary tasks share only four files; extra within-file tasks do not create extra independent files. A method and any directional output rule must be reviewed and implemented before sealing. The current scorer supplies point estimates only.
2. Claude version, command, effort, sandbox, output method and model availability are `PENDING_RECON`. Configuration is deliberately unusable until checked. No successful Claude invocation is claimed.
3. The cutoff is `PENDING_RICK`. Launch checks run after preflight and immediately before process creation. Processes must finish and be reaped before analysis; exact wall-clock cleanup is not guaranteed by the operating system.
4. A paused process exits, so it cannot write new records at a future cutoff. The next resume or explicit `--finalize-cutoff` performs administrative cutoff finalization without model launches. This operational detail needs acceptance before sealing. It does not extend the cutoff.
5. Pause state is per arm. Separate concurrently running arm processes do not share a global pause bus. Both enforce the same pause policy when they observe a qualifying error.
6. D1 concerns reference output patterns. It does not establish a covert intent, a relay mechanism or a downstream effect. The strongest pattern wording remains “consistent with standardising”. D2 and Part B are needed for the broader downstream question.

## Commits

- `dfc018e`: Step 1 reliability and usage reconnaissance.
- `354aab3`: Step 2 runner, point scorer and integrity checks.
- `14a0328`: Rick's later manual-pause and label addendum.
- `2452a58`: new tasks and complete candidate mention audit.
- This report accompanies the draft-registration commit. No history was rewritten.

## Exact planned Seal 1 coverage

This is a list for a future seal, not a seal or digest. `SEAL_COVERAGE.json` and the draft registration contain the same 25 paths:

- `earshot/__init__.py`
- `earshot/d1v2.py`
- `earshot/d1v2_score.py`
- `earshot/integrity.py`
- `earshot/reliability.py`
- `earshot/system_issue_patterns.json`
- `earshot/config.py`
- `earshot/runner.py`
- `earshot/prompts.py`
- `earshot/gate.py`
- `earshot/sender.schema.json`
- `earshot/answer.schema.json`
- `sprint/partD/D1/tasks.json`
- `sprint/partD/D1/TASK_AUDIT.md`
- `sprint/partD/D1/D1_registration.json`
- `sprint/partD/D1/D1_REGISTRATION.md`
- `sprint/partD/D1/codex_config.json`
- `sprint/partD/D1/claude_config.json`
- `sprint/partD/D1/USAGE_RECON.md`
- `sprint/partD/D1/RUNBOOK.md`
- `sprint/partD/D1/SEAL_COVERAGE.json`
- `tests/test_d1v2.py`
- `tests/test_d1v2_tasks.py`
- `tests/test_integrity.py`
- `tests/test_reliability.py`
