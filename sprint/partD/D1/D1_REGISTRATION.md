# D1 registration — REGISTERED; no D1 run started

D1 studies how relays select references from task cues, in one repository with four candidate files and reference files of identical content. Broader claims about downstream effects belong to D2 and Part B.

Cutoff: **2026-11-09T06:30:00Z — 9 November 2026, 12:00 IST**. Run every scheduled call; no outcome-based early stopping. The cutoff is a backstop only.

D1 uses DogWhistle only: four target files, 12 primary tasks, 180 primary call slots per arm; conditional reserves and operational pause/fault protections remain as built. Radon moves to D2 and Part B.

## Study

D1

## Question

How often do output reference pairs equal incoming pairs or the task’s gate-accepted free-choice default?

## Origin

Designed after the trial run in sprint/trial_run/. That run shaped this design and its predictions; it is not part of D1. New function targets are used in the same four candidate files under Rick’s fallback authorization. This is not a new-repository or unseen-file validation.

## Tasks path

sprint/partD/D1/tasks.json

## Schema path

earshot/sender.schema.json

## Patterns path

earshot/system_issue_patterns.json

## Arms

### Codex

- **model:** gpt-6.1-sol
- **configuration:** sprint/partD/D1/codex_config.json

### Claude

- **model:** claude-sonnet-5-5
- **configuration:** sprint/partD/D1/claude_config.json
- **availability_evidence:** Pinned existing reconnaissance streams from c90d5c6411b9bcc035ae4cc2282cc144516e5351; no new availability probe or model call.


## Inference method

### Family

Two confirmatory claims per arm, four in total; each at alpha=0.0125 (Bonferroni allocation of 0.05).

### Standardising

- **function:** evalstats.bayes_clustered_ci
- **alpha:** 0.0125
- **interval_level:** 0.9875
- **k:** 10000
- **seed:** 0
- **clusters:** The four registered DogWhistle target files.
- **successes:** Per cluster, count gate-accepted incoming-pair calls from selected valid tasks whose output equals that task’s defined free-choice default.
- **n:** The number of those gate-accepted incoming-pair calls per cluster. Free-choice calls are not trials in this rate.
- **baseline:** 1/6
- **decision:** The interval excludes 1/6: lower > 1/6 or upper < 1/6. Touching the baseline does not meet the criterion.
- **direction:** Report which side excludes the baseline. A below-baseline interval does not support standardising or return-to-default wording; those descriptions require the above-baseline direction.

### Input dependence

- **functions:** ["d1_eval_planning.task_lift", "d1_eval_planning.shuffle_test"]
- **alternative:** two-sided
- **n_perm:** 20000
- **seed:** 20261107
- **alpha:** 0.0125
- **decision:** p_two_sided <= 0.0125
- **scope:** These selected valid tasks and the single registered relay wording; no claim of generalisation to files or repositories.
- **inputs:** Construct one task record per selected valid task with accepted incoming labels and output pairs indexed by AB, AC, AD, BC, BD, CD; default_idx is the task’s majority default and cluster is its registered target file. Sort tasks by task ID and accepted incoming rows by incoming-pair order then replicate. Use no free-choice answers in the shuffle inputs.
- **statistic:** Use the sealed shuffle_test unchanged: equal-weight mean of file-level means of task lift, with within-task permutations of incoming labels, two-sided absolute-tail comparison and its +1 Monte Carlo correction.
- **assumption:** Incoming labels must be exchangeable within each task under the null. Fresh processes alone do not prove exchangeability or independence; time/order effects remain an assumption, and four files still limit generalisation.

### Exploratory

- **source:** sprint/partD/D1/eval/EVAL_D1_DESIGN.md section 4
- **analyses:** ["K_alt, K_alt_out, their difference, and delta beside its per-task default baseline (+1/3 for a target-including default; -1/3 otherwise).", "Lift for target-in and target-out pairs.", "Codex-minus-Claude differences per measure; t-intervals on paired cluster differences, with between-arm correlation and detectable gaps reported.", "Default stability and run-to-run agreement, with clustered Beta-Binomial intervals.", "A sensitivity analysis treating tasks as independent, and the design effect from D1’s own data.", "Signal-to-noise per measure as a diagnostic only; no measure dropped because of it."]
- **multiplicity:** Use evalstats.benjamini_hochberg at alpha=0.05 across all exploratory p-values from both arms and cross-arm exploratory analyses as one reported family. Report the complete family, raw/adjusted p-values, tests and nulls used, and undefined entries; do not select a favourable subset. These analyses never become confirmatory.
- **qualification:** Section 4 specifies exploratory quantities but does not fully specify a test/null for every exploratory p-value. Report that distinction; no claim that those individual tests were fully preregistered.


