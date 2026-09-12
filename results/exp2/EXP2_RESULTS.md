# Experiment 2A–2E Results — Attested Provenance for Evidence-Gated Autonomy

## Scope
These experiments extend the synthetic Evidence-Gated Autonomy benchmark after Experiment 1C showed that untrusted dependency/provenance metadata could be spoofed.

They do **not** demonstrate real-world security. They test whether cryptographically binding provenance claims changes failure behavior inside the benchmark.

## 2A — Signed provenance layer
- 500 HIGH-risk benchmark cases.
- 3,675 Ed25519 attestations.
- Signed objects cover documents, external weight evidence, authorization timing, and verifier outputs/dependency metadata.
- All signatures verified before attacks.

## 2B — Unsigned/untrusted metadata attacks
Evidence Gate v1 trusts visible provenance/dependency metadata.
Evidence Gate v2 requires a valid signature and a binding between the signed claim and the current evidence object.

Deterministic HIGH-risk ICAR:
- No attack: v1 0%, v2 0%.
- Dependency spoof: v1 10%, v2 0%.
- External-evidence masking: v1 10%, v2 0%.
- Timestamp masking: v1 10%, v2 0%.
- Combined spoof: v1 30%, v2 0%.

The v2 result means only that direct silent ACTs were prevented. It frequently escalated instead.

## 2C — Imperfect review after tamper detection
With a simulated 90%-accurate human escalation path:
- no attack: v1 ~6.1%, v2 ~5.9% ICAR;
- dependency spoof: v1 ~15.2%, v2 ~7.1%;
- external masking: v1 ~15.2%, v2 ~5.9%;
- timestamp masking: v1 ~15.9%, v2 ~7.1%;
- combined spoof: v1 ~34.0%, v2 ~7.1%.

Thus cryptographic binding reduces silent acceptance, but review errors remain.

## 2D — Trust-root compromise
A valid signature over a false claim defeats simple signature checking.

Evidence Gate v2 deterministic ICAR:
- compromise verifier_A: 10%;
- compromise external-sensor signer: 10%;
- compromise authorization signer: 10%;
- compromise all relevant roots: 30%.

A particularly important result is that compromising **one verifier signer** is sufficient to fabricate apparent evidence independence in the v2 design.

## 2E — Separation of duties / dual-lineage attestation
The verifier signs its output, while two independent lineage authorities separately attest its dependency lineage.

Deterministic ICAR:
- compromise verifier_A only: 0%;
- compromise lineage_A only: 0%;
- compromise lineage_B only: 0%;
- verifier_A + lineage_A: 0%;
- compromise both lineage authorities: 10%;
- verifier_A + both lineage authorities: 10%.

With imperfect 90%-accurate escalation:
- no compromise: ~6.0%;
- one verifier or one lineage authority compromised: ~7.1%;
- both lineage authorities compromised: ~15.0%.

## Main interpretation
Cryptographic attestation is not evidence truth. It can bind origin, integrity, and lineage claims to evidence. The benchmark suggests three distinct failure layers:

1. **untrusted metadata** — mitigated by signed binding;
2. **review/escalation failure** — remains after tampering is detected;
3. **trust-root compromise** — valid signatures can authenticate a lie.

Separating output authority from lineage authority and requiring multiple independent lineage attestations raises the compromise threshold for fabricated independence, but does not remove the trust-root problem.

## Claim boundary
Safe:
> In the synthetic benchmark, cryptographically binding evidence provenance prevented several unsigned metadata-spoofing attacks, while trust-root compromise remained a failure mode. Separating verifier output signatures from dual lineage attestations raised the compromise threshold for fabricated evidence independence.

Unsafe:
- cryptography proves evidence is true;
- signed provenance makes autonomous AI safe;
- the scheme is production-secure;
- dual attestation eliminates compromise risk.
