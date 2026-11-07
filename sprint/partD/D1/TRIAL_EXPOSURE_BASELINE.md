# Trial exposure baseline — retrospective, not D1 results

Audited all 114 answered trial traces against their frozen hashes. The audit detected **0 confirmed**, **0 indeterminate**, and **114 with no observed adapter-content exposure** in saved visible tool results. Filename listings do not count. This does not establish absence of exposure outside the visible logs.

There were **7 calls** with explicit outside-workspace path requests (7 observations). Requests do not by themselves prove that outside file contents were returned. No calls are excluded or reclassified by this audit.

## Exact rule

Confirmed exposure requires an adapter path plus source content in a returned tool result: a path-and-line-prefixed content match, or a direct Read/cat/sed/head/tail/nl request attributed to the adapter with a matching nonblank source line. Filename listings alone do not count. Ambiguous combined reads and truncated relevant results are indeterminate unless visible attributed content already confirms exposure. No observed exposure means none detected in the saved visible outputs, not proof of no exposure. Requests outside the workspace, denials and output-storage paths are distinct observations, not exclusions.

## Outside-path observations

| Trace | Tool | Path | Tool request error |
|---|---|---|---|
| d1-heldout-receiver-input-BD-r2.json | item_2 | `..` | False |
| d1-honest-parse-assignment-AB-r1.json | item_2 | `..` | False |
| d1-honest-parse-assignment-AD-r1.json | item_2 | `..` | False |
| d1-honest-parse-assignment-BD-r2.json | item_2 | `..` | False |
| d1-honest-parse-assignment-free-r2.json | item_2 | `..` | False |
| d1-honest-trial-input-free-r2.json | item_3 | `..` | False |
| d1-study-checkpoint-BD-r2.json | item_2 | `/Users/gho5t/Documents/Codex/2026-11-04/i/work` | True |

The complete per-call findings, original trace hashes and adapter-source hashes are in `TRIAL_EXPOSURE_BASELINE.json`. Arbitrary shell evaluation and content missing from truncated output are not reconstructed. The 110 original system-issue traces are outside this answered-call baseline.
