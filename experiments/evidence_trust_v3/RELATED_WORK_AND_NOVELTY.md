# Related Work and Novelty Boundaries — Evidence-Gated Autonomy

**Review date:** 17 November 2026  
**Status:** Targeted preliminary review, not a systematic literature review.

## Executive assessment

The v3 contribution must not be framed as inventing witness quorums, independent corroboration, cryptographic identity binding, provenance, or defeaters. Those ideas have substantial prior art. The defensible direction is a domain-specific, experimentally evaluated integration: document-grounded logistics decisions that combine document agreement, extraction consistency, provenance, authorization freshness, independently sourced physical measurements, and an explicit action gate. The current benchmark also evaluates pre-capture source forgery, shared administrative control, registry-root compromise, verifier false rejection, and the security/availability trade-off between 2-of-3 and 3-of-3.

Even that applied contribution is preliminary. All current measurements and identities are synthetic; administrative-domain labels are declared inputs, not independently proven facts. The benchmark does not yet establish real-world independence or deployment safety.

## Prior work and standards

| Work | Relevant contribution | Implication for this project |
|---|---|---|
| Kahn (1998), *Tolerating Penetrations and Insider Attacks by Requiring Independent Corroboration* | Studies independent corroboration for compromise tolerance; explicitly treats independence as relative to interests and dependent on trust, known connections, and barriers to collusion. It also notes that replicated systems with identical implementations or administrators share vulnerabilities. | Independent corroboration and the difficulty of establishing independence are not new. The current v3 use of distinct identity/domain fields is a simple declared-attribute approximation, not a proof of independence. |
| Buijsman & Veluwenkamp (2022/2023), *Spotting When Algorithms Are Wrong* | Proposes undercutting defeaters (evidence that an algorithm is unreliable in a case) and rebutting defeaters (independent information that contradicts its output); studies a risk-classification system used by the Dutch tax authority. | The conceptual basis for witness-backed recovery from a machine-verifier false rejection is prior art. Our implementation is a narrow policy integration in a synthetic document-AI decision pipeline, not a new theory of defeaters. |
| UK NPSA, *Claims, Arguments and Evidence (CAE) Concepts* | Treats evidence as support or rebuttal for explicit claims; recommends addressing evidence credibility, authenticity, provenance, competence, and defeaters. | Evidence quality and defeater handling are established assurance-case concerns. The project should make claim-to-evidence relationships explicit rather than presenting signatures as proof of truth. |
| RFC 9943, *An Architecture for Trustworthy and Transparent Digital Supply Chains* (SCITT Architecture, March 2026) | Defines signed statements, transparency services, verifiable data structures, receipts, append-only and non-equivocation properties. It separates statement authenticity/transparency from application-specific truth and liability. | Use transparency/provenance infrastructure as a possible integration layer, not as a novelty claim. A valid signature or transparency receipt does not prove that a document or physical measurement is true. |
| Janbjer, *Deterministic Intent Verification (DIV) Protocol Specification*, draft-janbjer-div-01 (19 Oct 2026) | Active individual Internet-Draft for signed intent payloads, local trust anchors, identity-bound multi-approver requirements, freshness, nonce redemption, and execution-time verification. Its current reserved evidence field MUST be null. | Signed intent binding and distinct-identity approval quorums are direct adjacent work. Our witness roles are intended to attest observations, not to act as approvers; the current DIV draft does not define external-evidence-conditioned intent semantics in that reserved field. |
| Janbjer, *Deterministic Evidence & Witness Protocol (DEWP)*, draft-janbjer-dewp-01 (19 Oct 2026) | Active individual Internet-Draft for tamper-evident audit commitments, Merkle inclusion, independent anchors, and signed execution-evidence statements. It explicitly limits claims to what a caller-trusted evidence source reported; it does not prove the physical event. | Cryptographic evidence records, independent anchors, and source-trust separation are not new. Our benchmark concerns pre-action authorization from document and physical-observation evidence, rather than post-action audit-log commitments. |
| Hillier, *Attestation Reconciliation Protocol (ARP)*, draft-hillier-scitt-arp-06 (23 Oct 2026) | Active individual Internet-Draft (intended Standards Track) specifying witness sets and quorum rules with pairwise distinct operating-party identifiers and verification-method references, common-control exclusions, and an explicit limitation that declared independence is not proof of actual independence. | This is particularly close prior art for witness quorum and identity/domain distinctness. Our work must distinguish the logistics decision problem and its fault model, not claim the quorum mechanism itself as novel. |

**Internet-Draft status note:** DIV, DEWP, and ARP are individual Internet-Drafts. An Internet-Draft is a work-in-progress document and does not imply IETF endorsement or consensus. They are important public technical prior art, but must be cited as work in progress, not as published IETF standards.

