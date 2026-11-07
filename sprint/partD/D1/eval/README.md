# EVAL record for D1

This folder records how D1's design was chosen. EVAL was run on the trial run's traces before any D1 call, and the numbers it produced set D1's measures, its cluster count and its analysis plan. The folder is meant to be included in D1's Seal 1, so the reasoning is sealed before the data exist.

| File | What it is |
|---|---|
| `EVAL_D1_DESIGN.md` | The EVAL report: findings, design, module checks, hand-checks, assumptions |
| `DECISIONS.md` | Append-only log of the decisions taken on that evidence, and the ones still open |
| `eval_profile_v1.json`, `route_output_v1.md` | The profile and routing for D1 as first drafted (4 clusters) |
| `eval_profile_v2.json`, `route_output_v2.md` | The same after decision 1B (8 clusters) |
| `d1_eval_planning.py` | Computes every number in the report from `sprint/trial_run/traces/` |
| `planning_out.json` | Its output |
| `test_d1_eval_planning.py` | Checks for the two methods not taken from a cited source: lift and the shuffle test |
| `vendor/evalstats.py`, `vendor/SOURCE.md` | A copy of the EVAL toolkit's statistics library, with its hash and test results |
| `MANIFEST.json` | SHA-256 of every file here |

**Re-run** from the Earshot repository root (needs numpy and scipy):

```sh
python3 sprint/partD/D1/eval/d1_eval_planning.py . > /tmp/planning_out.json
python3 sprint/partD/D1/eval/test_d1_eval_planning.py
```

The output should match `planning_out.json`. The random parts use fixed seeds, so small differences can only come from different numpy or scipy versions. The original run used numpy 2.5.3 and scipy 1.18.1.

No model was called to produce anything in this folder. The trial run is not part of D1; it is used here only for planning.
