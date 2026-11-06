# D1 execution record

## Preconditions before live calls

All five foundation commits are ancestors of HEAD. The foundation suite passed 86/86; after Step 1 it passed 88/88, and after Step 2 it passed 95/95 (zero failures or skips). The workspace is pinned to `1a4b471b3cfb4ed6d5def7c61356c5230af8c082`, has empty porcelain status with the documented verified fixture exclusion, and all four refs match SHA-256 `260defc28224d9f6c3b189c5f27a8e85b091ed76aeff09c077c21d9fc60771bd`. CLI version probe exactly matched `codex-cli 0.165.0-alpha.1.2`.

The pasted request is the execution authority. The Downloads document matches it after stripping final whitespace; it differs only by final newline.

## Operational definitions fixed before data

Incoming groups contain six calls each: three target-including pairs times two replicates, and three target-excluding pairs times two replicates. Free choice is an intentionally empty input, not an accepted pair; the output must still pass the two-ref gate. Failed processes cannot contribute accepted outputs even if partial output parses. Rejected outputs never contribute their fallback refs to measured rates. Raw answers, fallback handoffs, gate results and measurements are retained.

Task primary rates use accepted incoming-pair calls only. Tasks are equally weighted. Task validity requires at least five accepted calls per incoming group. Reserves replace invalid primaries in fixed order, and an invalid reserve is consumed without filling the replacement. All 14 calls are completed for each reserve used. Free-choice agreement requires both free outputs to be accepted and their sets to agree. K_alt excludes tasks without this agreement or without any accepted relevant alternative input. No defined K_alt yields an unresolved secondary. Its bootstrap resamples the eligible task rates. Bootstrap endpoints are sorted indices 250 and 9750 of 10,000 task means, using a fresh Random(20261107) per reported metric. Exact sign flipping uses rational fractions of the accepted counts. The share of outputs equal to free choice uses all accepted calls including free calls; tasks with undefined free choice are omitted and denominators are reported. Overall keep excludes free input. These details resolve underspecified denominators without changing the requested estimands.

The original relay prompt and requests are preserved. Prior public_refs, codeword_refs and hidden_pair are stripped from the D1 task objects and unused. No receiver or sender call is part of D1. The positive primary test can also occur for a relay with a fixed preferred target pair; the secondary is reported with its fixed rule, without a broader mechanistic claim.

The live runner refuses missing/uncommitted/edited registration and checks registered code/data hashes before calls. The committed source also pins runtime settings and CLI version. Registration is local only; nothing is pushed.

## Execution errors and deviations

The first Step 0 verification command resolved a relative repository path twice and failed before checking the commits. Its traceback ended in `FileNotFoundError` for a nested `work/Earshot_foundation/work/Earshot_foundation` directory. The actual precondition checks were then run from the correct repository root and passed before further work; the suite itself passed on the initial command too. No model call occurred in either check. No numeric expectation was changed.