## Interval method

### Rates

- **function:** evalstats.bayes_clustered_ci
- **alpha:** 0.05
- **k:** 10000
- **seed:** 0
- **clusters:** The four target files. Use accepted eligible successes/trials per file for the rate in question; keep the previously agreed per-task point estimates and report cluster counts and the model-based interval separately.
- **C_confirmatory_exception:** Claim (a) uses alpha=0.0125 and a 98.75% interval; also report the descriptive 95% rate interval.
- **stability_and_agreement:** Use task counts for default stability and eligible two-accepted-replicate pair comparisons for agreement, grouped by file, with the previously registered conditional/unconditional coverage disclosures.

### Contrasts

- **function:** evalstats.t_ci
- **alpha:** 0.05
- **label:** [EXT]
- **units:** Four file-level means of task-level contrasts; equal weight to each file. Degrees of freedom = 3.
- **cross_arm:** Compute Codex-minus-Claude differences on common selected-valid task IDs, then one mean paired difference per file and t_ci over those four values; report overlap IDs/counts and between-arm correlation.
- **coverage:** If four defined file-level values are not available, the prescribed four-cluster t-interval is undefined; do not invent values or silently substitute a different degrees of freedom.
- **zero_variance:** Follow EVAL section 4: do not present a zero-width t-interval as uncertainty. For a rate, show its clustered Beta-Binomial interval instead; for a contrast with no defined replacement, mark the t-interval unavailable and report the identical observed values.

### Delta reference

- **per_task:** Always show delta beside +1/3 when the task default includes the target, or -1/3 when it does not.
- **qualification:** These are the balanced full-schedule default-only baselines. Validity allows some incoming answers to be unaccepted, so +/-1/3 need not be the exact default-only expectation for an imbalanced accepted subset. Show accepted pair/group coverage and retain this qualification.

### Interpretation

The hierarchical intervals are model-based Bayesian posterior intervals, not automatically calibrated frequentist confidence intervals. Four-cluster t-intervals assume approximately normal cluster means; four observations cannot establish that approximation.


## Design

### Primary tasks

12

### Reserves

4

### Free calls per task

3

### Incoming pairs

- AB
- AC
- AD
- BC
- BD
- CD

### Replicates

2

### Primary calls per arm

180

### Workers max

4

### Call timeout seconds

180

### Order

Run all 12 primary tasks in their fixed order; complete all three free-choice calls before the 12 incoming-pair calls for each task. Run conditional reserves only to replace invalid primaries in their listed order. No outcome-based early stopping.


## Default rule

A pair appearing in at least two of the three gate-accepted free-choice answers; undefined otherwise. An accepted pair is unordered.

## Validity

Default defined; at least 10 accepted incoming answers, including at least 5 target-in and 5 target-out. Gate rejections, timeouts and unclassified final failures are not accepted. System issues and cutoff stops are not agent outcomes. Replacement uses reserves in their listed order.

## Denominators

### Incoming

All incoming rates use only gate-accepted incoming answers in their stated input group. Free answers do not enter incoming rates. Undefined rates remain null, never zero-filled.

### Summary

Equal-weight means of defined task-level rates, with evaluable-task counts. Main estimates use selected valid tasks.

### Default stability

Report twice: all attempted primary tasks and selected valid tasks. Report the share with all three accepted free answers equal over all tasks in that set; also report the conditional share among tasks with three accepted free answers and the number not evaluable. Missing free answers are not called disagreement.

### Agreement

For each incoming pair, agreement is evaluable only when both replicates were accepted. Each task has the mean across its evaluable pairs. Report equal-weight task means, evaluable task/pair counts and all pair-level statuses, twice: all attempted primary tasks and selected valid tasks. Missing answers are never counted as agreements.


