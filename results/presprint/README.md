# Earshot pre-sprint live-test evidence

These are byte-preserving copies of two saved local tests, imported on 6 November 2026. Original files and frozen seals remain unchanged. The source-to-copy SHA-256 records are in [IMPORT_MANIFEST.json](IMPORT_MANIFEST.json). No new model calls were made during this import.

| Test | Saved call count | Saved L1 D | Scope |
| --- | ---: | ---: | --- |
| [Direct handoff pilot](direct/RESULTS.md) | 4 senders + 48 listeners | 0.365972222222 | Four controlled tasks; planted convention; exact descriptive p = 0.0625 |
| [Relay smoke test](relay/provenance/RELAY.md) | 2 relays + 12 listeners | -0.002777777778 | SMOKE TEST, n = 1 task, not a result |

Direct raw traces and scores are in `direct/run-20261105-1/`. Relay raw traces and the saved summary are in `relay/relay_run/`. Original code and configuration are included for provenance; copied scripts retain their original path assumptions and should not be launched from this import directory.

The direct pilot used real source-inspection tool calls and planned review-minute allocations. It did not execute patches or test spontaneous collusion. In the relay smoke test, the public relay changed B,C to A,C and the codeword relay retained A,C, so both downstream arms received identical refs. The import independently recomputed L1 D from the saved answers and matched both saved summaries.
