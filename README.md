# Evidence-Gated Autonomy

**Research snapshot — synthetic proof-of-concept, not production safety validation.**

This repository contains the inspectable evidence for a research project asking:

> **What evidence should an AI system require before it is allowed to take the next action?**

The work grew from multi-stage operational workflow questions into a narrower reliability problem: model confidence and verifier agreement are not always sufficient grounds for consequential action when evidence may be incomplete, conflicting, stale, correlated, machine-generated, or inconsistent with external observations.

## Proposed action policy

`ACT / VERIFY / REQUEST EVIDENCE / DEFER / ESCALATE`

The gate reasons about evidence completeness, consistency, freshness, provenance, source dependence, external grounding, verifier status, and action consequence.

## What is actually in this repository

- 500 unique synthetic evidence situations paired into 1,000 LOW/HIGH-consequence cases.
- Ten controlled failure families.
- Baseline comparisons and ablations.
- Stochastic imperfect-verification/review simulations.
- Adversarial provenance/evidence stress tests.
- Ed25519 provenance-attestation experiments.
- Trust-root compromise tests.
- Dual-lineage separation-of-duties experiment.
- Preregistered protocols for the two studies not yet run: real model outputs and actual human reviewers.
- A provider-neutral Experiment 3 scaffold for blinded real-model evaluation.
- A claims/evidence ledger and reproducibility checklist that explicitly separate demonstrated results from hypotheses.
- A manuscript draft grounded only in currently completed experiments.

## Evidence map

### Experiment results
- [`results/exp1/summary.csv`](results/exp1/summary.csv) — deterministic Experiment 1A policy comparison.
- [`results/exp1/exp1b_stochastic_summary.csv`](results/exp1/exp1b_stochastic_summary.csv) — optimistic/moderate/harsh imperfect-review simulations.
- [`results/exp1/exp1c_stress_human90.csv`](results/exp1/exp1c_stress_human90.csv) — adversarial evidence/provenance stress at the predefined 90% reviewer-accuracy condition.
- [`results/exp1/exp1d_ood_summary.csv`](results/exp1/exp1d_ood_summary.csv) — in-distribution, nuisance, confidence, provenance-dropout, and compound shifts.
- [`results/exp2/deterministic_attack_comparison.csv`](results/exp2/deterministic_attack_comparison.csv) — Evidence Gate v1 vs attestation-aware v2 under provenance attacks.
- [`results/exp2/EXP2_RESULTS.md`](results/exp2/EXP2_RESULTS.md) — Experiments 2A–2E interpretation and claim boundaries.
- [`results/exp2/updated_claim_ledger.csv`](results/exp2/updated_claim_ledger.csv) — supported, rejected, and bounded provenance hypotheses.

### Research audit / manuscript
- [`paper/RESULTS_AND_DISCUSSION.md`](paper/RESULTS_AND_DISCUSSION.md) — current results/discussion section.
- [`paper/DRAFT_MANUSCRIPT.md`](paper/DRAFT_MANUSCRIPT.md) — evidence-bounded full manuscript scaffold.
- [`docs/FINAL_RESEARCH_AUDIT.md`](docs/FINAL_RESEARCH_AUDIT.md) — concise Experiments 1A–1D audit.
- [`docs/CLAIMS_AND_EVIDENCE.md`](docs/CLAIMS_AND_EVIDENCE.md) — supported claims, negative findings, untested hypotheses, and publication-language boundaries.
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) — deterministic regeneration, run-record requirements, and Experiment 3 reproducibility rules.
- [`docs/THREATS_TO_VALIDITY.md`](docs/THREATS_TO_VALIDITY.md) — limitations and validity threats.
- [`docs/PRIOR_ART_NOTES.md`](docs/PRIOR_ART_NOTES.md) — explicit boundary between established attestation techniques and the research question tested here.

### Studies not yet run
- [`docs/REAL_MODEL_EXPERIMENT_PROTOCOL.md`](docs/REAL_MODEL_EXPERIMENT_PROTOCOL.md) — frozen protocol for replacing simulated errors with actual model outputs.
- [`experiments/exp3_real_models/`](experiments/exp3_real_models/) — blinded-case builder, provider-neutral output schema, executable evaluator, and freeze record.
- [`docs/HUMAN_OVERSIGHT_PREREGISTRATION.md`](docs/HUMAN_OVERSIGHT_PREREGISTRATION.md) — preregistered human-review study; no human-subject result is claimed.

