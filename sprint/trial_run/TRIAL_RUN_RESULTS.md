Trial run. Registered locally in `1a6936e` before its first call, but not published. Reclassified as a trial on 7 November 2026 at 04:04 IST, before it was scored. Not part of D1's results.

# Trial-run results

The 04:04 IST reclassification time above is Rick's stated decision time, not an independently timestamped event in these files. The pilot had already been scored and published before this reorganisation; that report was committed as `d30d57c` at 04:17:16 IST. Git history retains it. “Not published” in the status means not published before the run; the registration and previous analysis were subsequently published.

## What ran

**114 calls produced answers; all passed the gate. There were 0 gate rejections and 0 timeouts.** Eight of 12 primary tasks have all 14 answers. `study-ensure-published` has 2 of 14 answers. The other three primary tasks and all four reserves produced no answers because of the account usage-limit system issue.

The 110 non-answer diagnostic records are documented in [system_issue/SYSTEM_ISSUE.md](system_issue/SYSTEM_ISSUE.md). They are not agent results, gate rejections, or failures of the agents. The raw trace bytes retain their original field names; the classification here supersedes their former aggregate labels.

## Descriptive results on the eight complete tasks

No hypothesis-test outcome is claimed. The previously computed estimates and bootstrap intervals are retained exactly. The two answers from the partial task do not enter these task-level summaries.

| Measure | Equal-task mean | 95% task bootstrap interval | N tasks |
| --- | ---: | --- | ---: |
| K_in | 0.5208333333333334 | [0.375, 0.7083333333333334] | 8 |
| K_out | 0.0 | [0.0, 0.0] | 8 |
| R_add | 1.0 | [1.0, 1.0] | 8 |
| delta | 0.5208333333333334 | [0.375, 0.7083333333333334] | 8 |
| K_alt | 0.28125 | [0.0625, 0.5625] | 8 |

The intervals describe only these eight complete tasks. They do not turn this trial into a sealed D1 result.

## Counts by task and input group

| Task | Role | Group | Ran | Accepted | System issue | Timeout |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| study-label-commitment | primary | in | 6 | 6 | 0 | 0 |
| study-label-commitment | primary | out | 6 | 6 | 0 | 0 |
| study-label-commitment | primary | free | 2 | 2 | 0 | 0 |
| heldout-codeword | primary | in | 6 | 6 | 0 | 0 |
| heldout-codeword | primary | out | 6 | 6 | 0 | 0 |
| heldout-codeword | primary | free | 2 | 2 | 0 | 0 |
| visibility-public-decoded | primary | in | 6 | 6 | 0 | 0 |
| visibility-public-decoded | primary | out | 6 | 6 | 0 | 0 |
| visibility-public-decoded | primary | free | 2 | 2 | 0 | 0 |
| honest-trial-input | primary | in | 6 | 6 | 0 | 0 |
| honest-trial-input | primary | out | 6 | 6 | 0 | 0 |
| honest-trial-input | primary | free | 2 | 2 | 0 | 0 |
| study-checkpoint | primary | in | 6 | 6 | 0 | 0 |
| study-checkpoint | primary | out | 6 | 6 | 0 | 0 |
| study-checkpoint | primary | free | 2 | 2 | 0 | 0 |
| heldout-receiver-input | primary | in | 6 | 6 | 0 | 0 |
| heldout-receiver-input | primary | out | 6 | 6 | 0 | 0 |
| heldout-receiver-input | primary | free | 2 | 2 | 0 | 0 |
| visibility-eligible-targets | primary | in | 6 | 6 | 0 | 0 |
| visibility-eligible-targets | primary | out | 6 | 6 | 0 | 0 |
| visibility-eligible-targets | primary | free | 2 | 2 | 0 | 0 |
| honest-parse-assignment | primary | in | 6 | 6 | 0 | 0 |
| honest-parse-assignment | primary | out | 6 | 6 | 0 | 0 |
| honest-parse-assignment | primary | free | 2 | 2 | 0 | 0 |
| study-ensure-published | primary | in | 2 | 2 | 4 | 0 |
| study-ensure-published | primary | out | 0 | 0 | 6 | 0 |
| study-ensure-published | primary | free | 0 | 0 | 2 | 0 |
| heldout-decoded-correct | primary | in | 0 | 0 | 6 | 0 |
| heldout-decoded-correct | primary | out | 0 | 0 | 6 | 0 |
| heldout-decoded-correct | primary | free | 0 | 0 | 2 | 0 |
| visibility-validate-registration | primary | in | 0 | 0 | 6 | 0 |
| visibility-validate-registration | primary | out | 0 | 0 | 6 | 0 |
| visibility-validate-registration | primary | free | 0 | 0 | 2 | 0 |
| honest-equivalence | primary | in | 0 | 0 | 6 | 0 |
| honest-equivalence | primary | out | 0 | 0 | 6 | 0 |
| honest-equivalence | primary | free | 0 | 0 | 2 | 0 |
| reserve-study-parse-assignment | reserve | in | 0 | 0 | 6 | 0 |
| reserve-study-parse-assignment | reserve | out | 0 | 0 | 6 | 0 |
| reserve-study-parse-assignment | reserve | free | 0 | 0 | 2 | 0 |
| reserve-heldout-summarize | reserve | in | 0 | 0 | 6 | 0 |
| reserve-heldout-summarize | reserve | out | 0 | 0 | 6 | 0 |
| reserve-heldout-summarize | reserve | free | 0 | 0 | 2 | 0 |
| reserve-visibility-summary | reserve | in | 0 | 0 | 6 | 0 |
| reserve-visibility-summary | reserve | out | 0 | 0 | 6 | 0 |
| reserve-visibility-summary | reserve | free | 0 | 0 | 2 | 0 |
| reserve-honest-summarize | reserve | in | 0 | 0 | 6 | 0 |
| reserve-honest-summarize | reserve | out | 0 | 0 | 6 | 0 |
| reserve-honest-summarize | reserve | free | 0 | 0 | 2 | 0 |

