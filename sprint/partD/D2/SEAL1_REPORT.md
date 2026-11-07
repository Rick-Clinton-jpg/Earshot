# D2 Seal 1 verification report — no model calls

This report is committed only on `d2-seal1-report`. `main` and `d2-claude` remain at Seal 1. No runner was started and no model call was made. The E2E check used scripted executors; temporary test fixtures are not study seals or observations.

## Seal and approval

- **Seal commit:** `2e51a0aced72e944a9a93d7241b93a1785eb1094`.
- **SEAL1.sha256:** `159435d2e2df6571ee19d0d0376c249d323147df58ed0364b3c56c98a4749502`.
- **Sealed files:** **135**.
- Registration: **REGISTERED**, approved by **Rick** at **2026-11-07T18:14:00+05:30** after `sprint/partD/D2/eval_final/EVAL_D2_FINAL.md`.
- Final EVAL SHA-256: `c2df5bf5866e53215a7ae4b1f016856b01b2d03a4e08fa87a0992723ed17378a`.
- Seal commit message: `D2: Seal 1 registration (Radon; harness-planted codewords; no model calls)`.

Only registration status, the approval record and four final-EVAL coverage paths changed in the registration. No experimental rule or stage code changed. Seal JSON contains exactly the registration's sorted 135 paths. Its digest file has the SHA-256 followed by one newline. Before writing it, every listed path existed and its Git index bytes matched the sealed bytes. No listed path is inside a run, traces, runtime, attempt, system-issue, stopped or configuration-fault folder. This report is deliberately outside the seal and outside main's commit history after Seal 1.

## Final EVAL import and rerun

- ZIP SHA-256 verified before import: `1e570aed433ba8bbf988b0883468c9bee02aa2525982415d79ee0d78d66ea2e2`.
- All three manifest entries and the four-file folder inventory verified. Imported bytes, including supplied `e2e_out.json`, remain unchanged.
- Command, from the main checkout's root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3 sprint/partD/D2/eval_final/e2e_check.py . sprint/partD/D2/sim > /tmp/earshot_d2_task9_e2e_stdout.txt
```

Exit **0**, ending with **E2E CROSS-CHECK PASSED**. Actual output is **byte-identical** to the supplied `e2e_out.json`.

Both outputs' SHA-256: `28569cef7ceab9ca73e2c4c798d00a94051afed296d5bc1576f135a36a623235`. Differences: **none**, including decisions. Across three synthetic scenarios the check compares 432 values and 24 confirmatory decisions. The rerun reproduces the supplied record; these scenarios are not real D2 data or new power estimates. The supplied output includes the final PASSED line and was compared in full, without reformatting.

## Tests and the only updated test

**255 tests passed, 0 failed** before sealing: 247 configured repository tests plus 8 supplied simulation tests. Existing D1 tests and prior-work integrity checks passed.

```sh
PYTHONDONTWRITEBYTECODE=1 EARSHOT_TEST_WORKSPACE=/Users/gho5t/Documents/Codex/2026-11-04/i/work/earshot_d1_isolated/workspace /Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3 -m pytest -q -p no:cacheprovider tests sprint/partD/D2/sim/test_sim_c.py
```

Only **`tests/test_d2.py::test_relay_cli_and_draft_guard`** changed. It now makes a temporary copy of the real registration, sets that copy's status to DRAFT and points the CLI test at it. Its assertions are unchanged: the draft is refused before backend creation, no runtime directory is created, and the obsolete phase is rejected. No other test changed.

Every Python execution used `PYTHONDONTWRITEBYTECODE=1`; pytest disabled the cache provider. No cache files were created in D2. All 59 D1 sealed files remain hash-identical. The 13 role-check records and calibration records remain unchanged. Python/environment: 3.12.14; NumPy 2.5.4; SciPy 1.18.1; jsonschema 4.26.0; pytest 9.2.0. No dependencies were changed.

## Published-branch and workspace verification

The function called in each checkout was:

```python
verify_phase(repo, branch, SEAL1, SEAL1_DIGEST, registration, 'relay')
```

| Checkout branch | seal_1_commit | phase_commit | Result |
|---|---|---|---|
| main | `2e51a0aced72e944a9a93d7241b93a1785eb1094` | `2e51a0aced72e944a9a93d7241b93a1785eb1094` | PASSED |
| d2-claude | `2e51a0aced72e944a9a93d7241b93a1785eb1094` | `2e51a0aced72e944a9a93d7241b93a1785eb1094` | PASSED |

Main checkout: `/Users/gho5t/Documents/Codex/2026-11-04/i/work/Earshot_foundation`.

Separate Claude worktree: `/Users/gho5t/Documents/Codex/2026-11-04/i/work/Earshot_d2_claude_sealed`.

In **both** checkouts, `earshot.d2_integrity.ready(registration, patterns)` passed, and D1's `earshot.d1v2.verify_workspace(workspace, task_data)` passed on `/Users/gho5t/Documents/Codex/2026-11-04/i/work/earshot_d2_isolated/workspace` at Radon `54b88e5878b2724bf4d77f97349588b811abdff2`. The workspace is clean, all four candidate hashes match, the four identical refs match, and the parent contains only the workspace. Both branch checkouts were clean after verification.

No D2 runtime checkpoint branch was created. No report commit was added to main. Approval to seal was used only for sealing and verification; no model run has started.
