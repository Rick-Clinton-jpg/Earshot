# Part B publication checks — 8 November 2026

No sealed source, test, study trace, registration or result number was changed. Generated results retain the SHA-256 fingerprints in CROSS_CHECK.md.

## Validation history

1. The initial full suite, including `sprint/partD/D2/sim/test_sim_c.py`, returned **369 passed, 1 failed**. The failure was `tests/test_partb_launch.py::test_real_cli_detached_worker_is_stopped_without_killing_other_session`: its scripted child PID was not in `killed_pids`. The saved fixture already contained its `late-edit` file; cleanup reported verified with no remaining process. This is consistent with the two-second child finishing before cleanup, rather than being killed by it. The fixture evidence and complete validation logs are retained locally outside the repository. No study session was rerun.
2. The unchanged fixture passed in isolation: **1 passed**.
3. One full-suite repeat, with no source or test edits, returned **370 passed**. The initial failure remains recorded here.

Both full-suite commands used `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, the controller virtual environment, and `EARSHOT_TEST_WORKSPACE=/Users/gho5t/Documents/Codex/2026-11-04/i/work/earshot_d1_isolated/workspace`:

```sh
python3 -m pytest -q -p no:cacheprovider tests sprint/partD/D2/sim/test_sim_c.py
```

This suite includes the prior-work import-manifest check. Every entry in D1, D2 and Part B's source seals was checked against its SHA-256 and remained unchanged. README/result-document local links and the results checksum manifest were checked. The D2 exploratory input digest and spec-before-results commit ancestry were checked; those analysis records remain on their separate published branch and are linked from the README at a pinned commit.

These are publication validation checks, separate from the 180-session study observations and the second-machine scorer cross-check. Local scripted CLI fixtures use a scripted server, not a hosted model.
