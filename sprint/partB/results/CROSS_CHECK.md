# Part B scoring cross-check

On 8 November 2026, the author supplied the complete SHA-256 fingerprints from Claude's second-machine scoring run, described by the author as completed without looking at the Codex output. Both fingerprints equal the original sealed-scorer fingerprints recorded by Codex. This is a computational cross-check of the same study data, not an independent experimental replication. The second machine was not accessed from this checkout. The author subsequently supplied its environment and command, recorded below as reported provenance.

| Output | Codex SHA-256 | Claude SHA-256 supplied by the author | Match |
| --- | --- | --- | --- |
| PART_B_RESULTS.md | `abd3fc503603f2d242e579509f9defaf6443f3248a3b553082eb13391f94c8a0` | `abd3fc503603f2d242e579509f9defaf6443f3248a3b553082eb13391f94c8a0` | Exact |
| PART_B_SCORES.json | `61b113da1b25c80ce6e2c40dc404833f022af9f3f76d9c01b7782a86e985a719` | `61b113da1b25c80ce6e2c40dc404833f022af9f3f76d9c01b7782a86e985a719` | Exact |

## Second-machine execution (reported provenance)

The author supplied this record from the second executor after the original fingerprint match:

- Machine: Claude cloud workspace, Ubuntu 24.04.5 LTS, Linux 6.18 x86_64.
- Python: 3.13.18 (CPython).
- Checkout: fresh clone of main at `79c4cf1`, the runtime-ledger commit.
- Codex's scored outputs were not read before this scoring run, according to the supplied record.
- Command from the clone root, with `$OUT` a new empty temporary directory:

```sh
python3 -m earshot.partb_score --repo . --branch main --registration sprint/partB/PART_B_registration.json --seal sprint/partB/SEAL1.json --seal-digest sprint/partB/SEAL1.sha256 --run-dir sprint/partB/codex --ledger sprint/partB/codex_LEDGER.json --ledger-digest sprint/partB/codex_LEDGER.sha256 --output "$OUT/score"
```

The outputs match byte for byte across Python 3.12.14 on macOS and Python 3.13.18 on Linux. This establishes reproducible computation on the same saved data across those environments.

## Codex execution

- Python: 3.12.14 (CPython).
- Executable: `/Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3`.
- Scorer exit code: 0.
- Source-seal commit: `5d2e7f38f4b40319ed1e1c479367e1fe3dd6c329`.
- Published runtime/ledger commit used for scoring: `79c4cf1fe77796569b32c0c0bf3e3095d064e6e6`.
- Source-seal SHA-256: `ba73a8935c1cecdb436ced5650a30890eef88b111816b063d7ebe76b1d996561`.
- Runtime-ledger SHA-256: `cbebccfc4fc8f2ec6c5e0ba71f46b195bd15483f827e874adc1ab548a00130f0`.
- No model calls were made by scoring or publication.

The RUNBOOK command was used with only a new output path substituted:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/gho5t/Documents/Codex/2026-11-04/i/work/.venv/bin/python3 -m earshot.partb_score --repo /Users/gho5t/Documents/Codex/2026-11-04/i/work/Earshot_foundation --branch main --registration sprint/partB/PART_B_registration.json --seal sprint/partB/SEAL1.json --seal-digest sprint/partB/SEAL1.sha256 --run-dir sprint/partB/codex --ledger sprint/partB/codex_LEDGER.json --ledger-digest sprint/partB/codex_LEDGER.sha256 --output /var/folders/35/rk0bf5190y36pdyn6fgrmptw0000gn/T/earshot_partb_scoring_20261108_y1953kxo/scored
```

The scorer rechecked the published source seal and complete runtime ledger, recomputed artifact measures and reparsed independent evaluation logs. The generated JSON and Markdown are copied here byte-identically. No number or table was edited for publication.