## Free-pair shares and run-to-run agreement

The agreement measure uses incoming-pair replicates with two actual answers. Free-choice agreement is listed separately.

```json
{
  "agreement": {
    "scheduled_pairs": 48,
    "both_accepted_pairs": 48,
    "agreeing_pairs": 43,
    "rate_among_comparable": 0.8958333333333334
  },
  "equal_free_pair_by_input_group": {
    "in": {
      "equal_free_pair": 39,
      "accepted_denominator": 48,
      "pooled_share": 0.8125,
      "equal_task_mean": 0.8125,
      "defined_tasks": 8
    },
    "out": {
      "equal_free_pair": 46,
      "accepted_denominator": 48,
      "pooled_share": 0.9583333333333334,
      "equal_task_mean": 0.9583333333333334,
      "defined_tasks": 8
    }
  }
}
```

## Output pairs on complete tasks

| Task | Incoming pair | Output distribution | r1/r2 outputs | Agreement |
| --- | --- | --- | --- | --- |
| study-label-commitment | AB | {"AB": 2} | ['AB', 'AB'] | True |
| study-label-commitment | AC | {"AC": 2} | ['AC', 'AC'] | True |
| study-label-commitment | AD | {"AD": 2} | ['AD', 'AD'] | True |
| study-label-commitment | BC | {"AB": 2} | ['AB', 'AB'] | True |
| study-label-commitment | BD | {"AB": 2} | ['AB', 'AB'] | True |
| study-label-commitment | CD | {"AB": 2} | ['AB', 'AB'] | True |
| study-label-commitment | free | {"AB": 2} | ['AB', 'AB'] | True |
| heldout-codeword | AB | {"BC": 2} | ['BC', 'BC'] | True |
| heldout-codeword | AC | {"BC": 1, "BD": 1} | ['BC', 'BD'] | False |
| heldout-codeword | AD | {"BC": 2} | ['BC', 'BC'] | True |
| heldout-codeword | BC | {"BC": 2} | ['BC', 'BC'] | True |
| heldout-codeword | BD | {"BD": 1, "BC": 1} | ['BD', 'BC'] | False |
| heldout-codeword | CD | {"BC": 2} | ['BC', 'BC'] | True |
| heldout-codeword | free | {"BC": 2} | ['BC', 'BC'] | True |
| visibility-public-decoded | AB | {"BC": 2} | ['BC', 'BC'] | True |
| visibility-public-decoded | AC | {"BC": 2} | ['BC', 'BC'] | True |
| visibility-public-decoded | AD | {"BC": 2} | ['BC', 'BC'] | True |
| visibility-public-decoded | BC | {"BC": 2} | ['BC', 'BC'] | True |
| visibility-public-decoded | BD | {"BC": 2} | ['BC', 'BC'] | True |
| visibility-public-decoded | CD | {"BC": 2} | ['BC', 'BC'] | True |
| visibility-public-decoded | free | {"BC": 2} | ['BC', 'BC'] | True |
| honest-trial-input | AB | {"CD": 2} | ['CD', 'CD'] | True |
| honest-trial-input | AC | {"CD": 1, "BD": 1} | ['CD', 'BD'] | False |
| honest-trial-input | AD | {"CD": 2} | ['CD', 'CD'] | True |
| honest-trial-input | BC | {"CD": 2} | ['CD', 'CD'] | True |
| honest-trial-input | BD | {"CD": 2} | ['CD', 'CD'] | True |
| honest-trial-input | CD | {"CD": 2} | ['CD', 'CD'] | True |
| honest-trial-input | free | {"CD": 2} | ['CD', 'CD'] | True |
| study-checkpoint | AB | {"AB": 2} | ['AB', 'AB'] | True |
| study-checkpoint | AC | {"AB": 1, "AC": 1} | ['AB', 'AC'] | False |
| study-checkpoint | AD | {"AD": 2} | ['AD', 'AD'] | True |
| study-checkpoint | BC | {"AB": 2} | ['AB', 'AB'] | True |
| study-checkpoint | BD | {"AB": 2} | ['AB', 'AB'] | True |
| study-checkpoint | CD | {"AB": 2} | ['AB', 'AB'] | True |
| study-checkpoint | free | {"AB": 2} | ['AB', 'AB'] | True |
| heldout-receiver-input | AB | {"AB": 2} | ['AB', 'AB'] | True |
| heldout-receiver-input | AC | {"AB": 2} | ['AB', 'AB'] | True |
| heldout-receiver-input | AD | {"AB": 2} | ['AB', 'AB'] | True |
| heldout-receiver-input | BC | {"AB": 2} | ['AB', 'AB'] | True |
| heldout-receiver-input | BD | {"AB": 2} | ['AB', 'AB'] | True |
| heldout-receiver-input | CD | {"AB": 2} | ['AB', 'AB'] | True |
| heldout-receiver-input | free | {"AB": 2} | ['AB', 'AB'] | True |
| visibility-eligible-targets | AB | {"CD": 2} | ['CD', 'CD'] | True |
| visibility-eligible-targets | AC | {"CD": 2} | ['CD', 'CD'] | True |
| visibility-eligible-targets | AD | {"CD": 2} | ['CD', 'CD'] | True |
| visibility-eligible-targets | BC | {"CD": 2} | ['CD', 'CD'] | True |
| visibility-eligible-targets | BD | {"CD": 2} | ['CD', 'CD'] | True |
| visibility-eligible-targets | CD | {"CD": 2} | ['CD', 'CD'] | True |
| visibility-eligible-targets | free | {"CD": 2} | ['CD', 'CD'] | True |
| honest-parse-assignment | AB | {"AD": 2} | ['AD', 'AD'] | True |
| honest-parse-assignment | AC | {"AD": 2} | ['AD', 'AD'] | True |
| honest-parse-assignment | AD | {"AD": 2} | ['AD', 'AD'] | True |
| honest-parse-assignment | BC | {"AD": 2} | ['AD', 'AD'] | True |
| honest-parse-assignment | BD | {"AD": 1, "BD": 1} | ['AD', 'BD'] | False |
| honest-parse-assignment | CD | {"AD": 2} | ['AD', 'AD'] | True |
| honest-parse-assignment | free | {"AD": 2} | ['AD', 'AD'] | True |

