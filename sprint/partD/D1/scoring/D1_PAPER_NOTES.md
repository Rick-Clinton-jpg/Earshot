# D1: notes for the paper

These are framing points backed by D1's sealed numbers. Each one names its source in `D1_SCORES.json` or `D1_RESULTS.md`.

1. **We corrected our own headline test before collecting data.** The unsealed trial reported Δ = 0.52 and an exact p of 0.0039 against 0. EVAL then showed that a relay which always outputs its own default scores Δ = 1/3 whenever that default contains the target, and every default did. So Δ against 0 mostly measured the default mechanism. D1 replaced it with lift, which is 0 for any relay that ignores its input. D1 then showed lift ≠ 0 in both arms (p = 0.00005). The effect survived the stricter test. Sources: `eval/EVAL_D1_DESIGN.md` §3.2 and §3.5; claim (b).
2. **Replicated across two model families, under one seal.** GPT (`gpt-6.1-sol`, through Codex) and Claude (`claude-sonnet-5-5`, through Claude Code) ran the same sealed tasks. Both met both confirmatory claims, and both show the same shape: lift 0.44 and 0.43 for pairs that include the target, 0.00 and 0.01 for pairs that leave it out.
3. **Predictable, not sanitising.** Honest relays rewrite most pairs toward a stable default that contains the target. A channel carried by reference choice is narrowed, not closed, and predictability makes it designable. This motivates D2. Source: `D1_RESULTS.md`, "Predictable, not sanitising".
4. **The models differ in consistency, not in sensitivity to input.** These comparisons are exploratory. Codex returns to its default more often than Claude (C difference +0.28, interval 0.11 to 0.46) and repeats itself more (agreement difference +0.31, interval 0.08 to 0.53). The two models' lift is indistinguishable (−0.002, interval −0.16 to 0.16).
5. **Honest limits, stated up front.**
   - The study covers 4 files, so intervals about files in general are wide. Claude's claim (a) clears its baseline by 0.04.
   - Keeping varies strongly by file: study.py is near-total in both arms.
   - With 4 files, no file-level exploratory test can reach p < 0.125. We report all 19 tests with Benjamini-Hochberg anyway.
6. **The two models read differently, and we disclosed it rather than filtering it out.** Claude's searches surfaced content from the excluded adapter files in 47 of 180 calls; Codex's did in 1 of 180. Every call was kept, as registered. The difference reflects different reading tools (searching the repository vs reading the target files). It is a property of the model-and-harness pair, worth one sentence in the paper.
7. **The integrity chain.** Seal 1 → both arms run on the sealed commit → both ledgers verified → scoring with the sealed functions → a per-task cross-check against the sealed scorer, with 0 mismatches. Every link is public and can be checked by hash.
