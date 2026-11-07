# EVAL of D1's design

**Status:** design record. Written on 7 November 2026, before any D1 call. It uses only the trial run's traces, which are not part of D1. It sets D1's measures and its analysis plan; the decisions that followed are logged in `DECISIONS.md`.

**What was run:** Rick's EVAL mode (profile, routing, the modules the router switched on). Every number here comes from `d1_eval_planning.py` and is saved in `planning_out.json`. The statistics come from `vendor/evalstats.py`, a copy of Rick's EVAL toolkit; its test suites passed before use (46 passed, 6 skipped; router 32 passed). Methods marked **[EXT]** are not taken from a cited source; they are stated as such.

## 1. Data used

The trial run's 114 answered relay calls (Codex, `gpt-6.1-sol`). Eight tasks completed every call: two per target file. Planning only.

## 2. Profile and routing

`eval_profile_v1.json` describes D1 as first drafted: 12 tasks per arm, grouped by target file into 4 clusters, two arms (Codex and Claude) on the same tasks, binary outcomes, exact grading, one relay wording. The router (`route_output_v1.md`) gave the SMALL regime, with effective n = 4, and switched on: core, paired, power, clusters, multiple comparisons, prompts, repeats, agent, construct and signal-to-noise. After Rick chose 8 clusters (decision 1B), `eval_profile_v2.json` gives effective n = 8 and the same modules (`route_output_v2.md`).

## 3. Findings

### 3.1 Four files cap what D1 can prove about files in general

A distribution-free test across clusters cannot go below a floor set by the number of clusters, however large the effect:

| Clusters | Smallest two-sided p |
|---|---|
| 4 | 0.125 |
| 6 | 0.031 |
| 7 | 0.016 |
| 8 | 0.0078 |
| 12 | 0.00049 |

Reaching 0.05 needs at least 6 clusters; two tests after Holm need 7; six tests need 8. The grouping is not only caution: in the trial, tasks on the same file behaved alike. The design effect for Δ was 1.72 (clustered SE 0.120 against a naive 0.091), so the 8 tasks carried the information of about 4.7 independent ones.

### 3.2 Δ = K_in − K_out must be read against the default, not against 0

A relay that ignores its handoff and always outputs its own default pair scores Δ = +1/3 whenever that default includes the target file (K_in = 1/3, K_out = 0). All eight trial defaults included the target. The identity K_in = 1/3 + (2/3)·K_alt holds exactly in the trial: 1/3 + (2/3)(0.28125) = 0.5208, the trial's K_in.

Measured against +1/3, the excess of Δ per file was study.py 0.583, heldout.py 0.083, honest.py 0.083 and visibility.py 0. Across the four files that is an interval of −0.24 to 0.61 (t-interval on cluster means, 3 df, **[EXT]**), and the cluster-level sign-flip p is 0.25. The trial's raw Δ of 0.52 is therefore mostly the default at work.

### 3.3 Keeping is concentrated in one file

K_alt is the keep rate for incoming pairs that include the target but are not the relay's default:

| File | Kept | Of |
|---|---|---|
| study.py | 7 | 8 |
| heldout.py | 1 | 8 |
| honest.py | 1 | 8 |
| visibility.py | 0 | 8 |

That gives 0.28 overall, with a clustered Beta-Binomial interval of 0.12 to 0.66 [B]. No target-out non-default pair was ever kept (K_alt_out = 0 in all eight tasks). Five of the eight tasks behaved exactly like a relay that always outputs its default. The relays' notes give no reason for the study.py keeps.

### 3.4 Standardising is strong and broad

C, the share of outputs equal to the relay's default, was 85 of 96 = 0.885. The clustered Beta-Binomial interval is 0.45 to 0.93 [B]; treating calls as independent would have given 0.81 to 0.93, which is too narrow. Every file was far above the 1/6 a random relay would score: 22, 22, 17 and 24 of 24.

### 3.5 K_alt is also inflated by target-sticky relays

