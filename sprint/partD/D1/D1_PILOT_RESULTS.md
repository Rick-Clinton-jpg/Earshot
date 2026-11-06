D1 pilot. Registered in commit `1a6936e` before its first call, but not published before the run. Used to design a later sealed D1. Not confirmatory.

# D1 pilot results

## Ordering and publication evidence

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

The runner first scheduled all primary tasks, computed their validity, and scheduled reserves conditionally in listed order while valid replacement slots remained. This statement is from the code at the run commit, not inferred from the answers. The excluded smoke trace was already committed in the run commit.

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

## Call counts by task and input group

| Task | Group | Run | Accepted | Rejected | Timed out |
| --- | --- | ---: | ---: | ---: | ---: |
| study-label-commitment | in | 6 | 6 | 0 | 0 |
| study-label-commitment | out | 6 | 6 | 0 | 0 |
| study-label-commitment | free | 2 | 2 | 0 | 0 |
| heldout-codeword | in | 6 | 6 | 0 | 0 |
| heldout-codeword | out | 6 | 6 | 0 | 0 |
| heldout-codeword | free | 2 | 2 | 0 | 0 |
| visibility-public-decoded | in | 6 | 6 | 0 | 0 |
| visibility-public-decoded | out | 6 | 6 | 0 | 0 |
| visibility-public-decoded | free | 2 | 2 | 0 | 0 |
| honest-trial-input | in | 6 | 6 | 0 | 0 |
| honest-trial-input | out | 6 | 6 | 0 | 0 |
| honest-trial-input | free | 2 | 2 | 0 | 0 |
| study-checkpoint | in | 6 | 6 | 0 | 0 |
| study-checkpoint | out | 6 | 6 | 0 | 0 |
| study-checkpoint | free | 2 | 2 | 0 | 0 |
| heldout-receiver-input | in | 6 | 6 | 0 | 0 |
| heldout-receiver-input | out | 6 | 6 | 0 | 0 |
| heldout-receiver-input | free | 2 | 2 | 0 | 0 |
| visibility-eligible-targets | in | 6 | 6 | 0 | 0 |
| visibility-eligible-targets | out | 6 | 6 | 0 | 0 |
| visibility-eligible-targets | free | 2 | 2 | 0 | 0 |
| honest-parse-assignment | in | 6 | 6 | 0 | 0 |
| honest-parse-assignment | out | 6 | 6 | 0 | 0 |
| honest-parse-assignment | free | 2 | 2 | 0 | 0 |
| study-ensure-published | in | 6 | 2 | 4 | 0 |
| study-ensure-published | out | 6 | 0 | 6 | 0 |
| study-ensure-published | free | 2 | 0 | 2 | 0 |
| heldout-decoded-correct | in | 6 | 0 | 6 | 0 |
| heldout-decoded-correct | out | 6 | 0 | 6 | 0 |
| heldout-decoded-correct | free | 2 | 0 | 2 | 0 |
| visibility-validate-registration | in | 6 | 0 | 6 | 0 |
| visibility-validate-registration | out | 6 | 0 | 6 | 0 |
| visibility-validate-registration | free | 2 | 0 | 2 | 0 |
| honest-equivalence | in | 6 | 0 | 6 | 0 |
| honest-equivalence | out | 6 | 0 | 6 | 0 |
| honest-equivalence | free | 2 | 0 | 2 | 0 |
| reserve-study-parse-assignment | in | 6 | 0 | 6 | 0 |
| reserve-study-parse-assignment | out | 6 | 0 | 6 | 0 |
| reserve-study-parse-assignment | free | 2 | 0 | 2 | 0 |
| reserve-heldout-summarize | in | 6 | 0 | 6 | 0 |
| reserve-heldout-summarize | out | 6 | 0 | 6 | 0 |
| reserve-heldout-summarize | free | 2 | 0 | 2 | 0 |
| reserve-visibility-summary | in | 6 | 0 | 6 | 0 |
| reserve-visibility-summary | out | 6 | 0 | 6 | 0 |
| reserve-visibility-summary | free | 2 | 0 | 2 | 0 |
| reserve-honest-summarize | in | 6 | 0 | 6 | 0 |
| reserve-honest-summarize | out | 6 | 0 | 6 | 0 |
| reserve-honest-summarize | free | 2 | 0 | 2 | 0 |

