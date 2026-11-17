# Evidence-Trust Architecture v2 — Threat Experiment Protocol

**Status:** Implemented as a deterministic synthetic experiment; CI validation pending. No production trust infrastructure is implemented.

## 1. Research question

Does separating capture, interpretation, independent witness and authorization attestations reduce the ability of a compromised authority to produce an unsafe high-consequence action? Which combinations of compromised roles defeat the proposed controls, and what happens when the supposedly independent witness shares an upstream dependency with the source?

This is a new experiment over the 700 HIGH-risk cases in benchmark v0.4. It is not a reproduction of the v1 document-root experiment or the historical reconstruction experiments.

## 2. Authorities and signed statements

The prototype uses four role-specific Ed25519 keys:

1. **Capture authority (CA):** signs tenant/case scope, raw document-instance digest, source identifier, acquisition channel and capture-session identifier.
2. **Interpretation authority (IA):** signs normalized quantity, gross weight and HS fields, parser name/version, and the digest of the raw input. Its signature attests to a claimed transformation lineage, not semantic correctness.
3. **Independent witness authority (IWA):** signs a separate synthetic scale/inspection record with its own acquisition-domain label. In the baseline model its values are derived from the benchmark ground-truth record. This is a deliberately idealized independent witness, not a real external source.
4. **Authorization authority (AA):** verifies role signatures, tenant/case scope, parent digests, witness agreement and the existing `evidence_gate_v1` policy, then signs the resulting action and evidence-graph digest.

The experiment uses deterministic test-only keys. The code does not implement KMS/HSM custody, independent signer enrollment, durable replay state, distributed transactions, secure capture or production revocation.

## 3. Threat-capability model

A compromised role receives only its named capability:

- **CA:** can rewrite the raw/normalized document representations and sign a capture receipt for them. If IA is honest, the synthetic honest parser re-reads the changed invoice.
- **IA:** can alter and sign the extracted fields and parser lineage; it cannot sign CA or IWA records.
- **IWA:** can falsify and sign the independent measurement/inspection record; in this model it controls the external measured-weight channel.
- **AA:** can sign an arbitrary authorization decision, including ACT, without the other roles' approval.

The runner evaluates all 15 non-empty subsets of the four roles: four single-role compromises, six pairs, four triples and the all-four compromise. It does not assume that compromise of one key automatically compromises the other roles.

## 4. Separate controls

Two deterministic controls are evaluated separately from key compromise:

- **Source forgery before capture:** the source document is already forged when an otherwise honest capture authority receives it. IA processes the captured document and IWA retains the independent ground-truth value.
- **Shared-dependency witness:** the witness is deliberately copied from the same forged document source and the external measurement is aligned to that source. No signing key is compromised. The authorization gate compares the declared witness source identifier and acquisition domain with the capture source; a disclosed shared source must be rejected.

The distinction matters: source forgery is not the same event as capture-key compromise. Likewise, a compromised IWA signing key is modeled as control over the IWA's signed measurement claim, not as automatic compromise of CA or IA.

## 5. Procedure

For every HIGH-risk v0.4 case and every compromise combination:

1. Apply only the capabilities assigned to compromised roles.
2. Issue capture, interpretation and witness attestations.
3. Verify signatures, role identity, tenant/case scope, validity and parent digests.
4. Check that the capture digest matches the raw document instances and that the IA input digest points to the capture digest.
5. Check witness agreement with interpretation and the ground-truth item type.
6. Run the existing evidence gate as an additional policy condition.
7. Have AA sign the resulting action; under AA compromise, model an arbitrary ACT decision.
8. Compare ACT with the original `safe_to_act` label.

The runner emits one row per case/scenario and a scenario summary. The deterministic matrix is not a Monte Carlo study and has no sampling-based confidence intervals. The shared-dependency control is expected to fail the explicit independence check when the common source is truthfully declared; a compromised IWA can still falsify its signed source/measurement claims, which is a different threat.

## 6. Metrics

For each scenario, report:

- unsafe ACT / all HIGH-risk cases;
- unsafe ACT / all ACT decisions;
- safe ACT coverage among ground-truth-safe cases;
- false-block rate among ground-truth-safe cases;
- total ACT and ESCALATE decisions;
- family-level outcomes in the case-level CSV.

## 7. Falsification and interpretation

The architecture's single-compromise resilience hypothesis is falsified for a role if its single-role scenario produces unsafe ACT. Pair/triple scenarios identify the additional trust combinations needed to defeat the gate. The shared-dependency control is expected to show why a second signature is not independent corroboration when it inherits the same upstream source.

A compromised AA is expected to be able to authorize arbitrary action because AA is the final authorization boundary. This is an explicit trust assumption, not a claim that signatures can defend against compromise of the component that enforces policy.

## 8. Claim boundary and limitations

Even a passing synthetic matrix would establish only behavior under the specific benchmark, role capabilities and implementation tested. The benchmark ground-truth witness is an oracle-like simulation. Real independence requires separate acquisition, administration, identity assurance and failure domains, which are not proven here. A valid signature does not establish truth. The experiment is not evidence of production security, real customs-system validation or deployment safety.

## 9. Reproduction

The CI workflow runs:

```bash
python -m unittest discover -s tests -v
python scripts/generate_benchmark_v04.py
python scripts/verify_benchmark_v04.py
python scripts/run_evidence_trust_v2.py
```

Outputs are archived as the GitHub Actions artifact `ega-evidence-trust-v2` and written to `results/evidence_trust_v2/`.
