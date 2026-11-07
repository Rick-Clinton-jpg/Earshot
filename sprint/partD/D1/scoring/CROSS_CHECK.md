# D1 scoring independent cross-check — no model calls

## Input verification

ZIP SHA-256 matches `2179bfbb53cc13ab6d425d465e1233964115d30ac9c05e7c15a38edf662d5b51`. All seven MANIFEST entries match byte counts and SHA-256. All eight supplied files, including MANIFEST.json, remain byte-identical to the ZIP. This CROSS_CHECK.md is the only added file; the imported manifest remains the manifest of the supplied payload.

- Codex input checkout: `main` at `57f77088d200df06d4c67410baa28bf35b243d44`.
- Claude input checkout: `d1-claude` at `421e561fe6a93d0d4d07b125bb3b872657d4ea2a`, created with the requested worktree/checkout commands.
- Both sealed-scorer commands exited 0 after their built-in source-seal and published-ledger checks. The combined scoring command exited 0.

## Environment

Actual rerun: **Python 3.12.14, NumPy 2.5.4, SciPy 1.18.1**. Executable: `/Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3`. No packages or Earshot dependencies were changed for this task. `PYTHONDONTWRITEBYTECODE=1` prevented cache writes outside the scoring folder.

The supplied README reports Python 3.13.18, NumPy 2.5.3, SciPy 1.18.1 for its original execution. That is the source author’s environment record, not an independently reconstructed original environment.

## Commands executed

```sh
git fetch --no-tags origin d1-claude
git worktree add /tmp/earshot_d1_claude origin/d1-claude
git -C /tmp/earshot_d1_claude checkout -B d1-claude origin/d1-claude
```

Main checkout; working directory `/Users/gho5t/Documents/Codex/2026-11-04/i/work/Earshot_foundation`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3 -m earshot.d1v2_score --repo . --branch main --registration sprint/partD/D1/D1_registration.json --seal sprint/partD/D1/SEAL1.json --seal-digest sprint/partD/D1/SEAL1.sha256 --ledger sprint/partD/D1/codex_LEDGER.json --ledger-digest sprint/partD/D1/codex_LEDGER.sha256 --run-dir sprint/partD/D1/codex > /tmp/d1_out/sealed_scorer_codex.json
```

Claude checkout; working directory `/tmp/earshot_d1_claude`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3 -m earshot.d1v2_score --repo . --branch d1-claude --registration sprint/partD/D1/D1_registration.json --seal sprint/partD/D1/SEAL1.json --seal-digest sprint/partD/D1/SEAL1.sha256 --ledger sprint/partD/D1/claude_LEDGER.json --ledger-digest sprint/partD/D1/claude_LEDGER.sha256 --run-dir sprint/partD/D1/claude > /tmp/d1_out/sealed_scorer_claude.json
```

