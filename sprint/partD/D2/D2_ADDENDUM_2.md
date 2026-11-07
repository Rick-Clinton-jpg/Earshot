# D2 registration v3, addendum 2: the ratio and the exploratory family

**Status:** settled before implementation. No D2 data exists, and nothing is built, sealed or run.

**Why this exists:** Codex raised two open statistical definitions after addendum 1.

**Precedence:** where this addendum differs from addendum 1 or from `D2_REGISTRATION.md`, this addendum governs.

## 1. The ratio D_sender / D_last

**Point estimate:** the ratio of the task means, mean(D_sender) / mean(D_last). The means are taken over tasks where both are defined. Per-task ratios are not computed, because they become unstable whenever a task's D_last is near zero.

**When it is reported:** only if the 95% t-interval for D_last over the 4 file means lies entirely above zero (`evalstats.t_ci`, 3 df, **[EXT]**). Otherwise the report says: "ratio not defined: D_last is not distinguishable from zero".

**No interval is given for the ratio itself.** An interval would need a method outside the sealed `evalstats` functions, such as Fieller's, with only 4 clusters. Uncertainty is shown instead through the intervals for D_sender, D_last and Δ, each a t-interval over the 4 file means. The ratio is descriptive and is never a decision.

This replaces the registration's wording "D_sender and D_sender/D_last with intervals". Intervals apply to D_sender, D_last and Δ, not to the ratio.

## 2. The exploratory family

There is **one Benjamini–Hochberg family** (`evalstats.benjamini_hochberg`, q = 0.05), fixed before any data. It has **10 tests**:

| Tests | Count |
|---|---|
| H1 keep-only, per arm | 2 |
| H3 for T-in only, per arm | 2 |
| H3 for T-out only, per arm | 2 |
| Cross-arm, Codex minus Claude, for each of the H1–H4 statistics | 4 |

**How the tests are run:**
- **All 10** use `evalstats.sign_flip_test`, exact and two-sided.
- **Coverage:** each test needs at least 8 tasks with a defined statistic. Below that it is INCONCLUSIVE, with p = 1, and stays in the family.
- **Cross-arm tests** pair tasks by ID and use only tasks selected in both arms. They make no directional prediction: the observed direction is reported. They compare model-and-harness pairs, not models alone.
- **If the Claude coalition-role check fails before sealing**, the family is fixed at Seal 1 as 5 tests:
  - H1 keep-only, per arm (2);
  - H3 for T-in and for T-out, Codex arm only (2);
  - cross-arm H1 (1).

**Nothing else gets a p-value.**
- P-d to P-f are reported descriptively.
- The file-level check is reported as two things: the number of file means in the predicted direction (out of 4), and the design effect. It gets no p-value. A sign-flip over 4 file means can never go below 0.125, so it could only inflate the number of tests without informing anything.

This replaces the registration's "sign-flip over the 4 file means" in section 9 with the file-direction count.

**Every exploratory result is labelled exploratory.** None is promoted to a claim.
