# EGA Evidence-Trust Architecture v2 — Design Proposal

**Status:** Design proposal implemented as a deterministic synthetic four-authority experiment in `src/evidence_trust_v2.py` and `scripts/run_evidence_trust_v2.py`. CI-validated in [run 44025577491](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44025577491); results are reviewed in [`experiments/evidence_trust_v2/RESULTS_REVIEW.md`](../evidence_trust_v2/RESULTS_REVIEW.md). Production controls remain unimplemented.

## Decision

Do not treat a document-root signature as a semantic truth certificate. Separate four authorities that have different responsibilities and should not share a signing key, administrative control plane or runtime trust boundary:

1. **Capture authority (CA):** attests only to receipt/capture facts: source identity as authenticated by the acquisition channel, tenant/case scope, acquisition channel, receipt timestamp, immutable raw-object digest and capture-session identifier. It must not sign OCR-extracted field values as true.
2. **Interpretation authority (IA):** attests to transformations derived from raw objects: OCR/extraction output, parser/model/version, configuration, normalized fields, confidence and parent raw-object digest. Its signature proves which transformation produced the output, not semantic correctness.
3. **Independent witness authority (IWA):** supplies independently acquired corroboration for high-consequence fields, such as a separately administered measurement or authoritative external record. It must not merely re-read or re-sign the same upstream document or extraction output.
4. **Authorization authority (AA):** verifies the signed evidence graph and policy conditions, then signs the decision, policy version, evidence-root digest, action consequence, expiry and idempotency key. It must not issue or control capture/interpretation keys.

A separate key-administration plane provisions, rotates and revokes keys. It must not be controlled by the runtime model, capture service or authorization process.

## Evidence graph

Every derived object carries an immutable parent reference:
- raw object -> capture receipt;
- capture receipt + parser/model/version -> extraction record;
- extraction record + independent witness record -> corroboration result;
- evidence graph + policy version + consequence class -> authorization decision.

The authorization engine verifies signatures and parent links, rejects missing or stale links, checks that claimed independence corresponds to distinct acquisition and administrative domains, and fails closed when required evidence is unavailable.

## Required distinctions

- **Integrity:** bytes/fields have not changed relative to a signed digest.
- **Origin/capture provenance:** a specific enrolled acquisition authority attested to a capture event.
- **Transformation lineage:** a particular parser/model/configuration produced a derived representation from a parent object.
- **Corroboration:** a separate source independently supports a high-consequence field.
- **Truth:** a claim corresponds to the real world. No signature alone establishes this.

## Threat model for the next experiment

The v2 experiment now varies compromise of:
- CA only;
- IA only;
- IWA only;
- AA only;
- CA + IA;
- CA + IWA;
- IA + IWA;
- CA + AA;
- IA + AA;
- IWA + AA;
- CA + IA + IWA;
- all four authorities.

It should also test source-side document forgery before capture, replay across tenants/cases, signer revocation during a workflow, stale capture receipts, parser substitution, parent-link substitution, collusion between capture and interpretation authorities, and compromise of key administration.

The benchmark must explicitly distinguish key compromise from source forgery and from compromise of the actual underlying measurement. Attackers should not automatically receive capabilities beyond the named compromised roles.

## Required controls

- distinct keys and separately administered trust domains for CA, IA, IWA and AA;
- KMS/HSM-backed signing with least-privilege access and audited signing operations;
- independently authenticated signer enrollment and tenant binding;
- short-lived, versioned attestations and operational revocation;
- durable, atomic, concurrency-safe nonce/idempotency state;
- append-only audit records with externally anchored checkpoints;
- independently acquired corroboration for high-consequence fields;
- explicit policy rules for missing, conflicting, stale or revoked evidence;
- safe default to VERIFY / REQUEST EVIDENCE / DEFER / ESCALATE rather than ACT.

These are design requirements, not implemented features.

Implementation protocol: [`experiments/evidence_trust_v2/PROTOCOL.md`](../evidence_trust_v2/PROTOCOL.md). The runner evaluates all 15 non-empty compromise combinations and three separate source/dependency/key-administration controls. It uses the existing `evidence_gate_v1` as an additional policy condition and models a synthetic ground-truth-derived witness. The prototype checks declared source identifiers, acquisition-domain labels and administrative-domain labels, but does not authenticate administrative ownership or prove that the domains are operationally independent.\n\n## Evaluation plan

Report at least:
- unsafe ACT rate over all HIGH-risk cases;
- unsafe ACT rate conditional on ACT;
- safe ACT coverage;
- false-block rate;
- escalation/request-evidence rate;
- per-family and per-compromise-combination results;
- attack detection and containment rate;
- intervention cost;
- paired differences against v1 and Risk Gate baselines.

Use deterministic adversarial cases for capability coverage and a prespecified stochastic layer for uncertain availability/review. Freeze the attack-capability matrix, policy, benchmark version, cost matrix and seeds before running. Report Monte Carlo uncertainty separately from deterministic attack success.

## Falsification criteria

The proposed architecture fails its intended claim if:
- compromise of a single non-authorization authority routinely produces unsafe ACT despite other independent evidence;
- the claimed independent witness shares a hidden upstream dependency with the source it corroborates;
- the authorization engine accepts invalid parent links, stale or revoked attestations, or replayed decisions;
- the system reports an independence property that cannot be traced to distinct acquisition and administrative domains;
- a safe fallback cannot be maintained when one authority is unavailable.

## Claim boundary

Even if the synthetic v2 experiment passes, it would show only that the tested protocol resists the specified synthetic compromises. It would not establish that documents are genuine, that external authorities are honest, that operational keys are secure, or that a deployed system is safe. Production validation and independent review would still be required.
