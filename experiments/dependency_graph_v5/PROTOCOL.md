# Dependency-Aware Witness Independence — v5 Protocol

**Status:** preregistered synthetic experiment design; implementation and results pending  
**Parent research line:** Evidence-Trust v3 and claim-scoped evidence provenance v4  
**Benchmark:** v0.4, 700 HIGH-risk cases per scenario  
**Purpose:** test whether transitive dependency ancestry detects common-control and common-source failures that flat identity/domain labels miss.

## 1. Research question

When two or more signed witnesses have distinct IDs, keys, acquisition domains, gateways and administrative-domain labels, can they still share an upstream dependency that makes their evidence non-independent?

The experiment compares key uniqueness, direct-field diversity, threshold strictness and graph-aware ancestry checks. It does not propose a new quorum theory or structural-cut metric. EFD already formalizes epistemic fault domains and structural quorum resilience; ARP already specifies witness-set diversity and common-control exclusions. The intended contribution is an EXIM-inspired empirical comparison under a reproducible synthetic threat matrix.

## 2. Hypotheses

- **H1 — key uniqueness is insufficient:** distinct key IDs alone will admit false corroboration when two signers share a parent, identity provider, KMS, firmware pipeline or upstream feed.
- **H2 — direct-field diversity is insufficient:** distinct source/admin/gateway labels will still admit false corroboration when the dependency graph contains a shared ancestor.
- **H3 — strict 3-of-3 trades safety for availability:** it will block two-witness collusion when the third witness is honest, but it will not block full-roster compromise and may fail closed under one invalid credential.
- **H4 — graph-aware admission improves detection of declared transitive dependencies:** it will reject matching supporters whose verified dependency ancestry intersects.
- **H5 — graph-aware admission remains trust-root dependent:** a compromised registry that signs an incomplete or falsified dependency graph can hide a shared ancestor.

## 3. Dependency graph model

A graph manifest is a signed, tenant-scoped, time-bounded object:

`G = (V, E, graph_id, version, tenant, issued_at, expires_at)`

Each node is an entity or dependency. Directed edges `u -> v` mean that `u` depends on `v`. A witness credential binds its source identity to a leaf node and the digest of the signed graph manifest. The leaf identifier is deterministically bound to the credential's `source_id` (the graph leaf is `source:{source_id}`), preventing a credential from selecting an unrelated dependency branch.

Threat-relevant node classes include:

1. parent/legal control root;
2. administrative operator;
3. cloud tenant or identity provider;
4. key-management root;
5. firmware/build/deployment pipeline;
6. acquisition device and gateway;
7. physical measurement source;
8. upstream database, OCR model, sensor aggregator or data feed.

The verifier validates the graph signature, tenant, validity window, digest, acyclicity, and resolution of every referenced parent. It computes transitive ancestors for each selected witness. The graph-aware policy rejects a quorum if any two selected supporters share a threat-relevant ancestor.

The graph is a registry-signed assertion, not an independently verified map of reality. Missing, cyclic, unresolved or explicitly incomplete graph data must not silently count as independence.

## 4. Compared policies

| Policy | Threshold | Independence condition |
|---|---:|---|
| K2 — key-unique | 2 of 3 | Distinct witness IDs and key IDs |
| F2 — field-distinct | 2 of 3 | K2 plus distinct source IDs, acquisition domains, administrative domains, gateways and key-admin domains |
| F3 — strict field-distinct | 3 of 3 | F2 conditions across all three matching witnesses |
| G2 — graph-aware | 2 of 3 | F2 plus pairwise disjoint transitive dependency ancestry |

For each policy, only assertions that match the controller's expected measurement and case/action scope may form a quorum. Independence must be checked within the matching supporters; a dissenting witness cannot lend independence to a colluding pair.

## 5. Threat scenarios

Every scenario runs over the same 700 HIGH-risk cases.

| ID | Scenario | Purpose |
|---|---|---|
| S0 | Honest baseline | Measure safe-action coverage and false blocks |
| S1 | One witness compromised | Check tolerance of one bad signer |
| S2 | Two witnesses compromised | Check 2-of-3 collusion against strict 3-of-3 |
| S3 | All three witnesses compromised | Expose full-roster compromise limit |
| S4 | Direct shared administrative domain | Verify direct-field exclusion |
| S5 | Hidden shared parent organization | Distinct direct labels, common parent ancestor |
| S6 | Hidden shared cloud identity provider | Distinct gateways/admins, shared identity root |
| S7 | Hidden shared KMS/key-management root | Distinct keys, common key custody root |
| S8 | Hidden shared firmware/build pipeline | Distinct devices, common software supply chain |
| S9 | Hidden shared acquisition gateway/upstream feed | Distinct witness labels, common measurement ancestry |
| S10 | Incomplete dependency manifest | Verify fail-closed behavior for unknown ancestry |
| S11 | Missing/cyclic graph node | Verify graph-integrity rejection |
| S12 | Dependency-graph signature tampering | Verify graph authenticity |
| S13 | Registry-root compromise | Test forged credentials and falsified dependency ancestry |

