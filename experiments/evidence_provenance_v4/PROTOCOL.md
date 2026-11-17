# Evidence Provenance v4 — Research Protocol and Threat Model

**Status:** Design protocol; experiments not yet run.  
**Branch:** `research/adversarial-evidence-provenance-v4`  
**Date:** 2026-11-18  
**Data policy:** Synthetic benchmark only in this phase. No private customs records, client documents, credentials, or production API calls.

## 1. Why this direction changed

The v3 2-of-3 authenticated witness quorum is a useful engineering experiment, but it is not a new quorum theory. The related literature now includes:

- [The Illusion of Independent Quorums: Epistemic Fault Domains and Correlated Cognitive Failures in Agentic Quorums](https://arxiv.org/abs/2609.02925), which formalizes shared evidence ancestry, structural quorum cuts, dependency-aware selection/admission, and synthetic plus external benchmark protocols.
- [Engineering Reliable Commit Gates for Agentic AI: Cost-Aware Verification Portfolios under Common-Mode Data Failures](https://arxiv.org/abs/2609.10969), which evaluates common-mode verifier failures, evidence-source diversity, verification portfolios, and commit-time enforcement.
- [TradeSense-EQA](https://doi.org/10.3390/s26165272), which already combines trade documents, physical sensing, declaration-to-fact alignment, trade-process evidence chains, and abstention for cross-border trade risk analysis. Its limitations explicitly include inability to fully exclude deliberate sensor manipulation or simultaneous sensor failures; its data are available on request.
- Work on commit-time authorization, execution-boundary contracts, runtime proof of execution, IoT data provenance and remote attestation, and supply-chain provenance.

Accordingly, v4 does **not** propose another generic quorum, another generic evidence-grounded trade anomaly detector, or a claim that signatures prove truth. It investigates the security boundary between a signed evidence object and the specific business claim and action that object is used to justify.

## 2. Research question

> In document-driven, high-consequence trade workflows, which combinations of source authenticity, freshness, subject/claim applicability, transformation lineage, measurement competence, calibration status, and dependency separation are necessary to prevent forged, stale, misbound, or semantically inapplicable evidence from authorizing an action?

A secondary question is:

> Can a claim-scoped admission policy recover legitimate cases rejected by a fallible verifier without turning missing, contradictory, stale, misbound, or compromised evidence into automatic authorization?

These questions are narrower than generic agentic quorum reliability and more security-focused than trade anomaly classification.

## 3. Assurance properties kept distinct

The protocol treats the following as separate predicates. Passing one never implies the others.

1. **Content integrity:** the bytes or canonical claim have not changed since the digest/signature was made.
2. **Origin authentication:** the signature chains to an enrolled key and an explicitly named issuer/trust root.
3. **Freshness and anti-replay:** the evidence is within its validity interval and the credential's validity window, has an observation time no later than issuance, has a monotonic per-source sequence/nonce, and has not already been consumed for this action. The caller must provide replay state across claim evaluations; the prototype does not implement a durable distributed nonce store.
4. **Subject applicability:** the evidence is bound to the exact shipment, container, declaration, party, and transaction under review.
5. **Claim applicability / source competence:** the source type is permitted to support this particular claim. A weighbridge may support gross weight; it cannot establish HS classification or country of origin.
6. **Transformation lineage:** each OCR/parser/normalization/classification step identifies its input digest, output digest, tool/version, and signer. A valid parser signature attests to a claimed transformation, not correctness of the transformation.
7. **Measurement assurance:** calibration status, unit, tolerance, device status, and acquisition method are explicit. A valid signature does not make a miscalibrated sensor truthful.
8. **Dependency separation:** the evidence items credited as independent do not share a declared source, acquisition gateway, administrative domain, key-administration root, or other modeled common dependency.
9. **Action binding:** the authorization is bound to the exact materialized action, document set, claim set, policy version, subject identifiers, and decision time.

The system reports each predicate separately and preserves the reason for denial. It must not collapse these properties into a single undifferentiated “trusted” flag.

## 4. Claim-specific evidence obligations

The initial synthetic claim set is:

| Claim | Example evidence types that may support it | Explicitly insufficient by itself |
|---|---|---|
| Gross weight | Signed weighbridge event; calibrated scale record; invoice/packing-list cross-check | HS classifier, GPS point, generic agent vote |
| Package / item count | RFID scan, physical tally, packing list, inspection record | Weighbridge value alone |
| HS / RITC classification | Goods description, applicable tariff nomenclature/version, classification rationale, authorized review where required | Weight witness, RFID count, model consensus |
| Country of origin | Certificate of origin from an authorized issuer, manufacturer/exporter records, applicable origin rule | GPS route alone, signed invoice alone |
| Container identity | Container number from transport documents plus independent gate/RFID/visual capture | A document parser's extracted string alone |
| Seal state / custody event | E-seal event, gate scan, timestamped inspection and custody handover | Invoice/packing-list signature |
| Party identity | Verified exporter/importer/authorized representative registry record | OCR text or an unverified company-name string |
| Authorization validity | Issuer-bound permit/approval, scope, policy version, expiry and revocation status | An earlier approval detached from the current action |

This is an initial protocol taxonomy, not a claim that these are the only valid legal or operational sources. Domain experts and applicable regulations must refine it before deployment claims.

## 5. Evidence object and decision binding

Each synthetic evidence record should contain at least:

- `evidence_id`, `claim_id`, `claim_type`, `value`, `unit`;
- `subject_id` (shipment/container/declaration/party as applicable);
- `source_id`, `source_type`, `source_key_id`, `issuer_id` / `trust_root_id`;
- `acquisition_method`, `acquisition_event_id`, `gateway_id`;
- `observed_at`, `issued_at`, `expires_at`, `sequence_number`, `nonce`;
- `document_digest`, `input_digest`, `output_digest`, `transformation_id`, `tool_version`, expected `unit`;
- `administrative_domain`, `key_admin_domain`, `trust_root_id`;
- `calibration_id`, `calibration_valid_until`, `device_health`;
- signature and verification metadata.

An action envelope binds the canonical action payload to the evidence IDs and digests, exact subject, policy version, required claims, decision timestamp, and expiry. A later action with a different payload or subject must not reuse the earlier authorization.

## 6. Threat model and attack matrix

The benchmark will distinguish attacks that the earlier v2/v3 experiments partially combined.

| ID | Attack | Security property under test |
|---|---|---|
| A0 | Honest, complete evidence | Baseline safety and liveness |
| A1 | Post-signature content mutation | Content integrity |
| A2 | Source document forged before honest capture | Difference between authentic capture and truthful source |
| A3 | Forged or wrong-role credential | Origin authentication and role binding |
| A4 | Stale evidence outside its validity window | Freshness and credential-window enforcement |
| A4b | Duplicate evidence/nonce replayed in one action batch or a later evaluation | Anti-replay state and monotonic source sequence |
| A5 | Evidence from another shipment/declaration | Subject applicability |
| A6 | Weight evidence reused to approve HS/origin claim | Claim applicability and source competence |
| A7 | Parser/OCR transformation input or output substituted | Transformation lineage |
| A8 | Expired or invalid calibration record | Measurement assurance |
| A9 | Two apparently different sources share gateway/admin domain | Dependency separation |
| A10 | Trust-store / registry-root compromise | Trust-anchor assumption |
| A11 | Multiple sensors under one compromised control plane | Common-cause compromise |
| A12 | Evidence changes after approval but before action | Action binding / time-of-check-to-time-of-use |
| A13 | Missing or contradictory evidence | Fail-closed behavior and availability |
| A14 | Isolated model-verifier false rejection with independently sufficient evidence | Bounded recovery |
| A15 | False-accepting verifier plus internally consistent but wrong documents | Semantic false acceptance |
| A16 | Full compromise of every enrolled evidence source | Explicit residual trust boundary |
| A17 | Compromised tariff registry plus two independent false-accepting verifiers | Residual semantic false-accept path even when verifier dependency labels are distinct |

The adversary capabilities will be stated per attack. Compromise of a source key does not silently imply compromise of other authorities; registry compromise does not silently imply hardware compromise; a forged source document before capture is not the same as a forged capture signature.

## 7. Baselines and ablations

- **B0 — Existing policy gate:** current evidence-gate v1 without signed provenance.
- **B1 — Role-separated attestations:** v2 capture / interpretation / witness / authorization chain.
- **B2 — Authenticated witness quorum:** v3, reported as a threshold baseline rather than a novel architecture.
- **B3 — Generic signed evidence:** signatures, expiry and action scope, but no claim-type competence or dependency checks.
- **B4 — Claim-scoped evidence admission:** candidate v4 policy with claim/source compatibility and explicit freshness, subject, transformation, calibration and action-binding checks.
- **Ablations:** remove one property at a time (freshness, subject binding, claim competence, transformation binding, calibration, dependency separation, action binding, bounded recovery).

The EFD structural-cut metric and VP-CONTROL portfolio ideas are related baselines to discuss and, where feasible, reproduce or adapt with attribution. v4 will not claim to supersede them.

## 8A. Scenario interpretation

The runner includes separate cases for stale evidence and duplicate replay, and for isolated tariff-registry compromise and a compound tariff-registry compromise plus two independently labeled false-accepting verifiers. The isolated attack is expected to be contained by the existing verifier-dependency guard in the C8 correlated-verifier family. The compound scenario changes the verifier dependency labels to distinct values while preserving their false-accept decisions; this is deliberately a stronger counterexample showing that declared diversity is not equivalent to correctness. The two scenarios must not be conflated in reporting.

## 9. Outcomes

Primary outcomes, reported per attack family and overall:

- unsafe ACT / all unsafe cases;
- unsafe ACT / all ACT decisions;
- safe-action coverage among ground-truth-safe cases;
- false-block rate among ground-truth-safe cases;
- per-claim false-accept and false-reject counts;
- stale/replay acceptance rate;
- cross-subject and cross-claim substitution acceptance;
- invalid-signature / invalid-lineage acceptance;
- calibration-invalid acceptance;
- action-binding / TOCTOU bypass rate;
- human-review / escalation rate.

If a probabilistic simulation is added, its probabilities must be explicitly labeled as programmed assumptions, not fitted real-world rates. Deterministic scenario counts must never be described as probabilities.

## 10. Falsifiable hypotheses

- **H1:** Signature verification alone rejects post-signature tampering but does not reject a forged source document honestly signed at capture.
- **H2:** Freshness and subject binding reject replay and cross-shipment substitution that remain possible under signature-only evidence.
- **H3:** Claim-type competence checks reject cross-claim substitution even when every reused evidence item has a valid signature.
- **H4:** Transformation binding detects parser/OCR lineage substitution but cannot establish semantic correctness of the parser output.
- **H5:** Dependency checks reject declared shared-gateway or shared-administration evidence, but cannot prove that undeclared common dependencies do not exist.
- **H6:** Action binding rejects stale approvals and evidence/action substitution at the commit boundary, subject to complete mediation and atomic enforcement assumptions.
- **H7:** Bounded recovery improves safe-action coverage only for isolated verifier false rejections where all claim-specific evidence obligations independently pass; it must not recover from source, scope, freshness, conflict, or trust-root failures.

Each hypothesis must be supported by an executable test and a counterexample test.

## 11. Claim boundaries

- All v4 records are synthetic unless a separately approved, privacy-reviewed dataset is later introduced.
- Ed25519 signatures authenticate enrolled keys and signed bytes; they do not prove physical truth, lawful authority, calibration correctness, or operational independence.
- Administrative-domain labels are assertions unless independently audited.
- No production PKI, hardware root of trust, TPM/TEE attestation, customs-system connector, or secure sensor acquisition is implemented in this phase.
- No production-readiness, real-world probability, or deployment-safety claim is permitted.
- This protocol is a research design, not a customs compliance recommendation.

## 12. Related work to compare before claiming novelty

- He and Yu, [The Illusion of Independent Quorums](https://arxiv.org/abs/2609.02925), 2026.
- Zheng et al., [Engineering Reliable Commit Gates for Agentic AI (VP-CONTROL)](https://arxiv.org/abs/2609.10969), 2026.
- Chen et al., [TradeSense-EQA](https://doi.org/10.3390/s26165272), *Sensors* 26(16), 5272 (2026).
- Wu et al., [From Intent to Execution Grant](https://arxiv.org/abs/2609.11596), 2026.
- Rhodes and Kang, [Proof of Execution](https://arxiv.org/abs/2607.05397), 2026.
- Santos-Grueiro, [Temporary Authority, Permanent Effects](https://arxiv.org/abs/2607.10487), 2026.
- Chang and Geng, [Mnemosyne](https://arxiv.org/abs/2607.00269), 2026.
- Faraj, Megías and García-Alfaro, [Security Approaches for Data Provenance in the Internet of Things: A Systematic Literature Review](https://doi.org/10.1145/3718735), *ACM Computing Surveys* 57 (2025).
- Dirin, Oliver and Laine, [A Security Framework for Increasing Data and Device Integrity in Internet of Things Systems](https://doi.org/10.3390/s23177532), *Sensors* 23 (2023).
- Pan, Stakhanova and Ray, [Data Provenance in Security and Privacy](https://doi.org/10.1145/3593294), *ACM Computing Surveys* 55 (2023).
- Brito et al., [Decentralized Proof-Of-Location for Content Provenance: Towards Capture-Time Authenticity](https://arxiv.org/abs/2603.27883), IEEE ICSA-C (2026); DOI to be checked against publisher metadata before formal citation.
- Triepels, Daniels and Feelders, [Data-driven fraud detection in international shipping](https://doi.org/10.1016/j.eswa.2018.01.007), *Expert Systems with Applications* 99 (2018).
- Chen et al., [The use of machine learning to identify the correctness of HS Code for the customs import declarations](https://doi.org/10.1109/DSAA53316.2021.9564203), DSAA (2021).

## 13. Exit criteria for v4

Do not open a v4 PR or claim a research result until:
1. the attack matrix and evidence schema are implemented;
2. unit tests include both positive and negative cases for every assurance property;
3. the same frozen synthetic cases are run through B0–B4 and ablations;
4. the summary includes complete confusion matrices and per-claim metrics;
5. independent code review checks that no evidence field is silently trusted merely because it is signed;
6. full CI and manuscript build pass;
7. a final novelty matrix records what is replicated, extended, and still potentially distinct.
