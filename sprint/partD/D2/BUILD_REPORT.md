# D2 stage build — draft, no model calls, no seal

> Historical Task 7 build record. The current design is governed by addendum 3 and SEAL_PREP_REPORT.md: no sender calls; the pre-relay audit uses harness-planted codewords; calibrated patterns; fixed families of 8 and 10. Earlier budgets, pending statuses and removed fallback rules below describe the earlier build.

Built on 7 November 2026 under Task 7 and addenda 1 and 2. No D2 study observations exist. Fake-backend records are test fixtures, not agent results. No model CLI was called; the failing-CLI test executes a local Python fixture only. No registration was sealed, no Seal 2 was created, and no run was started.

## Imports and provenance

- Package: `d2_v3_addendum1_9f824ef8.zip`; SHA-256 `9f824ef88f54e4e6625f073758c65c8ce4ba9598e03400072dc084be40f00e74`, verified before extraction.
- Addendum 2: SHA-256 `2fdf272f29ffb763202e2de45044dce6f6bb55ffe1b46a5a250cd4629384c437`, verified before import. Saved byte-identically as `D2_ADDENDUM_2.md`.
- All six EVAL manifest entries, twenty original simulation manifest entries and four addendum-1 manifest entries verified. The only simulation files outside its original manifest are `v3_literal.py`, `v3_literal.json` and `v3_literal.log`, each covered by the addendum manifest.
- All 34 ZIP files and addendum 2 remain byte-identical. Registration rename is the sole name mapping.
- Precedence: addendum 2, addendum 1, registration. Earlier simulation shortcuts and obsolete numbers remain in imported historical records and are superseded, not edited. The operating-characteristic simulations were not rerun in this build; their supplied numbers are not presented as newly verified results.

## Built

- Six new modules: `earshot/d2.py`, `d2_design.py`, `d2_integrity.py`, `d2_reliability.py`, `d2_checkpoint.py`, `d2_score.py`. No existing source file changed.
- Sixteen Radon tasks, seeded opaque IDs, three primaries and one reserve per file. `TASK_AUDIT.md` gives every target definition/line, source evidence of unique candidate relevance, workspace verification and complete phrase-search scope. The whole tracked Radon repository produced zero hits for the six requested phrases. This is a source audit, not a claim that agents will select those targets.
- Radon `54b88e5878b2724bf4d77f97349588b811abdff2` in `/Users/gho5t/Documents/Codex/2026-11-04/i/work/earshot_d2_isolated/workspace`, clean; its parent contains only the workspace. Candidate hashes recorded. All four ref files match D1 SHA-256 `260defc28224d9f6c3b189c5f27a8e85b091ed76aeff09c077c21d9fc60771bd`.
- Sender validity and file-specific reserve replacement finish before relays. Each accepted hop-1 answer has exactly one hop-2 child. Missing one kind skips that task's entire receiver phase. A future per-arm Seal 2 includes skipped IDs, selected IDs, delivered pairs, immutable sender/relay inventory and the seeded receiver order.
- Receiver deduplication shares the actual saved calls on equal refs. D is computed with frozen `x_w_s` and allocation L1. Symmetric comparisons use canonical pair ordering to avoid arithmetic-order differences in the transparent-relay identity. Identical refs give S=0 analytically; the transparent-relay placement difference is exactly zero.
- Honest/coalition prompt wording and D1 builders reused unchanged. Conceal composition inserts exactly one space and the approved sentence before `\nTrial input:`. Provenance never enters receiver prompt bytes.
- D1 Codex/Claude configurations carried over unchanged in the JSON, including models, versions, settings, 180-second timeout and four workers. Their current installation versions were not probed. The future runner refuses version drift.
- D1 backend invocation and controls reused. A new durable-attempt module preserves D1's retry implementation while changing only role validation: receivers require the allocation schema and frozen `action()`, whereas sender/relay answers retain D1 classification/gating. Usage/unknown-answer/Claude 90% pauses, durable counts, cutoff checks and Rick-only manual resume are preserved.
- New phase integrity binds source bytes to Seal 1, requires published current-phase HEAD, checks Seal 1 ancestry at Seal 2, validates explicit input coverage, and binds each arm ledger to its arm/source seal. The scorer requires final phase state to agree with Seal 2. Checkpoints use D2 runtime branches and reject altered immutable records; no force pushes.
- Scoring covers section 7 descriptives, survival labels, continuous two-hop survival, recreation, incomplete chains, default/primary accuracy, allocations, following, text flags, all audits/contrasts, ratio, zero-survival bounds, interval summaries, coverage and report-only exposure. Confirmatory and exploratory families follow both addenda; file checks have direction counts and design effects, without p-values.
- `D2_registration.json` is DRAFT, retains the exact text/hash of all three governing documents and includes their resolved operational fields, unchanged arm configurations, proposed seal list and empty remaining-ambiguities list. `RUNBOOK.md` documents the later lifecycle. Text patterns remain `PENDING_CALIBRATION` with no patterns.

