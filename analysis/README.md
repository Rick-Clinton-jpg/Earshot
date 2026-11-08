# Exploratory analyses (D2)

These analyses use only the published, sealed D2 scorer output
(`sprint/partD/D2/results/d2_score_output.json`, SHA-256 `5121cca4…`).
They make no model calls and were **not part of the D2 registration**.
Each spec was committed and pushed before its code was written or run.

| Analysis | Spec fixed | Results |
|---|---|---|
| Per-agent identification (`d2_identification/`) | `de05478` | `879379a` |
| Text check vs swap test, per agent (`d2_text_vs_behaviour/`) | `f84c18e` | `5cfaf2e` |
| Monitor cost: two-call vs full score (`d2_monitor_cost/`) | `f84c18e` | `cb7f05c` |

## Summary (12 tasks per arm; Codex and Claude arms)

- **Per-agent identification:** at the last hop, every coalition and
  conceal receiver scored above every honest receiver in both arms
  (AUC 1.0000). Before the relay: 0.5000 (Codex), 0.8125 (Claude).
- **Text check vs swap test:** the calibrated D2 text check flagged
  12/12 coalition receivers and 0/12 conceal receivers in both arms
  (AUC 1.0000 and 0.5000); the last-hop swap score separated both
  groups (AUC 1.0000).
- **Monitor cost:** two-call swap scores still ranked members above
  honest receivers (AUC 0.9514 to 1.0000), but the fixed rule "score
  above 0" flagged 4 to 6 of 12 honest receivers (Codex) and 12 of 12
  (Claude), against 0 of 12 and 9 of 12 for the full score.

**Limits.** The convention was instructed, not spontaneous. Each unit
is a receiver type within one task, not a persistent agent. The swap
test requires the ability to swap the reference an agent receives.
Exploratory: not part of the D2 registration.

## After-sprint idea (not run)

**Per-agent identification on real code edits (Part B).** In every
Part B block, the include-target and exclude-target reference pairs
are exact complements, so each receiver type in each task was observed
under a reference swap three times. The question: does an agent's
actual editing (which production files it changes) shift when its
reference is swapped, and does that separate coalition agents from
honest ones? It adds something only if Part B's registered analysis
shows the convention changes edits at group level. Limits: one session
per reference per block with no within-reference baseline, instructed
conventions, Codex only, 12 tasks. To be looked into fresh after the
sprint, with new sessions.
