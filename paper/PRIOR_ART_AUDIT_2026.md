# Prior-Art Audit — EGA v1

## Core adjacent areas reviewed

### AI control
Greenblatt et al., *AI Control: Improving Safety Despite Intentional Subversion* (ICML 2024), evaluates protocols designed to remain safe against intentional model subversion. EGA differs by treating the evidence chain and action-authorization state as the experimental object rather than evaluating untrusted-model coding behavior.

### Scalable oversight
Kenton et al., *On scalable oversight with weak LLMs judging strong LLMs* (2024), evaluates debate, consultancy and direct judging under capability asymmetry. EGA differs by making evidence completeness, source dependence and provenance explicit variables before authorization.

### Oversight communication and disagreement
Recent work studies collaborative disagreement resolution and strategic communication in oversight. These results reinforce the need to examine how evidence is elicited and presented, not only whether the final verdict is correct.

### Provenance
in-toto and SLSA provide established provenance/attestation mechanisms. EGA uses the same broad integrity principle as an experimental tool but studies the separate failure mode where a trusted signer can attest to a false claim.

## Novelty boundary

The manuscript should **not** claim invention of:
- AI control
- scalable oversight
- cryptographic provenance
- signed attestations
- separation of duties

The defensible contribution is the **synthetic benchmark and experimental framing that jointly varies evidence sufficiency, source independence, provenance integrity, trust-root compromise and escalation reliability for consequential action authorization**.

## Submission requirement

Before arXiv submission, perform one final literature search immediately before freezing v1 so the related-work section reflects the current state of the field.

## Expanded prior-art review — 18 November 2026

This update supersedes the earlier short v1-only review. It remains a targeted review, not a systematic literature review.

### Direct overlaps discovered

