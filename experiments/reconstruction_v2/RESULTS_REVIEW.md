# Reconstruction v2 — Results and Sensitivity Review

**Benchmark:** v0.4 (1,400 cases; 700 HIGH-risk cases; 14 families)  
**Protocol:** [PROTOCOL.md](PROTOCOL.md)  
**Runner:** [run_reconstruction_v2.py](../../scripts/run_reconstruction_v2.py)  
**Output manifest:** generated as `results/reconstruction_v2/manifest.json`  
**Status:** Synthetic reconstruction. Not a historical reproduction and not manuscript-approved.

The CI artifact contains per-seed CSVs, aggregate summaries, paired sensitivity deltas and a SHA-256 manifest. All percentages below are computed on the v0.4 synthetic benchmark. Monte Carlo intervals describe simulation-seed variability only.

## 1B — Imperfect verification, retrieval and escalation

| Regime | Evidence Gate ICAR | Risk Gate ICAR | Paired EGA − Risk Gate (95% t interval) |
|---|---:|---:|---:|
| Optimistic | 0.82% | 0.95% | −0.13 pp (−0.32, +0.05) |
| Moderate | 5.03% | 5.72% | −0.70 pp (−1.25, −0.14) |
| Harsh | 14.12% | 15.48% | −1.35 pp (−1.97, −0.74) |

Evidence Gate's modeled mean intervention cost is 1.4286 units versus 1.0000 for Risk Gate, a difference of **+0.4286 units per HIGH-risk case** in this cost model. The optimistic paired ICAR interval includes zero; moderate and harsh intervals do not. This is a conditional trade-off, not a universal performance claim.

## 1C — Adversarial metadata stress

Evidence Gate ICAR:
- No attack: **5.99%**
- Dependency spoof: **12.12%**
- External-evidence masking: **12.57%**
- Timestamp masking: **12.95%**
- Combined metadata spoof: **25.72%**

The attack transformations are synthetic and target selected benchmark families. They do not cover the full space of possible provenance attacks.

## 1D — Distribution shifts

Evidence Gate ICAR:
- In-distribution: **6.28%**
- Nuisance shift: **5.98%**
- Confidence shift: **6.17%**
- Provenance dropout: **5.77%**
- Compound shift: **5.94%**

The current shift designs do not increase ICAR. They therefore remain inadequate to establish robustness or degradation under realistic distribution shift. The result is a limitation of the present OOD protocol, not proof of robustness.

## 2B–2E — Provenance and compromise experiments

- **2B unsigned metadata attacks:** v1 ICAR is 7.14% for each individual dependency, external-evidence and timestamp attack, and 21.43% for combined spoofing. The signed variant records 0 unsafe ACTs in these tested conditions by escalating when the covered component digest no longer validates.
- **2C imperfect escalation:** with 90%-accurate simulated review, ICAR is 2.79% with no attack, 8.74% under dependency spoof, 2.65% under external masking, 8.45% under timestamp masking and 8.42% under combined spoofing.
- **2D trust-root compromise:** a single relevant root compromise yields 7.14% ICAR; all three covered roots compromised yields 21.43%.
- **2E dual lineage:** no/single-authority compromise yields 0% ICAR in the tested C8 cases; both lineage authorities compromised yields 7.14%.

The 2B/2D signature reconstruction covers verifier, sensor and authorization components. It does **not** yet include a dedicated document-root signer over the raw invoice/packing-list/declaration instances. It must not be described as authenticating raw document content.

## Parameter sensitivity — paired Evidence Gate minus Risk Gate ICAR

All differences are percentage points; negative values favor Evidence Gate on ICAR, positive values favor Risk Gate. Each condition has 30 paired seeds.

| Varied parameter | Value | EGA − Risk Gate | 95% paired t interval |
|---|---:|---:|---:|
| Verifier accuracy | 0.75 | −11.37 pp | (−11.83, −10.90) |
| Verifier accuracy | 0.85 | −5.40 pp | (−5.88, −4.91) |
| Verifier accuracy | 0.93 | −0.62 pp | (−0.98, −0.27) |
| Verifier accuracy | 0.99 | **+2.80 pp** | (+2.49, +3.11) |
| Retrieval success | 0.70 | −0.28 pp | (−0.51, −0.05) |
| Retrieval success | 0.85 | −0.89 pp | (−1.15, −0.62) |
| Retrieval success | 0.92 | −0.88 pp | (−1.18, −0.59) |
| Retrieval success | 0.99 | −1.23 pp | (−1.48, −0.98) |
| Human accuracy | 0.70 | **+5.16 pp** | (+4.79, +5.52) |
| Human accuracy | 0.80 | **+2.04 pp** | (+1.64, +2.44) |
| Human accuracy | 0.90 | −0.92 pp | (−1.23, −0.60) |
| Human accuracy | 0.98 | −3.47 pp | (−3.76, −3.18) |
| Escalation availability | 0.70 | −0.88 pp | (−1.13, −0.63) |
| Escalation availability | 0.85 | −0.79 pp | (−1.01, −0.56) |
| Escalation availability | 0.95 | −1.02 pp | (−1.31, −0.74) |
| Escalation availability | 1.00 | −0.99 pp | (−1.27, −0.70) |

### Human accuracy × escalation availability interaction

The paired ICAR difference is positive at human accuracy 0.70 (+4.90 to +5.30 pp across the three availability levels), slightly positive at 0.85 (+0.46 to +0.57 pp), and negative at 0.98 (−3.43 to −3.54 pp). Changing availability across the tested levels has a smaller effect than changing reviewer accuracy in this simulation.

### Main interpretation

1. Evidence Gate's ICAR advantage is conditional on downstream verifier/reviewer quality.
2. At verifier accuracy 0.99, Always Verify/Risk Gate outperform Evidence Gate on ICAR by 2.80 pp. A gate that authorizes directly in selected cases can lose its advantage when verification becomes highly reliable.
3. At human accuracy 0.70, Evidence Gate is worse than Risk Gate by 5.16 pp; at 0.98, it is better by 3.47 pp. Escalation quality is therefore a first-order system dependency, not a minor implementation detail.
4. Evidence Gate costs 0.4286 additional intervention units per HIGH-risk case under the current cost matrix.
5. These are one-factor and selected two-factor sweeps, not a global sensitivity analysis or a calibrated real-world model.

## Benchmark v0.4 security boundary

The v0.4 SHA-256 document-set digest is unkeyed. A regression test coherently rewrites document, extraction and external-weight values, recomputes the digest, and confirms the gate returns ACT. This is expected: a public unkeyed digest detects mismatch/corruption but cannot authenticate who supplied the evidence. A trusted document-root signature/attestation and explicit key-compromise threat model remain necessary.

## Required next work

1. Add a document-root signer covering raw document instances and normalized documents.
2. Test coherent document-set rewrite, signer compromise, key rotation/revocation and cross-tenant replay.
3. Redesign OOD transformations so they represent evidence-quality and dependency shifts rather than perturbations that trigger easy escalation.
4. Add broader factorial/global sensitivity analysis and a prespecified cost/utility analysis.
5. Inspect per-case false accepts and false blocks by family and severity.
6. Recover or retire historical Experiment 1A's downstream-resolution claims.
7. Reconcile the manuscript against this new reconstruction without fitting parameters to historical numbers.
8. Perform an independent literature/novelty and methods review.

**Do not replace historical manuscript tables with these outputs until the above review and independent validation are complete.**