## Call budget

1. **Scheduled:** with all relay calls accepted, 41–65 per selected task; 492–780 per arm for twelve selected tasks. Missing accepted hop-1 answers reduce hop-2 calls; missing a kind skips receivers. The supplied expected counts around 590/655 are simulation estimates, not observations or guarantees.
2. **Replacement overhead:** two sender calls for each replaced primary, at most eight per arm under the registered one-reserve-per-file rule. Sender outcomes and reduced task coverage remain separately visible in phase state and call counts.
3. **Retries:** system-issue attempts are separate, durable records; D1's five-attempt ceiling applies per logical call. No retry count is estimated here. The local fake transparent pipeline completed 492 logical calls per arm; this verifies scheduling only and is not study data.

## Verification

Environment: Python 3.12.14, NumPy 2.5.4, SciPy 1.18.1, jsonschema 4.26.0, pytest 9.2.0. No dependency installation or Earshot dependency changes.

Every command used `PYTHONDONTWRITEBYTECODE=1`; every pytest command disabled its cache provider. Tests used no real model backend.

- Supplied simulation: `python -m pytest -q -p no:cacheprovider sprint/partD/D2/sim/test_sim_c.py` — **8 passed**.
- D2 plus supplied simulation after guard additions: `python -m pytest -q -p no:cacheprovider tests/test_d2.py sprint/partD/D2/sim/test_sim_c.py` — **36 passed**.
- Full suite: `EARSHOT_TEST_WORKSPACE=/Users/gho5t/Documents/Codex/2026-11-04/i/work/earshot_d1_isolated/workspace python -m pytest -q -p no:cacheprovider` — **237 passed** (final run).
- Tests cover frozen S, transparent control with nonconstant allocations, call counts/deduplication, all codeword cycles and task naming, both prompt families, source lines/pin, two-hop denominators, missing defaults and H4 followers, eight-task coverage and opposite-direction Holm step-down, exact 10/5 BH families, ratio gating, file checks without p-values, all allocation validation cases, phase refusal, no late replacement, deterministic receiver order, saved-answer restart, fake CLI usage pause, unknown-answer pause, Claude 90% signal, cutoff refusal, local-bare-remote publication, source/input edits, immutable checkpoint restore and ledger tampering.
- Initial D2 tests: 21 passed, one failed because the sealed design-effect function divides by zero for identical task statistics. The new D2 wrapper now reports that mathematically undefined quantity as null with its reason; the sealed function was not changed. The regression and complete fake pipelines pass.
- All 59 D1 sealed file hashes verified unchanged. Existing D1 tests and prior-work checks remain part of the full suite. Imported bytes verified again after testing. No cache artifacts exist under D2 or in the proposed seal list. `git diff --check` reports preexisting trailing whitespace in imported SIM_C_REPORT.md and v3_literal.log; those bytes are intentionally preserved under the import rule.

## Remaining work and limits

Remaining ambiguities: none identified after applying both addenda. Nothing required for this build was left unimplemented.

This is not permission to run: Claude's coalition-role check, text calibration, EVAL on the implementation, registration approval and sealing are still future tasks. The role-check outcome fixes the 8/5 family before Seal 1. Real scoring refuses pending calibration; dry runs give H4 p=1 and label every decision `DRY RUN: not a result`.

The build does not verify the statistical independence assumptions. H3 retains its sharp-null qualification and [EXT] directional-consistency interpretation beyond those nulls. H4 remains a conditional output contrast among followers. Four-file t-intervals are unavailable without all four defined file means; no missing values or degrees of freedom are invented. Zero-variance design effects remain undefined. Exposure is report-only and is not proof of a universal filesystem boundary.
