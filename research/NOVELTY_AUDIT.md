# Research Novelty Audit — Evidence-Gated Autonomy

**Review date:** 2026-11-18  
**Scope:** Public literature surfaced in the initial novelty review of Evidence-Trust v1–v3.  
**Status:** Preliminary but material; expand before any manuscript submission.  
**Purpose:** Prevent the project from claiming novelty for mechanisms already substantially described in prior work.

## Executive finding

The broad claim that independent agents/witnesses do not create independent assurance when they share upstream evidence, and that authorization should account for common-cause dependencies, is **not novel**. A directly overlapping paper was submitted to arXiv on 2026-08-24:

- Jun He and Deying Yu, [The Illusion of Independent Quorums: Epistemic Fault Domains and Correlated Cognitive Failures in Agentic Quorums](https://arxiv.org/abs/2609.02925), arXiv:2609.02925 (2026).

It introduces Epistemic Fault Domains, a Structural Epistemic Cut, a Semantic Compromise Cut, dependency-aware quorum selection and runtime admission, analytical/Monte Carlo mechanism studies, and a frozen 120-task operational benchmark. Its document-policy compliance category and separated evidence packages also overlap the broad setting of evidence-backed enterprise decisions.

**Consequence:** Evidence-Trust v3's 2-of-3 authenticated witness quorum, source/admin-domain diversity checks, shared-dependency controls, and 2-of-3 versus 3-of-3 sensitivity must not be presented as a new quorum theory or a novel solution to correlated agent failures. They are best described as a domain-specific implementation/extension and a controlled synthetic replication of related failure mechanisms.

## Comparison with the current repository

| Current project element | Prior-work overlap | Safe characterization |
|---|---|---|
| Three witnesses, 2-of-3 and 3-of-3 | EFD paper evaluates 2-of-3 and 3-of-3, shared versus separated evidence paths, and quorum failure under common causes | Implementation-level threshold study; not novel quorum theory |
| Distinct source, acquisition and administrative-domain labels | EFD formalizes shared epistemic ancestry and warns that false separation/fabricated lineage can inflate the structural cut | A credential-binding prototype; domain labels are claims, not proof of independence |
| Registry-root compromise and forged identity credential | EFD explicitly discusses incomplete provenance and fabricated lineage metadata as limitations; PKI trust-root failure is established security territory | Threat-model extension in this synthetic document workflow |
| Source forgery before capture | EFD's benchmark includes corrupted evidence roots and its theory distinguishes evidence ancestry from agent identity | Domain-specific pre-capture document-origin control |
| Evidence-gated action and authorization chain | Overlap with runtime proof of execution, commit-time authorization, governed execution and proof-derived authority | Do not claim generic agent execution gating as novel |
| EXIM trade documents plus physical sensing and evidence chains | TradeSense-EQA already integrates declarations, weighing, RFID, GPS/AIS, seals, process graphs and abstention | Do not claim generic multimodal trade evidence fusion or trade anomaly detection as novel |
| Bounded recovery from isolated verifier false rejection | Related to selective prediction/reject-option research and prover-verifier deliberation; the exact combination with document evidence and witness-backed policy recovery remains to be audited | Candidate differentiator, not yet an established novelty claim |

## High-priority related work

1. **Jun He and Deying Yu (2026), [The Illusion of Independent Quorums](https://arxiv.org/abs/2609.02925), arXiv:2609.02925.** Direct overlap: common-cause evidence ancestry, quorum structural resilience, dependency-aware admission and external benchmark design.
2. **Zihao Zheng, Baichuan Li, Junyi Yao and Jiayu Long (2026), [Engineering Reliable Commit Gates for Agentic AI: Cost-Aware Verification Portfolios under Common-Mode Data Failures](https://arxiv.org/abs/2609.10969), arXiv:2609.10969.** Direct overlap with verifier portfolios, shared versus independent evidence sources, cost-aware verification and commit gates. Their abstract reports a fixed-call 2×2 experiment separating model and evidence diversity.
3. **Bo Wu, Lin Wang, Yong Zhang and Jiang Deng (2026), [From Intent to Execution Grant: An Execution-Boundary Conformance Profile for High-Risk AI Actions](https://arxiv.org/abs/2609.11596), arXiv:2609.11596.** Overlap with canonical action binding, evidence obligations, deterministic adjudication, decision derivation, execution grants and redemption-time checks.
4. **Jason D. Rhodes and George Kang (2026), [Proof of Execution: Runtime Verification for Governed AI Agent Actions](https://arxiv.org/abs/2607.05397), arXiv:2607.05397.** Overlap with execution contracts, causal event streams, cryptographic attestations, authorization/effect/history binding and replay.
5. **Igor Santos-Grueiro (2026), [Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents](https://arxiv.org/abs/2607.10487), arXiv:2607.10487.** Overlap with current justifications, exact-effect binding, revocation and atomic commit-time authorization.
6. **Edward Y. Chang and Longling Geng (2026), [Mnemosyne: Agentic Transaction Processing for Validating and Repairing AI-generated Workflows](https://arxiv.org/abs/2607.00269), arXiv:2607.00269.** Overlap with deterministic admission, append-only transition logs, bounded repair and re-admission.
7. **Jun He and Deying Yu (2026), [Verifiable Agentic Infrastructure: Proof-Derived Authorization for Sovereign AI Systems](https://arxiv.org/abs/2605.15228), arXiv:2605.15228.** Overlap with proof-derived execution authority and append-only evidence chains.
8. **Jun He, Openkedge Io and Deying Yu (2026), [When AI Agents Commit: Cognitive Serializability Across Data, Evidence, Policy, and Authority](https://arxiv.org/abs/2609.20261), arXiv:2609.20261.** Overlap with stale evidence/policy/authority at commit time and witness-bound grants.
9. **Elias Calboreanu (2026), [LATTICE: a governance-first architecture for authorized autonomous AI operations](https://doi.org/10.3389/frai.2026.1800407), Frontiers in Artificial Intelligence 9 (2026).** Overlap with separation of planning, execution and governance, deterministic policy gates, human escalation and cryptographic audit trails.
10. **M. Llambí-Morillas and D. Fernández-Fernández (2026), [Cryptographically verifiable authorization for autonomous AI agents: a falsifiable hypothesis and proof of concept](https://doi.org/10.3389/fcomp.2026.1966725), Frontiers in Computer Science 8 (2026).** Related to cryptographic binding of agent principal, request, context and policy. The peer-reviewed article was published 24 September 2026; DOI: 10.3389/fcomp.2026.1966725.
11. **João Sedoc, Baotong Zhang and Dean P. Foster (2026), [Trust but Verify: Prover-Verifier Deliberation for Selective LLM Prediction](https://arxiv.org/abs/2605.25133), arXiv:2605.25133.** Related to verifier challenge/accept/reject protocols and coverage–precision trade-offs.
12. **Dekun Yang (2026), [Calibrated Selective Fact-Checking via Evidence Chain Evaluation](https://arxiv.org/abs/2607.18240), arXiv:2607.18240.** Related to evidence-chain evaluation, source metadata and abstention when evidence is weak or inconsistent.
13. **Kilian Hendrickx, Lorenzo Perini, Dries Van der Plas, Wannes Meert and Jesse J. Davis (2024), [Machine learning with a reject option: a survey](https://doi.org/10.1007/s10994-024-06534-3), Machine Learning 113 (2024), 3073–3110.** Established foundations for reject-option/abstention and coverage–risk evaluation.

## What the current experiment actually contributes

The present v3 code is a deterministic, synthetic EXIM/document-evidence adaptation with:
- registry-signed witness identity credentials;
- case-scoped, signed measurement assertions;
- explicit source, acquisition-domain, administrative-domain and key identifiers;
- a distinction between pre-capture source forgery and credential tampering;
- registry-root compromise and witness collusion controls;
- a narrowly bounded recovery path for isolated verifier false rejection, requiring the other v1 evidence gates to pass;
- explicit 2-of-3 versus 3-of-3 availability/safety sensitivity.

These are useful engineering and experimental artifacts. They do **not** prove real-world source identity, operational independence, source truth, calibrated risk, or production security. The current benchmark's oracle-like witness is generated from synthetic ground truth, and the benchmark has only 700 HIGH-risk cases.

14. **Meitong Chen et al. (2026), [TradeSense-EQA: Artificial Intelligence-Driven Sensing of Cross-Border Trade Risks Through Declaration-to-Physical-Fact Alignment and Evidence-Grounded Question Answering](https://doi.org/10.3390/s26165272), *Sensors* 26(16), 5272.** Direct overlap with the EXIM application: trade documents, GPS/AIS, RFID, electronic seals, port weighing, environmental sensors, evidence chains, cross-modal anomaly detection, and abstention. The paper explicitly notes that reliability weighting cannot fully exclude deliberate sensor manipulation or simultaneous sensor failures. Its data availability statement says data are available on request; no public code/data repository is linked from the article page.
15. **Omair Faraj, David Megías and Joaquín García-Alfaro (2025), [Security Approaches for Data Provenance in the Internet of Things: A Systematic Literature Review](https://doi.org/10.1145/3718735), *ACM Computing Surveys* 57(10), Article 261.** Broad prior work on provenance security, IoT attacks, trustworthiness, integrity, confidentiality and availability.
16. **Bofeng Pan, Natalia Stakhanova and Suprio Ray (2023), [Data Provenance in Security and Privacy](https://doi.org/10.1145/3593294), *ACM Computing Surveys* 55(14s), Article 323.** Foundational survey of secure provenance and threat provenance; rules out claiming generic cryptographic provenance as novel.
17. **Amir Dirin, Ian Oliver and Teemu H. Laine (2023), [A Security Framework for Increasing Data and Device Integrity in Internet of Things Systems](https://doi.org/10.3390/s23177532), *Sensors* 23, 7532.** IoTAttest uses TPM 2.0 and remote attestation for device, data and control-plane integrity.
18. **Eduardo Brito et al. (2026), [Decentralized Proof-of-Location for Content Provenance: Towards Capture-Time Authenticity](https://arxiv.org/abs/2603.27883), arXiv:2603.27883.** Related to multi-observer physical-event validation and capture-time authenticity; device signatures alone are not enough.
19. **Ron Triepels, Hennie Daniels and Ad Feelders (2018), [Data-driven fraud detection in international shipping](https://doi.org/10.1016/j.eswa.2018.01.007), *Expert Systems with Applications* 99, 193–202.** Prior work on document manipulation, miscoding and smuggling using shipment data.
20. **Hao Chen et al. (2021), [The use of machine learning to identify the correctness of HS Code for the customs import declarations](https://doi.org/10.1109/DSAA53316.2021.9564203), IEEE DSAA.** Prior work on HS-code correctness using customs ground-truth data.

## Additional direct prior art and standards recovered from the repository's earlier audit

The existing v3 review also identifies prior work and current technical specifications that must remain in the novelty boundary:

- Clifford Kahn (1998), [Tolerating Penetrations and Insider Attacks by Requiring Independent Corroboration](https://www.nspw.org/papers/1998/nspw1998-kahn.pdf). Independent corroboration and the difficulty of proving independence are established concepts.
- Stefan Buijsman and Herman Veluwenkamp (2023), [Spotting When Algorithms Are Wrong](https://doi.org/10.1007/s11023-022-09591-0), *Minds and Machines* 33, 541–562. Undercutting and rebutting defeaters are prior conceptual foundations for bounded recovery.
- UK National Protective Security Authority, [Claims, Arguments and Evidence (CAE) Concepts](https://www.npsa.gov.uk/system/files/documents/npsa-concepts-and-their-applicationcae-concepts1.pdf). Evidence credibility, authenticity, provenance, competence and defeaters are established assurance-case concerns.
- IETF [RFC 9943 — An Architecture for Trustworthy and Transparent Digital Supply Chains (SCITT Architecture)](https://www.rfc-editor.org/rfc/rfc9943.html) (March 2026). Signed statements, transparency services, receipts, append-only and non-equivocation properties are existing infrastructure.
- Christian Janbjer, [Deterministic Intent Verification (DIV) Protocol Specification](https://datatracker.ietf.org/doc/html/draft-janbjer-div-01), draft-janbjer-div-01 (19 Oct 2026), work in progress. Signed intent payloads, local trust anchors, identity-bound multi-approver requirements, freshness, nonce redemption and execution-time verification are adjacent prior art.
- Christian Janbjer, [Deterministic Evidence & Witness Protocol (DEWP)](https://datatracker.ietf.org/doc/html/draft-janbjer-dewp-01), draft-janbjer-dewp-01 (19 Oct 2026), work in progress. Tamper-evident audit commitments, Merkle inclusion, independent anchors and signed execution-evidence statements overlap with provenance and witness evidence.
- Joel Hillier, [Attestation Reconciliation Protocol (ARP)](https://datatracker.ietf.org/doc/html/draft-hillier-scitt-arp-06), draft-hillier-scitt-arp-06 (23 Oct 2026), work in progress. Witness sets, pairwise distinct operating-party identifiers, common-control exclusions, and the explicit limitation that declared independence is not proof of actual independence are particularly close to v3's quorum mechanism.

DIV, DEWP and ARP are Internet-Drafts, not IETF-endorsed standards. They are still relevant public technical prior art and must be cited as work in progress.

## Candidate research reframing

The broad directions of generic quorum reliability, trade anomaly detection, evidence chains, cryptographic provenance and execution-time authorization are already occupied by substantial prior work. The current evidence does not justify a novelty claim for any of those ideas in isolation.

The narrower candidate is an **adversarial security evaluation of provenance-to-action binding in document-driven trade workflows**:

> Can a controller distinguish content integrity, signer authenticity, evidence freshness, subject applicability, claim/source competence, transformation lineage, calibration assurance, dependency separation, and exact-action binding—and which combinations are necessary to prevent a signed but stale, misbound, semantically inapplicable, or compromised evidence item from authorizing a high-consequence trade action?

This is not yet a novelty claim. It must be compared against EFD/DAQC, VP-CONTROL, TradeSense-EQA, commit-time authorization, execution-boundary contracts, runtime proof of execution, IoT provenance/remote attestation, and capture-time authenticity research.

A possible contribution is a reproducible EXIM-focused adversarial benchmark that attacks the *assurance properties* of evidence objects and their binding to specific claims and actions, rather than proposing another generic quorum or anomaly detector. For example, a signed weighbridge record may support gross weight but must not be accepted as evidence for HS classification; a fresh measurement for another container must not satisfy the current shipment; a valid signature over a stale measurement must not authorize a current filing; and a valid capture receipt must not imply that a source document was truthful before capture. This would be an empirical security evaluation with explicit assumptions, not a new cryptographic primitive or general theory.

A separate follow-on experiment, already identified in the earlier v3 review, should compare key-unique, direct-field-distinct 2-of-3, direct-field-distinct 3-of-3, and graph-aware witness selection using transitive dependency ancestry (parent control, cloud identity provider, key-management root, firmware/build pipeline, acquisition device, physical measurement source and upstream feed). It should inject cases where identifiers differ while an ancestor is shared, and cases where dependency manifests are incomplete or falsified. EFD and ARP already cover much of the general theory, so this should be framed as an EXIM-specific empirical comparison and not as a new structural-cut metric.

## Required next research work

1. Complete a structured novelty matrix against the full texts and released artifacts of the highest-overlap papers, especially EFD, VP-CONTROL, EBL-Core, Proof of Execution, CTA and Mnemosyne.
2. Inspect the EFD code and frozen benchmark; determine which current tests are reproductions, which are orthogonal, and whether any benchmark design is too similar to reuse without clear attribution.
3. Re-run the latest v3 source commit and verify the newly added pre-registered 2-of-3/3-of-3 output assertions against the artifact. Do not cite the earlier artifact if its schema predates the recovery and sensitivity code.
4. Report the bounded-recovery results separately from quorum results. Preserve all false-accept and false-reject cases in the confusion matrix.
5. Design a claim-level EXIM benchmark with source, transformation, authority, time and cross-document conflict attacks. Keep synthetic and real data clearly separated.
6. Only after those steps, choose whether to retain v3 as a reproducibility/engineering extension, create a new research branch for the claim-level contribution, or substantially revise the manuscript.

## Claim discipline

Do not claim:
- a new quorum theory, EFD metric, or general solution to common-mode failure;
- cryptographic signatures prove semantic truth or real-world independence;
- zero observed unsafe actions imply a zero failure probability;
- synthetic deterministic case counts are real-world probabilities;
- production readiness or deployment safety.

Any eventual novelty statement must be supported by a dated search, full-text comparison, exact baseline implementations, and a falsifiable experiment.


## Additional literature recovered on 18 November 2026

This targeted follow-up adds several direct overlaps that materially narrow the novelty claim. The sources were checked against arXiv records, full-text pages or publisher/standards records; this is not a systematic review.

| Work | Direct overlap with EGA | Implication |
|---|---|---|
| He and Yu, [The Honest Quorum Problem: Epistemic Byzantine Fault Tolerance for Agentic Infrastructure](https://arxiv.org/abs/2607.16109) (2026) | Authenticated, protocol-compliant validators can still endorse semantically invalid transitions due to correlated evidence/model/tool dependencies; derives safety and liveness threshold conditions | Do not claim epistemic quorum failure or a general quorum threshold theory |
| Mazzocchetti, [Aegis: Runtime Governance for Agentic AI](https://arxiv.org/abs/2608.16891) (2026) | Trusted provenance-aware runtime action boundary, fail-closed behavior and Senate-style quorum; 6,300-row sandbox evaluation | Runtime action gating and provenance-aware execution are not novel in isolation |
| Zhou, [CATP: Design and Evaluation of Local Agent Authorization and Audit Evidence](https://arxiv.org/abs/2609.38223) (2026) | Signed authorization records bind enforcement-time policy and normalized action; durable pre-execution evidence, offline receipt verification, replay and substitution tests | EGA's action/evidence binding is an applied profile, not a new authorization primitive |
| Zhu and Wang, [Explanation-Bound Tool Execution for AI Agents](https://arxiv.org/abs/2607.25364) (2026) | Server-verifies typed action claims against intent, policy, payload, tool, risk, provenance and freshness; 136 conformance scenarios | Direct overlap with claim-scoped evidence and fail-closed action eligibility |
| Liu Yanglet, Wang and Capponi, [No Certificate, No Execution](https://arxiv.org/abs/2605.24462) (2026) | Proposal--Certification--Execution formalism; execution conditional on certificates for whole traces | Do not claim the general principle of certified execution |
| Kainan and Hershman, [Agentic Process Evidence](https://arxiv.org/abs/2610.40071) (2026) | Signed, tamper-evident process attestations linked to outcomes and in-toto-style provenance | Agent-process attestation is prior art |
| Wang et al., [From Agent Traces to Trust](https://arxiv.org/abs/2606.04990) (2026) | Survey of typed execution provenance graphs, evidence tracing, trace assurance and end-to-end provenance benchmarks | EGA's graph representation is a narrow domain-specific schema, not a new general provenance graph |
| Zhai et al., [Heading Off Correlated Failures through Independence-as-a-Service](https://doi.org/10.5555/2685048.2685073), EuroSys 2014 | Proactive collection of multi-layer dependencies and graph-based auditing of hidden common dependencies across network, hardware and software | The v5 graph experiment is an EXIM-inspired application of established dependency auditing, not a new graph-independence algorithm |
| Choi, [Identifying Trade Mis-Invoicing Through Customs Data Analysis](https://doi.org/10.55596/001c.116214), *World Customs Journal* 13(2), 59--76 (2019) | Uses actual customs data, abnormal unit-price filters and mirror-trade discrepancies, validated against customs interventions | Customs-data fraud screening is established; EGA's distinct question is evidence-to-action authorization under synthetic attacks |

### Revised research contribution

The strongest defensible contribution is a **reproducible, EXIM-inspired synthetic threat-matrix and comparative systems evaluation** of how cross-document evidence, independent-source claims, capture integrity, claim-scoped provenance, action binding and transitive dependency metadata interact before a consequential action.

The work does not establish a new theory or primitive for quorum safety, runtime action-boundary governance, signed authorization records, certified traces, cryptographic provenance, graph-based independence auditing, customs fraud detection or multimodal trade sensing.

The v4/v5 experiments improve the controlled threat model, but all outcomes remain synthetic. The project has not established operational error rates, true source independence, or production safety. A credible stronger empirical contribution would require independently adjudicated and consented EXIM cases, or a clearly scoped benchmark contribution with an external replication.

### Trust-root threat-model correction

All registry-root scenarios must be described precisely. The current v3/v4/v5 code models compromise of the existing registry signing private key while retaining the original public key as the verifier's trust anchor. This is distinct from replacing the trust anchor itself. The v4 scenario additionally assumes the compromised issuer can enroll attacker-controlled keys across all evidence roles; the v5 scenario uses two colluding witnesses and an honest third witness while the compromised issuer signs a graph that omits their true shared dependency.

### Submission boundary

The current work should be presented as a synthetic systems/benchmark study, not as a validated safety mechanism. The arXiv gate remains **NOT READY** until v3/v4/v5 runs and hashes are pinned, the manuscript separates historical reported outputs from new reproductions, the latest literature is integrated, a clean-checkout reproduction is recorded, and an independent technical review is completed.
