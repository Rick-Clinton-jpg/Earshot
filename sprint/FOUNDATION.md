# Earshot sprint foundation — 6 November 2026

Foundation complete locally. No model call or experiment was made. Nothing was pushed, and Part D was not started. Tests replay saved records and simulate runner subprocess results; they do not validate live model execution. The isolated working checkout is `work/Earshot_foundation/`; it is separate from the earlier local archive checkout.

## Commit boundary

The unchanged preexisting import boundary is **0feb01bdc8b7134ffd85f5eda876c8fa8f398f46**. `PREEXISTING.md` lists source paths and all seven SHA-256 values. The seven imported code/schema files match their source bytes in that commit. The provenance document itself was written during the sprint.

| Step | Commit | Message |
| --- | --- | --- |
| 1 | `29e21e20cdea7f8a4d5d999d2097b8a0b793c778` | docs: sprint README and context (Parts D, B, E) |
| 2 | `0feb01bdc8b7134ffd85f5eda876c8fa8f398f46` | Import preexisting pre-sprint harness unchanged (written before 6 Nov 2026) |
| 3 | `14e8226f9d4f213bb0687b12d344cca2057e9b06` | Refactor pre-sprint harness into earshot package (behaviour unchanged) |
| 4 | `674b6c7021f2c2ff951a46fb79243a9e82ac502b` | Add tests reproducing pre-sprint scores, prompts and gate |
| 5 | Resolve with `git log -1 --format=%H -- sprint/FOUNDATION.md` | sprint: foundation report |

A commit cannot contain its own literal hash without changing that hash. The Step 5 hash is therefore reported in the executor handoff and is discoverable with the command above. The Step 3 commit was amended before Step 4 to retain version-probe failures as trace records; its superseded local hash was `efd6ad5`. There was no push of either version.

## Function and behavior mapping

| Preexisting function or component | New location | Change |
| --- | --- | --- |
| `run.canonical` | `earshot.prompts.canonical` | Same sorted JSON separators and encoding |
| `run.run_agent` / `run_sprint.run_agent` | `earshot.runner.run_agent` | Explicit Config; UTC start/finish; CLI version; exclusive trace creation and per-call reservation; safe filename validation; version-probe failure trace |
| `run.sender_prompt`, `run.listener_prompt`, `WORDINGS` | `earshot.prompts` | Candidate mapping passed explicitly; rendered prompt bytes preserved |
| `relay_smoke.relay_prompt` | `earshot.prompts.relay_prompt` | Task and files passed explicitly; rendered prompt bytes preserved |
| `run.accepted_refs` | `earshot.gate.accepted_refs` | Same valid ref sorting and fallback; malformed non-string/unhashable refs now reject without TypeError |
| Fixed handoff embedded in listener builders | `earshot.gate.fixed_handoff`, `gate_handoff` | Same fixed schema/objective/refs; parse raw JSON and strip every other sender field |
| `score.action`, `dist`, `x_w_s`, `exact_p` | `earshot.score` | Source functions copied unchanged; AST equality tested |
| `score.read`, `score.score` | `earshot.score.score_pilot` | Read closure uses explicit run directory, design and legacy design-reference metadata; no writes |
| `relay_smoke.score`, `relay_refs` | `earshot.relay.score_relay` | Pure read-only replay from explicit traces, task and saved sender; all saved values reproduced |
| `score_sprint.load_record`, `sender_valid`, `score_task`, `score` | `earshot.selection` | Explicit design/registration/files; same pre-sprint validity, reserve and numeric logic; no import-time I/O |
| `run.senders`, `listeners`; relay `run_relay`, `run_listeners` | Deferred experiment orchestration | Removed import-time global paths and dynamic imports. No live experiment entrypoint enabled in this foundation |
| `run_sprint.stub_suite` | Replaced by runner guard and offline mocked-runner tests | Foundation makes no synthetic experiment records or claims; stub mode refuses any subprocess |
| Script `main` blocks | `earshot.run_sprint.main` | Config parsing retained; rejects experiment execution pending registration |
| Hardcoded HERE/ROOT/RUN/MODEL settings | `earshot.config.Config`, `from_args` | CLI/environment workspace, run directory, model, reasoning, timeout, workers, CLI executable and stub/live setting |
| Implicit old task workspace | `earshot.workspace.build`, `verify`, `compare` | External local clone at pinned commit; independently verified ref bytes and tracked status |

The requested commit title says “behaviour unchanged”; that applies to prompt rendering, numerical formulas and saved replay outputs. It does not mean the old experiment orchestration or all malformed-input failure behavior was retained. The changes above are explicit. No post-refactor live equivalence has been tested or claimed.

## Regression evidence

Final command, executed from the foundation repository root:

```sh
EARSHOT_TEST_WORKSPACE=/Users/gho5t/Documents/Codex/2026-11-04/i/work/earshot_foundation_workspace /Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=sprint/test_tmp tests
```

Full final pytest output is saved in `sprint/pytest_final.txt`:

