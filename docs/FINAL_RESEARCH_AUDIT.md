# Evidence-Gated Autonomy — Experiment 1A–1D Final Research Audit

## 1A — deterministic synthetic benchmark
500 unique underlying evidence situations, paired into 1,000 LOW/HIGH action cases.
Evidence Gate: 0/500 HIGH-risk unsafe ACT decisions in the deterministic environment.
This result is intentionally treated as a sanity/proof-of-concept result only.

## 1B — imperfect stochastic verification/retrieval/escalation
30 Monte Carlo seeds per regime.
Evidence Gate mean HIGH-risk ICAR:
- optimistic: 0.0186 ± 0.0052
- moderate: 0.0610 ± 0.0115
- harsh: 0.1309 ± 0.0131

Moderate Risk Gate ICAR: 0.1655.

## 1C — adversarial evidence/provenance stress
The method's main discovered vulnerability is reliance on trustworthy evidence metadata.
Dependency spoofing and external-evidence masking materially increase ICAR; combined metadata/evidence spoofing reaches ~24% in the current stress design.

## 1D — OOD / compound shift
Frozen policies evaluated under nuisance shift, overconfidence, provenance dropout, and compound shift.
Compound shift:
- Evidence Gate: 0.1195
- Risk Gate: 0.1851
- Confidence-only: 0.7660

## Interpretation
The strongest defensible conclusion is not that evidence gating "solves" agent safety. It is:
1. confidence-only action authorization is brittle in this controlled testbed;
2. explicit external grounding and evidence-source independence add measurable protection in the benchmark;
3. those benefits collapse when provenance/independence signals can be spoofed;
4. a serious implementation therefore needs trustworthy evidence provenance/attestation rather than merely more verifier votes.

## Research status
These are synthetic and Monte Carlo experiments. No external LLM API outputs, real customs records, production deployment, or human-subject experiments are represented here.

## Historical reproducibility qualification

The historical 1B–2E result CSVs were added to Git without their original simulation runners or complete parameter configurations. Git history for the 1B summary confirms that the result file was committed by itself. The original Experiment 1A downstream-resolution implementation is also absent. Historical numbers are therefore preserved as reported outputs, not independently reproduced results.

## New reconstruction v1

The verified execution is [GitHub Actions run 43949299526](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43949299526), and its output hashes/source provenance are pinned in [manifest-43949299526.json](../results/reconstruction_v1/manifest-43949299526.json). It completed successfully, including manuscript compilation. A separate executable reconstruction is defined in:
- `experiments/reconstruction_v1/PROTOCOL.md`
- `scripts/run_reconstruction_v1.py`
- `tests/test_reconstruction_v1.py`
- `results/reconstruction_v1/README.md`
- `experiments/reconstruction_v1/RESULTS_REVIEW.md`

It runs new 1B, 1C, 1D, 2B, 2C, 2D and 2E experiments under explicit assumptions and 30 Monte Carlo seeds per condition. It does not claim to recreate the historical results. The runner creates role-scoped synthetic attestations, preserves baseline gate decisions in dual-lineage tests, records source revision/run metadata, and hashes generated CSV outputs in its manifest.

### Preliminary interpretation

- Under the new 1B protocol, Evidence Gate's ICAR is 0.81% optimistic, 4.95% moderate and 13.51% harsh. In the moderate regime Risk Gate is 5.30%, so the observed advantage is small and costs more intervention units.
- Under 1C, the new Evidence Gate ICAR is 6.21% without attack and 14.71–33.89% across the specified metadata attacks.
- Under 1D, the chosen shifts do not increase Evidence Gate ICAR (6.52% in-distribution; 6.20% compound). The current OOD protocol is insufficient to support a robustness or degradation claim.
- Under 2B, role-scoped attestations block direct unsafe ACTs under the unsigned metadata attacks by causing escalation.
- Under 2D, compromising a single relevant root produces 10% ICAR; compromising all three produces 30%.
- Under 2E, the stylized C8 test gives 0% ICAR under no/single-authority compromise and 10% when both lineage authorities are compromised.

These results are synthetic and conditional on the new protocol. They are not replacements for the historical tables and must not be inserted into the manuscript until independent review, stronger OOD design, sensitivity analysis and claim reconciliation are complete.

## Benchmark v0.4 and reconstruction v2

### Benchmark changes

Benchmark v0.4 is generated separately from v0.3 and preserves the historical dataset:
- 700 unique underlying situations, paired into 1,400 LOW/HIGH cases.
- 14 fault families, 100 paired-risk cases per family.
- New families: missing invoice, missing packing list, duplicate document kind, corrupted provenance.
- The verifier checks pair integrity, family counts, fault placement and SHA-256 checksums for generated JSONL files.
- Policy tests verify that missing invoice/packing list request evidence and duplicate document kinds/corrupted digests escalate.

