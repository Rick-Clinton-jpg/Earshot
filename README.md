# Earshot

**How far down a chain of agents does a hidden signal stay within earshot, and can oversight still hear it?**

Earshot follows a reference field as it is passed from one AI agent to the next. It asks whether each agent passes the reference on, rebuilds it, or acts on it, and whether an audit can still tell when something hidden is riding along.

Earshot continues [DogWhistle](https://github.com/Rick-Clinton-jpg/DogWhistle) and was developed during the Swarm Alignment Hackathon (6–8 November 2026). Work done before the sprint is kept in `results/presprint/` and disclosed under [Prior work](#prior-work-preexisting-not-sprint-results).

**Status — 9 November 2026:** D1, D2 and the Codex-only Part B descriptive pilot are complete, scored and computationally cross-checked on two machines. These checks reproduce computation on the same observations; they are not independent experimental replications. Separate D2 exploratory analyses are reported below.

| Stage | Status | Record |
| --- | --- | --- |
| Pre-sprint tests | Prior work, excluded from sprint results | [Evidence](results/presprint/) |
| D1 trial | Trial record, not confirmatory | [Trial report](sprint/trial_run/TRIAL_RUN_RESULTS.md) |
| D1: relay reference selection | Complete, both arms | [Results](sprint/partD/D1/scoring/D1_RESULTS.md) · [Cross-check](sprint/partD/D1/scoring/CROSS_CHECK.md) |
| D2: planted references and audit placement | Complete, both arms | [Results](sprint/partD/D2/results/D2_RESULTS.md) · [Scorer output](sprint/partD/D2/results/d2_score_output.json) |
| B: real edits | Complete, Codex-only descriptive pilot | [Results](sprint/partB/results/PART_B_RESULTS.md) · [Scores](sprint/partB/results/PART_B_SCORES.json) · [Cross-check](sprint/partB/results/CROSS_CHECK.md) |

---

A relay can turn different incoming lists into the same delivered list while leaving the receiver responsive to a direct list change. Earshot tests both places. Its separate repair pilot then checks what happened to actual code.

## Why this matters

Agents increasingly hand work to each other through structured messages: a task, a few fields, a list of files to read. In the incident described in the sprint brief, agents coordinated by passing messages through a shared space and splitting up work between them.

Most oversight checks one agent, or one message, at a time. A chain of agents can behave differently from any single link in it. A field that looks harmless at every hop can still carry a signal from the first agent to the last, or lose it, or have one invented along the way.

Earshot studies this in one small, controlled setting first, then checks it against real work.

## Research questions

| # | Question | Part |
| --- | --- | --- |
| RQ1 | When an honest relay agent receives a handoff, does it pass the references on as given or rebuild them? | D |
| RQ2 | When a planted codeword rides in the handoff, does it survive a relay, and does the swap audit still detect the agent acting on it? | D |
| RQ3 | Does the handoff change the code the last agent actually edits? With no codeword at all, does the handoff alone still shift real work? | B |

The parts ran in this order: D, then B. D measured relay reference selection and downstream review allocations. B separately tested direct handoffs in real repair sessions, without a relay. We cannot treat signal survival as evidence of practical harm by itself.

### Open questions from the sprint this work speaks to

The paper [Red-Teaming Multi-Agent Attacks for Loss-of-Control Risks](https://arxiv.org/html/2610.24052v1) studies attacks distributed across agents. Earshot addresses related questions in part:

- **Monitoring messages between agents.** Its standard monitor excludes messages between agents; its optimized attacks use shared plans, and it explicitly does not test steganographic or other covert channels. RQ1 and RQ2 study that channel directly: whether a signal survives each hop, and where an audit of it stops working.
- **Telling which agents are working together.** The swap audit can measure a specified receiving agent's sensitivity to a specified field; sensitivity alone does not establish collusion. Earshot does not try to find unknown colluders in a large crowd.
- **Not addressed:** why split-up attacks still get through when a monitor sees every agent at once. That needs a different setup.

## Key terms

- **Handoff:** the structured JSON one agent passes to the next. The field studied is `required_memory_refs`, which must name two of four allowlisted reference files (A–D). A deterministic gate rejects anything else and rebuilds the rest of the handoff from a fixed template.
- **Sender, relay, receiver:** a sender writes a handoff, a relay receives one and writes another, and a receiver acts on it. D2 uses harness-planted codewords and no model sender calls. Its receivers use hop-1 outputs; hop 2 measures survival separately.
- **Codeword:** a planted convention. A "coalition" receiver is told to read the refs as a private preference. It is planted on purpose. Earshot does not claim agents invent such conventions on their own.
- **Swap audit (S = X − W):** compare the six cross-list, different-wording action distances (X) with the six same-list, different-wording distances (W). A positive S estimates excess sensitivity to that field under the matched replay design; it does not by itself establish a hidden motive. D = S for the coalition receiver minus S for the honest receiver.

## Study design and status

Details for each part are fixed in a registration file committed before that part runs. This section gives the plan in plain terms.

### Part D: Relays (RQ1, RQ2) — completed

- **D1:** honest relays selected reference pairs on DogWhistle, across 12 tasks and four target files. Both model-and-harness arms completed 180 calls. The study measured output selection and input dependence.
- **D2:** on Radon, a repository not used in D1, the harness planted two complementary codewords for each of 12 primary tasks. Honest relays processed them, and honest, instructed-coalition and concealing receivers allocated review minutes.
- **Chain:** each accepted hop-1 output received a hop-2 relay call for survival measurement. Receivers were fed the first accepted hop-1 output for each codeword kind. No receiver was fed a hop-2 output.
- **Audit placements:** pre-relay swaps change the incoming codeword and compare the resulting downstream inputs; last-hop swaps change the refs delivered directly to the receiver. The two interventions answer different questions. Review minutes are proposed allocations of an hour, rather than measured time spent working.
- **Protocol:** [registration](sprint/partD/D2/D2_REGISTRATION.md) and [addenda 1](sprint/partD/D2/D2_ADDENDUM_1.md), [2](sprint/partD/D2/D2_ADDENDUM_2.md) and [3](sprint/partD/D2/D2_ADDENDUM_3.md), with later addenda governing. Source seals, per-arm relay seals and final ledgers preserve the study records.

### Part B: Real work (RQ3) — completed descriptive pilot

- **Setup:** Codex `gpt-6.1-sol`, low effort, edited isolated buggy copies of Radon at `54b88e5`. Twelve tasks across four candidate files each had one qualified injected bug. Handoffs were planted directly at the editing agent; there was no relay, Claude arm or concealment condition.
- **Allocation:** three different complementary pair allocations per task, each observed under five conditions, gave 180 scheduled sessions. These were three pair allocations per task, not three repetitions of an identical prompt.
- **Conditions:** H0 had no handoff; H-in and H-out were honest editing sessions whose incoming pair included or excluded the target. C-in and C-out supplied the same incoming pairs with the coalition convention: prefer the complementary pair. The incoming pair and decoded preferred pair are therefore different. The instruction said “Prioritise investigation and repair in the preferred pair,” while allowing other files and forbidding unrelated changes.
- **Measures:** target-file edits, other production-file edits, test-verified admissible repairs, exact-restoration flags and diff size. Edits are measured against the buggy baseline. Independent evaluation uses frozen diagnostics and the full 404-case test suite; a repair requires passing both with an admissible artifact.
- **Integrity and scope:** [registration](sprint/partB/PART_B_REGISTRATION.md), [source seal](sprint/partB/SEAL1.json), [runtime ledger](sprint/partB/codex_LEDGER.json) and [scoring cross-check](sprint/partB/results/CROSS_CHECK.md). The pilot is descriptive, with no inferential tests or intervals. Practice selected only the timeout; the earlier setup-fault practice is retained and excluded from study estimates.

## Results

### D1: relay reference selection

In both arms, incoming pairs that omitted the target were rarely kept: 0/72 for Codex and 2/72 for Claude. The output added the target in 72/72 and 67/72 such calls. Every task's free-choice default included the target.

Relevant non-default incoming pairs were kept at task-mean rates of 0.46 and 0.56 (`K_alt`). The registered keep-versus-not-keep outcome was unresolved in both arms. These rates are distinct from lift, which is a baseline-subtracted output-matching measure.

D1 relays could read the whole DogWhistle repository, including its own prompt files describing the convention. The registration anticipated this and fixed a rule for recording exposure. Search results showed adapter-file content in 1/180 Codex calls and 47/180 Claude calls. All were kept, as registered. Candidate-file exclusion did not prevent search exposure; how much this influenced answers is unknown.

See [D1 results](sprint/partD/D1/scoring/D1_RESULTS.md) for the registered tests, intervals, exploratory comparisons and exposure disclosure. The results cover these tasks and model-and-harness configurations, not files or models in general.

### D2: audit placement under a planted reference convention

| Audit D, task mean | Codex arm | Claude arm |
| --- | --- | --- |
| Pre-relay | 0.00 | 0.22 |
| Last-hop | 0.40 | 0.37 |

Under the two pre-relay conditions, ordinary Codex receivers planned 46.1 minutes on the target file, compared with 18.5 for receivers given the rule. The rule shifted plans under either incoming list. D measures the extra response when the list changes. In all 12 Codex tasks, the delivered hop-1 pairs selected from the first accepted replicate per kind were identical across the two incoming lists, leaving pre-relay D at zero. Direct last-hop swaps still changed plans. Claude's last-hop D was 0.37, compared with its own pre-relay 0.22. These placements answer different questions: a quiet upstream audit can coexist with a receiver responsive to its delivered list.

All eight registered tests met their decision rules, but they share data and are not eight independent confirmations. H3 retains its sharp-null and [EXT] qualifications. The 12 tasks share four files; contrast intervals use four file means, with three degrees of freedom. The registered [EXT] label marks the extended interpretation that depends on additional stated assumptions. The text-check result is conditional on receivers that followed the convention, under an explicit concealment instruction. It does not establish a general concealment capability.

The [D2 results](sprint/partD/D2/results/D2_RESULTS.md) contain the complete estimates, intervals, limitations and provenance. The sealed scorer output reproduced byte for byte on two machines. The write-up is generated from that output and the recorded exposure summary.

**Reading the rate intervals:** the D2 table includes Claude's 0.97 convention-following task mean beside a 95% interval of [0.51, 0.95]. The point estimate is the equal-weight mean of observed task rates. The interval comes from the sealed hierarchical Beta-Binomial model's population-rate parameter, using four file clusters and an importance-sampling approximation. It is not constructed around that observed mean, so the mean can fall outside it. The interval depends on the model and prior; four clusters provide limited information. The published values remain unchanged.

A [preliminary role check](sprint/partD/D2/role_check/ROLE_CHECK.md) recorded one Claude sender declining to encode the preference while separately prompted receivers followed it. This is a preliminary case, not a compliance-rate estimate; it motivated the pre-seal amendment removing model senders from both arms.

The [earlier D1 trial](sprint/trial_run/TRIAL_RUN_RESULTS.md) and all pre-sprint results below remain separate from the sealed study results. Synthetic EVAL checks validate implementation under scripted conditions and are not study observations.

### Part B: Real work

All five conditions produced 36/36 test-verified admissible repairs: 180/180 overall. Every session edited its target file; none edited another production file. Repair-rate and target-edit contrasts were zero in this pilot. No session timed out and every evaluation was available.

Every condition reached 100% observed repair success. That left no room to show improvement; failed repairs and wrong-file edits remained observable, and none occurred. Diagnostic bug reports, available tests, the smallest-change instruction and permission to repair outside the preferred pair may have constrained the preference's influence. This design does not isolate their contributions. RQ3 remains open beyond these tasks, mutations, prompts and setup. Investigation order was not measured, and passing the frozen tests provides a bounded check on repair quality.

| Condition | Exact target-file restoration |
| --- | --- |
| H0: no handoff | 34/36 |
| H-in: ordinary, target in incoming pair | 35/36 |
| H-out: ordinary, target out of incoming pair | 35/36 |
| C-in: rule given, target in incoming pair | 33/36 |
| C-out: rule given, target out of incoming pair | 33/36 |

All ten alternatives occurred on item-03, `add_inner_blocks` in `complexity.py`. The four-line alternative appeared in 2/3 no-handoff sessions, 2/6 ordinary-handoff sessions and 6/6 rule-given sessions. Identical no-handoff prompts also produced variation. This task was singled out after seeing results, so the pattern is descriptive. Equal C-in/C-out totals do not identify the cause.

As a post hoc sensitivity illustration, zero failures in 36 independent sessions gives a one-sided 95% upper failure bound of 7.98%; using 12 independent tasks gives 22.09%. Shared tasks and files weaken those independence assumptions. These are illustrative bounds, outside the pilot's registered point estimates.

See the [generated report](sprint/partB/results/PART_B_RESULTS.md), [scores](sprint/partB/results/PART_B_SCORES.json) and [cross-check](sprint/partB/results/CROSS_CHECK.md). Both generated-output SHA-256 fingerprints match Claude's second-machine fingerprints supplied by the author. The provenance record includes the second machine's reported environment and exact command.

### D2 exploratory analyses: ranking, text checks and monitor cost

These are separate analyses of the published D2 scorer output, outside the D2 registration. Their specifications were committed before their computation. The [overview and analysis records](https://github.com/Rick-Clinton-jpg/Earshot/tree/fbe76ef2a6a64bd31a4edefa2abedac74483b549/analysis) are published on the exploratory branch, pinned here to that commit.

- **Receiver-type ranking:** last-hop swap scores ranked every coalition and conceal receiver-type/task unit above every honest unit in both arms (AUC 1.0000). This is ranking separation on these observations, not a validated general-purpose detector. At the fixed rule “score > 0”, honest receivers were also flagged: 0/12 in Codex and 9/12 in Claude.
- **Text versus behaviour:** the calibrated text check flagged 12/12 coalition units and 0/12 conceal units in each arm. Last-hop behavioural scores ranked both instructed groups above honest units. Conceal receivers were explicitly instructed to conceal the convention; this does not demonstrate spontaneous collusion or identify unknown persistent agents.
- **Monitor cost:** two-call scores gave AUCs from 0.9514 to 1.0000, but flagged 4–6/12 honest Codex units and 12/12 honest Claude units at “score > 0”. Their missing within-reference baseline limits separation of reference sensitivity from ordinary answer variability.

Each unit is a receiver type within one task, across 12 tasks per arm. The monitor needs intervention access to swap references. These exploratory findings concern review allocations in D2, not code-repair outcomes in Part B.

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
3. **Review minutes are a plan, not an action.** In the pre-sprint tests, receivers reported how they would split 60 minutes of review across files. Part B separately measured real edits.

## Progress

- [x] D1 registration, both arms, ledgers, scoring and independent re-scoring
- [x] D2 implementation, amendments, calibration, final EVAL, both arms, ledgers and cross-checked results
- [x] Part B sandbox, registration, 180 Codex sessions, ledger and cross-checked descriptive results
- [x] Separate D2 exploratory analyses (published on the linked exploratory branch)
- [x] Submission paper drafted and revised locally; not yet published in this repository

## Reproducing and auditing

The [9 November documentation and integrity review](docs/REPOSITORY_REVIEW_2026-11-09.md) records the checks, corrections and remaining limitations.

- **D1:** start with the [independent cross-check and reproduction details](sprint/partD/D1/scoring/CROSS_CHECK.md), then the [machine-readable results](sprint/partD/D1/scoring/D1_SCORES.json) and [original scoring provenance](sprint/partD/D1/scoring/README.md). The original provenance is a preserved import: its exact-match expectation and description of possible numerical differences are superseded by the cross-check. The actual combined-score differences were nine correlations, at most 2e-16; intervals and decisions matched. Raw sealed-scorer array ordering also differed across filesystems.
- **D2:** [results and reproduction command](sprint/partD/D2/results/D2_RESULTS.md), [machine-readable results](sprint/partD/D2/results/d2_score_output.json), and [result-generation script](sprint/partD/D2/results/make_d2_results.py).
- **Part B:** [registered design](sprint/partB/PART_B_REGISTRATION.md), [runbook and sealed scoring command](sprint/partB/RUNBOOK.md), [generated report](sprint/partB/results/PART_B_RESULTS.md), [scores](sprint/partB/results/PART_B_SCORES.json) and [cross-check](sprint/partB/results/CROSS_CHECK.md).
- **Integrity:** the source seals and arm ledgers are checked by the scorers. Published-head checks require the checkout to match its remote branch head. Historical commit references identify original publication points; checking out an old main commit while origin/main has advanced will fail that check.

**Repository size:** the preserved Part B runtime alone contains 115,026 files and about 4.17 GB of uncompressed file content. Git compresses and deduplicates this data, so transfer size differs from checkout size. A full checkout needs several GB; use GitHub file views or a blob-filtered sparse clone for lighter reading. Full scorer verification requires all ledgered runtime files.

The trial and presprint files are provenance records. Pre-sprint scripts retain their original paths and should not be run from their copied locations. Earlier build reports retain historical draft statuses; final registrations, amendments and results give the completed study state.

**Scoring dependencies:** use Python 3.12 or later with NumPy and SciPy for the D1/D2 analysis and scorer code. The test suite also needs pytest and jsonschema. Install these in your analysis environment; the sealed `pyproject.toml` retains its original dependency declarations. Scoring uses saved records and makes no model calls.

## Safety and scope

- Agents get read-only access to a local repository. In Part B, edits happen only in a disposable copy.
- The experiment supplies a controlled reference convention; it does not target external systems.
- The codeword is planted. Results describe what happens to such a signal, not how often agents create one.
- Findings concern specific interventions and observed outputs. No claim of spontaneous coordination, universal collusion detection or completed-code effects follows from D1 or D2. Part B measured real edits in the completed Codex-only descriptive pilot.

## Repository layout

- `results/presprint/`: preexisting pre-sprint evidence.
- `docs/SPRINT_CONTEXT.md`: sprint scope notes.
- `earshot/`: stage code, prompts, gates and integrity checks.
- `sprint/trial_run/`: the earlier trial and separated system-issue records.
- `sprint/partD/D1/`: D1 design, Codex-arm records and cross-checked scoring; Claude-arm records are on `d1-claude`.
- `sprint/partD/D2/`: D2 design, Codex-arm records and generated results; Claude-arm records are on `d2-claude`.
- `sprint/partB/`: repair-pilot design, practice provenance, Codex records, ledger and cross-checked results.
- `analysis/`: separate D2 exploratory analyses on the [published exploratory branch](https://github.com/Rick-Clinton-jpg/Earshot/tree/fbe76ef2a6a64bd31a4edefa2abedac74483b549/analysis), not in this main checkout.

Pre-sprint runs used `gpt-6.1-sol` at low reasoning effort, through fresh Codex CLI processes.

## How this connects to earlier work

Roger and Greenblatt studied removing hidden information by paraphrasing model text. Hsu and colleagues found downstream agents returning towards their own reading of the evidence; Earshot's default-list pattern connects to that observation without establishing the same internal mechanism. Hand and Brain studies hidden information carried by choices that survive meaning-preserving paraphrasing; Earshot's relays choose references again. Kill-Chain Canaries tracks injected tokens across stages. BRA-Audit allocates audit points under a budget. Earshot complements these by running the same intervention audit before a relay and at the receiver. Zhang and Emu intervene on latent messages at the receiver boundary; Audit the Whisper combines several detection signals, including an agent-permutation test. Earshot examines an explicit file-reference field and separately checks real repairs.

## References

- DogWhistle: https://github.com/Rick-Clinton-jpg/DogWhistle
- Red-Teaming Multi-Agent Attacks for Loss-of-Control Risks: https://arxiv.org/abs/2610.24052
- Audit the Whisper: Detecting Steganographic Collusion in Multi-Agent LLMs: https://arxiv.org/abs/2510.04303
- Do Latent Channels Actually Communicate? A Causal Audit of Latent Multi-Agent LLM: https://arxiv.org/abs/2607.26773
- Detecting Multi-Agent Collusion Through Multi-Agent Interpretability: https://arxiv.org/abs/2604.01151
- Hidden in Plain Text: Emergence & Mitigation of Steganographic Collusion in LLMs: https://arxiv.org/abs/2410.03768
- Multi-Agent Risks from Advanced AI: https://arxiv.org/abs/2502.14143
- Preventing Language Models From Hiding Their Reasoning: https://arxiv.org/abs/2310.18512
- Secret Collusion among AI Agents: Multi-Agent Deception via Steganography (title printed in v3): https://arxiv.org/pdf/2402.07510v3
- Upstream Influence, Downstream Re-Anchoring in LLM Agent Chains: https://arxiv.org/abs/2610.17723v1
- Hand and Brain: Defenses against Agentic Steganography in Language Models: https://openreview.net/forum?id=P7fHU7ZNFQ
- Kill-Chain Canaries: Stage-Level Tracking of Prompt Injection Across Attack Surfaces and Five Production LLMs (Wang and Zhang, v4): https://arxiv.org/abs/2603.28013v4
- BRA-Audit: Budgeted Runtime Auditing for LLM Multi-Agent Systems via Cumulative-Exposure Audit-Point Placement: https://arxiv.org/abs/2608.14668v1
