# D1 design decisions (append-only log)

Each entry records a decision about D1's design, when it was made, and the evidence in front of the person who made it. Entries are never edited; a changed decision gets a new entry.

| When (IST) | Who | Decision | Evidence at the time |
|---|---|---|---|
| 2026-11-07 05:41 | Rick | Run EVAL with the profile as filled in: "run everything that is necessary" | `eval_profile_v1.json`, `route_output_v1.md` |
| 2026-11-07 05:51 | Rick | **1B:** add a second set of four candidate files, giving 8 clusters instead of 4 | EVAL sections 3.1–3.3: four clusters cap tests at p ≥ 0.125 |
| 2026-11-07 05:51 | Rick | **2:** K_alt is the main keeping measure; add K_alt_out; always show Δ beside its default baseline | EVAL section 3.2: Δ = +1/3 for a relay that only outputs its default |
| 2026-11-07 05:51 | Rick | **3:** keep one relay wording; describe results as results for that wording | Prompts module; no paraphrase budget |
| 2026-11-07 06:18 | Rick | The second set of four files comes from **a different repository**, not DogWhistle. It is also intended as the second repository for D2 and Part B. | EVAL 3.1 and 3.3; a second codebase addresses the "one codebase" limit |
| 2026-11-07 06:18 | Rick | Codex proposes 2–3 candidate repositories against stated criteria, and Rick picks one | — |
| 2026-11-07 06:18 | Rick | **Adopt lift with the within-task shuffle test** as the confirmatory "the handoff mattered" claim. Per arm: C above 1/6, and lift different from 0, giving four claims, each held to 0.0125. K_alt stays the main reported keeping measure. | EVAL 3.5 |
| 2026-11-07 06:18 | Rick | Keep `vendor/evalstats.py` public, so the planning numbers can be reproduced | — |
| 2026-11-07 07:15 | Rick | D1 runs on DogWhistle only (4 target files, 12 tasks, 180 primary calls per arm). Radon (picked at 06:51) moves to D2 and Part B. Reason: Codex usage budget; the lift shuffle test does not depend on the number of files. | EVAL 3.5; SECOND_REPO_SHORTLIST.md |
| 2026-11-07 07:15 | Rick | Stopping rule: run every scheduled call, with no early stopping. The cutoff of 2026-11-09 12:00 IST (06:30 UTC) is a backstop only. | — |

## Open, to be decided before sealing

None for D1.
