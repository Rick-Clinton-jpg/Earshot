# Frozen unsealed run — excluded from confirmatory analysis

Frozen at 2026-11-06T22:23:07.176157Z. Registration `1a6936ef646e45671768928c5e245a053897d9a7` was committed locally but not published before these calls. These traces are excluded from confirmatory analysis and must be reported as unsealed prior observations.

The original process had already ended by the time the superseding freeze instruction was processed. The executor has paused all further calls and analysis under that instruction. A pause partway through the call schedule cannot be substantiated from this inventory.

## Inventory only — no outcome analysis

224 trace files exist. All 12 primary tasks and all four reserves have 14 scheduled trace filenames. This is call-record completeness, not gate acceptance or task validity. There is no partially populated task schedule. Exact filenames, byte counts, and SHA-256 values are in `UNSEALED_RUN.json`.

The executor did not parse answers, compute scores, or inspect outcomes while creating this freeze. Only filenames and raw-byte hashes were inspected. No further calls may be written to this folder.

## Required corrections to the requested account

The request described a paused partial schedule and said no reserves were used. The saved-file inventory contradicts those statements. The record reports all four reserve schedules rather than asserting that they were unused. All saved traces, including failures, are retained unchanged.

The new request is truncated midway through Step G, ending with “No tests on”. Step H is absent. The freeze does not invent the missing instructions.

## Task schedules

| Task | Role | Trace files present | Missing filenames |
| --- | --- | ---: | --- |
| study-label-commitment | primary | 14 | none |
| heldout-codeword | primary | 14 | none |
| visibility-public-decoded | primary | 14 | none |
| honest-trial-input | primary | 14 | none |
| study-checkpoint | primary | 14 | none |
| heldout-receiver-input | primary | 14 | none |
| visibility-eligible-targets | primary | 14 | none |
| honest-parse-assignment | primary | 14 | none |
| study-ensure-published | primary | 14 | none |
| heldout-decoded-correct | primary | 14 | none |
| visibility-validate-registration | primary | 14 | none |
| honest-equivalence | primary | 14 | none |
| reserve-study-parse-assignment | reserve | 14 | none |
| reserve-heldout-summarize | reserve | 14 | none |
| reserve-visibility-summary | reserve | 14 | none |
| reserve-honest-summarize | reserve | 14 | none |