```text
........................................................................ [ 83%]
..............                                                           [100%]
86 passed in 0.13s
```

**86 passed, 0 failed, 0 skipped.** An earlier run before adding version-failure and timeout coverage passed 84 tests in 0.19 s (`sprint/pytest_initial.txt`). No pytest test failed, so there is no failing-test traceback to report.

- Pilot: complete saved score object equals replay, including all four metrics, all per-task W/X/S/D values, all target-minute vectors, sender details and counts. Per-task L1 D rounds to +0.4583, +0.4333, +0.3444, +0.2278; mean 0.3659722222222222 and p = 0.0625. The legacy absolute `design` string is passed explicitly as inert provenance metadata to preserve object equality; the scorer does not open that legacy path.
- Relay: complete saved summary equals replay, including both ref retention records, target minutes, W/X/S and D = −0.002777777777777782.
- Prompts: **66/66** saved `prompt_sha256` values reproduced (4 pilot senders, 48 pilot listeners, 2 relays, 12 downstream listeners). No prompt hash was substituted or score rounded to force a match.
- Gate: accepts two distinct allowlisted refs; rejects one, three, duplicate, non-string/unhashable or outside refs and malformed JSON; reconstructs fixed fields and drops sender notes.
- Stub mode: raises before subprocess startup, including a version probe or arbitrary executable request. A global test guard forbids actual non-Git subprocesses during tests; runner tests replace subprocess.run with local fakes.
- Runner: tests retained traces are reused without byte changes, timestamp order, version field, version-probe failure recording and timeout recording. These are mocks, not model calls.
- Prior work: all **86 manifest entries** match SHA-256 and byte counts. `git diff` against the starting GitHub commit shows no changes anywhere under `results/presprint/`.

## Runtime and workspace

Python: **3.12.14**, build `main, Sep 1 2026, 14:09:38`, Clang 22.1.3. CLI version-only probe: **codex-cli 0.165.0-alpha.1.2**. `codex exec` was never launched. Dependencies are standard library plus the already available pytest; no new dependency was added or installed.

The external workspace is `work/earshot_foundation_workspace/`, built once from the existing local DogWhistle clone using a clone without hardlinks, then checked out detached at `1a4b471b3cfb4ed6d5def7c61356c5230af8c082`. No network clone of DogWhistle or source edit was needed. The source DogWhistle checkout remains clean.

HEAD matches the pin; `git status --porcelain` is empty. All four refs equal the prior-work copies and have SHA-256 `260defc28224d9f6c3b189c5f27a8e85b091ed76aeff09c077c21d9fc60771bd`. They are **ignored fixture files, not tracked DogWhistle files**: the rebuilt clone's `.git/info/exclude` excludes `/handoff_refs/`. Thus clean status does not conceal an assertion that these fixture files belong to the upstream commit. They are checked separately. Full output is in `sprint/workspace_check.json`.

The original workspace identified by the saved import manifest still exists at `work/live_workspace/`. Comparison of every non-Git file found zero missing, additional or byte-different files; no extra `AGENTS.md` exists. `.git/` is excluded from the source-content comparison because clone metadata necessarily differs. In particular, the rebuilt `.git/info/exclude` includes the documented fixture exclusion, and its checkout is detached. No claim of equal Git metadata is made.

## Failures, discrepancies and deviations

1. The user explicitly said the README was already updated. Step 1 therefore preserved the verified GitHub README instead of restoring the earlier pasted draft byte for byte. That draft had factual overstatements corrected in the published version. Only the requested context paragraph changed in Step 1.
2. “Every file in this commit was written before the sprint” cannot truthfully include the new `PREEXISTING.md` itself. Its wording distinguishes the seven unchanged imports from this new provenance document. “Subsequent commits are sprint work” describes the commits, not a claim that inherited source text was newly written.
3. Adding refs and demanding clean Git status conflict unless refs are tracked or excluded. They were locally excluded and separately hashed, preserving the pinned upstream commit. This decision is disclosed above.
4. The first pytest shell invocation was issued from the parent workspace, so redirection failed before pytest started: `zsh:166: no such file or directory: sprint/pytest_initial.txt`. The invocation was corrected to the repository root. No test or model process ran in the failed invocation.
5. Gate validation previously could raise on unhashable malformed refs. It now rejects those inputs safely. Valid output handling is unchanged.
6. Old implicit-path orchestration was not retained as an enabled experiment launcher. The foundation entrypoint rejects execution pending sprint registration. This is a deliberate safety and scientific-boundary change, rather than a silent claim of complete operational equivalence.
7. `git mv` was used for run.py→runner.py, relay_smoke.py→relay.py and score_sprint.py→selection.py. Git's final similarity heuristic displays only selection.py as a rename; the others appear as delete/add because of the larger refactor. The boundary commit preserves their exact predecessors and permits full diff review.
8. The report commit's own literal SHA cannot be embedded in itself. Resolve it using the command in the commit table; it is also included in the final handoff.

No experiment was run, no results were modified, no hashes were relaxed, and no Part D registration or run was started.
