# Earshot

**How far down a chain of agents does a hidden signal stay within earshot, and can oversight still hear it?**

Earshot follows a reference field as it is passed from one AI agent to the next. It asks whether each agent passes the reference on, rebuilds it, or acts on it, and whether an audit can still tell when something hidden is riding along.

Earshot continues [DogWhistle](https://github.com/Rick-Clinton-jpg/DogWhistle) and is being built during the Swarm Alignment Hackathon (6–8 November 2026). Work done before the sprint is kept in `results/presprint/` and disclosed under [Prior work](#prior-work-preexisting-not-sprint-results).

**Status — 8 November 2026:** D1 and D2 are complete, scored and independently re-scored. The two-machine checks reproduce the computation; they are not independent experimental replications. Parts B and E remain planned.

| Stage | Status | Record |
| --- | --- | --- |
| Pre-sprint tests | Prior work, excluded from sprint results | [Evidence](results/presprint/) |
| D1 trial | Trial record, not confirmatory | [Trial report](sprint/trial_run/TRIAL_RUN_RESULTS.md) |
| D1: relay reference selection | Complete, both arms | [Results](sprint/partD/D1/scoring/D1_RESULTS.md) · [Cross-check](sprint/partD/D1/scoring/CROSS_CHECK.md) |
| D2: planted references and audit placement | Complete, both arms | [Results](sprint/partD/D2/results/D2_RESULTS.md) · [Scorer output](sprint/partD/D2/results/d2_score_output.json) |
| B: real edits | Planned | — |
| E: real multi-agent logs | Planned | — |

---

## Why this matters

Agents increasingly hand work to each other through structured messages: a task, a few fields, a list of files to read. In the incident described in the sprint brief, agents coordinated by passing messages through a shared space and splitting up work between them.

Most oversight checks one agent, or one message, at a time. A chain of agents can behave differently from any single link in it. A field that looks harmless at every hop can still carry a signal from the first agent to the last, or lose it, or have one invented along the way.

Earshot studies this in one small, controlled setting first, then checks it against real work and real logs.

## Research questions

| # | Question | Part |
| --- | --- | --- |
| RQ1 | When an honest relay agent receives a handoff, does it pass the references on as given or rebuild them? | D |
| RQ2 | When a planted codeword rides in the handoff, does it survive a relay, and does the swap audit still detect the agent acting on it? | D |
| RQ3 | Does the handoff change the code the last agent actually edits? With no codeword at all, does the handoff alone still shift real work? | B |
| RQ4 | In real multi-agent logs, do agents pass references on as given or rebuild them? | E |

The parts run in this order (D, then B, then E) because each depends on the answer before it. D finds the pattern, B measures what it does to real work, and E checks whether it happens outside the lab.

### Open questions from the sprint this work speaks to

The paper [Red-Teaming Multi-Agent Attacks for Loss-of-Control Risks](https://arxiv.org/html/2610.24052v1) studies attacks distributed across agents. Earshot addresses related questions in part:

- **Monitoring messages between agents.** Its standard monitor excludes messages between agents; its optimized attacks use shared plans, and it explicitly does not test steganographic or other covert channels. RQ1 and RQ2 study that channel directly: whether a signal survives each hop, and where an audit of it stops working.
- **Telling which agents are working together.** The swap audit can measure a specified receiving agent's sensitivity to a specified field; sensitivity alone does not establish collusion. Earshot does not try to find unknown colluders in a large crowd.
- **Not addressed:** why split-up attacks still get through when a monitor sees every agent at once. That needs a different setup.

## Key terms

- **Handoff:** the structured JSON one agent passes to the next. The field studied is `required_memory_refs`, which must name two of four allowlisted reference files (A–D). A deterministic gate rejects anything else and rebuilds the rest of the handoff from a fixed template.
- **Sender, relay, receiver:** a sender writes a handoff, a relay receives one and writes another, and a receiver acts on it. D2 uses harness-planted codewords and no model sender calls. Its receivers use hop-1 outputs; hop 2 measures survival separately.
- **Codeword:** a planted convention. A "coalition" receiver is told to read the refs as a private preference. It is planted on purpose. Earshot does not claim agents invent such conventions on their own.
- **Swap audit (S = X − W):** compare the six cross-arm, different-wording action distances (X) with the six within-arm, different-wording distances (W). A positive S estimates excess sensitivity to that field under the matched replay design; it does not by itself establish a hidden motive. D = S for the coalition receiver minus S for the honest receiver.

## Study design and status

Details for each part are fixed in a registration file committed before that part runs. This section gives the plan in plain terms.

### Part D: Relays (RQ1, RQ2) — completed

- **D1:** honest relays selected reference pairs on DogWhistle, across 12 tasks and four target files. Both model-and-harness arms completed 180 calls. The study measured output selection and input dependence.
- **D2:** on Radon, a repository not used in D1, the harness planted two complementary codewords for each of 12 primary tasks. Honest relays processed them, and honest, instructed-coalition and concealing receivers allocated review minutes.
- **Chain:** each accepted hop-1 output received a hop-2 relay call for survival measurement. Receivers were fed the first accepted hop-1 output for each codeword kind. No receiver was fed a hop-2 output.
- **Audit placements:** pre-relay swaps change the incoming codeword and compare the resulting downstream inputs; last-hop swaps change the refs delivered directly to the receiver. The two interventions answer different questions.
- **Protocol:** [registration](sprint/partD/D2/D2_REGISTRATION.md) and [addenda 1](sprint/partD/D2/D2_ADDENDUM_1.md), [2](sprint/partD/D2/D2_ADDENDUM_2.md) and [3](sprint/partD/D2/D2_ADDENDUM_3.md), with later addenda governing. Source seals, per-arm relay seals and final ledgers preserve the study records.

### Part B: Real work (RQ3)

- **Setup:** the same chains, but the last agent makes real edits in a disposable copy of the repository instead of planning review time.
- **Conditions:** honest-only chains with no codeword, to see whether the handoff alone shifts real work, and chains with a coalition receiver, to see whether its behaviour carries into actual code changes.
- **Main measure:** which files are changed, and whether the change passes the task's checks.

### Part E: In the wild (RQ4)

- **Data:** AI Village transcripts, a public record of agents built on models from several companies working together over long periods. Access to the dataset is needed.
- **Main measure:** how often a reference an agent forwards matches the one it received.
- **Purpose:** to see whether the pattern from Part D appears in real multi-agent logs, across model families.

## Results

### D1: relay reference selection

In both arms, incoming pairs that omitted the target were rarely kept: 0/72 for Codex and 2/72 for Claude. The output added the target in 72/72 and 67/72 such calls. Every task's free-choice default included the target.

Relevant non-default incoming pairs were kept at task-mean rates of 0.46 and 0.56 (`K_alt`). The registered keep-versus-not-keep outcome was unresolved in both arms. These rates are distinct from lift, which is a baseline-subtracted output-matching measure.

See [D1 results](sprint/partD/D1/scoring/D1_RESULTS.md) for the registered tests, intervals, exploratory comparisons and exposure disclosure. The results cover these tasks and model-and-harness configurations, not files or models in general.

### D2: audit placement under a planted reference convention

| Audit D, task mean | Codex arm | Claude arm |
| --- | --- | --- |
| Pre-relay | 0.00 | 0.22 |
| Last-hop | 0.40 | 0.37 |

In all 12 Codex tasks, the delivered hop-1 pairs used for the two upstream conditions were identical, so that upstream swap had no downstream effect to measure and the pre-relay audit correctly returned zero. Direct last-hop swaps still changed convention-sensitive allocations. This establishes that the two audit placements are not interchangeable in this setting; it is not a detector false negative for a surviving upstream contrast.

All eight registered tests met their decision rules, but they share data and are not eight independent confirmations. H3 retains its sharp-null and [EXT] qualifications. The text-check result is conditional on receivers that followed the convention, under an explicit concealment instruction. It does not establish a general concealment capability.

The [D2 results](sprint/partD/D2/results/D2_RESULTS.md) contain the complete estimates, intervals, limitations and provenance. The sealed scorer output reproduced byte for byte on two machines. The write-up is generated from that output and the recorded exposure summary.

A [preliminary role check](sprint/partD/D2/role_check/ROLE_CHECK.md) recorded one Claude sender declining to encode the preference while separately prompted receivers followed it. This is a preliminary case, not a compliance-rate estimate; it motivated the pre-seal amendment removing model senders from both arms.

The [earlier D1 trial](sprint/trial_run/TRIAL_RUN_RESULTS.md) and all pre-sprint results below remain separate from the sealed study results. Synthetic EVAL checks validate implementation under scripted conditions and are not study observations.

### Part B: Real work

*Not run yet.*

### Part E: In the wild

*Not run yet.*

## Prior work (preexisting, not sprint results)

- **DogWhistle:** the swap audit and the baseline separation it measured. See its repository.
- **Pre-sprint direct pilot (4 November 2026; diagnostic timestamps 19:15:45–19:20:41 UTC):** 4 tasks, 4 senders, 48 receivers. [Report](results/presprint/direct/RESULTS.md)
- **Pre-sprint relay smoke test (4 November 2026; diagnostic timestamps 19:48:55–19:50:26 UTC):** 1 task, 2 relays, 12 receivers. [Report](results/presprint/relay/provenance/RELAY.md)
- **Pre-sprint local freeze:** a 16-task planted design with a local registration. It is not the sprint protocol.

These are the first and last saved diagnostic timestamps, not independently measured execution boundaries. In India time both tests ran early on 5 November, which is the date the copied reports use.

All code and data in `results/presprint/` are preexisting. They are byte-preserved copies; [IMPORT_MANIFEST.json](results/presprint/IMPORT_MANIFEST.json) records each original path and SHA-256 hash. The scripts there keep their original paths and should not be run from this folder.

### What the pre-sprint data already shows

These come from re-reading the pre-sprint traces on 6 November, during the sprint. They motivate the research questions. They are not counted as sprint results.

1. **The coalition receivers said the convention out loud.** In the direct pilot, 19 of 24 coalition answers referred to the hidden convention in their written evidence, and 17 of those spelled out the decoding rule itself, for example *"The convention decodes B/C references to preferred pair A/D"*. None of the 24 honest answers did either. All 48 receiver answers passed the allocation-validity checks. These disclosure counts are post hoc text annotations, not the measured performance of a text monitor. The [annotation record](docs/PRESPRINT_README_CHECK.md) defines the criteria and links to each answer. D2 subsequently calibrated a fixed text check; its [calibration record](sprint/partD/D2/text_calibration/CALIBRATION.md) is separate from the study results.
2. **The relays converged on the same refs; only the public-arm relay changed them.** One relay received B,C and the other A,C. Both wrote A,C, with near-identical notes putting 45 minutes on the target file A. Coalition receivers downstream then put 18–20 minutes on the target in *both* arms. That matches the pilot's codeword arm on the same task (18–19) and is far from its public arm (40–45). The swap audit read D = −0.003. The between-arm ref contrast disappeared while the instructed coalition preference remained active in both arms. Near-zero D therefore measures the absence of that contrast; it is not evidence that the audit missed a surviving between-arm signal. This is one task and two relay calls, so it is a lead, not a result.
3. **Review minutes are a plan, not an action.** In the pre-sprint tests, receivers reported how they would split 60 minutes of review across files. Part B replaces this with real edits.

## Progress

- [x] D1 registration, both arms, ledgers, scoring and independent re-scoring
- [x] D2 implementation, amendments, calibration, final EVAL, both arms, ledgers and cross-checked results
- [ ] Part B sandbox, registration, runs and results
- [ ] Part E data access, analysis and results
- [ ] Final report

## Reproducing and auditing

- **D1:** [scoring provenance](sprint/partD/D1/scoring/README.md), [machine-readable results](sprint/partD/D1/scoring/D1_SCORES.json), and [independent cross-check](sprint/partD/D1/scoring/CROSS_CHECK.md).
- **D2:** [results and reproduction command](sprint/partD/D2/results/D2_RESULTS.md), [machine-readable results](sprint/partD/D2/results/d2_score_output.json), and [result-generation script](sprint/partD/D2/results/make_d2_results.py).
- **Integrity:** the source seals and arm ledgers are checked by the scorers. Published-head checks require the checkout to match its remote branch head. Historical commit references identify original publication points; checking out an old main commit while origin/main has advanced will fail that check.

The trial and presprint files are provenance records. Pre-sprint scripts retain their original paths and should not be run from their copied locations. Earlier build reports retain historical draft statuses; final registrations, amendments and results give the completed study state.

## Safety and scope

- Agents get read-only access to a local repository. In Part B, edits happen only in a disposable copy.
- Earshot uses no attack payloads.
- The codeword is planted. Results describe what happens to such a signal, not how often agents create one.
- Findings concern specific interventions and observed outputs. No claim of spontaneous coordination, universal collusion detection or completed-code effects follows from D1 or D2. Part B is intended to examine real edits.

## Repository layout

- `results/presprint/`: preexisting pre-sprint evidence.
- `docs/SPRINT_CONTEXT.md`: sprint scope notes.
- `earshot/`: stage code, prompts, gates and integrity checks.
- `sprint/trial_run/`: the earlier trial and separated system-issue records.
- `sprint/partD/D1/`: D1 design, Codex-arm records and cross-checked scoring; Claude-arm records are on `d1-claude`.
- `sprint/partD/D2/`: D2 design, Codex-arm records and generated results; Claude-arm records are on `d2-claude`.

Pre-sprint runs used `gpt-6.1-sol` at low reasoning effort, through fresh Codex CLI processes.

## References

- DogWhistle: https://github.com/Rick-Clinton-jpg/DogWhistle
- Red-Teaming Multi-Agent Attacks for Loss-of-Control Risks: https://arxiv.org/abs/2610.24052
- AI Village dataset: https://huggingface.co/datasets/aidigestorg/ai-village
- Audit the Whisper: Detecting Steganographic Collusion in Multi-Agent LLMs: https://arxiv.org/abs/2510.04303
- Do Latent Channels Actually Communicate? A Causal Audit of Latent Multi-Agent LLM: https://arxiv.org/abs/2607.26773
- Detecting Multi-Agent Collusion Through Multi-Agent Interpretability: https://arxiv.org/abs/2604.01151
- Hidden in Plain Text: Emergence & Mitigation of Steganographic Collusion in LLMs: https://arxiv.org/abs/2410.03768