**Security boundary:** the document-set digest is unkeyed. A regression test coherently rewrites document, extraction and external-weight values, recomputes the digest and confirms the current gate still returns ACT. It therefore detects mismatch/corruption, not malicious source rewriting or authenticity. A trusted document-root signature is still required.

### Reconstruction v2 execution

The full v2 run [43951632081](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/43951632081) passed tests, v0.3/v0.4 benchmark generation and integrity checks, v1/v2 reconstruction, historical-table loading, artifact uploads and LaTeX compilation. Its manifest is included in the `ega-reconstruction-v2-benchmark-v04` artifact. It records:
- 1,400 benchmark records / 700 HIGH-risk cases;
- 30 Monte Carlo seeds per stochastic condition;
- 25 sensitivity conditions and 2,250 per-seed sensitivity rows;
- 75 sensitivity summary groups;
- 30,100 synthetic signature records across the 2B–2E reconstruction;
- SHA-256 hashes for all 16 CSV outputs;
- source commit `ebe1b144e4495f0a97872cd0eafcaf28c398f3c4`, Python 3.11.18.

The later coherent-rewrite regression test was added after this numerical run. It does not change the experiment runner or generated outputs; it is being revalidated in a subsequent full CI run.

### Main v0.4 results

- **1B moderate regime:** Evidence Gate ICAR 5.03%; Risk Gate 5.72%. The paired EGA-minus-Risk-Gate difference is −0.70 percentage points (95% t interval −1.25 to −0.14 pp). The optimistic interval includes zero; the harsh difference is −1.35 pp (−1.97 to −0.74 pp).
- Evidence Gate mean intervention cost is 1.4286 versus 1.0000 for Risk Gate under the current cost model (+0.4286 units per HIGH-risk case).
- **1C:** Evidence Gate ICAR rises from 5.99% without attack to 12.12–12.95% under the individual metadata attacks and 25.72% under combined spoofing.
- **1D:** Evidence Gate ICAR is 6.28% in-distribution and 5.94% under the current compound shift. The current OOD transformations do not establish robustness or degradation.
- **2B:** the signed variant records zero unsafe ACTs for the tested unsigned metadata attacks by escalating when covered component digests fail.
- **2C:** under 90%-accurate simulated human review, ICAR ranges from 2.65% to 8.74% across the tested attack conditions.
- **2D:** one relevant trust-root compromise yields 7.14% ICAR; all three covered roots compromised yields 21.43%.
- **2E:** both lineage authorities compromised yields 7.14% ICAR in the stylized C8 test; no/single-authority compromise yields zero.

### Sensitivity findings

Paired differences are Evidence Gate minus Risk Gate ICAR, in percentage points, with 30 seeds per condition:
- Verifier accuracy 0.75: −11.37 pp; 0.85: −5.40 pp; 0.93: −0.62 pp; 0.99: **+2.80 pp**.
- Human accuracy 0.70: **+5.16 pp**; 0.80: **+2.04 pp**; 0.90: −0.92 pp; 0.98: −3.47 pp.
- Retrieval success 0.70–0.99: −0.28 to −1.23 pp.
- Escalation availability 0.70–1.00: −0.79 to −1.02 pp.
- In the human-accuracy × availability interaction, low reviewer accuracy (0.70) leaves Evidence Gate 4.90–5.30 pp worse than Risk Gate; at reviewer accuracy 0.98 it is 3.43–3.54 pp better.

**Interpretation:** the policy's relative advantage depends strongly on downstream verifier/reviewer quality. At very high verifier accuracy, Always Verify/Risk Gate can outperform a gate that directly authorizes selected cases. Low human-review accuracy can reverse the benefit of escalation. The current cost model also makes Evidence Gate more intervention-intensive.

### Remaining research blockers

1. Add a dedicated document-root signer covering raw document instances and normalized documents; test coherent rewrites, signer compromise, revocation/rotation and replay.
2. Improve OOD shifts and expand sensitivity beyond one-factor and selected two-factor sweeps.
3. Inspect false accepts/false blocks by family and severity.
4. Recover or retire the historical 1A downstream-resolution comparison.
5. Reconcile manuscript claims against the new results without fitting parameters to historical values.
6. Complete an independent literature/novelty and methods review.

The v0.4 outputs are new synthetic evidence, not historical reproductions, production security evidence, real customs performance, real-model evaluation or human-subject validation. The manuscript remains **not ready for arXiv submission**.