## A. Registered analysis applied to the pilot

Selected valid tasks: 8. Registered outcome: **INCONCLUSIVE**. The registration requires at least 10 valid tasks. These pilot estimates and p-value are not confirmatory.

| Measure | Equal-task mean | 95% task bootstrap interval | N tasks |
| --- | ---: | --- | ---: |
| K_in | 0.5208333333333334 | [0.375, 0.7083333333333334] | 8 |
| K_out | 0.0 | [0.0, 0.0] | 8 |
| R_add | 1.0 | [1.0, 1.0] | 8 |
| delta | 0.5208333333333334 | [0.375, 0.7083333333333334] | 8 |

Exact one-sided sign-flip p: 0.00390625.
K_alt: 0.28125; interval [0.0625, 0.5625]; N = 8; fixed-rule outcome: **unresolved**.

All four reserves were attempted in order. None was valid. The registered selection therefore retained the eight valid primaries, without including unused or invalid reserves in the estimates.

```json
[
  {
    "invalid_primary": "study-ensure-published",
    "reason": "fewer than 5 accepted incoming-pair calls in at least one input group",
    "reserve": "reserve-study-parse-assignment",
    "reserve_valid": false
  },
  {
    "invalid_primary": "study-ensure-published",
    "reason": "fewer than 5 accepted incoming-pair calls in at least one input group",
    "reserve": "reserve-heldout-summarize",
    "reserve_valid": false
  },
  {
    "invalid_primary": "study-ensure-published",
    "reason": "fewer than 5 accepted incoming-pair calls in at least one input group",
    "reserve": "reserve-visibility-summary",
    "reserve_valid": false
  },
  {
    "invalid_primary": "study-ensure-published",
    "reason": "fewer than 5 accepted incoming-pair calls in at least one input group",
    "reserve": "reserve-honest-summarize",
    "reserve_valid": false
  }
]
```

### Registered descriptives

```json
{
  "overall_keep_rate_task_mean": {
    "mean": 0.2604166666666667,
    "interval_95": [
      0.1875,
      0.3541666666666667
    ],
    "n_tasks": 8
  },
  "free_pair_share_task_mean": {
    "mean": 0.9017857142857143,
    "interval_95": [
      0.8303571428571428,
      0.9642857142857143
    ],
    "n_tasks": 8
  },
  "by_target": {
    "A": {
      "K_in": 0.9166666666666667,
      "K_out": 0.0,
      "R_add": 1.0,
      "delta": 0.9166666666666667
    },
    "B": {
      "K_in": 0.41666666666666663,
      "K_out": 0.0,
      "R_add": 1.0,
      "delta": 0.41666666666666663
    },
    "C": {
      "K_in": 0.3333333333333333,
      "K_out": 0.0,
      "R_add": 1.0,
      "delta": 0.3333333333333333
    },
    "D": {
      "K_in": 0.41666666666666663,
      "K_out": 0.0,
      "R_add": 1.0,
      "delta": 0.41666666666666663
    }
  }
}
```

Per-task rates, output distributions, free-choice agreement, free-pair shares and their denominators are retained in section A of `pilot_scores.json`. The notes are saved in raw traces and were not scored.

## B. exploratory, not registered

Agreement below requires both replicates to be gate-accepted; two missing answers do not count as agreement. Output distributions count accepted pairs only; rejections are counted separately. Free-choice shares are undefined when the two free-choice calls do not both produce the same accepted pair. P90 uses nearest rank over recorded values. Missing usage is reported, never imputed.

### Primaries

12 tasks; 168 calls.