The hidden-dependency scenarios make two compromised witnesses agree on the document-derived value in the C4 consistent-but-wrong family, while their direct identity fields remain distinct. The graph manifest reveals a shared ancestor. The registry-root compromise scenario isolates trust-anchor failure from full-roster compromise: w1 and w2 share a true parent and collude, w3 remains honest, but the compromised registry signs a graph that omits the shared parent and enrolls the witness credentials. The signed graph therefore appears disjoint. F3 should still reject because the honest third witness disagrees; G2 may be fooled because it cannot recover truth omitted by its compromised graph authority.

## 6. Outcome measures

For every policy and scenario, report:

- unsafe ACT count and rate over all cases;
- unsafe ACT conditional on ACT;
- safe-ACT coverage;
- false-block rate over safe cases;
- ACT/quorum availability;
- rejection reason and graph-validation failure counts;
- family-level breakdown, especially C4 consistent-but-wrong.

Counts are deterministic synthetic outcomes, not real-world probabilities. Compare all four policies on identical cases and source assertions.

## 7. Falsifiable expectations

- S0: all policies should authorize the 100 safe cases and produce zero unsafe ACT.
- S1: K2/F2/G2 should tolerate one bad witness when two honest matching witnesses remain; F3 may lose availability if the bad witness dissents.
- S2: K2/F2 can accept two matching compromised witnesses; F3/G2 should reject when the third honest witness disagrees.
- S3: all policies may accept when all three witnesses are compromised and agree on the same false value, unless the graph independently exposes a shared ancestor.
- S5–S9: K2 and F2/F3 may accept when direct labels are distinct; G2 should reject if the signed graph correctly records the shared ancestor.
- S10–S12: G2 should fail closed; key-only and direct-field policies do not use the graph and may still authorize.
- S13: K2/F2 and G2 may be fooled when two colluding witnesses share a true parent omitted by the compromised registry; F3 should reject because the third witness remains honest.

Any deviation must be explained from the case-level output; do not change the hypotheses after inspecting results without recording a protocol amendment.

## 8. Security and validity limitations

- All identities, graphs, source values, signatures and attacks are synthetic.
- A signed dependency graph authenticates the registry's assertion, not the truth or completeness of the dependency relationships.
- Distinct graph nodes do not prove independent ownership, operation, hardware, software, or data.
- Registry-root compromise can falsify credentials and graph ancestry. In S13, the compromised registry signs a graph that hides a true shared parent while only two of three witnesses collude; this is distinct from S3 full-roster compromise.
- No production PKI, KMS/HSM custody, hardware attestation, cloud-provider audit, supply-chain SBOM verification, trusted time or atomic action commit is implemented.
- No new EFD/structural-cut metric is claimed. The experiment uses pairwise transitive-ancestor intersection as a transparent operational check.
- Results do not establish production security or real-world risk probabilities.

## 9. Prior art

- He and Yu, [The Illusion of Independent Quorums: Epistemic Fault Domains and Correlated Cognitive Failures in Agentic Quorums](https://arxiv.org/abs/2609.02925), arXiv:2609.02925 (2026).
- Zheng et al., [Engineering Reliable Commit Gates for Agentic AI](https://arxiv.org/abs/2609.10969), arXiv:2609.10969 (2026).
- Hillier, [Attestation Reconciliation Protocol (ARP)](https://datatracker.ietf.org/doc/html/draft-hillier-scitt-arp-06), Internet-Draft, work in progress (23 Oct 2026).
- Kahn, [Tolerating Penetrations and Insider Attacks by Requiring Independent Corroboration](https://www.nspw.org/papers/1998/nspw1998-kahn.pdf) (1998).

## 10. Exit criteria

The experiment is complete only when:

1. graph validation and cycle/missing-node tests pass;
2. all compared policies run on the same benchmark cases and source assertions;
3. all 14 scenarios produce complete case-level CSVs, summary CSVs and a hash manifest;
4. expected fail-closed and residual-compromise cases are checked against the preregistered hypotheses;
5. a results review records both security gains and availability costs;
6. the full CI workflow and manuscript compilation pass;
7. no novelty claim exceeds the prior-art boundary above.