## Claim boundaries for EGA v3

### Claims we should not make

- First use of independent corroboration, witness quorums, threshold signatures, or distinct-identity approval.
- Cryptographic signatures prove that a source's observation is physically true.
- Distinct administrative-domain strings prove operational independence.
- A 2-of-3 or 3-of-3 threshold is universally optimal.
- The synthetic benchmark establishes production security or real-world compromise probabilities.
- Witness-backed recovery from a false rejection is a new general theory; it is an applied defeater mechanism.

### Potentially defensible contribution

A reproducible, domain-specific policy and benchmark that evaluates how independently sourced physical measurements interact with document extraction, cross-document consistency, provenance, authorization freshness, and a risk-aware action gate. The current results show:

1. A narrowly scoped witness-backed recovery can repair the benchmark's C7 verifier-false-reject cases while retaining the other v1 evidence guards.
2. A 2-of-3 policy tolerates one invalid credential but is vulnerable to two matching compromised witnesses in the C4 consistent-but-wrong family.
3. A 3-of-3 policy blocks the tested two-witness collusion but loses availability under one invalid credential or a compromised registry root; it still fails if all three witnesses collude.
4. Pre-capture source forgery must be labelled unsafe relative to the unchanged physical ground truth; safe-action coverage is undefined for that attack scenario.

These are benchmark-specific findings, not general security guarantees.

## Main unresolved gap: independence is a dependency graph, not a set of labels

The current v3 credential binds witness ID, key ID, source ID, acquisition domain, administrative domain, and tenant. The verifier checks that the matching supporters have distinct values in the required fields. This catches exact duplicates and a declared shared-administration case, but it cannot detect transitive or hidden common control.

For example, three witnesses may have distinct child administrators and signing keys while sharing a parent company, cloud identity provider, deployment pipeline, firmware, physical scale, sensor feed, OCR model, or upstream database. Kahn's influence-based account and ARP's common-control discussion both make this limitation central.

### Proposed next experiment: dependency-aware witness independence

Add an explicit, synthetic dependency graph for each witness, with at least these layers:

- legal/parent control root;
- administrative operator;
- cloud tenant or identity provider;
- key-management root;
- acquisition device and firmware;
- physical measurement source;
- upstream data feed or shared interpretation component.

Compare four policies on the same case matrix:

1. key-unique only;
2. current field-distinct 2-of-3;
3. current field-distinct 3-of-3;
4. graph-aware quorum requiring the selected matching supporters to be disjoint on the threat-relevant control and measurement roots.

Fault-inject compromise at each root separately and in combinations. Include cases where identifiers differ but the underlying parent or measurement dependency is shared. Report unsafe ACT, safe-action coverage, false-block rate, abstention rate, and unsafe ACT conditional on ACT. Unknown or unverified dependency relationships must not silently count as independent.

This experiment is the most important next step before making a stronger novelty or security claim.

## References

1. Clifford Kahn (1998), “Tolerating Penetrations and Insider Attacks by Requiring Independent Corroboration,” New Security Paradigms Workshop. https://www.nspw.org/papers/1998/nspw1998-kahn.pdf
2. Stefan Buijsman and Herman Veluwenkamp (2022/2023), “Spotting When Algorithms Are Wrong,” *Minds and Machines*, 33, 541–562. https://doi.org/10.1007/s11023-022-09591-0
3. UK National Protective Security Authority, “Claims, Arguments and Evidence (CAE) Concepts.” https://www.npsa.gov.uk/system/files/documents/npsa-concepts-and-their-applicationcae-concepts1.pdf
4. IETF RFC 9943 (March 2026), “An Architecture for Trustworthy and Transparent Digital Supply Chains.” https://www.rfc-editor.org/rfc/rfc9943.html
5. Christian Janbjer (19 Oct 2026), “Deterministic Intent Verification (DIV) Protocol Specification,” draft-janbjer-div-01, work in progress. https://datatracker.ietf.org/doc/html/draft-janbjer-div-01
6. Christian Janbjer (19 Oct 2026), “Deterministic Evidence & Witness Protocol (DEWP) Specification,” draft-janbjer-dewp-01, work in progress. https://datatracker.ietf.org/doc/html/draft-janbjer-dewp-01
7. Joel Hillier (23 Oct 2026), “Attestation Reconciliation Protocol,” draft-hillier-scitt-arp-06, work in progress. https://datatracker.ietf.org/doc/html/draft-hillier-scitt-arp-06

## Review limitations

This was a targeted search, not an exhaustive systematic review. The Internet-Drafts were located through the IETF Datatracker and read as work in progress. A full paper-level novelty audit should additionally search academic databases for provenance-aware document processing, sensor fusion under common-cause compromise, assurance-case defeaters, and safety-critical AI authorization.