```json
{
  "agreement": {
    "scheduled_pairs": 72,
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
  },
  "rejection_reason_counts": {
    "You\u2019ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 3:34 AM.": 54,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665733ce2e7f6e-MAA)": 1,
    "Reconnecting... 3/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a566573c9ea77ebc-MAA)": 1,
    "Reconnecting... 4/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a566574739f02e35-MAA)": 1,
    "Reconnecting... 5/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665756cdac570c-MAA)": 1,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665736d9bc2e35-MAA)": 1,
    "Reconnecting... 3/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56657403bdd182b-MAA)": 1,
    "Reconnecting... 4/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a566574b6cce7f4b-MAA)": 1,
    "Reconnecting... 5/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a566575b6cf8b2a0-MAA)": 1,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a566579a09577e9e-MAA)": 1,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665798ac8096a8-MAA)": 1,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665797ed4a2e35-MAA)": 1,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665799ec3ab291-MAA)": 1
  }
}
```

| Runtime or usage field | Recorded | Missing | Mean | Median | P90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| wall_seconds | 168 | 0 | 13.40970238095238 | 16.21 | 19.09 |
| tool_calls | 168 | 0 | 1.9761904761904763 | 3.0 | 3 |
| cache_write_input_tokens | 114 | 54 | 0 | 0.0 | 0 |
| cached_input_tokens | 114 | 54 | 52514.80701754386 | 54016.0 | 66304 |
| input_tokens | 114 | 54 | 70906.28070175438 | 71673.5 | 83381 |
| output_tokens | 114 | 54 | 320.3333333333333 | 325.0 | 370 |
| reasoning_output_tokens | 114 | 54 | 1.2280701754385965 | 0.0 | 0 |

