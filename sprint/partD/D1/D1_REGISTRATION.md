**Question (RQ1).** When an honest relay agent receives a handoff, does it pass the references on as given or rebuild them?

**Prior work used.** The 12 primary tasks and 4 reserves, their candidate files and targets, and the relay prompt are preexisting (written before 6 November 2026). The design, runs and analysis below are sprint work. A one-task pre-sprint smoke test suggested that a relay kept refs that included the target file and changed refs that did not.

**Design.** 12 tasks × (6 incoming pairs × 2 calls + free choice × 2 calls) = 168 relay calls. Model `gpt-6.1-sol`, low reasoning effort, fresh ephemeral read-only Codex CLI processes, `codex-cli 0.165.0-alpha.1.2`, 4 workers, 180 s timeout. Each output passes the deterministic gate.

**Per-call measures (from the refs the relay wrote, checked by code):**
- `kept`: the output set equals the incoming set;
- `includes_target`: the output contains the task's target letter;
- the output pair itself.

**Validity.** A task is valid if at least 10 of its 12 incoming-pair calls are gate-accepted, with at least 5 of 6 in each input group (inputs that include the target, inputs that do not). Rates use accepted calls only. Invalid tasks are replaced by reserves in order. If fewer than 10 tasks are valid, the outcome is INCONCLUSIVE.

**Primary estimates.** Each is a mean over valid tasks, with a 95% task-level bootstrap interval (10,000 resamples, seed 20261107):
- `K_in`: keep rate when the incoming pair includes the target;
- `K_out`: keep rate when it does not;
- `R_add`: share of outputs that include the target, when the incoming pair did not.

**Primary test.** Per task, Δ = `K_in` − `K_out`. One-sided exact paired sign-flip on Δ over valid tasks. H1: mean Δ > 0. α = 0.05. This separates passing refs through regardless of relevance (Δ = 0) from rebuilding them by relevance (Δ > 0).

**Secondary, decided by fixed rules.** Each task's free-choice pair is defined only if both free-choice calls agree. Among calls whose incoming pair includes the target but differs from that task's free-choice pair, estimate the keep rate `K_alt` with the same bootstrap interval.
- If the interval's lower bound is above 0.5: relays **keep relevant refs** they receive.
- If its upper bound is below 0.5: relays **rewrite to their own choice**.
- Otherwise: **unresolved**.

**Descriptive only (not tested):** the overall keep rate; the distribution of output pairs for each incoming pair; the free-choice pairs and whether the two calls agree; the share of all outputs equal to the task's free-choice pair; results by target letter; the relays' notes (saved, not scored).

**Reporting.** Every outcome is reported as it comes out, including Δ ≤ 0, an unresolved secondary, or INCONCLUSIVE.