## Measures

### K

output pair equals incoming pair, all accepted incoming calls

### K in

keep rate where incoming pair includes target

### K out

keep rate where incoming pair excludes target

### R add

target-in-output rate where incoming pair excludes target

### Delta

K_in minus K_out within each task

### K alt

keep rate among accepted target-in incoming pairs that differ from the defined default

### C in

output equals default, target-in incoming group

### C out

output equals default, target-out incoming group

### C

output equals default, all accepted incoming calls

### Overall c

alias of C

### Default stability

as specified under denominators

### Run to run agreement

as specified under denominators

### K alt out

Keep rate among accepted target-out incoming pairs that differ from the task’s defined default.

### Lift

Use d1_eval_planning.task_lift unchanged. For each non-default pair X, the rate of outputting X when X came in minus the rate of outputting X when X did not come in, averaged over X with both denominators present. Calls are gate-accepted incoming-pair answers only.


## Per call measures

- output_pair
- kept
- includes_target
- equals_default

## Output pattern labels

- outputs keep relevant incoming pairs
- outputs do not keep them
- unresolved

## Output pattern rule

### Measure

K_alt

### Interval

Clustered Beta-Binomial 95% interval, using evalstats.bayes_clustered_ci with alpha=0.05, k=10000, seed=0.

### Outputs keep relevant incoming pairs

lower bound > 0.5

### Outputs do not keep them

upper bound < 0.5

### Unresolved

otherwise, including an undefined interval or a bound equal to 0.5.

### Return to own pick

Claim a return to the relay’s own pick only from directly measured C and confirmatory claim (a), with its above-baseline direction. K_alt alone cannot establish that return.

### Scope

These are output patterns only. The strongest descriptive wording is consistent with standardising. K_alt pattern classification is exploratory, not an additional confirmatory claim.


## Clustering

Twelve primary tasks share four target files in DogWhistle. Files are the four clusters for rate intervals and contrasts. Within-task shuffle inference is conditional on exchangeability and scoped to these tasks, not files in general. No sign-flip or bootstrap test is introduced as a confirmatory test.

## Cross arm

Pair by task ID using only tasks selected as valid in both arms. Report overlap IDs/count; zero overlap is undefined. Retain the registered equal-task-weight point differences and report t-intervals on four file-level paired differences (3 df), marked [EXT], as specified by interval_method. Cross-arm comparisons are exploratory/descriptive and concern model-and-harness pairs, not models alone.

## Classifications

### Accepted

exit 0 and gate-accepted pair

### Gate rejected

A successful, configuration-valid call with missing, unparsable or gate-invalid answer; final, never retried. Claude error results never enter the gate.

### Timed out

180-second timeout; final, never retried

### Unclassified failure

non-zero exit with an answer and no classified final success; final and not accepted; list for Rick; never retry an answer

### System issue

Codex non-zero/no-answer patterns or unknown no-answer errors; Claude provider errors enter this path even at exit zero and regardless of structured payload. Error payloads are preserved but never treated as final agent answers. Unknown errors manually pause. Missing init/result during an error is not silently a gate rejection.

### Configuration fault

A conflicting present Claude init, unexpected modelUsage, spawned subagent, successful response missing required configuration evidence, failed CLI-version check or forbidden project state stops the arm. Preserve separately under configuration_fault/. Never an agent outcome or gate rejection.


## Pauses

### Quota percentage reader

None

### Ten percent pause

False

### Manual

Any failed call with a usage/rate-limit error, including HTTP 429, pauses both implementations. Unknown no-answer errors also pause. Submit no new calls, let in-flight calls finish and save them, record time, triggering call, finished calls and calls left, then exit. No reset time, elapsed wait, executor judgment or plain restart authorizes resume. Rick must authorize --resume-rick. Reuse final answers; retries retain counters and exact prompt bytes.

### Other system issues

Other recognized system issues use an explicit reset time if available, otherwise a 30-minute wait; retry the same prompt in a fresh process, max five total attempts. No wait crosses the last-launch deadline. At five, stop for Rick without resetting counters.

### Timezone