- He and Yu, [The Illusion of Independent Quorums: Epistemic Fault Domains and Correlated Cognitive Failures in Agentic Quorums](https://arxiv.org/abs/2609.02925) (2026), directly studies shared evidence ancestry, structural quorum cuts, dependency-aware selection/admission, and correlated failures in agentic quorums. The v3 2-of-3/3-of-3 mechanism and common-dependency scenarios must not be claimed as new quorum theory.
- Zheng et al., [Engineering Reliable Commit Gates for Agentic AI: Cost-Aware Verification Portfolios under Common-Mode Data Failures](https://arxiv.org/abs/2609.10969) (2026), directly studies verifier portfolios, common-mode data failures and commit-gate enforcement.
- Chen et al., [TradeSense-EQA](https://doi.org/10.3390/s26165272), *Sensors* 26(16), 5272 (2026), already combines cross-border trade declarations, physical sensing, evidence chains, anomaly detection and abstention. EGA must not claim generic trade-document/physical-sensor fusion or trade anomaly detection as novel.
- Wu et al., [From Intent to Execution Grant](https://arxiv.org/abs/2609.11596), Rhodes and Kang's [Proof of Execution](https://arxiv.org/abs/2607.05397), Santos-Grueiro's [Temporary Authority, Permanent Effects](https://arxiv.org/abs/2607.10487), and Chang and Geng's [Mnemosyne](https://arxiv.org/abs/2607.00269) overlap with execution-boundary contracts, commit-time authorization, runtime proof of execution and action-bound authority.
- IoT provenance and capture-time authenticity are established areas: Faraj et al.'s [systematic review](https://doi.org/10.1145/3718735), Pan et al.'s [data-provenance survey](https://doi.org/10.1145/3593294), Dirin et al.'s [IoTAttest](https://doi.org/10.3390/s23177532), and Brito et al.'s [capture-time authenticity work](https://arxiv.org/abs/2603.27883). Generic cryptographic provenance, signatures or remote attestation are not novel claims.
- Selective prediction and verifier-assisted abstention are prior work: Hendrickx et al.'s [reject-option survey](https://doi.org/10.1007/s10994-024-06534-3) and Sedoc et al.'s [Trust but Verify](https://arxiv.org/abs/2605.25133). Bounded recovery from verifier false rejection is an applied policy choice, not a new general theory.
- Trade-specific fraud and classification work predates EGA, including Triepels et al., [Data-driven fraud detection in international shipping](https://doi.org/10.1016/j.eswa.2018.01.007), and machine-learning assessment of HS-code correctness in customs declarations [Chen et al. (2021)](https://doi.org/10.1109/DSAA53316.2021.9564203).

### Additional standards and work in progress

- Kahn (1998), [Tolerating Penetrations and Insider Attacks by Requiring Independent Corroboration](https://www.nspw.org/papers/1998/nspw1998-kahn.pdf), establishes the difficulty of independence under common interests and administration.
- Buijsman and Veluwenkamp (2023), [Spotting When Algorithms Are Wrong](https://doi.org/10.1007/s11023-022-09591-0), provides prior conceptual work on undercutting and rebutting defeaters.
- The UK NPSA's [Claims, Arguments and Evidence concepts](https://www.npsa.gov.uk/system/files/documents/npsa-concepts-and-their-applicationcae-concepts1.pdf) already address evidence credibility, authenticity, provenance, competence and defeaters.
- [RFC 9943 — SCITT Architecture](https://www.rfc-editor.org/rfc/rfc9943.html) (March 2026) specifies signed statements, transparency services, receipts, append-only and non-equivocation properties.
- The 2026 Internet-Drafts [DIV](https://datatracker.ietf.org/doc/html/draft-janbjer-div-01), [DEWP](https://datatracker.ietf.org/doc/html/draft-janbjer-dewp-01), and [ARP](https://datatracker.ietf.org/doc/html/draft-hillier-scitt-arp-06) are especially relevant work in progress. ARP already describes witness sets, pairwise distinct operating-party identifiers, common-control exclusions, and the limitation that declared independence does not prove actual independence. These are Internet-Drafts, not IETF-endorsed standards, but they are public technical prior art.

### Updated novelty position

The broad contribution is **not** a new quorum, provenance, execution-gating, trade-sensing or defeater theory. The current v3 work is a synthetic implementation and threshold-sensitivity study that integrates document agreement, extraction consistency, freshness, external physical measurements, registry-signed source identities, and a narrow verifier-false-reject recovery rule in an EXIM-inspired action gate.

The v4 branch adds claim-specific source competence, unit checks, credential/evidence validity windows, replay-state interfaces, parser input/output binding, calibration fields, and exact action-payload binding. It is still a synthetic prototype; its dependency and trust metadata are declared/signed test fields, not independently audited facts.

### Next experiment required by the earlier audit

The next witness-independence study should compare:
1. key-unique only;
2. direct-field-distinct 2-of-3;
3. direct-field-distinct 3-of-3;
4. graph-aware selection using transitive dependency ancestry across parent control, cloud identity provider, key-management root, firmware/build pipeline, acquisition device, physical measurement source and upstream feed.

It should include distinct identifiers with a shared ancestor, incomplete dependency manifests, and compromised trust-root metadata. EFD and ARP already cover the general theory; this should be an EXIM-specific empirical comparison, not a new structural-cut metric.

**Submission decision remains NOT READY.** The original historical 1B–2E result runners and complete parameter configurations are still absent; the new reconstruction runners are new simulations, not historical reproductions. v3/v4 supplementary runners are separate experiments. A final full-text novelty audit, clean-checkout rerun, and manuscript/security review remain required.


### Additional direct overlaps verified on 18 November 2026

The following sources were checked against their arXiv records, full-text pages or publisher/standards records. This is a targeted source review, not a systematic review.

- He and Yu, [The Honest Quorum Problem: Epistemic Byzantine Fault Tolerance for Agentic Infrastructure](https://arxiv.org/abs/2607.16109) (2026), explicitly models authenticated, responsive, protocol-compliant validators that can nevertheless endorse semantically invalid transitions because of correlated evidence, model, prompt, retrieval, toolchain or infrastructure dependencies. It derives semantic-safety and liveness threshold conditions. This is a direct theoretical overlap with the EGA quorum motivation; EGA must not claim to introduce epistemic quorum failure or a general quorum threshold theory.
- Mazzocchetti, [Runtime Governance for Agentic AI: Action-Boundary Control with Trusted Provenance and Fail-Closed Execution](https://arxiv.org/abs/2608.16891) (Aegis, 2026), places a trusted runtime decision layer before tool side effects, resolves provenance server-side, fails closed and uses a Senate-style quorum path. Its sandbox evaluation reports 6,300 rows. This is a close systems-level overlap with EGA's action boundary and provenance gate.
- Zhou, [CATP: Design and Evaluation of Local Agent Authorization and Audit Evidence](https://arxiv.org/abs/2609.38223) (2026), binds local pre-execution authorization evidence to the enforcement-time policy and adapter-normalized action, persists evidence before permission is returned, and verifies receipts offline. It tests tampering, substitution, replay, concurrency and persistence. EGA's action-payload binding and audit evidence are not novel in isolation.
- Zhu and Wang, [Explanation-Bound Tool Execution for AI Agents: Server-Verified Action Claims Without Trusting Model Rationales](https://arxiv.org/abs/2607.25364) (EBTE, 2026), converts decision-relevant rationales into typed action claims and checks them against server-held intent, policy, payload, tool, risk, provenance and freshness. Its conformance suite includes 136 scenarios and hard contradictions. This directly overlaps with EGA's claim-scoped evidence checks and fail-closed action eligibility.
- Liu Yanglet, Wang and Capponi, [No Certificate, No Execution: Certified Traces as a Foundation for Trustworthy AI Agents](https://arxiv.org/abs/2605.24462) (2026), formalizes Proposal--Certification--Execution and requires a checkable certificate for an entire proposed execution trace. This overlaps with the broad principle of evidence-conditioned execution.
- Kainan and Hershman, [Agentic Process Evidence: Process-Aware Logging for Agentic Governance](https://arxiv.org/abs/2610.40071) (2026), proposes signed, tamper-evident, machine-readable process attestations linked to outcomes and aligned with in-toto-style supply-chain attestations. Generic agent-process provenance is therefore not an EGA novelty claim.
- Wang et al., [From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents](https://arxiv.org/abs/2606.04990) (2026), defines typed execution provenance graphs and evidence-tracing relations, including trace assurance and provenance origin. It identifies gaps in integrated trust functions and end-to-end provenance benchmarks. EGA's graph representation is deliberately narrower and domain-specific, not a new general trace schema.
- Zhai et al., [Heading Off Correlated Failures through Independence-as-a-Service](https://doi.org/10.5555/2685048.2685073), EuroSys 2014, proactively collects multi-layer network, hardware and software dependencies and audits hidden common dependencies. This is direct prior art for the v5 dependency-graph experiment. The v5 result is an application-specific comparison in an EXIM-inspired threat matrix, not a new graph-independence algorithm.
- Choi, [Identifying Trade Mis-Invoicing Through Customs Data Analysis](https://doi.org/10.55596/001c.116214), *World Customs Journal* 13(2), 59--76 (2019), uses actual customs data, abnormal unit-price filtering and mirror-trade discrepancies, with validation against customs interventions. This establishes prior art for customs-data fraud screening, though it does not provide the same cryptographic source-to-action authorization model.

### Revised contribution statement

The strongest defensible contribution is a **reproducible, EXIM-inspired synthetic threat-matrix and comparative systems evaluation** of how cross-document evidence, independent-source claims, capture integrity, claim-scoped provenance, action binding, and transitive dependency metadata interact before a consequential action. The work compares specified baselines and attack cases and documents where each mechanism fails.

The work does **not** establish a new theory or primitive for:
- quorum safety or epistemic fault tolerance;
- runtime action-boundary governance;
- signed authorization records or certified execution traces;
- cryptographic provenance or supply-chain attestations;
- graph-based independence auditing;
- customs fraud detection or multimodal trade sensing.

The benchmark is synthetic. It does not establish real-world false-positive/false-negative rates, operational source independence, or deployment safety. The v4 and v5 additions improve the controlled threat model, but they do not remove the need for independently adjudicated EXIM data and external replication.

### Revised arXiv gate

Before submission, the manuscript must:
1. cite and explicitly compare the direct overlaps above;
2. report v3, v4 and v5 as separate supplementary experiments with exact run IDs and artifact hashes;
3. distinguish a compromised registry signing private key (with the original public key pinned) from trust-anchor replacement;
4. keep historical 1B--2E reported outputs separate from newly generated reconstruction results;
5. state that all current EGA benchmark outcomes are synthetic and avoid deployment-probability claims;
6. undergo a clean-checkout reproduction and independent technical review.

**Submission decision remains NOT READY.** The research line has progressed, but a synthetic benchmark and internal CI success are not substitutes for real-world validation or independent review.