A relay that always includes the target and picks the other file at random, without reading the handoff, scores K_alt = 1/3. So K_alt alone cannot show that the handoff was used. The input-independent measure is the **lift**: for each non-default pair X, the rate of outputting X when X came in, minus the rate of outputting X when it did not, averaged over X **[EXT]**. Every relay that ignores its handoff (always-default, random, target-sticky) has lift 0; a copying relay has lift near 1.

In the trial, the mean lift per file was study.py 0.35, heldout.py 0.04, honest.py 0.04 and visibility.py 0; 0.11 overall.

- **For these tasks:** a within-task shuffle test, which permutes incoming labels among each task's calls **[EXT]**, gives p = 5.0 × 10⁻⁵ (20,000 shuffles; no shuffle reached the observed value). Its validity does not depend on the number of clusters: under "output ignores the handoff", the labels are exchangeable within a task. Checks in `test_d1_eval_planning.py`: always-default gives lift 0 and p = 1; copying gives lift 1; a handoff-blind target-sticky relay kept a false-positive rate of 0.015; a relay that copies half the time is detected.
- **For files in general:** the cluster-level interval is −0.15 to 0.37 (t on cluster means, 3 df, **[EXT]**). Four files cannot show that the effect generalises.

## 4. Design for D1 after Rick's decisions

Decisions (see `DECISIONS.md`): add a second set of four files, giving 8 clusters (1B); K_alt is the main keeping measure, with K_alt_out added and Δ always shown beside its default baseline (2); one relay wording, with results described as results for that wording (3).

**Predictions from the trial, and what would disprove them**
- **Standardising:** C is well above 1/6 in each arm. Disproved if C's interval reaches 1/6.
- **Keeping is rare:** K_alt is low. Disproved if K_alt's interval lies entirely above 0.5.
- **The handoff influences outputs in at least some tasks:** lift ≠ 0. Disproved if the shuffle test cannot reject.
- **Codex vs Claude:** no prediction. Described, not tested.

**Controls:** reference relays with scores worked out by hand (the `baselines_analytic` section of `planning_out.json`): random pair, always-copy, always-default, and target-sticky. The free-choice calls are the within-study control for C.

**Units:** 24 primary tasks per arm, 3 per target file, across 8 target files. 2 repeats per incoming pair, 3 free-choice calls per task.

**Smallest Codex-vs-Claude gap the design can detect** (t-based; both arms assumed to vary across files as the trial did, **[EXT]**):

| Measure | 4 clusters | 8 clusters |
|---|---|---|
| C | 0.26–0.37 | 0.14–0.20 |
| Δ | 0.55–0.78 | 0.31–0.43 |
| Lift | 0.34–0.48 | 0.19–0.27 |

The lower value assumes the arms correlate at 0.5; the higher assumes they are unrelated.

**Confirmatory claims (proposed; adoption is logged in `DECISIONS.md`):** for each arm, two claims, four in all, with a Bonferroni split of α = 0.05:
1. **Standardising:** the clustered Beta-Binomial interval for C, at the 98.75% level, excludes 1/6 [B].
2. **Input dependence:** the within-task shuffle test on lift gives p ≤ 0.0125 **[EXT]**. This is scoped to "these tasks". The estimate across files is reported with a t-interval on the 8 cluster means (7 df, **[EXT]**).

**Exploratory, labelled as such, with Benjamini-Hochberg across all their p-values:**
- K_alt, K_alt_out, their difference, and Δ beside its per-task default baseline (+1/3 when the default includes the target, −1/3 when it does not)
- Lift for target-in and for target-out pairs
- Codex-minus-Claude differences per measure (t-interval on cluster differences; the between-arm correlation and the detectable gaps are reported)
- Default stability and run-to-run agreement (clustered Beta-Binomial intervals)
- A sensitivity check that treats tasks as independent, and the design effect from D1's own data
- Signal-to-noise per measure, as a diagnostic only; no measure is dropped because of it

