# Addendum 2 development checks

No model calls were made. Tests use the existing pinned streams, in-memory synthetic variants explicitly named test-only, fake subprocesses/clocks, and temporary local bare Git remotes.

The first new targeted run produced **10 failed, 63 passed**. Nine failures followed from resolving the fixture's Linux `/home/...` path through this Mac's filesystem, which rewrote it to `/System/Volumes/Data/home/...`. The parser now compares the provided fixture cwd lexically; the live backend canonicalizes its own actual workspace before invoking the parser. The raw fixtures were not changed. The remaining failure showed that an empty `memory/` directory had passed the state-directory check. The check now requires UUID session directories and their tool-results contents only.

The corrected targeted suite passed **82 tests** (`ADDENDUM2_TARGETED_TESTS.txt`). Additional regressions cover per-call version checks, the pause/launch interleaving, preserved counts across separate pause episodes, cutoff handling, an actual-parent check through a symlink, checkpoint inventory/hashes, an ignored runtime file and rejected pushes. The final full-suite output is in `ADDENDUM2_FULL_TESTS.txt`.

The timezone test starts a subprocess that refuses imports of both `zoneinfo` and `tzdata`, then imports the reliability code and checks all three India timezone aliases against the fixed offset. The local interpreter was Python 3.12.14; no claim is made that Python 3.13.18 was run here.

Deliberate corruption and deletion in checkpoint tests apply only to temporary fake data. Neither the saved trial nor pre-sprint files were altered, deleted or rerun.