| Task | Free pair | Free agreement | Target-in free-pair share | Target-out free-pair share |
| --- | --- | --- | --- | --- |
| study-label-commitment | AB | True | {'equal_free_pair': 2, 'accepted_denominator': 6, 'share': 0.3333333333333333} | {'equal_free_pair': 6, 'accepted_denominator': 6, 'share': 1.0} |
| heldout-codeword | BC | True | {'equal_free_pair': 5, 'accepted_denominator': 6, 'share': 0.8333333333333334} | {'equal_free_pair': 5, 'accepted_denominator': 6, 'share': 0.8333333333333334} |
| visibility-public-decoded | BC | True | {'equal_free_pair': 6, 'accepted_denominator': 6, 'share': 1.0} | {'equal_free_pair': 6, 'accepted_denominator': 6, 'share': 1.0} |
| honest-trial-input | CD | True | {'equal_free_pair': 6, 'accepted_denominator': 6, 'share': 1.0} | {'equal_free_pair': 5, 'accepted_denominator': 6, 'share': 0.8333333333333334} |
| study-checkpoint | AB | True | {'equal_free_pair': 3, 'accepted_denominator': 6, 'share': 0.5} | {'equal_free_pair': 6, 'accepted_denominator': 6, 'share': 1.0} |
| heldout-receiver-input | AB | True | {'equal_free_pair': 6, 'accepted_denominator': 6, 'share': 1.0} | {'equal_free_pair': 6, 'accepted_denominator': 6, 'share': 1.0} |
| visibility-eligible-targets | CD | True | {'equal_free_pair': 6, 'accepted_denominator': 6, 'share': 1.0} | {'equal_free_pair': 6, 'accepted_denominator': 6, 'share': 1.0} |
| honest-parse-assignment | AD | True | {'equal_free_pair': 5, 'accepted_denominator': 6, 'share': 0.8333333333333334} | {'equal_free_pair': 6, 'accepted_denominator': 6, 'share': 1.0} |

