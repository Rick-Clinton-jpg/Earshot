# D2 seal preparation — DRAFT, not sealed, no model calls

Task 8 completed on 7 November 2026. No model calls, live probes, D2 study run or study seal were made. All executions used offline calibration, scripted backends, fake CLI fixtures and local bare Git remotes. Temporary integrity-test seal fixtures are not D2 study seals.

## Imported evidence and integrity

- Package SHA-256 verified before import: `e094cdd172779c07aa2c3e316d14fa57551dcb336086ec6e0bf5448343359734`.
- Addendum 3 imported byte-identically: `bcb1c7a249385238c7017c5b5fa5c6ba0a7c00168e7d3da46542c3c12b3f37ca`.
- Fast-forwarded main from `1ca4fd320c194c02b458605af659a90509b89306` to `ccfc663f453aea9ff3af7865650ce55661da90a0`. Confirmed that commit has exactly that one parent and adds only the 13 role-check files. All 13 remain byte-identical to that commit. The failed check is not relabelled.
- Verified all six calibration manifest entries and exact folder inventory. `presprint_annotations.json` matches `docs/PRESPRINT_TEXT_ANNOTATIONS.json` byte for byte. `rolecheck_results.json` matches `role_check/results.json` byte for byte.
- Ran `python3 calibrate.py` inside `sprint/partD/D2/text_calibration/` using the project Python and `PYTHONDONTWRITEBYTECODE=1`. Exit code **0**; every manifest entry remains byte-identical after execution.
- Calibration reproduced 48 pre-sprint annotations: broad coalition 19/24, strict coalition 17/24, broad honest 0/24, strict honest 0/24, with zero per-answer disagreements. All four supplied Claude receiver check labels also matched. These are checks on saved calibration material, not new D2 results or established accuracy on future answers.
- Copied calibrated patterns into `text_check_patterns.json` byte-identically; status CALIBRATED, SHA-256 `273868b53eb7d98004759c2999a2b9da74810ebb85bc388b630e290574be0bfe`.
- All **59 D1 sealed files** remain hash-identical. No presprint files, task definitions, Radon source, frozen formulas, D1 configs or historical role-check records were edited. No Python/pytest cache artifact exists under D2 or in the proposed seal list.

## Implementation

- Removed model sender scheduling, its builder and phase, sender backends, sender-dependent validity and reserve replacement. Spec construction refuses a sender role. Both arms select exactly the 12 primary IDs at initialization and persist that state. Reserves are never scheduled; incompatible saved selection/state is refused.
- Relay calls start immediately. Both hop-1 codewords are planted through the gate's fixed template. Tests compare those relay prompt bytes against a compliant fake sender's gated answer (refs plus discarded note), for both kinds on two tasks. No model sender is used by this test.
- Renamed the CLI phase to `--phase relay`; `sender-relay` is rejected. Free/hop-1/hop-2 order, accepted-chain rules, missing-data rules, per-arm Seal 2, deduplicated receiver scheduling and published-head/source/ledger guards remain in force.
- `ready()` still requires REGISTERED and CALIBRATED. It accepts only role `passed` + family 8, or role `failed` + family 8 with `family_size_reason` naming the approved addendum-3 path and SHA-256. Other roles/families are refused. The actual registration remains **DRAFT**, records the failed check and `ccfc663`, and cannot launch.
- Removed the reduced-family scorer path: exactly eight Holm tests and ten BH exploratory tests remain. Inconclusive entries retain p=1. Calibrated fake dry scores compute H4; decision labels remain `DRY RUN: not a result`. Pending-pattern fake tests still exercise the old pending guard; real-data CLI scoring still refuses pending calibration and retains all publication/ledger checks.
- Added active output labels for the **pre-relay audit** and **pre-relay arms**, including P-d/P-f. Compatibility fields `D_sender`, `audits.sender` and target-minute fields retain their names and are documented to mean pre-relay. Updated RUNBOOK and marked BUILD_REPORT as the historical Task 7 record, with current design guidance at its top. Immutable imported historical records retain their original wording under the explicit amendment precedence.
- Reported the supplied strict text-pattern subset descriptively per receiver answer (`strict_text_flag`); H4 continues to use the calibrated broad flag rule. No extra hypothesis or p-value is introduced.
- Corrected an existing descriptive reporting bug discovered during review: primary-file accuracy included extra-set receiver calls. The registration reserves the extra set for H4 and following measures. Primary accuracy now uses the first set only; a regression test verifies that extra-set accuracy cannot change it. Frozen action/distance/statistical functions and saved outputs were not changed.

## Registration and seal preparation

`D2_registration.json` mirrors the registration and all three addenda, with precedence 3 → 2 → 1 → registration. Its status remains DRAFT. It records the failed role check and source commit, the full family and approved reason, primary-only selection, planted refs, calibrated pattern hash, new budget and pre-relay compatibility terminology.

