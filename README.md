# Earshot

Earshot continues the DogWhistle research on structured agent handoffs and the sensitivity statistic S = X − W.

**Prior work disclosure:** both live tests, their code, and the local freeze were completed before the Swarm Alignment sprint (6–8 November 2026). Publishing them during the sprint does not make them sprint results. DogWhistle is the earlier research baseline: https://github.com/Rick-Clinton-jpg/DogWhistle.

The sprint direction is to test unplanted handoffs on genuine repository work, using actual downstream actions and task-quality checks. That study has not yet been run here. The existing planted review-minute harness does not implement that study.

## Saved pre-sprint live tests

The [pre-sprint evidence index](results/presprint/README.md) contains the reports, scores, and all 66 raw agent-call traces copied from the saved local runs. The import manifest records each original path and SHA-256 hash.

- [Direct handoff pilot](results/presprint/direct/RESULTS.md): four tasks, four senders and 48 listeners; normalized allocation L1 D = +0.3659722222, descriptive exact p = 0.0625.
- [Relay smoke test](results/presprint/relay/provenance/RELAY.md): one task, two relays and 12 listeners; L1 D = −0.0027777778. Both relays delivered the same refs downstream. This is a smoke test, not a result.

These controlled tests used a planted convention and planned review-minute allocations. They do not establish spontaneous collusion or effects on executed code changes. The original frozen records remain in the local archive. The published copies preserve their bytes and original labels. See [sprint scope and submission constraints](docs/SPRINT_CONTEXT.md).
