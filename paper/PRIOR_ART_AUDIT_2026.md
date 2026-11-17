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