The proposed `seal_1_files` has **131 paths**. Added frozen `earshot/score.py`, addendum 3, every calibration file and every role-check file, plus the new preparation report and original annotation evidence. Coverage tests traverse repository-owned imports statically, including imports inside functions: 18 reachable earshot modules, the package initializer and the dynamically loaded sealed evalstats module. Schemas, tasks, system-issue patterns, calibrated text patterns and registration are also covered. Runtime state and study trace directories are excluded. Installed standard-library/third-party dependencies are environment dependencies, not repository seal paths; their versions are recorded below. This is a proposed list, not a seal.

## Budget

With every relay call accepted:

- Per primary task: **39–63 scheduled calls** = 3 free + 6 hop-1 + 6 hop-2 + 24–48 receivers.
- Per arm, 12 primaries: **468–756 scheduled calls**.
- Replacement overhead: **0**. No reserves are used.
- System-issue retries: counted separately under the unchanged durable D1 rules. Failed/unaccepted hop-1 calls can reduce hop-2 calls and skip receiver phases under the registered missing-data rules; primary selection never changes.

## Verification and tests

Environment: Python **3.12.14**, NumPy **2.5.4**, SciPy **1.18.1**, jsonschema **4.26.0**, pytest **9.2.0**. No dependency installation or dependency-file changes.

All Python executions used `PYTHONDONTWRITEBYTECODE=1`; pytest used `-p no:cacheprovider`. Tests made no model calls.

- Initial revised D2 suite: **35 passed**.
- Full configured suite after the descriptive reporting correction: **246 passed**.
- Final complete configured suite plus the supplied simulation, including the additional CLI guard test: **255 passed** (247 configured tests + 8 supplied simulation tests), **0 failed**.

Final command, from the repo root:

```sh
PYTHONDONTWRITEBYTECODE=1 EARSHOT_TEST_WORKSPACE=/Users/gho5t/Documents/Codex/2026-11-04/i/work/earshot_d1_isolated/workspace /Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3 -m pytest -q -p no:cacheprovider tests sprint/partD/D2/sim/test_sim_c.py
```

All existing D1 tests, including prior-work integrity checks, passed. Existing D2 missing-data, exact-formula, transparent-control, cutoff, pause/resume, immutable-record, checkpoint, seal-publication and ledger tests still pass.

### Every existing test updated

All are in `tests/test_d2.py`:

| Test | Authorized update |
|---|---|
| `test_schedule` | New 15 relay calls and 39–63 total, retaining distinct-pair/informative-pair checks |
| `test_prompts` | Removed the deleted sender-builder assertion; frozen relay/receiver/conceal prompt checks retained |
| `test_decisions_and_family` | Removed the withdrawn five-test fallback assertion; eight-test coverage/direction/Holm tests retained |
| `test_exploratory_fixed_family` | Fixed ten-test BH family instead of the withdrawn reduced case; inconclusive family retention still tested |
| `test_phase_skip_and_hop2` | Starts at relay rather than requiring a sender phase; missing-kind skip/two-hop checks retained |
| `test_full_fake_pipeline` | Starts at relay and expects 468 calls per fake transparent arm; restart, identity and pending-calibration checks retained |
| `test_receiver_publication_refusal_and_no_late_replacement` | Starts at relay; replays saved completed relay state without a sender phase or late replacement |

The fake executor helper now rejects sender specs instead of synthesizing them. No D1 test was edited, skipped or weakened.

### New tests

- `test_planted_vs_compliant_sender_byte_identity`: both kinds on two tasks; identical gated template and relay bytes; sender note discarded.
- `test_no_senders_or_reserves_regardless_of_outcome`: three scripted modes—accepted calls, missing hop-1 kind, rejected receivers—retain exactly 12 primaries, no senders and no reserves.
- `test_ready_only_approved_family_states`: both allowed states, missing amendment reason, invalid roles/families, DRAFT and pending calibration.
- `test_full_repository_import_and_data_seal_coverage`: recursive repository closure, dynamic vendor module, data files, all role-check/calibration files, existing paths and excluded runtime traces.
- `test_calibrated_dry_and_non_dry_fake_scores`: H4 is defined on every fake task, exact p=2/4096 for the scripted positive contrasts, dry labels retained; the non-dry pure function accepts calibrated fake records. No fake result is reported as study data.
- `test_calibrated_broad_and_strict_text_flags`: broad union and strict subset are distinguished using the actual patterns.
- `test_extra_receiver_set_excluded_from_primary_accuracy`: accuracy remains unchanged when only extra-set accuracy differs.
- `test_relay_cli_and_draft_guard`: new phase accepted up to the DRAFT guard; old phase refused; no backend instantiated or runtime folder created.

## Remaining ambiguities and next boundary

Remaining ambiguities: **none identified**. No requirement of Task 8 is deferred.

The existing failed role-check case and the supplied calibration remain limited to their recorded material. The stage studies propagation and audit placement conditional on signal introduction; it does not measure sender willingness or spontaneous coordination. The statistical qualifications in the governing documents remain unchanged.

EVAL on the prepared implementation, approval/status change, sealing and any model run require later tasks. No seal was created and no model run was started here.
