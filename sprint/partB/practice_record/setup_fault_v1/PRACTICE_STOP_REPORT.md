# Practice stopped: test setup fault

Rick approved practice only to set the study timeout, with no behaviour-based changes to prompts, instructions, bugs or conditions. If setup was broken, execution had to stop and be reported before any change.

**Stopped after the honest call. The coalition call was not launched. No study timeout is selected.** The control journal is manually paused for the setup fault; no automatic retry or resume is allowed.

The honest Codex process completed, exit 0, in **36.192 seconds** of launcher wall time. Its patch independently passed all **404** tests and matched the reference reversal. These are pre-study observations on the reserve, not study results or a reason to change any scientific input.

However, the agent's own plain `python -m pytest -q radon/tests` returned **377 passed and 27 setup errors**: `fixture 'mocker' not found`. The prepared environment explicitly disables pytest plugin autoloading. The independent evaluator explicitly loads `pytest_mock`; the agent's ordinary command did not. Thus the full-suite interface available to the agent was not working as intended. The missing fixture is an environment/setup fault, not evidence of an agent repair failure. The run also recorded nonfatal Git/Xcode cache permission warnings; these were not changed or suppressed.

All 23 frozen input files retain their pre-call hashes, including both prompts, instruction source, bug/fix patches, task/condition schedule and launcher sources. D1/D2 seals remain unchanged. The original auth file remained unchanged, its disposable copy was removed, and no credentials were included in this report. No scientific input or setup code was modified after observing practice.

Potential repair, **not applied**: explicitly load the installed pytest-mock plugin in the agent test environment while preserving the plugin-autoload restriction. This could be done through a reviewed environment setting without changing prompt wording. It needs review and authorization before implementation or more calls. Any approved change must get a new setup record and offline check; the existing failed-setup practice attempt must remain intact. Whether to repeat the honest timing practice must also be explicitly decided, because the approved two-call plan has been interrupted.

PLAN.json, FROZEN_INPUTS.json, prompt files, preparation records, the immutable raw CLI events/artifact, independent evaluation logs, TIMING.json and PRACTICE_STOP.json remain in this folder. The honest model output and independent test pass do not override the requirement to stop on broken setup.
