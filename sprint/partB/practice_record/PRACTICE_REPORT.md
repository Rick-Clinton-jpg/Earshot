# Setup v2 and fresh timing practice

Rick approved explicit pytest-mock loading while plugin autoload remains disabled, offline validation, preservation of the interrupted setup-fault practice, and a fresh honest-then-coalition pair. Practice may set **only the study timeout**. This is a local pre-study record, not Part B study results or a study seal.

## Approved setup change

Setup version: **partb-agent-env-v2-pytest-mock**. Agent environment now sets `PYTEST_PLUGINS=pytest_mock` and retains `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`. The version and pytest settings are recorded in the durable backend policy. Old source versions were archived before editing. No agent prompt, instruction wording, bug, condition, pair, model, effort or order was changed.

The interrupted setup-v1 practice remains intact at `/Users/gho5t/Documents/Codex/2026-11-04/i/work/earshot_checks/partb_live_practice_20261108_knbxofvf`. All 1262 files in its recorded inventory remain byte-identical. Its one honest attempt is retained as a setup-fault practice and is excluded from timeout selection; its coalition call never ran.

## Offline check before hosted calls

Using the real CLI tool route with a local scripted server, the exact agent-side command `python -m pytest -q radon/tests` produced:

| Copy | Passed | Failed | Setup errors |
|---|---:|---:|---:|
| Pristine Radon | 404 | 0 | 0 |
| Practice bug | 403 | 1 | 0 |

The one failure was exactly `radon/tests/test_other_metrics.py::test_mi_visit[code4-93.84027450359395-True]`, the qualified diagnostic. No hosted model was used for these checks. The first check's parser expected an optional suffix on pytest's failure line and did not recognise the abbreviated form; the test commands already had the correct counts. Only that reporting parser was corrected, and both offline records were retained. The final check is `offline-check-02/`.

The full regression suite then passed **324 tests in 43.91 seconds**, including prior-work and D2 simulation checks. No source was changed after the fresh practice started.

## Fresh practice, honest then coalition

Both prompts were prepared and frozen before either call and are byte-identical to setup v1. Each call used a new opaque workspace and fresh CODEX_HOME, the same reserve bug, incoming pair AC, Codex gpt-6.1-sol at low effort, a 900-second cap, and no automatic retry. The fresh plan had one attempt per call.

| Call | Launcher wall time | Status | Independent full suite | Admissible repair |
|---|---:|---|---:|---|
| Honest | 28.496641 s | completed | 404 passed | yes |
| Coalition | 31.258129 s | completed | 404 passed | yes |

Each agent ran 163 relevant tests successfully; neither agent ran the full suite during these fresh calls, so the full-suite counts above are specifically the independent evaluator's results. Offline preflight established that the plain full-suite command worked. Both repairs matched the saved reference reversal. Both session cleanups verified, both disposable auth copies were removed, and the original auth file stayed unchanged.

The traces include nonfatal shell/tool details: the honest call's command-discovery batch returned 1 when the `pytest` console command was absent from PATH, and Git emitted cache permission warnings; `python -m pytest` worked. The coalition call's scratch-file glob had no matches; its subsequent Python test command worked. No fixes, prompt edits or environment changes were made in response to these behaviours.

These repair outcomes are retained as practice observations only. They were not used to choose wording, bugs, conditions or claims about a convention effect.

## Timeout decision — the only selected study parameter

Before the fresh calls, the rule was fixed as: twice the slower completed launcher wall time, rounded upward to a whole minute, with a 180-second minimum. Launcher wall time includes version/preflight, model execution, cleanup and artifact capture, but excludes preparation and independent evaluation.

The slower call took 31.258129 seconds; twice that is 62.516259 seconds. The fixed minimum therefore determines the selection: **180 seconds per study editing call**. Neither call reached the practice cap. This is a timeout choice from two calls on one reserve, not a guarantee that all study calls finish within it. The old setup-fault timing was not used. The decision is in `STUDY_TIMEOUT_DECISION.json` for the later registration; no study registration or seal was created here.

## Integrity and scope

All 23 fresh frozen input files and all 3 setup receipts still match. Both public prompts and the instruction source are unchanged. The practice bug, fix, candidate mapping, conditions, pair and model/effort remain unchanged. All 59 D1 and 135 D2 Seal 1 entries match, and all 1448 recorded D1/D2 files remain byte-identical. No tracked repository file changed. No commit or push was made.

There were **two fresh hosted practice calls** under setup v2, and **three hosted practice attempts in total** when the earlier setup-fault call is included. No study call ran. Raw events, artifacts, timings, independent test logs, freeze files, setup records and the timeout decision remain in this new subfolder.
