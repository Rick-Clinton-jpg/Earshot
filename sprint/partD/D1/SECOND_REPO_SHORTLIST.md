# Second-repository shortlist — no model calls

**Recommendation: Radon**, pinned to `54b88e5878b2724bf4d77f97349588b811abdff2`. It has the clearest fit to the file-size range, four separable source areas, and a substantially larger passing offline regression suite. **Multipledispatch** is the smaller, less-starred alternative; its variadic module is 95 lines, approximately 100, and its thinner tests and closely related modules are disadvantages for later edit evaluation. Rick has not selected a repository.

Assessment date: **7 November 2026, Asia/Calcutta**. GitHub stars are a snapshot, not a test of model familiarity. Neither project is an AI/LLM/agent/safety project, and their GitHub owners are `rubik` and `mrocklin`. Both repositories are public, non-archived, and not forks according to GitHub metadata. The pinned source commits are within the last approximately two years.

Only candidate screening clones and isolated test environments were created. They are under `/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107`, outside Earshot and outside both the current isolated D1 task-workspace parent and the older workspace parent. No D1 workspace, handoff refs, task requests, tasks file, code change or registration change was made. All candidate tracked source remained unchanged.

## Measured comparison

| Candidate | Licence | Stars | Repository created / age | Pin date | Shallow clone | Full offline pytest |
|---|---|---:|---|---|---|---|
| [radon](https://github.com/rubik/radon) | MIT | 2,037 | 2012-09-20 / 14.1 years | 2024-10-20 | 1.28 s; .git 2,152 KiB | 404 passed; 0 failed/errors/skips; 0.490 s pytest / 0.719 s wall |
| [multipledispatch](https://github.com/mrocklin/multipledispatch) | BSD, three-clause text | 849 | 2014-02-17 / 12.7 years | 2024-12-05 | 1.06 s; .git 152 KiB | 63 passed; 0 failed/errors/skips; 2.728 s pytest / 3.017 s wall |

Timing is one measured run on macOS arm64, Python 3.12.14 and pytest 9.2.0. Tests took seconds, below the few-minute budget. Dependency installation occurred online beforehand in separate environments; the actual test processes and their descendants ran under the macOS profile `(version 1)(allow default)(deny network*)`. A separate socket probe produced `PermissionError: Operation not permitted`, confirming denial. No test deselection, source patch, skipped test, benchmark disable flag or project build was used. Tests imported the original source through PYTHONPATH.

## Audit method

All Git-tracked files at each pin, including hidden files and binary blobs, were scanned case-insensitively for the literal regular expression `coalition|codeword|decod|required_memory_refs|handoff`. Git metadata is excluded. Function counts come from Python AST parsing: module-level functions plus distinct qualified methods in module-level classes; inherited and nested functions are excluded, and duplicate getter/setter names count once. Line counts include comments and blank lines. Four symbol/line witnesses per file demonstrate target capacity; they are not task requests or a primary/reserve assignment.

Agent-file screening covered names/paths containing AGENTS, CLAUDE, GEMINI, Copilot instructions, Cursor/Windsurf/Cline/Roo rules, Aider, Codex, LLMS, instructions, prompts, .continue/.junie/.qodo and conventions. Content screening additionally covered agent/assistant/prompt terms, common model/provider names and agent-role phrases, with lexical hits manually inspected. No agent-instruction files or agent/LLM prompt text were found in either shortlisted tree. Ordinary Qt Assistant build instructions and browser UI prompt words are not agent prompts. Files are directly readable Python source with no build, network or generated-file prerequisite.

## radon

Python source-code metrics: raw line/token analysis, cyclomatic complexity, maintainability and AST visitors.

**Repository:** [rubik/radon](https://github.com/rubik/radon). **Pin:** [`54b88e5878b2724bf4d77f97349588b811abdff2`](https://github.com/rubik/radon/commit/54b88e5878b2724bf4d77f97349588b811abdff2). **Licence:** [MIT](https://github.com/rubik/radon/blob/54b88e5878b2724bf4d77f97349588b811abdff2/LICENSE).

GitHub metadata: [2,037 stars; created 2012-09-20](https://api.github.com/repos/rubik/radon). Latest pinned commit time: `2024-10-20T11:52:52+02:00`. Audited tracked files: **304**. Clone time: **1.282 s**; shallow .git size: **2,152 KiB**. Size/time refer to these screening clones, not a full-history clone.

### Proposed files — provisional A–D only

| Letter | File | Lines | Top-level functions | Distinct direct methods | Total | Four distinct symbol witnesses (`line`) |
|---|---|---:|---:|---:|---:|---|
| A | [radon/raw.py](https://github.com/rubik/radon/blob/54b88e5878b2724bf4d77f97349588b811abdff2/radon/raw.py) | 245 | 8 | 0 | 8 | `_split_tokens` (82); `_get_all_tokens` (96); `_logical` (122); `analyze` (185) |
| B | [radon/complexity.py](https://github.com/rubik/radon/blob/54b88e5878b2724bf4d77f97349588b811abdff2/radon/complexity.py) | 108 | 6 | 0 | 6 | `cc_rank` (15); `average_complexity` (47); `sorted_results` (59); `add_inner_blocks` (78) |
| C | [radon/metrics.py](https://github.com/rubik/radon/blob/54b88e5878b2724bf4d77f97349588b811abdff2/radon/metrics.py) | 157 | 7 | 0 | 7 | `halstead_visitor_report` (69); `mi_compute` (98); `mi_parameters` (120); `mi_rank` (150) |
| D | [radon/visitors.py](https://github.com/rubik/radon/blob/54b88e5878b2724bf4d77f97349588b811abdff2/radon/visitors.py) | 460 | 1 | 31 | 32 | `ComplexityVisitor.generic_visit` (220); `ComplexityVisitor.visit_Assert` (256); `ComplexityVisitor.visit_FunctionDef` (268); `ComplexityVisitor.visit_ClassDef` (297) |

### Tests

Run from `/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/radon`:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 PYTHONPATH=/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/radon /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/env-radon/bin/python -m pytest -q -p no:cacheprovider --junitxml=/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/radon_pytest.xml --strict-markers
```

The JUnit file and full stdout are retained outside Earshot at `/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/radon_pytest.xml` and `/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/radon_pytest.log`. The exact command, wall time, Python version and complete package freeze are in `/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/radon_test_result.json`.

**Result: 404 passed, 0 failed, 0 errors, 0 skipped; exit 0.** Pytest time 0.490 s; process wall time 0.719 s. No warnings were reported. The strict-markers option follows the project’s own `radon/tests/run.py`; default discovery was otherwise left intact.

Setup packages actually used: `pytest==9.2.0`, `pytest-mock==3.17.0`, `nbformat==5.11.1`, `mando==0.7.1`, `colorama==0.4.6` (transitive versions in the retained freeze). No Radon wheel or editable project installation was needed.

### Audit results

**Four proposed files: zero forbidden-pattern matches. Entire tracked repository: 6 matches. Agent-instruction filenames: zero. Agent/LLM prompt text found: zero.**

Every forbidden-pattern match follows; all are outside A–D and concern ordinary text/source decoding.

| Path and line | Exact matched line |
|---|---|
| [radon/cli/__init__.py:72](https://github.com/rubik/radon/blob/54b88e5878b2724bf4d77f97349588b811abdff2/radon/cli/__init__.py#L72) | `except tomllib.TOMLDecodeError as exc:` |
| [radon/cli/tools.py:92](https://github.com/rubik/radon/blob/54b88e5878b2724bf4d77f97349588b811abdff2/radon/cli/tools.py#L92) | `should be used to decode a Python source file. It requires one` |
| [radon/cli/tools.py:125](https://github.com/rubik/radon/blob/54b88e5878b2724bf4d77f97349588b811abdff2/radon/cli/tools.py#L125) | `# Decode as UTF-8. Either the line is an encoding` |
| [radon/cli/tools.py:128](https://github.com/rubik/radon/blob/54b88e5878b2724bf4d77f97349588b811abdff2/radon/cli/tools.py#L128) | `line_string = line.decode('utf-8')` |
| [radon/cli/tools.py:129](https://github.com/rubik/radon/blob/54b88e5878b2724bf4d77f97349588b811abdff2/radon/cli/tools.py#L129) | `except UnicodeDecodeError:` |
| [radon/cli/tools.py:350](https://github.com/rubik/radon/blob/54b88e5878b2724bf4d77f97349588b811abdff2/radon/cli/tools.py#L350) | `return et.tostring(ccm).decode('utf-8')` |

Other prompt-word lexical hits were ordinary Qt Assistant commands (`docs/Makefile:82`, `docs/make.bat:104`), MathJax browser UI prompts (`docs/_static/extensions/MathMenu.js:19`) and a Pygments CSS `Generic.Prompt` class (`docs/_themes/solar/static/solarized-dark.css:36`). A broader AI-term scan also produced ordinary README “if you are” prose, short minified identifiers and binary font coincidences. None is an agent/LLM prompt. The literal forbidden-pattern scan included all 65 tracked binary files and added no matches.

### Risks for D1, D2 and Part B

- **D1:** some complexity/metrics functions call the visitor module, so request wording must distinguish the requested operation without mentioning filenames. File clusters are not independent merely because filenames differ. Its 2,037 stars and 14-year public history leave more model-familiarity risk than multipledispatch; no familiarity probe was run.
- **D2:** the 404-case suite covers AST visitors, raw metrics, complexity helpers, CLI and notebook handling, making it a stronger existing edit oracle here. Coverage was not measured and no edit/mutation trial was performed; passing this baseline is not evidence that every harmful edit would be caught.
- **Part B:** an AST/code-analysis subject differs from DogWhistle, but still concerns programming tools. Its bundled documentation assets add repository-wide search noise, and six ordinary decoding matches remain outside the candidates. Preserve that disclosure. Last code activity is October 2024, not continuous 2026 maintenance. Recheck the unchanged pin on the actual future execution environment, especially if it uses Python 3.13.

## multipledispatch

Type-signature dispatch, ambiguity ordering and variadic argument matching.

**Repository:** [mrocklin/multipledispatch](https://github.com/mrocklin/multipledispatch). **Pin:** [`a55aff03d19573f2bab40d0648f8e85c07a5d77b`](https://github.com/mrocklin/multipledispatch/commit/a55aff03d19573f2bab40d0648f8e85c07a5d77b). **Licence:** [BSD, three-clause text](https://github.com/mrocklin/multipledispatch/blob/a55aff03d19573f2bab40d0648f8e85c07a5d77b/LICENSE.txt).

GitHub metadata: [849 stars; created 2014-02-17](https://api.github.com/repos/mrocklin/multipledispatch). Latest pinned commit time: `2024-12-05T07:42:44-08:00`. Audited tracked files: **30**. Clone time: **1.058 s**; shallow .git size: **152 KiB**. Size/time refer to these screening clones, not a full-history clone.

The source licence contains the three BSD redistribution conditions and `setup.py` declares BSD. GitHub’s automated licence field says `NOASSERTION`; that metadata discrepancy is retained rather than treated as permission evidence. The recommendation relies on the pinned licence text.

### Proposed files — provisional A–D only

| Letter | File | Lines | Top-level functions | Distinct direct methods | Total | Four distinct symbol witnesses (`line`) |
|---|---|---:|---:|---:|---:|---|
| A | [multipledispatch/conflict.py](https://github.com/mrocklin/multipledispatch/blob/a55aff03d19573f2bab40d0648f8e85c07a5d77b/multipledispatch/conflict.py) | 121 | 7 | 0 | 7 | `consistent` (39); `ambiguous` (71); `ambiguities` (76); `ordering` (109) |
| B | [multipledispatch/dispatcher.py](https://github.com/mrocklin/multipledispatch/blob/a55aff03d19573f2bab40d0648f8e85c07a5d77b/multipledispatch/dispatcher.py) | 464 | 8 | 22 | 30 | `Dispatcher.register` (128); `Dispatcher.get_func_annotations` (168); `Dispatcher.add` (186); `Dispatcher.dispatch` (304) |
| C | [multipledispatch/utils.py](https://github.com/mrocklin/multipledispatch/blob/a55aff03d19573f2bab40d0648f8e85c07a5d77b/multipledispatch/utils.py) | 138 | 6 | 0 | 6 | `_toposort` (33); `reverse_dict` (68); `groupby` (90); `typename` (114) |
| D | [multipledispatch/variadic.py](https://github.com/mrocklin/multipledispatch/blob/a55aff03d19573f2bab40d0648f8e85c07a5d77b/multipledispatch/variadic.py) | 95 | 1 | 4 | 5 | `VariadicSignatureType.__subclasscheck__` (6); `VariadicSignatureType.__eq__` (12); `isvariadic` (32); `VariadicSignatureMeta.__getitem__` (61) |

`variadic.py` is **95 lines**, five below 100; this uses the requested approximate range without padding or changing the source. If 100 is intended as a strict floor, this alternative should be ruled out. Radon does not need that tolerance.

### Tests

Run from `/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/multipledispatch`:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 PYTHONPATH=/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/multipledispatch /usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' /Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/env-multipledispatch/bin/python -m pytest -q -p no:cacheprovider --junitxml=/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/multipledispatch_pytest.xml
```

The JUnit file and full stdout are retained outside Earshot at `/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/multipledispatch_pytest.xml` and `/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/multipledispatch_pytest.log`. The exact command, wall time, Python version and complete package freeze are in `/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107/multipledispatch_test_result.json`.

**Result: 63 passed, 0 failed, 0 errors, 0 skipped; exit 0.** Pytest time 2.728 s (terminal output reports 2.72 s); process wall time 3.017 s. All four collected benchmark cases ran. **Three warnings** were reported: one unused benchmark fixture and two dispatch ambiguity warnings; they were not suppressed.

Setup packages actually used: `pytest==9.2.0` and `pytest-benchmark==5.3.1` (including `py-cpuinfo2==10.1.1`). The benchmark plugin is required by the repository’s tests. No project wheel or editable installation was needed.

### Audit results

**Four proposed files: zero forbidden-pattern matches. Entire tracked repository: 0 matches. Agent-instruction filenames: zero. Agent/LLM prompt text found: zero.**

There are no repository-wide matches to list.

The only agent/prompt-word lexical hits are Qt Assistant documentation-build commands at `docs/Makefile:82` and `docs/make.bat:104`. There are no tracked binaries and no agent-instruction files.

### Risks for D1, D2 and Part B

- **D1:** the 95-line module is at the approximate lower boundary and uses metaclass methods; it is smaller and more specialized than the other files. All four files belong to one tightly connected dispatch implementation. Future requests must separate signature matching, conflict ordering and dispatch behavior. Its 849 stars reduce one popularity indicator, but 12.7 years of public history do not establish unfamiliarity to a model.
- **D2:** the 63-case suite is much thinner than Radon’s. Utility functions are tested largely through callers; no dedicated `test_utils.py` is present. Benchmark measurements are machine-sensitive and should not become a semantic-success threshold. No edit/mutation trial or coverage measurement was performed.
- **Part B:** the repository is exceptionally small and has no forbidden-term exposure anywhere, but four dispatch-related files provide a narrower behavioral domain. The GitHub licence-label discrepancy and 95-line approximation need to remain visible. Last code activity is December 2024. Recheck the pin and test dependencies on the eventual Python/OS environment.

## Selection recommendation and limits

**Choose Radon** if the priority is an exact source-size fit and useful existing tests for D2/Part B. Its files offer distinct raw-token, complexity, maintainability and visitor behavior, with 404 passing tests and no required source/build changes. Multipledispatch is a defensible lower-popularity alternative if Rick accepts 95 as “about 100” and prefers minimal dependencies and zero repository-wide forbidden matches over a larger regression suite.

Two repositories and eight deliberately selected files still form a convenience sample, not a random sample of Python files or repositories. This shortlist does not validate the pending inferential method or show a substantive Earshot effect. D1 reference selection and later tested edits require separate evaluation; no model calls or edit runs were made here.

## Screened out

Current [Suor/funcy](https://github.com/Suor/funcy) at `a876c7e1cf11e7c746e91fce4632ebfa93865428` was cloned only for screening and **rejected**, because it contains `AGENTS.md`, `CLAUDE.md` and `.claude/settings.json`. No tests were run and no instruction files were removed. Its two forbidden-regex matches are `docs/flow.rst:86` (`json.JSONDecodeError`) and `type_tests/run.py:163` (`json.JSONDecodeError`). It is not one of the two candidates.

## Evidence and unchanged scope

All clone/timing records, AST inventories, full-repository audit hits, setup logs, test stdout, JUnit XML and dependency freezes are retained under `/Users/gho5t/Documents/Codex/earshot_second_repo_screening_20261107`. The final shortlist alone is added to Earshot. No D1 code, registration, seal list, planning-record byte, prior result or task workspace was changed. Stop for Rick’s pick; no candidate is activated by this document.
