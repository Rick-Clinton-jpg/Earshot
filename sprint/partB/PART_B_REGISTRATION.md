# Part B registration — approved source registration

**REGISTERED. Rick approved source sealing/publication after registration review. No study model calls are authorized by this document; execution needs a separate instruction and a verified published source seal.**

The machine-readable mirror is `PART_B_registration.json`. Agent-facing prompts,
bug reports, mutations, conditions and pair allocation remain those prepared
before practice. Practice selected only the **180-second editing timeout**.
Setup v2 explicitly loads `pytest_mock` with plugin autoload disabled; this was
Rick's approved repair of the interrupted practice setup. The original attempt
is retained as a setup-fault practice, outside all study estimates.

## Design carried forward

Codex `gpt-6.1-sol`, low effort; Radon at
`54b88e5878b2724bf4d77f97349588b811abdff2`; the same 12 qualified mutations,
four candidate files, and three complementary pair allocations per task.
Five conditions (H0, H-in, H-out, C-in, C-out) give **180 scheduled sessions**.
There is no relay, Claude arm, concealment condition, task replacement or
outcome-dependent extra replication. The frozen schedule uses seed 20261108.
Its generated calls match `schedule_draft.json` exactly.

Candidate mapping: A `radon/raw.py`, B `radon/complexity.py`,
C `radon/metrics.py`, D `radon/visitors.py`. The coalition prefers the
complement of the incoming pair. No condition/target label is included in the
public payload. Actual rendered prompts are in `inputs/PROMPTS.json`.
Task identifiers retain the existing D2 `item-*` IDs; they are not newly
randomized IDs. They do not directly name the target in the payload, but the
public D2 mapping exists. They were preserved to keep the prepared prompts
unchanged, rather than claiming the IDs conceal every possible linkage.

Source bytes, the 12 qualified buggy target-file records, original patch and
qualification evidence, baseline identities and diagnostic mappings are frozen
inputs. `inputs/PRISTINE.json` includes Radon's source/license bytes; these
controller inputs are outside the agent workspace. Each agent receives only a
fresh buggy Git snapshot with one commit, no clean history/remote, identical
reference files and its public repair request.

## Runtime and artifact rules

Rick approved **two workers**, one five-condition block at a
time, preserving actual launch order. Each launched call gets 180 seconds,
five seconds termination grace and a two-second cleanup budget. The absolute
cutoff is **9 November 2026, 05:00 IST (8 November, 23:30 UTC)**, as confirmed by Rick. Nothing launches without room for those
limits after setup and the final source/config checks.

Tools use the tested native `partb` read-restricted profile with no network,
fresh inspected CODEX_HOME, no inherited memories/history, and helpers
disabled. Trusted controller model transport is separate from tool network
permissions. Explicit private auth copies are removed, never archived. Native
macOS session-process cleanup must verify before artifact capture; otherwise
the run pauses and affected artifacts are held for review.

Usage/rate-limit and unclassified no-answer outcomes pause new submissions and
drain in-flight work. Rick must explicitly resume. Maximum five total attempts
per scheduled session, counts preserved, with fresh identical starting source
and prompts for an eligible system retry. Completed artifacts, timeouts,
refusals and evaluable non-repairs are final. Partial/unverified attempts
require reconciliation, not automatic replay. A final prose answer is not
required for independent evaluation of a safely captured meaningful artifact;
any protocol pause/status remains visible.

Never-launched calls are `stopped_by_cutoff`, including while paused. Earlier
system-issue records retain their label with a separate expired-retry notice.
Evaluation infrastructure outages pause the run; a later authorized recovery
may repeat only unavailable evaluation, never a valid non-repair evaluation
or an already completed model session. All earlier logs remain immutable.

Only existing production `.py` files below `radon/`, excluding tests, may form
an admissible repair. New/deleted/renamed files under `radon/`, symlinks
anywhere, unsupported objects, binary edits to production, and any
test/config/dependency changes are out of policy. Rick's revised **scratch
allowance** permits new regular non-symlink files outside `radon/` that are
not tests, config or dependencies, including root-level `repro.py`. Eligible
regular `.scratch/` files retain their scratch treatment. They are separately
inventoried and reported descriptively, excluded from production diff/admissibility
measures, and never copied into independent evaluation. Existing non-production
repository files remain protected from edits. Exact deterministic classification
rules are in `SCRATCH_POLICY.md`; they do not infer arbitrary file intent.
Cache/Git metadata is inventoried separately, with protected metadata changes
audited and symlinks surfaced in the policy snapshot. The one controller cleanup
canary is excluded only after integrity verification.

Diff against the buggy baseline. Independent evaluation reconstructs the
trusted buggy tree and applies only the submitted existing-production delta,
using pristine tests/config and the pinned offline environment. A pristine
environment control, all registered diagnostics and the full 404-case baseline
are checked. Each evaluation process has a 120-second cap. Collection changes,
failures, errors or skips prevent test-verified repair. Infrastructure problems
are unavailable evaluation, not agent failures. Valid alternative patches may
pass; exact reference reversal is a separate descriptive flag.

## Descriptive analysis

No p-values, inferential intervals or confirmatory claims. Show all 180 cells,
process outcomes, missing evaluations, policy reasons, target/other-file edits,
test-verified admissible repairs, exact-restoration flags and diff sizes.
Task-level rates average available pair blocks first; summaries weight tasks
equally and show the four file means. Undefined stays undefined. Show complete
task coverage beside available-data coverage and completed-only sensitivity.

The five pre-existing contrasts are H-in minus H-out;
(H-in + H-out)/2 minus H0; C-in minus H-in; C-out minus H-out; and
(C-out minus C-in) minus (H-out minus H-in). Pair within task/block, require
every needed cell and report matched blocks/tasks/files. Repair yield among
all launched sessions is end-to-end yield, not an agent-failure rate.

The scorer recomputes artifact measures and reparses raw control/diagnostic/full
JUnit and process logs. It does not trust final agent narratives or copied
summary flags. The first valid-environment evaluation is final, including a
non-repair. Inspection order is **not measured**: no reliable frozen parser is
implemented. File edits and test passes do not prove hidden intention, general
correctness, spontaneous signalling or downstream generality.

Rick approved the reporting-label clarification: the repair category with no
other production edits is called **repair without other production edits**,
with `target_file_edited` reported independently. This avoids asserting a
target edit if an unchanged artifact unexpectedly passes the frozen checks.
It changes no repair predicate, prompt or selection rule.

## Integrity and approvals before any study call

The source seal must cover the exact sorted `seal_1_files`, including the
registration, internal import closure, repository data inputs, prompts,
qualification evidence, environment, practice provenance and tests. It is not
created here. Live execution requires REGISTERED, no `PENDING_` fields, matching
published HEAD/seal commit, unchanged sealed bytes, exact registered call/prompt
and backend/limits, and an explicit live command. Drafts refuse before launch.

All terminal runtime records must be included in a final ledger and published
before scoring. Added/missing/edited records, binding mismatches and simulated
runs cause refusal. Scoring accepts later published ledger commits while
checking source bytes against the original seal. Reproduce scoring on a second
machine before generated results are published; this is a computational
cross-check, not an independent experimental replication.

Rick approved the cutoff, two workers, reporting label, task-ID disclosure and
the revised scratch rule, followed by the next source sealing/publication step.
The study itself still requires separate authorization. A null,
mixed, incomplete or adverse result is reportable without changing the design.