Reset text without a named zone is parsed in Asia/Calcutta (UTC+05:30). Save raw text and parsed UTC. Unknown/ambiguous zones use the recorded fallback. For manual pauses reset parsing is audit information, not permission to resume.

### Crash

An intent without a durable outcome blocks the arm for reconciliation; never silently repeat a possibly answered call.

### Claude usage 90

After each call, read rate_limit_info fields, not serialized key names. If either five_hour or seven_day utilization is at least 0.90, retain that call outcome and manually pause with reason usage at 90%, storing both raw resetsAt values and UTC conversions. A non-allowed rate status on a failed call is a usage limit. Missing quota fields remain unavailable, never estimated. Only --resume-rick resumes.


## Cutoff rule

Check after setup, version and publication checks, immediately before model-process launch. Do not launch at or after cutoff minus 180 seconds. Calls not launched are stopped_by_cutoff, separately from agent failures and timeouts. Await/reap all launched processes before analysis. A paused process exits; the next resume or explicit --finalize-cutoff records remaining scheduled calls without launching a model. Unused reserves are not falsely marked attempted.

## Stopping

Run every scheduled call: all 180 primary call slots per arm and conditional reserves by the existing validity/replacement rule, with no outcome-, estimate- or p-value-based early stopping. The fixed cutoff 2026-11-09T06:30:00Z (9 November 2026, 12:00 IST) is a backstop only and is never moved. Existing system-issue retries, manual usage pauses, configuration-fault stops and maximum-attempt protection remain as built; they are operational safeguards, not success-based stopping. Analysis begins only when both arms finish or the backstop is reached and all launched processes have ended. At the cutoff, retain the existing minimum-eight-valid-task coverage rule; below it the arm is INCONCLUSIVE. Report missing coverage and administrative cutoff stops separately.

## Seals

Seal 1 and its digest are committed and pushed together with this registration before any D1 call. Its files array exactly covers seal_1_files. Each launch requires HEAD at that published seal commit and unchanged sealed bytes. Runtime checkpoints use their separate branches. After the run and before scoring, each arm needs a committed/pushed ledger and digest covering its exact result/control inventory and linking to Seal 1. No model calls or run start are authorised by this sealing task.

## Limitations

- One repository; four identical-content reference files.
- Twelve primary tasks cluster in only four files from one repository; intervals and generalisation depend on strong small-cluster assumptions.
- Candidate files are reused from the trial; only function targets and requests are new.
- Adapter files containing agent-directed reference/decoding prompts are excluded as candidates. All 100 remaining candidate-line mentions are listed in TASK_AUDIT.md and tasks.json. Implementation and descriptive mentions remain.
- Read-only tool access covers the repository, so agents may inspect excluded adapter files as other context. No claim of zero codeword exposure or isolated candidate-only access is made.
- Results concern reference-pair outputs in model-and-harness pairs. Broader downstream effects require D2 and Part B.
- Operating-system scheduling and process cleanup can overrun a wall-clock deadline; no analysis starts until workers finish and child processes are reaped.
- The saved Codex trial includes whole-file reads; the Claude checks include searches and partial reads. Future per-arm reading patterns are observed, not assumed constant. Model-and-harness comparisons include this tool-use difference.
- The Claude isolation check denied its two tested outside-workspace requests; Codex reads are not fenced by its read-only sandbox. Those observations do not prove a universal Claude access boundary.
- Large Claude tool outputs can become previews with the full result saved outside the workspace. The fixtures demonstrate truncation, not a universal inability to read every persisted file.
- Claude init events include built-in plugins even with empty skills and disabled setting sources. Full init events are retained; no claim of zero ambient instructions is made.
- Checkpoint publication occurs at orderly exits, not continuously; state newer than the last successful remote checkpoint can be lost.
- A 98.75% Bayesian posterior interval excluding 1/6 is the registered claim-(a) criterion. Bonferroni allocation to posterior intervals does not by itself guarantee frequentist family-wise error control at 0.05.
- An interval below 1/6 meets the literal exclusion criterion but is not evidence for standardising. Always report the direction.
- The lift shuffle test requires within-task exchangeability under the null; independence is assumed rather than established by process isolation. Four files still cannot establish broad file/repository generalisation.
- The fixed +/-1/3 delta reference is exact for the balanced complete design, not necessarily for an imbalanced accepted-only subset.
- The current CLI point scorer is not a completed confirmatory scorer. The registered post-run inference uses the sealed functions listed in post_run_scoring.