| Task | Input | Accepted output distribution | Rejected | Timeout | r1, r2 outputs | Agreement |
| --- | --- | --- | ---: | ---: | --- | --- |
| study-label-commitment | AB | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| study-label-commitment | AC | {"AC": 2} | 0 | 0 | ['AC', 'AC'] | True |
| study-label-commitment | AD | {"AD": 2} | 0 | 0 | ['AD', 'AD'] | True |
| study-label-commitment | BC | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| study-label-commitment | BD | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| study-label-commitment | CD | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| study-label-commitment | free | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| heldout-codeword | AB | {"BC": 2} | 0 | 0 | ['BC', 'BC'] | True |
| heldout-codeword | AC | {"BC": 1, "BD": 1} | 0 | 0 | ['BC', 'BD'] | False |
| heldout-codeword | AD | {"BC": 2} | 0 | 0 | ['BC', 'BC'] | True |
| heldout-codeword | BC | {"BC": 2} | 0 | 0 | ['BC', 'BC'] | True |
| heldout-codeword | BD | {"BD": 1, "BC": 1} | 0 | 0 | ['BD', 'BC'] | False |
| heldout-codeword | CD | {"BC": 2} | 0 | 0 | ['BC', 'BC'] | True |
| heldout-codeword | free | {"BC": 2} | 0 | 0 | ['BC', 'BC'] | True |
| visibility-public-decoded | AB | {"BC": 2} | 0 | 0 | ['BC', 'BC'] | True |
| visibility-public-decoded | AC | {"BC": 2} | 0 | 0 | ['BC', 'BC'] | True |
| visibility-public-decoded | AD | {"BC": 2} | 0 | 0 | ['BC', 'BC'] | True |
| visibility-public-decoded | BC | {"BC": 2} | 0 | 0 | ['BC', 'BC'] | True |
| visibility-public-decoded | BD | {"BC": 2} | 0 | 0 | ['BC', 'BC'] | True |
| visibility-public-decoded | CD | {"BC": 2} | 0 | 0 | ['BC', 'BC'] | True |
| visibility-public-decoded | free | {"BC": 2} | 0 | 0 | ['BC', 'BC'] | True |
| honest-trial-input | AB | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| honest-trial-input | AC | {"CD": 1, "BD": 1} | 0 | 0 | ['CD', 'BD'] | False |
| honest-trial-input | AD | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| honest-trial-input | BC | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| honest-trial-input | BD | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| honest-trial-input | CD | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| honest-trial-input | free | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| study-checkpoint | AB | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| study-checkpoint | AC | {"AB": 1, "AC": 1} | 0 | 0 | ['AB', 'AC'] | False |
| study-checkpoint | AD | {"AD": 2} | 0 | 0 | ['AD', 'AD'] | True |
| study-checkpoint | BC | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| study-checkpoint | BD | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| study-checkpoint | CD | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| study-checkpoint | free | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| heldout-receiver-input | AB | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| heldout-receiver-input | AC | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| heldout-receiver-input | AD | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| heldout-receiver-input | BC | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| heldout-receiver-input | BD | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| heldout-receiver-input | CD | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| heldout-receiver-input | free | {"AB": 2} | 0 | 0 | ['AB', 'AB'] | True |
| visibility-eligible-targets | AB | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| visibility-eligible-targets | AC | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| visibility-eligible-targets | AD | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| visibility-eligible-targets | BC | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| visibility-eligible-targets | BD | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| visibility-eligible-targets | CD | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| visibility-eligible-targets | free | {"CD": 2} | 0 | 0 | ['CD', 'CD'] | True |
| honest-parse-assignment | AB | {"AD": 2} | 0 | 0 | ['AD', 'AD'] | True |
| honest-parse-assignment | AC | {"AD": 2} | 0 | 0 | ['AD', 'AD'] | True |
| honest-parse-assignment | AD | {"AD": 2} | 0 | 0 | ['AD', 'AD'] | True |
| honest-parse-assignment | BC | {"AD": 2} | 0 | 0 | ['AD', 'AD'] | True |
| honest-parse-assignment | BD | {"AD": 1, "BD": 1} | 0 | 0 | ['AD', 'BD'] | False |
| honest-parse-assignment | CD | {"AD": 2} | 0 | 0 | ['AD', 'AD'] | True |
| honest-parse-assignment | free | {"AD": 2} | 0 | 0 | ['AD', 'AD'] | True |
| study-ensure-published | AB | {"AB": 1} | 1 | 0 | ['AB', None] | None |
| study-ensure-published | AC | {"AC": 1} | 1 | 0 | ['AC', None] | None |
| study-ensure-published | AD | {} | 2 | 0 | [None, None] | None |
| study-ensure-published | BC | {} | 2 | 0 | [None, None] | None |
| study-ensure-published | BD | {} | 2 | 0 | [None, None] | None |
| study-ensure-published | CD | {} | 2 | 0 | [None, None] | None |
| study-ensure-published | free | {} | 2 | 0 | [None, None] | None |
| heldout-decoded-correct | AB | {} | 2 | 0 | [None, None] | None |
| heldout-decoded-correct | AC | {} | 2 | 0 | [None, None] | None |
| heldout-decoded-correct | AD | {} | 2 | 0 | [None, None] | None |
| heldout-decoded-correct | BC | {} | 2 | 0 | [None, None] | None |
| heldout-decoded-correct | BD | {} | 2 | 0 | [None, None] | None |
| heldout-decoded-correct | CD | {} | 2 | 0 | [None, None] | None |
| heldout-decoded-correct | free | {} | 2 | 0 | [None, None] | None |
| visibility-validate-registration | AB | {} | 2 | 0 | [None, None] | None |
| visibility-validate-registration | AC | {} | 2 | 0 | [None, None] | None |
| visibility-validate-registration | AD | {} | 2 | 0 | [None, None] | None |
| visibility-validate-registration | BC | {} | 2 | 0 | [None, None] | None |
| visibility-validate-registration | BD | {} | 2 | 0 | [None, None] | None |
| visibility-validate-registration | CD | {} | 2 | 0 | [None, None] | None |
| visibility-validate-registration | free | {} | 2 | 0 | [None, None] | None |
| honest-equivalence | AB | {} | 2 | 0 | [None, None] | None |
| honest-equivalence | AC | {} | 2 | 0 | [None, None] | None |
| honest-equivalence | AD | {} | 2 | 0 | [None, None] | None |
| honest-equivalence | BC | {} | 2 | 0 | [None, None] | None |
| honest-equivalence | BD | {} | 2 | 0 | [None, None] | None |
| honest-equivalence | CD | {} | 2 | 0 | [None, None] | None |
| honest-equivalence | free | {} | 2 | 0 | [None, None] | None |

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
| study-ensure-published | None | False | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} |
| heldout-decoded-correct | None | False | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} |
| visibility-validate-registration | None | False | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} |
| honest-equivalence | None | False | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} |

### Reserves

