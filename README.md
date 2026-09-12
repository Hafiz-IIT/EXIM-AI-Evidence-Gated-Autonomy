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

## Reproduce integrity checks

```bash
python scripts/verify_benchmark.py
python scripts/reproduce_tables.py
```

## Repository boundaries

This repository intentionally excludes:
- real client documents;
- private family-business workflows;
- commercial EXIM roadmap details;
- scanner/radiation engineering concepts;
- live government credentials/integrations.

All benchmark records are synthetic.

## Current research direction

The strongest open problem emerging from the experiments is not merely verification. It is:

> **How should an action-gating system establish trustworthy provenance and independence for the evidence on which its authorization decision depends, while remaining robust to compromised trust roots and imperfect human escalation?**

See `paper/RESULTS_AND_DISCUSSION.md` and `docs/REAL_MODEL_EXPERIMENT_PROTOCOL.md`.
