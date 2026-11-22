# Action Consequence Binding and Metadata Spoof Experiment v1

**Status:** Deterministic synthetic policy experiment. This tests a trust assumption that is not varied in the original v0.4 benchmark.

## Problem

The v1 evidence gate trusts the action risk label in the input object. It returns ACT immediately when risk_level is LOW, before checking document completeness, provenance or verifier state. If an untrusted planner can downgrade a consequential action from HIGH to LOW, it bypasses the evidence checks.

The action object also contains reversibility and external_effect fields, but v1 does not validate them.

## Proposed control

The new evidence_gate_v2 requires:
- a trusted_action_id supplied from an authorization context independent of the proposed action;
- a trusted action catalog maintained outside the model;
- exact agreement between the proposed action name and trusted action ID;
- exact agreement on risk_level, reversibility and external_effect.

Unknown actions, missing catalog entries and any metadata mismatch return ESCALATE. If the metadata matches, v2 delegates to the existing evidence_gate_v1 logic. The original v1 policy and historical results are unchanged.

## Experiment

- Benchmark: v0.4 HIGH-risk subset (700 synthetic cases).
- Policies: v1 and v2.
- Variants: unmodified, risk-level downgrade, reversibility spoof, external-effect spoof and action-identity substitution.
- Outputs: case-level decisions, aggregate unsafe ACT and coverage metrics, and per-family summaries.

This is a deterministic policy-level test, not a deployment evaluation. The experiment assumes the trusted action ID and catalog are supplied by an independent authorization context. It does not authenticate that context or bind the eventual external tool call to the action ID.

## Metrics

- Unsafe ACT / all HIGH-risk cases.
- Unsafe ACT / all ACT decisions.
- Safe ACT coverage.
- False-block rate among safe cases.
- Escalation rate.
- Per-family results.

## Reproduction

The manuscript workflow runs:

    python scripts/run_action_consequence_spoof.py

Outputs are written to results/action_consequence_binding/ and uploaded as a CI artifact.