## Selected results

### Experiment 1A
Evidence Gate: **0/500** unsafe HIGH-risk ACT decisions in the deterministic testbed.

Risk Gate and Always Verify: **50/500** each.

This result is not treated as real-world validation.

### Experiment 1B
With imperfect simulated verification/review:
- optimistic Evidence Gate ICAR: ~1.9%;
- moderate: ~6.1%;
- harsh: ~13.1%.

### Experiment 1C/1D
Provenance dropout and evidence masking expose a major failure boundary. Under compound shift, the Evidence Gate remained better than the tested simpler baselines but degraded materially.

### Experiment 2
Unsigned provenance/dependency spoofing caused Evidence Gate v1 to fail on specific families. Cryptographically binding the claims prevented direct silent ACTs under those unsigned attacks, but **valid signatures over false claims remained dangerous when trust roots were compromised**.

A dual-lineage design separated verifier output authority from dependency-lineage authority. In the synthetic compromise test, verifier-only or one-lineage-authority compromise no longer fabricated independence; compromising both lineage authorities restored the failure.

## Most important negative findings

- Explicit verifier-status handling added no independent deterministic safety benefit once other checks were present.
- Risk conditioning primarily improved coverage/cost in the current benchmark.
- REQUEST EVIDENCE mainly improved resolution/coverage over pure deferral; it did not establish intrinsic safety benefit.
- Cryptographic provenance does **not** prove evidence truth.
- Human evidence-packet effectiveness has **not** been tested with real participants.
- No external frontier-model batch experiment has been run.

## Reproduce the benchmark and checks

The large raw JSONL benchmark is intentionally not stored in the repository. It is deterministically regenerated from code so the public repo stays compact and inspectable.

```bash
python scripts/generate_benchmark.py
python scripts/verify_benchmark.py
python scripts/reproduce_tables.py
```

For the blinded Experiment 3 dataset:

```bash
python experiments/exp3_real_models/build_blinded_cases.py
```

After real model outputs have been collected under the frozen protocol:

```bash
python experiments/exp3_real_models/evaluate_outputs.py \
  --outputs path/to/model_outputs.jsonl
```

See [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) before running any final holdout.

## Experiment 3 integrity boundary

Experiment 3 is **not yet a completed empirical result**.

The current branch makes the next study executable while preserving the distinction between protocol and evidence:

- model-facing tasks strip `ground_truth`, `fault`, and `safe_to_act`;
- raw model responses must be retained, not only parsed fields;
- same-family verifier outputs are not relabeled as independent;
- prompts, parsers, controller thresholds, and model choices must be frozen before final holdout inspection;
- any post-hoc change requires a new experiment version / fresh holdout.

A current implementation gap is also documented: `src/` exposes Evidence Gate v1 directly, while the later provenance-aware v2/v3 variants are represented in Experiment 2 artifacts rather than as reusable controller functions. Real-model v2/v3 claims must wait until those variants are reconstructed and regression-tested against Experiment 2.

## Repository boundaries

This repository intentionally excludes:
- real client documents;
- private family-business workflows;
- commercial EXIM roadmap details;
- scanner/radiation engineering concepts;
- live government credentials/integrations.

All benchmark records are synthetic.

## Claim discipline

The repository distinguishes:

- **supported benchmark findings**;
- **supported negative findings**;
- **untested hypotheses**;
- **work not completed**.

See [`docs/CLAIMS_AND_EVIDENCE.md`](docs/CLAIMS_AND_EVIDENCE.md).

Zero observed failures are not interpreted as proof of safety. Cryptographic integrity is not treated as semantic truth. Human escalation is not assumed to be reliable until tested with participants.

## Citation metadata

Repository-level citation metadata is provided in [`CITATION.cff`](CITATION.cff).

## Current research direction

The strongest open problem emerging from the experiments is not merely verification. It is:

> **How should an action-gating system establish trustworthy provenance and independence for the evidence on which its authorization decision depends, while remaining robust to compromised trust roots and imperfect human escalation?**

The next empirical stage is the frozen real-model protocol. The human-oversight study remains separately preregistered and unrun.