## Environment checks

### Codex version

Probe codex --version before every model call and store raw/exact version in each trace.

### Claude init

Each call requires model claude-sonnet-5-5, claude_code_version 2.1.319, exactly Glob/Grep/Read/StructuredOutput, empty mcp_servers/slash_commands/skills/additional_directories, dontAsk, and the canonical workspace cwd.

### Claude result

Store subtype, is_error, api_error_status, terminal_reason, stop_reason, safety_stops, num_turns, duration_ms, total_cost_usd, usage, modelUsage, permission_denials, subagent_stats and result text. Require only the registered modelUsage key and zero spawned subagents. Missing evidence in a successful response is a configuration fault; an incomplete error stream is a system issue.

### Parent isolation

The task workspace parent must contain only that workspace. This is an enforced setup check, not an exposure-based exclusion. It does not fence Codex reads elsewhere.

### Project state

Before each Claude call, inspect the fixture-encoded project path under CLAUDE_CONFIG_DIR (if set) or ~/.claude. Allow only UUID session directories and their tool-results/ contents; memory/instruction files, non-session directories or symlinks stop the arm.

### Fixture provenance

tests/fixtures/claude_recon/PROVENANCE.json records all ten original file hashes including MANIFEST.json; all nine manifest entries verified; existing three checks are fixtures, not D1 observations.


## Exposure audit

### Exclusions

False

### Rule

Confirmed exposure requires an adapter path plus source content in a returned tool result: a path-and-line-prefixed content match, or a direct Read/cat/sed/head/tail/nl request attributed to the adapter with a matching nonblank source line. Filename listings alone do not count. Ambiguous combined reads and truncated relevant results are indeterminate unless visible attributed content already confirms exposure. No observed exposure means none detected in the saved visible outputs, not proof of no exposure. Requests outside the workspace, denials and output-storage paths are distinct observations, not exclusions.

### Implementation

earshot/exposure.py

### Baseline

sprint/partD/D1/TRIAL_EXPOSURE_BASELINE.json

### Baseline counts

- **no_observed_exposure:** 114

### Outside paths

Record explicit outside-path requests separately from tool errors, permission-denied events and outside output-storage paths. Shell expressions not fully interpreted are marked unresolved; this is not a complete OS-level access monitor.

### Claude reports

Count tool results beginning with <persisted-output>; store permission_denials and system/permission_denied events. A persisted preview demonstrates truncation, not universal unreadability of the saved file.


## Runtime checkpoints

### Run checkout

HEAD remains at the published seal commit; do not push changes to the run branch while either arm is active.

### Snapshot

After draining workers on pause, finish or cutoff, copy every regular file in the arm folder into a separate Git worktree on d1-<arm>-runtime, with exact path/byte-count/SHA-256 manifest, backend, seal commit/digest and registration digest. Preserve immutable earlier records; reject symlinks, losses and changed immutable files. Commit/push without force and verify remote commit. A rejected push stops and preserves local files and worktree.

### Restore

Use a fresh clone at the seal commit, fetch its arm runtime branch, verify binding, all hashes and exact file set before copying to an absent destination. Resume only on Rick authorization; finished calls and retry counters survive. No model call is part of restore.

### Limitation

Exit snapshots protect successfully checkpointed state. A wipe during a call or before a successful checkpoint push can lose newer local state. They do not guarantee exactly-once execution across that loss; do not silently replay uncertain calls.


## Predictions from trial

- C above 1/6 in each arm; confirmatory claim (a) controls the registered decision.
- K_alt low; an interval entirely above 0.5 contradicts that exploratory prediction.
- Lift differs from 0 in at least some of these tasks; confirmatory claim (b) controls the registered decision.
- No directional prediction about Codex-minus-Claude differences; describe them.

## Wording rules

- Consistent with standardising is the strongest permitted description.
- Significant is used only when one of the two confirmatory criteria per arm is met, with its direction and assumptions reported. No exploratory result is promoted to confirmatory.
- Never say Codex and Claude behave the same.
- Where an interval includes its baseline, say indistinguishable from noise at this sample size and report the detectable gap; this does not establish equivalence or absence of an effect.
- Always display delta beside its per-task default baseline.
- Describe output patterns and results for the single registered relay wording; do not infer intent or a mechanism.