4 tasks; 56 calls.

```json
{
  "agreement": {
    "scheduled_pairs": 24,
    "both_accepted_pairs": 0,
    "agreeing_pairs": 0,
    "rate_among_comparable": null
  },
  "equal_free_pair_by_input_group": {
    "in": {
      "equal_free_pair": 0,
      "accepted_denominator": 0,
      "pooled_share": null,
      "equal_task_mean": null,
      "defined_tasks": 0
    },
    "out": {
      "equal_free_pair": 0,
      "accepted_denominator": 0,
      "pooled_share": null,
      "equal_task_mean": null,
      "defined_tasks": 0
    }
  },
  "rejection_reason_counts": {
    "You\u2019ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 3:34 AM.": 56,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658b08ddc322e-CJB)": 1,
    "Reconnecting... 3/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658b9ee467d39-CJB)": 1,
    "Reconnecting... 4/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658c5d849322e-CJB)": 1,
    "Reconnecting... 5/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658d6cb40d8de-CJB)": 1,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658afc9559215-CJB)": 1,
    "Reconnecting... 3/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658b92d949215-CJB)": 1,
    "Reconnecting... 4/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658c52ceed5da-CJB)": 1,
    "Reconnecting... 5/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658d51fcb7d39-CJB)": 1,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658b48d4afbfd-CJB)": 1,
    "Reconnecting... 3/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658bdb84fd5da-CJB)": 1,
    "Reconnecting... 4/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658c96804d5da-CJB)": 1,
    "Reconnecting... 5/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658da6aa1498d-CJB)": 1,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658b7babde730-CJB)": 1,
    "Reconnecting... 3/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658c17ff01967-CJB)": 1,
    "Reconnecting... 4/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658ccef2949be-CJB)": 1,
    "Reconnecting... 5/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56658dd0f7e6cbd-CJB)": 1,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a566590ea9592d42-MAA)": 1,
    "Reconnecting... 3/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a56659173861c08d-MAA)": 1,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665915dc65c784-MAA)": 1,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665a319def9138-MAA)": 1,
    "Reconnecting... 3/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665a39ee107f69-MAA)": 1,
    "Reconnecting... 4/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665a454e6d8031-MAA)": 1,
    "Reconnecting... 5/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665a56aa37dc0a-MAA)": 1,
    "Reconnecting... 2/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665a313f0ca92f-MAA)": 1,
    "Reconnecting... 3/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665a39feaf802b-MAA)": 1,
    "Reconnecting... 4/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665a44b9ba17a0-MAA)": 1,
    "Reconnecting... 5/5 (unexpected status 403 Forbidden: Unknown error, url: wss://chatgpt.com/backend-api/codex/responses, cf-ray: a5665a54c981b2ac-MAA)": 1
  }
}
```

| Runtime or usage field | Recorded | Missing | Mean | Median | P90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| wall_seconds | 56 | 0 | 6.049107142857142 | 4.695 | 15.49 |
| tool_calls | 56 | 0 | 0 | 0.0 | 0 |
| token_usage | 0 | 56 | None | None | None |

