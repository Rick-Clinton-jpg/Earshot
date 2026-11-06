# Codex quota reconnaissance — no model calls

Pinned CLI version for the planned study: `codex-cli 0.165.0-alpha.1.2`.

Inspected `codex --help`, `codex exec --help`, and 180 saved successful event streams (114 trial, 52 direct pre-sprint, 14 relay pre-sprint). Their usage fields are `input_tokens`, `cached_input_tokens`, `cache_write_input_tokens`, `output_tokens`, and `reasoning_output_tokens`. No remaining-account-quota or reset field was found by recursive inspection of the events. No quota/status subcommand is advertised in the pinned command help.

Official documentation describes interactive `/status` and `/usage`, and the non-interactive JSONL example reports token consumption. It does not establish a machine-readable account-quota interface for this pinned batch runner. No interactive session, app server, live model call, reset-credit purchase, or API-key request was made. This finding is limited to the inspected interfaces; it is not proof that no internal interface exists.

- https://learn.chatgpt.com/docs/pricing (account limits, interactive status)
- https://learn.chatgpt.com/docs/non-interactive-mode (JSONL events and usage example)
- https://learn.chatgpt.com/docs/developer-commands?surface=cli (interactive usage commands)

The 10%-remaining pause is omitted from code and the draft registration. The implemented protection is durable system-issue handling. The original requested fake-10%-reading test is therefore not applicable; no quota reader is fabricated. System pauses store raw error text, parsed reset UTC and interpretation. Time-of-day resets without dates use the next future occurrence in Asia/Calcutta unless an explicit supported timezone is present. Unparseable or ambiguous times use the prescribed 30-minute fallback. Waits stop at the last-launch deadline and never extend the analysis cutoff.

## Rick's later addendum supersedes the usage-limit retry policy

Usage-limit/rate-limit errors now cause a durable manual pause in both backends, followed by an exit after in-flight calls finish. No automatic retry or time-based resume is allowed for these errors. The pattern file contains the exact usage-limit message found in the trial error events, including its saved `3:34 AM` reset text, plus general usage/rate-limit recognition. The raw reset text and parsed UTC remain audit information only; they do not authorize resumption. Unknown non-zero/no-answer errors take the same manual-pause path as system issues, not agent failures. A timeout remains final, and exit-zero missing/unparsable output remains the already-classified gate rejection.

`--resume-rick` is the explicit operator action for a Rick-authorized restart. Counters and saved answers survive restarts. Other recognized system issues retain the bounded registered automatic retry rule. Because a paused process exits, future cutoff records are materialized by the next resume or explicit `--finalize-cutoff` command; no process is kept running to modify future records. Both commands enforce the original cutoff. No such command has been run on study data.
