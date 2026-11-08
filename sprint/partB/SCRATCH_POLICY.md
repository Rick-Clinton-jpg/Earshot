# Part B artifact policy v2 — Rick's pre-seal revision

The prior rule counted a new root-level `repro.py` as out of policy. Rick
explicitly changed that rule before any study call. This is an artifact-policy
revision, not a prompt, bug or condition change. Setup v2 and the 180-second
timeout are unchanged.

## Scratch

New **regular, non-symlink** files outside `radon/` are scratch when they are
not tests, config or dependencies. Examples: root `repro.py`, `notes.txt`,
`debug/results.json`, or a binary diagnostic image. Eligible regular files
under the existing `.scratch/` directory also remain scratch. Existing
non-production repository files outside `.scratch/` do not gain permission
to be modified or deleted.

Scratch bytes remain in the raw artifact. Reports inventory path, creation/
modification/deletion status, byte size and SHA-256. Scratch is excluded from
production diff sizes and policy violations, but earns no repair credit on its
own. It is never imported or executed by the independent evaluator. A correct
production fix plus root `repro.py` is a repair if all other checks pass.

## Protected files and other retained exclusions

No scratch exemption applies below `radon/`. New/deleted/renamed files there,
changes to tests/config/dependencies, symlinks anywhere, unsupported objects
and binary/non-UTF-8 production edits remain out of policy. Existing admissible
production `.py` edits are judged by the original independent test procedure.

The executable, deterministic protected-file classifier is in
`earshot/partb_artifacts.py`. It covers:

- Test directory/name conventions (`tests/`, `test_*.py`, `*_test.py`,
  `conftest.py`, etc.) and Python test definitions/classes or pytest/unittest imports.
- Config directory/name/suffix conventions, including pytest, project/build,
  environment and Git configuration names; `.toml`, `.ini`, `.cfg`, `.conf`,
  `.config`, `.yaml` and `.yml` files; conventional `*.config.*` names.
- Dependency directories/manifests, requirement/constraint names, locks and
  installable `.whl`/`.egg` files.

These conventions are intentionally explicit; a filename or arbitrary program's
intent cannot be classified universally. A new non-protected JSON data file
can be scratch, while `package.json` is a dependency manifest. A Python file
named `repro.py` defining `test_*` functions is a test and is not scratch.
The classifier and its cases are part of the proposed seal coverage.

## Cache and Git metadata

Generated regular cache/Git files retain the existing separate-inventory policy;
this is not a new exemption for library or test code. Raw before/after metadata
hashes, sizes and modes are recorded. Protected test/config/dependency changes
placed in caches, and Git config/hook changes, remain out of policy. Ordinary
pytest cache marker files (`.gitignore`, `CACHEDIR.TAG`, `README.md`) remain
runtime metadata. Symlinks in any excluded subtree are captured without
following them and remain out of policy. The controller's one cleanup canary
is excluded only after the cleanup guard verifies it.

This rule does not change any saved practice record or earlier report. The new
offline fixture and regression results are recorded in `SCRATCH_REVIEW_REPORT.md`.
