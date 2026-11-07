# Addendum 2 implementation report — no new model calls, no seal

The Claude backend, operational fixes, exposure audit and runtime-checkpoint lifecycle are implemented and checked offline. Inference and interval methods remain `PENDING_REVIEW`; cutoff remains `PENDING_RICK`; registration status remains DRAFT. Both arms and scoring still refuse this registration. No D1 study result is claimed.

## Fixture provenance

Fetched `claude-recon` and verified exactly `c90d5c6411b9bcc035ae4cc2282cc144516e5351`. Imported its ten original files byte for byte, including `MANIFEST.json`; all nine entries in that manifest match their byte counts and SHA-256. `tests/fixtures/claude_recon/PROVENANCE.json` records the source branch, commit, original/destination paths and all ten original hashes. The branch was not merged. These are the three pre-existing environment-check calls on trial material, not new model calls or D1 observations.

Both existing relay and listener structured outputs parse and validate against the repository schemas. The relay passes the shared gate with AB. The isolation fixture is rejected by the relay init check because it lacks StructuredOutput. Its two outside-workspace Read/Glob requests were denied. Relay and listener each show one persisted-output preview.

## Implementation

- Replaced the timezone-database dependency with UTC+05:30 while retaining IST, Asia/Calcutta and Asia/Kolkata parsing aliases.
- Filled Claude version 2.1.319, requested model, low effort, four workers, 180 seconds, exact fixture-derived argv, compact inline schema and merged updater environment. The method is marked reviewed only after its existing raw fixtures pass. CLI raw version text is normalized separately from the init-event version. Codex is probed before every model call and stores the result in each trace.
- Added strict Claude init/model/subagent checks, complete requested result metadata, error-text handling and field-based rate/quota decisions. Exit-zero provider errors cannot become gate rejections. A configuration-valid successful result with no gate-valid pair remains a gate rejection. Configuration faults are saved separately and stop the arm, not counted as agent outcomes.
- Added the Claude-only 90% manual pause. It preserves that call's outcome and records the two available raw/UTC reset times with reason `usage at 90%`. Ordinary restarts do not resume. Usage/rate-limit and unknown no-answer errors still require Rick's resume instruction. Rate-limit key names and normal overage-rejected metadata do not trigger false pauses.
- Fixed the manual-pause/launch race by rechecking blocked state under the launch lock. Separate pause episodes retain their original finished/left counts. Cutoff no longer schedules unused reserves or relabels a configuration-fault call as unlaunched.
- Enforced a task workspace with an otherwise-empty actual parent, including symlink resolution. A new isolated workspace was cloned and verified without model calls; the original workspace and DogWhistle remain untouched. Claude project-state checks allow only UUID session tool-results trees and refuse memory/instruction or other files and symlinks.
- Added report-only per-attempt exposure observations to saved calls and scoring reports, including outside requests, adapter content, persisted previews and permission denials. No call is excluded because of exposure observations.
- Added separate runtime worktrees/branches, complete copied-file manifests, immutable-record checks, publication verification and fresh-clone restore with exact inventory and hash checking. Tests include pause/checkpoint/test-folder-loss/restore/authorized-resume, final-answer reuse, counter preservation, changed/extra files, ignored-file preservation and rejected pushes. These pushes were only to temporary local bare remotes. No real online runtime branch or model worker was started.

## Trial baseline — observed logs only

Audited all **114 answered trial traces**, after checking their frozen hashes:

| Adapter-content status | Calls |
|---|---:|
| Confirmed | 0 |
| Indeterminate under the stated rule | 0 |
| No observed adapter content in saved visible outputs | 114 |

All 114 contained adapter filenames in visible output; filename listings alone do not establish content exposure. An independent scan found no path-and-line-prefixed adapter content blocks and no direct named-adapter read commands. There were **seven calls with explicit outside-workspace path requests**. Requests are not proof that outside file contents were returned.

The exact detection rule, every call's findings and hash, and every outside-path observation are in `TRIAL_EXPOSURE_BASELINE.json`; `TRIAL_EXPOSURE_BASELINE.md` provides the seven-row table. The audit does not reconstruct arbitrary shell execution or invisible/truncated content and does not establish that exposure was impossible. It changes no original result or trace.

## Validation and preserved material

Final full suite: **209 passed, zero failed, zero skipped**, on Python **3.12.14**. The no-timezone-database test blocks zoneinfo/tzdata imports; Python 3.13.18 was not executed here. Initial development failures and corrections are disclosed in `ADDENDUM2_DEVELOPMENT_LOG.md`; raw pinned fixtures were never edited to make tests pass.

Separate checks verified **86 prior-work manifest files**, **all 224 trial hashes against `424528e`**, fixture provenance and the argv/schema comparison. No changes to `results/presprint/`, `sprint/trial_run/`, frozen trial runner/scorer code, or DogWhistle. The new task workspace is clean at the source pin and has the verified identical-content refs. `ADDENDUM2_CHECKS.json` records these checks.

The planned future Seal 1 covers **46 files**, listed exactly in the updated registration and `SEAL_COVERAGE.json`. This is a coverage list, not a seal or digest. No new study trace, study ledger or study seal was generated.

## Qualifications and disagreements incorporated

1. Isolation evidence is limited to the tested denied requests; it is not proof of a universal Claude read boundary. Persisted-output previews prove truncation, not universal unreadability of the saved files.
2. The empty-parent requirement is an enforced setup check. Outside-path and adapter observations are report-only and never used for post-hoc exclusions.
3. “Codex prints whole files; Claude reads less” describes these saved checks, not a guaranteed property of every future call. The registration discloses different tools, observed reading patterns and truncation per arm, as well as built-in Claude plugins.
4. Exit checkpoints preserve successfully published state. A sudden wipe during a call or before checkpoint publication can lose newer local state. There is no exactly-once guarantee across that loss; uncertain completion requires reconciliation, never silent replay. The sealed run branch stays frozen while either arm runs.
5. Missing init/result during an error is a system issue. Actual conflicting configuration, or missing required configuration evidence on a successful response, stops the arm separately. This prevents platform faults being called agent failures.
6. There is still no inferential method or interval. Four-file dependence remains unresolved before sealing; these engineering checks do not establish Earshot's substantive hypothesis.

## Commits

- `97923a8`: import pinned reconnaissance fixtures without merging.
- `b1b3975`: Claude stream checks, operational fixes, exposure audit and runtime checkpoint/restore code with tests.
- This report accompanies the configuration, registration, runbook and check-record commit. No history was rewritten and no force-push was used.