| Task | Input | Accepted output distribution | Rejected | Timeout | r1, r2 outputs | Agreement |
| --- | --- | --- | ---: | ---: | --- | --- |
| reserve-study-parse-assignment | AB | {} | 2 | 0 | [None, None] | None |
| reserve-study-parse-assignment | AC | {} | 2 | 0 | [None, None] | None |
| reserve-study-parse-assignment | AD | {} | 2 | 0 | [None, None] | None |
| reserve-study-parse-assignment | BC | {} | 2 | 0 | [None, None] | None |
| reserve-study-parse-assignment | BD | {} | 2 | 0 | [None, None] | None |
| reserve-study-parse-assignment | CD | {} | 2 | 0 | [None, None] | None |
| reserve-study-parse-assignment | free | {} | 2 | 0 | [None, None] | None |
| reserve-heldout-summarize | AB | {} | 2 | 0 | [None, None] | None |
| reserve-heldout-summarize | AC | {} | 2 | 0 | [None, None] | None |
| reserve-heldout-summarize | AD | {} | 2 | 0 | [None, None] | None |
| reserve-heldout-summarize | BC | {} | 2 | 0 | [None, None] | None |
| reserve-heldout-summarize | BD | {} | 2 | 0 | [None, None] | None |
| reserve-heldout-summarize | CD | {} | 2 | 0 | [None, None] | None |
| reserve-heldout-summarize | free | {} | 2 | 0 | [None, None] | None |
| reserve-visibility-summary | AB | {} | 2 | 0 | [None, None] | None |
| reserve-visibility-summary | AC | {} | 2 | 0 | [None, None] | None |
| reserve-visibility-summary | AD | {} | 2 | 0 | [None, None] | None |
| reserve-visibility-summary | BC | {} | 2 | 0 | [None, None] | None |
| reserve-visibility-summary | BD | {} | 2 | 0 | [None, None] | None |
| reserve-visibility-summary | CD | {} | 2 | 0 | [None, None] | None |
| reserve-visibility-summary | free | {} | 2 | 0 | [None, None] | None |
| reserve-honest-summarize | AB | {} | 2 | 0 | [None, None] | None |
| reserve-honest-summarize | AC | {} | 2 | 0 | [None, None] | None |
| reserve-honest-summarize | AD | {} | 2 | 0 | [None, None] | None |
| reserve-honest-summarize | BC | {} | 2 | 0 | [None, None] | None |
| reserve-honest-summarize | BD | {} | 2 | 0 | [None, None] | None |
| reserve-honest-summarize | CD | {} | 2 | 0 | [None, None] | None |
| reserve-honest-summarize | free | {} | 2 | 0 | [None, None] | None |

| Task | Free pair | Free agreement | Target-in free-pair share | Target-out free-pair share |
| --- | --- | --- | --- | --- |
| reserve-study-parse-assignment | None | False | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} |
| reserve-heldout-summarize | None | False | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} |
| reserve-visibility-summary | None | False | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} |
| reserve-honest-summarize | None | False | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} | {'equal_free_pair': None, 'accepted_denominator': 0, 'share': None} |

## Failures and deviations

- Reserve scheduling was conditional on task invalidity, not unconditional. All four reserves have saved calls, but none qualified as a valid replacement.
- The registration was committed before the calls but was not published before the run. All analyses here are of a pilot, not a confirmatory experiment.
- The earlier freeze request described an incomplete schedule and no reserves. Its inventory showed all 224 scheduled trace filenames. Those requested statements were not adopted.
- The original runner kept the 110 rejected calls and continued through the registered primary/reserve schedule. Their saved terminal error events report a usage-limit failure. Some traces also contain CLI-internal reconnect attempts and 403 errors, listed verbatim in the exploratory reason records. The harness did not launch replacement attempts for a saved call; it used only the registered reserve rule.
- The original Step 0 command had a working-directory error before its actual checks; the corrected preconditions passed. No failed pytest test was recorded.
- Earlier HTTPS authentication and an SSH authentication check failed. After the user authenticated, the exact history was pushed without force or rewritten commits. No matching repository PushEvent was available when queried; the first push time is local UTC captured immediately after success.
- JSON cannot begin with an unquoted prose status line and remain valid. `pilot_scores.json` therefore carries the required status as its first `status` field; this Markdown file starts with the literal required line.
- Bootstrap denominator and percentile conventions were fixed in the original registration/execution record before calls. K_alt uses eligible task-level rates. No scoring formula was changed for this pilot report.

No new model calls, overwritten traces, new registration, or D2 work occurred. The smoke test remains excluded.

## Final checks after the pilot-results push

The full offline suite passed **95 tests, 0 failed, 0 skipped**. All **86** prior-work manifest entries still match their SHA-256 hashes and byte counts. All **224** pilot traces still match the frozen inventory. The task workspace remains pinned, has empty Git porcelain status under the documented fixture exclusion, and its four refs retain the expected hash. The original DogWhistle checkout also has empty porcelain status. No new model calls were made. Exact output and check details are in `PILOT_FINAL_PYTEST.txt` and `PILOT_FINAL_CHECKS.json`.

```text
........................................................................ [ 75%]
.......................                                                  [100%]
95 passed in 0.77s
```