Main checkout; working directory `/Users/gho5t/Documents/Codex/2026-11-04/i/work/Earshot_foundation`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3 sprint/partD/D1/scoring/score_d1.py . /tmp/earshot_d1_claude /tmp/d1_out
```

The output directory was created with `Path("/tmp/d1_out").mkdir(exist_ok=True)` before scoring. On this Mac `/tmp` resolves to `/private/tmp`; these names refer to the same output/worktree paths.

## D1_SCORES.json comparison

**Not byte-identical; not identical as parsed JSON.** An exhaustive recursive comparison found exactly **nine numeric differences**, all in `cross_arm.measures.<measure>.between_arm_task_correlation`. All other values, including intervals, p-values and decision fields, are exactly equal. No tolerance was used to suppress differences.

- Supplied SHA-256: `1e1d441d760dcf8fc71c66f113d5f549f267166f313fde62627240d97264fc95`.
- Rerun SHA-256: `de5254eefec4be204f45d650002cda129800f2542b3bcf66eeed66df1487310d`.

Every differing value is listed below. Paths are beneath `cross_arm.measures`; the changed field in each row is `between_arm_task_correlation`. Delta is **rerun minus supplied**, calculated as the exact decimal difference of the JSON number representations.

| Measure | Supplied value | Rerun value | Signed delta | Absolute delta |
|---|---:|---:|---:|---:|
| `C` | `0.14338313360537125` | `0.1433831336053713` | `5E-17` | `5E-17` |
| `C_in` | `0.12249323753917776` | `0.12249323753917778` | `2E-17` | `2E-17` |
| `K_alt` | `0.19248937327585083` | `0.1924893732758508` | `-3E-17` | `3E-17` |
| `K_in` | `0.3254274041362028` | `0.3254274041362027` | `-1E-16` | `1E-16` |
| `delta` | `0.4097027221239474` | `0.4097027221239476` | `2E-16` | `2E-16` |
| `delta_minus_baseline` | `0.4097027221239476` | `0.4097027221239475` | `-1E-16` | `1E-16` |
| `lift` | `0.1151012461333203` | `0.11510124613332032` | `2E-17` | `2E-17` |
| `lift_in` | `0.19421238053573753` | `0.19421238053573756` | `3E-17` | `3E-17` |
| `run_to_run_agreement` | `0.37962830118264834` | `0.3796283011826482` | `-1.4E-16` | `1.4E-16` |

Largest absolute delta: **2e-16**. These last-digit correlation differences are consistent with floating-point variation between environments; this check does not isolate Python, NumPy, architecture or another numerical-environment component as the cause. The supplied README’s claim about differences being restricted to Beta-Binomial interval digits is not the pattern observed here. The actual differences above are correlations; the interval values match.

## Sealed scorer output hashes

Neither sealed-scorer output is byte-identical to its supplied counterpart. The actual SHA-256 comparisons are:

| File | Supplied SHA-256 | Rerun SHA-256 | Byte-identical |
|---|---|---|---|
| `sealed_scorer_codex.json` | `7894b9730c7bc02c1f2da5426db40bb01de17442a7c3cc06544015ebce9311f3` | `336a9a66fdf71eb28e5250c581b7e8a4dc71cd3d3e5fdcf65a8907a4fbeff3e9` | No |
| `sealed_scorer_claude.json` | `a8656903e4f723e576641a596a89b3069aeaa8074dc9b7c5b58dd0630103cc9e` | `0c3c91c7b14d560c6c5e4c4f2674823c98e43fdc78bbc415a80afa4950cd846a` | No |

Both parsed outputs also differ positionally. To distinguish data changes from sequence ordering, a separate in-memory comparison aligned only these arrays:

- `exposure_audits` by `(name, attempt)`.
- Each task’s `per_call_measures` by call `name`.
- Each task’s `free_pairs` as an unordered multiset (the original occurrence order is deliberately ignored for this diagnostic).

**After this alignment, every value matches in both arms.** This establishes equality of the keyed call records, exposure records, free-pair multisets and remaining summary values; it does not make the saved files byte-identical. No input or output file was rewritten to achieve this comparison. The sealed scorer reads trace globs without sorting, so order can differ across filesystems.

| Output | Raw positional differences: exposure audits | Per-call measures | Free pairs | Other categories | Residual differences after alignment |
|---|---:|---:|---:|---:|---:|
| codex | 194 | 408 | 4 | 0 | 0 |
| claude | 590 | 479 | 4 | 0 | 0 |

## Preserved outputs and scope

Fresh outputs are retained in `/tmp/d1_out/`, including `comparison.json`, which contains every raw positional comparison and all nine D1 score differences. The supplied D1_SCORES.json and both supplied sealed-scorer files in this folder remain unchanged. The original source files, registration, seals, arm data and ledgers are unchanged. Only the scoring folder is added to main.

No model calls, run resumes, scorer modifications, reference-data replacements or analyses beyond the requested reruns were made. This is an independent execution/reproduction cross-check of the supplied scoring code on verified inputs, not a separately implemented statistical audit or independent verification of the source author’s chronology statements.