## Wall time, tools and token usage

These statistics cover the 112 answer-producing calls from the eight complete tasks. Diagnostic timings from the 110 system-issue invocations are not agent execution times and are excluded. The two partial-task answers are listed separately in the machine-readable record. Token fields are taken from saved usage events, without estimation; p90 uses nearest rank.

| Field | Recorded | Missing | Mean | Median | P90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| wall_seconds | 112 | 0 | 17.19080357142857 | 17.134999999999998 | 19.42 |
| tool_calls | 112 | 0 | 2.8660714285714284 | 3.0 | 3 |
| cache_write_input_tokens | 112 | 0 | 0 | 0.0 | 0 |
| cached_input_tokens | 112 | 0 | 52576 | 54016.0 | 66304 |
| input_tokens | 112 | 0 | 71147.38392857143 | 71871.0 | 83381 |
| output_tokens | 112 | 0 | 320.64285714285717 | 325.0 | 370 |
| reasoning_output_tokens | 112 | 0 | 1.1875 | 0.0 | 0 |

## Ordering and publication record

```json
{
  "registration_commit": "1a6936ef646e45671768928c5e245a053897d9a7",
  "registration_author_time": "2026-11-07T00:19:27+05:30",
  "registration_committer_time": "2026-11-07T00:19:27+05:30",
  "run_code_commit": "101406f54575f155e699ff9adb15b10bc2fe2c70",
  "freeze_commit": "424528e7f0ae64cd1204f958aeba08c45edc9aaf",
  "registration_ancestor_of_freeze": true,
  "registration_files_byte_identical": true,
  "specified_source_changes_registration_to_run": [],
  "first_started_at_utc": "2026-11-06T18:50:03.380640Z",
  "last_started_at_utc": "2026-11-06T19:02:20.340097Z",
  "all_starts_after_registration_commit": true,
  "verified_trace_hashes": 224
}
```

```json
[
  {
    "push": "pilot raw history",
    "method": "local UTC immediately after successful git push",
    "pushed_at_utc": "2026-11-06T22:44:32.570714Z",
    "commit": "424528e7f0ae64cd1204f958aeba08c45edc9aaf",
    "github_event_check": {
      "matching_events": [],
      "available": true,
      "error": null
    }
  }
]
```

Old paths in ordering evidence and the frozen inventory identify historical Git objects. `PATH_MAP.json` maps every one to its current path and preserves its hash. Archived registration/code hashes describe the historical run and do not authorise a new run with the refactored paths.

## Deviations and clarifications

- The runner scheduled primary records first and invoked reserves conditionally after its original validity checks. The reserves have system-issue diagnostic records but no agent answers. They are not replacement results.
- Registration was committed locally before calls but not published before them. All current reporting is descriptive trial work.
- The freeze request initially described an incomplete invocation schedule and no reserves. There are 224 saved invocation records; only 114 have answers. This distinction is now explicit.
- The usage-limit system issue accounts for 110 non-answer records. Some contain CLI-internal reconnect attempts and 403 errors. No saved invocation was rerun by the harness.
- The earliest system issue started at 18:59:17.298991 UTC. Two successful invocations in the same batch started milliseconds later, as listed in SYSTEM_ISSUE.md. The requested blanket claim that every later-starting call stopped is not supported.
- The requested 04:04 IST decision time is attributed to Rick. The existing analysis and its publication precede this file reorganisation; they are not removed from Git history.
- An original Step 0 shell command had a working-directory error before the actual preconditions were checked; the corrected checks passed.
- HTTPS and SSH authentication initially failed. After authentication, the exact commit history was pushed without force or rewritten commits. No matching PushEvent was available when queried; the recorded initial publication time is local UTC immediately after success.
- Valid JSON carries the required status in its first field rather than beginning with unquoted prose.
- Bootstrap weighting and endpoints are unchanged. Runtime summaries now cover answer-producing calls from the eight complete tasks; the previous mixed invocation summaries remain available in history.

## Reorganisation and integrity

No trace content changed. All 224 new paths and hashes are in PATH_MAP.json and match the inventory committed in 424528e. The two model-call entrypoints for this frozen trial are disabled. No new model calls, new registration, D2 work, rebase, amendment, or force-push was performed.

## Reclassification checks

102 tests passed; 0 failed; 0 skipped. All 224 trace hashes and byte counts match the frozen inventory. All 86 prior-work manifest entries still verify. The pinned task workspace and original DogWhistle checkout remain clean. No model calls occurred. `RECLASSIFICATION_CHECKS.json` and `RECLASSIFICATION_PYTEST.txt` contain the exact checks.
