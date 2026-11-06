# D1 draft registration — NOT SEALED, NOT RUN

Inference method: PENDING_REVIEW

Interval method: PENDING_REVIEW

D1 studies how relays select references from task cues, in one repository with four candidate files and reference files of identical content. Broader claims about downstream effects belong to D2 and Part B.

Both runners and the scorer refuse pending fields and DRAFT status. Claude command details and availability remain PENDING_RECON; cutoff remains PENDING_RICK. No model calls, study results, seal or ledger have been generated.

## Question

How often do output reference pairs equal incoming pairs or the task’s gate-accepted free-choice default?

## Origin

Designed after the trial run in sprint/trial_run/. That run shaped this design and its predictions; it is not part of D1. New function targets are used in the same four candidate files under Rick’s fallback authorization. This is not a new-repository or unseen-file validation.

## Default rule

A pair appearing in at least two of the three gate-accepted free-choice answers; undefined otherwise. An accepted pair is unordered.

## Validity

Default defined; at least 10 accepted incoming answers, including at least 5 target-in and 5 target-out. Gate rejections, timeouts and unclassified final failures are not accepted. System issues and cutoff stops are not agent outcomes. Replacement uses reserves in their listed order.

## Clustering

The 12 primary tasks share four files and are not independent. Any inference and interval method must account for that dependence. No sign-flip tests, Holm decisions or bootstrap intervals are specified or computed in this draft.

## Cross arm

Task-ID pairing only among tasks selected as valid in both arms. Report overlap size and IDs; zero overlap is undefined. Point differences (Codex minus Claude) in K, C_out, K_alt and K_out use equal task weights. Model-and-harness pairs, not model-only comparisons. Inference and intervals remain pending.

## Output pattern rule

PENDING_REVIEW. No interval, significance test or automatic directional rule is implemented. A low K_alt alone is not a return to the default. Default-return wording requires the directly measured equals-default share. Descriptions concern output patterns only; the strongest permitted wording is consistent with standardising.

## Cutoff rule

Check after setup, version and publication checks, immediately before model-process launch. Do not launch at or after cutoff minus 180 seconds. Calls not launched are stopped_by_cutoff, separately from agent failures and timeouts. Await/reap all launched processes before analysis. A paused process exits; the next resume or explicit --finalize-cutoff records remaining scheduled calls without launching a model. Unused reserves are not falsely marked attempted.

## Stopping

Finish both arms or reach the fixed cutoff. At least eight selected valid tasks are needed for point-estimate reporting at cutoff; fewer yields INCONCLUSIVE coverage. This is not a hypothesis outcome. No cutoff extension after sealing.

## Seals

No seal is created by this build. Before any call, a future Seal 1 and its digest must be committed and pushed; local HEAD must be the seal commit and equal origin’s specified branch. Sealed bytes must match. Any later commit blocks calls. Each completed arm then needs a separately committed and pushed ledger plus digest covering every final trace, system-issue attempt, intent, stopped record and runtime state. Scoring checks exact coverage and every hash; it also checks the ledger’s Seal 1 digest link.

## Design

- **primary_tasks:** 12
- **reserves:** 4
- **free_calls_per_task:** 3
- **incoming_pairs:** ["AB", "AC", "AD", "BC", "BD", "CD"]
- **replicates:** 2
- **primary_calls_per_arm:** 180
- **workers_max:** 4
- **call_timeout_seconds:** 180
- **order:** Fixed primary order; all three free calls complete before incoming calls; reserves in listed order only for invalid primary tasks.

## Denominators

- **incoming:** All incoming rates use only gate-accepted incoming answers in their stated input group. Free answers do not enter incoming rates. Undefined rates remain null, never zero-filled.
- **summary:** Equal-weight means of defined task-level rates, with evaluable-task counts. Main estimates use selected valid tasks.
- **default_stability:** Report twice: all attempted primary tasks and selected valid tasks. Report the share with all three accepted free answers equal over all tasks in that set; also report the conditional share among tasks with three accepted free answers and the number not evaluable. Missing free answers are not called disagreement.
- **agreement:** For each incoming pair, agreement is evaluable only when both replicates were accepted. Each task has the mean across its evaluable pairs. Report equal-weight task means, evaluable task/pair counts and all pair-level statuses, twice: all attempted primary tasks and selected valid tasks. Missing answers are never counted as agreements.

## Measures

- **K:** output pair equals incoming pair, all accepted incoming calls
- **K_in:** keep rate where incoming pair includes target
- **K_out:** keep rate where incoming pair excludes target
- **R_add:** target-in-output rate where incoming pair excludes target
- **delta:** K_in minus K_out within each task
- **K_alt:** keep rate among accepted target-in incoming pairs that differ from the defined default
- **C_in:** output equals default, target-in incoming group
- **C_out:** output equals default, target-out incoming group
- **C:** output equals default, all accepted incoming calls
- **overall_C:** alias of C
- **default_stability:** as specified under denominators
- **run_to_run_agreement:** as specified under denominators

## Classifications

- **accepted:** exit 0 and gate-accepted pair
- **gate_rejected:** exit 0 with missing, unparsable or gate-invalid answer; final, never retried
- **timed_out:** 180-second timeout; final, never retried
- **unclassified_failure:** non-zero exit with an answer and no classified final success; final and not accepted; list for Rick; never retry an answer
- **system_issue:** non-zero/no-answer matching sealed patterns, or unknown no-answer process error; not an agent failure; save every attempt separately

## Pauses

- **quota_percentage_reader:** null
- **ten_percent_pause:** false
- **manual:** Any failed call with a usage/rate-limit error, including HTTP 429, pauses both implementations. Unknown no-answer errors also pause. Submit no new calls, let in-flight calls finish and save them, record time, triggering call, finished calls and calls left, then exit. No reset time, elapsed wait, executor judgment or plain restart authorizes resume. Rick must authorize --resume-rick. Reuse final answers; retries retain counters and exact prompt bytes.
- **other_system_issues:** Other recognized system issues use an explicit reset time if available, otherwise a 30-minute wait; retry the same prompt in a fresh process, max five total attempts. No wait crosses the last-launch deadline. At five, stop for Rick without resetting counters.
- **timezone:** Reset text without a named zone is parsed in Asia/Calcutta (UTC+05:30). Save raw text and parsed UTC. Unknown/ambiguous zones use the recorded fallback. For manual pauses reset parsing is audit information, not permission to resume.
- **crash:** An intent without a durable outcome blocks the arm for reconciliation; never silently repeat a possibly answered call.

## Output labels

- outputs keep relevant incoming pairs
- outputs do not keep them
- unresolved

## Limitations

- One repository; four identical-content reference files.
- Twelve tasks clustered in four files; inference remains under review.
- Candidate files are reused from the trial; only function targets and requests are new.
- Adapter files containing agent-directed reference/decoding prompts are excluded as candidates. All 100 remaining candidate-line mentions are listed in TASK_AUDIT.md and tasks.json. Implementation and descriptive mentions remain.
- Read-only tool access covers the repository, so agents may inspect excluded adapter files as other context. No claim of zero codeword exposure or isolated candidate-only access is made.
- Read-only sandbox and fresh ephemeral sessions are specified for Codex. Claude model availability, sandbox, command, effort, output format and version remain unverified and PENDING_RECON.
- Results concern reference-pair outputs in model-and-harness pairs. Broader downstream effects require D2 and Part B.
- Operating-system scheduling and process cleanup can overrun a wall-clock deadline; no analysis starts until workers finish and child processes are reaped.

## Exact planned Seal 1 coverage

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
