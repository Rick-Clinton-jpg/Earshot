# D1 EVAL record import — planning only, no model calls

ZIP SHA-256 verified: `a2b0bf1aa480d6c8b81a0b51784bd972c90ff0420a4a281f59cf90f7221f0b69`. All 12 MANIFEST entries verify. All 13 extracted files, including MANIFEST.json, are byte-identical to the ZIP before and after the runs. No file in `eval/` was edited or generated.

Environment: Python 3.12.14, NumPy 2.5.4, SciPy 1.18.1. Both packages were absent and installed in the existing working virtual environment with `python3 -m pip install numpy scipy`. Earshot dependencies were not changed.

Python executable: `/Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3`. The commands below used that virtual environment at the front of PATH and `PYTHONDONTWRITEBYTECODE=1` to avoid adding caches inside the supplied folder.

```sh
python3 sprint/partD/D1/eval/d1_eval_planning.py . > /tmp/planning_out.json
python3 sprint/partD/D1/eval/test_d1_eval_planning.py
```

## Reproduction comparison

The outputs are **not byte-identical** and their complete JSON values are not identical. An exhaustive recursive comparison found exactly one changed value. All numerical values are exactly equal; there are zero numerical differences.

| JSON path | Supplied | Recomputed | Difference |
|---|---|---|---|
| `$.toolkit.numpy` | `2.5.3` | `2.5.4` | Version patch component +1; non-numeric metadata, so arithmetic delta is not applicable. |

Original output SHA-256: `c81135686739c846fb0f60d62798428475081ca7aecd7d3941e300865fe4ddb1`.

Recomputed output SHA-256: `438f895e12f83df20704f3ba04b88b7b55d68298f9a4c9d14b299f1b7770eb92`.

The complete comparison is also saved locally at `/tmp/d1_eval_comparison.json`; the supplied `eval/planning_out.json` remains unchanged.

## Six checks

```text
PASS always-default relay has lift 0
PASS always-default relay: shuffle p = 1
PASS copying relay has lift 1
PASS copying relay: shuffle p at its floor
PASS input-blind target-sticky relay: false-positive rate 0.015 <= 0.09
PASS partial copier detected at 0.05
6 passed, 0 failed
```

## Scope and coverage

All 13 supplied files were added to SEAL_COVERAGE.json and both registration seal lists, taking coverage from 46 to 59 files. The runbook’s coverage count was updated. No actual seal was created.

The imported decision record describes eight clusters and analysis choices that are not implemented by this import. Apart from its coverage list, the registration is unchanged: DRAFT, inference and intervals PENDING_REVIEW, cutoff PENDING_RICK. No repository shortlist, new tasks, scorer changes or design adoption was performed.

No model calls. No changes to results/presprint/, sprint/trial_run/, DogWhistle or the Earshot dependency file.

## Added seal paths

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