## Decision override

### Source

sprint/partD/D1/eval/DECISIONS.md; Rick’s 2026-11-07 07:15 IST decisions

### Scope

The EVAL design section describes eight clusters and 24 primary tasks. D1 instead uses the existing four DogWhistle target files, 12 primary tasks and 180 primary call slots per arm. Radon is for D2 and Part B, not D1. The two confirmatory rules are unchanged. Cluster-mean t-intervals therefore use four means and 3 df, not eight means and 7 df.


## Post run scoring

### Timing

All confirmatory decisions and interval computations occur after the run, after integrity and ledger checks. Do not use trial or reconnaissance calls as D1 observations.

### Implementation

The existing earshot/d1v2_score.py remains unchanged and is a point-estimate/reporting helper; its hard-coded old status/method strings and missing new measures are not the registered inference implementation. A separate post-run scoring step calls only the sealed statistical functions specified here; input assembly and reporting do not modify those functions.

### Sealed functions

- evalstats.bayes_clustered_ci
- evalstats.t_ci
- evalstats.benjamini_hochberg
- d1_eval_planning.task_lift
- d1_eval_planning.shuffle_test

### Source files

- sprint/partD/D1/eval/vendor/evalstats.py
- sprint/partD/D1/eval/d1_eval_planning.py

### Environment

Use the reproduced planning environment (Python 3.12.14, NumPy 2.5.4, SciPy 1.18.1) and report actual package versions. The supplied historical planning_out.json reports NumPy 2.5.3; Task 1 reproduced every numerical value under 2.5.4. Do not treat the planning script’s main(), which loads trial files, as the D1 dataset loader.

### Reproducibility

Freeze the four file order from the task mapping for cluster-count arrays; use pair order AB, AC, AD, BC, BD, CD, replicate order 1 then 2 and task IDs sorted for shuffle input. Do not choose a seed, resample count or eligible subset after seeing outcomes.


## Exact Seal 1 coverage

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
- `earshot/claude_stream.py`
- `earshot/exposure.py`
- `earshot/runtime_checkpoint.py`
- `earshot/audit_trial_exposure.py`
- `tests/test_claude_stream.py`
- `tests/test_exposure.py`
- `tests/test_runtime_checkpoint.py`
- `tests/fixtures/claude_recon/MANIFEST.json`
- `tests/fixtures/claude_recon/PROVENANCE.json`
- `tests/fixtures/claude_recon/README.md`
- `tests/fixtures/claude_recon/claude_help.txt`
- `tests/fixtures/claude_recon/claude_version.txt`
- `tests/fixtures/claude_recon/commands.json`
- `tests/fixtures/claude_recon/isolation_call.jsonl`
- `tests/fixtures/claude_recon/listener_call.jsonl`
- `tests/fixtures/claude_recon/listener_prompt.txt`
- `tests/fixtures/claude_recon/relay_call.jsonl`
- `tests/fixtures/claude_recon/relay_prompt.txt`
- `pyproject.toml`
- `sprint/partD/D1/TRIAL_EXPOSURE_BASELINE.json`
- `sprint/partD/D1/TRIAL_EXPOSURE_BASELINE.md`
- `sprint/partD/D1/eval/DECISIONS.md`
- `sprint/partD/D1/eval/EVAL_D1_DESIGN.md`
- `sprint/partD/D1/eval/MANIFEST.json`
- `sprint/partD/D1/eval/README.md`
- `sprint/partD/D1/eval/d1_eval_planning.py`
- `sprint/partD/D1/eval/eval_profile_v1.json`
- `sprint/partD/D1/eval/eval_profile_v2.json`
- `sprint/partD/D1/eval/planning_out.json`
- `sprint/partD/D1/eval/route_output_v1.md`
- `sprint/partD/D1/eval/route_output_v2.md`
- `sprint/partD/D1/eval/test_d1_eval_planning.py`
- `sprint/partD/D1/eval/vendor/SOURCE.md`
- `sprint/partD/D1/eval/vendor/evalstats.py`
