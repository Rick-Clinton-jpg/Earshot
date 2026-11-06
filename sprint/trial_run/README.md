# Frozen trial run

Current descriptive report: [TRIAL_RUN_RESULTS.md](TRIAL_RUN_RESULTS.md). Machine-readable summary: [trial_run_scores.json](trial_run_scores.json).

There are 114 answer-producing records in `traces/` and 110 usage-limit diagnostic records in `system_issue/`. The latter are not agent results or gate rejections. `PATH_MAP.json` maps all original trace paths to these locations and hashes them against the inventory in commit `424528e`.

`D1_registration.json`, `D1_REGISTRATION.md`, `D1_EXECUTION.md`, `UNSEALED_RUN.*`, `PILOT_PUSH_HISTORY.json` and `PILOT_FINAL_*` are archived records of the earlier labels and execution history. Their historical paths refer to Git objects from that period. Current filesystem resolution uses `PATH_MAP.json`. The archived registration is not a sealed D1 registration and must not launch another run; the old live entrypoint is disabled.

The excluded one-call smoke test remains at `sprint/partD/smoke/`, outside the 224-record inventory. No original trace bytes were changed by this reclassification.