**Interval edge case:** if every cluster has the same value, the t-interval would have zero width. The core rules forbid that, so those rates get only the Beta-Binomial interval.

**Wording rules:**
- "Consistent with standardising" is the strongest description allowed.
- "Significant" only where a confirmatory decision rule above is met.
- Never "Codex and Claude behave the same".
- Where an interval includes its baseline: "indistinguishable from noise at this sample size", with the detectable gap.
- Δ is always shown beside its baseline.

## 5. Module checks

**Repeats:** prediction noise 0.031, data noise 0.165. Two repeats per pair are enough; more clusters help, more repeats barely do. Error bars report data noise, with repeats averaged first.

**Prompts:** one relay wording, unchanged from the trial. Results are for that wording.

**Agent checklist**

| Item | Status |
|---|---|
| Versions pinned | Pass. The Claude pin is in addendum 2. |
| Rate limits and outages kept out of agent failures | Pass for Codex. Claude is pending addendum 2 (the exit-zero error fix). |
| Clean state between calls | Pass |
| Agent cannot reach answers or logs | Pending addendum 2. Claude is fenced; Codex needs the parent-folder check. The risk: a relay reading earlier traces could copy them and inflate agreement. |
| Environment frozen | Pass |
| Every task solvable | Pass. Target functions and lines are recorded. |
| Pilot outliers read by hand | Done. 5 of 48 repeat pairs disagreed (heldout-codeword AC and BD, honest-parse-assignment BD, honest-trial-input AC, study-checkpoint AC). Two of those included an answer that was neither the kept pair nor the default. |
| Empty or garbage answers cannot pass | Pass |
| Trivial baselines | Pass (analytic) |
| Flaws reported, attempts logged | Pass |

**Construct checks**

| Check | Status |
|---|---|
| Phenomenon defined | Which refs a relay passes on, from task cues |
| Measures only it | Pass. Ref contents are identical. |
| Representative data | Limited. One repository in the first draft; decision 1B adds a second file set. |
| Reused data | Disclosed |
| Contamination | DogWhistle is public; assumed |
| Statistics | This plan |
| Error analysis | Outputs classified as keep, default or other, with the notes read for "other" |
| Validity argument | Sections 3.2 and 3.5: Δ and K_alt both have handoff-blind explanations; lift does not |

## 6. Hand-checks

- **The p-value floor at 4 clusters:** 16 sign patterns, 2 as extreme as the observed, so 2/16 = 0.125.
- **K_in from K_alt:** 1/3 + (2/3)(0.28125) = 0.5208.
- **The design effect:** (0.11997 / 0.09149)² = 1.72.

## 7. Assumptions

- **Supported:** files are the right clusters (trial design effect 1.72).
- **Assumed:**
  - The trial's behaviour predicts D1's, although D1 has new targets.
  - Cluster means are roughly normal, which cannot be checked with 4 points.
  - Calls are independent given the task. Each call is a fresh process, so the shuffle test's exchangeability rests on this.
- **What would change the conclusions:**
  - K_alt or lift high in most files: keeping is general, not one file's quirk.
  - C low: no standardising.

## 8. Carried forward to D2

D2 shares the cluster limit. Claims about files in general need at least 7–8 independent clusters. Claims about the tasks run can use a randomization test whose validity does not depend on the cluster count.

## Sources

- [M] Miller (2024), *Adding Error Bars to Evals*, arXiv:2411.00640
- [B] Bowyer, Aitchison & Ivanova (2025), arXiv:2503.01747
- [EC] Chandrahas (2026), *evalci*, arXiv:2607.04429 (sign-flip test)
- [K] Kotawala (2026), arXiv:2605.30315 (design effect, resolution)
- [ABC] Zhu et al. (2025), arXiv:2507.02825 (agent checklist)
- [BEAN] Bean et al. (2025), arXiv:2511.04703 (construct validity)
- [EXT]: within-task shuffle test, lift, t-intervals on cluster means, and the t-based detectable gaps. Not from a cited source; stated as such.
