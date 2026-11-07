# D1 scoring

This folder scores D1 exactly as registered in `sprint/partD/D1/D1_registration.json`, Seal 1 (`174be2c41d36960190ec8936fa7b781beb28acf74e27c4e6fbaedf6d81cfc4f8`).

## Inputs

| Arm | Branch and results commit | Ledger digest | Traces |
|---|---|---|---|
| Codex (`gpt-6.1-sol`) | `main` at `57f7708` | `76a63a226a451123904e6c4bcd9ac85849a64976f3072e83b198677c70a42913` | 180, all accepted |
| Claude (`claude-sonnet-5-5`) | `d1-claude` at `421e561` | `b0748726deaba21faafc976d8dcc3a7e17ffb5dba1a07b5ec7190c5d9bcd3f5f` | 180, all accepted |

## How it was produced

1. **Sealed scorer.** `earshot.d1v2_score` was run unchanged on each arm. It re-verifies the seal and the ledger, then produces the registered task summaries, task validity and task selection. All 12 primary tasks are valid in both arms. Its output is `sealed_scorer_codex.json` and `sealed_scorer_claude.json`.
2. **`score_d1.py`.** This computes the confirmatory claims, intervals, contrasts, cross-arm differences and the exploratory family. Every registered statistic calls a sealed function unchanged: `evalstats.bayes_clustered_ci`, `t_ci`, `sign_flip_test`, `design_effect` and `benjamini_hochberg`, plus `d1_eval_planning.task_lift` and `shuffle_test`. The script itself only selects, counts and arranges inputs.
3. **Consistency check.** Before any result was read, the script's own per-task K, K_in, K_out, R_add, K_alt, C_in, C_out, C and Δ were compared with the sealed scorer's for all 24 task-arm pairs: 0 mismatches.

**Disclosure:** `score_d1.py` was written after both arms finished and both ledgers were verified, but before any D1 measure was computed. The registration fixes the method; this script implements it. A few choices are not fully specified by the registration and are labelled exploratory: lift split by target-in and target-out pairs, the tests and nulls in the exploratory family, and the signal-to-noise diagnostic.

**Environment:** Python 3.13.18, numpy 2.5.3, scipy 1.18.1.

**Where the statistics live.** The interval and test methods are not in this folder. They are in the sealed files that `score_d1.py` imports, and checking these numbers end to end needs those files:

| File | SHA-256 in Seal 1 |
|---|---|
| `sprint/partD/D1/eval/vendor/evalstats.py` | `2ced334a0fc6ebbeeacae1eec4585ac24b9bc306e2a361c03a452d84de78650b` |
| `sprint/partD/D1/eval/d1_eval_planning.py` | `82f25d3f89262b9466640d0c4b0d2ee7880e0613bdea20961e660252fbab49a9` |
| `earshot/d1v2_score.py` | `669a70928d416c266b639ae170ccd50aeef62fb6d9260d3773aee221921467e2` |

`bayes_clustered_ci` is hierarchical: it treats files as a source of variation. Its intervals are therefore wider than a calculation that holds the four files fixed. That is intended for claims resting on 4 clusters.

## Re-run

Check out each branch at its commit and run the sealed scorer, for example for the Codex arm:

```
python3 -m earshot.d1v2_score --repo . --branch main --registration sprint/partD/D1/D1_registration.json --seal sprint/partD/D1/SEAL1.json --seal-digest sprint/partD/D1/SEAL1.sha256 --ledger sprint/partD/D1/codex_LEDGER.json --ledger-digest sprint/partD/D1/codex_LEDGER.sha256 --run-dir sprint/partD/D1/codex > OUT/sealed_scorer_codex.json
```

For the Claude arm, use `--branch d1-claude` and replace `codex` with `claude`. Then run:

```
python3 score_d1.py <main checkout> <d1-claude checkout> OUT
```

`OUT/D1_SCORES.json` must match `D1_SCORES.json` here. The random parts use fixed seeds; different numpy or scipy versions can shift only the last digits of the Beta-Binomial intervals.

## Files

`MANIFEST.json` lists the SHA-256 of every file in this folder. `D1_RESULTS.md` summarises the numbers.
