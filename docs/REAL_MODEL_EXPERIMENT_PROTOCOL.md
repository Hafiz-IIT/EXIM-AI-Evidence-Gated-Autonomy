# Real-Model Experiment Protocol — Experiment 3

## Purpose
Replace synthetic extraction/verifier error probabilities with actual model outputs while keeping benchmark truth hidden and fixed.

## Status
Protocol only. No external LLM/API experiment is claimed.

## Freeze before running
- benchmark cases and test split;
- extraction prompts;
- verifier rubrics;
- Evidence Gate v1/v2/v3 policies;
- evaluation metrics;
- model/version identifiers;
- temperature/seed settings;
- maximum retries.

## Model roles
Use at least three independently developed model families where available:
1. generator/extractor;
2. verifier A;
3. verifier B.

A same-model self-verification condition remains as a baseline.

## Procedure
1. Render synthetic JSON cases into varied document-like text/layout representations.
2. Hide ground truth and fault labels.
3. Run extraction.
4. Run classification.
5. Run same-model and cross-model verification.
6. Record exact prompts, outputs, model version, timestamp, latency, and cost.
7. Feed only observable outputs to frozen controllers.
8. Evaluate against hidden benchmark truth after all outputs are saved.

## Primary metrics
HIGH-risk incorrect consequential action rate, false authorization, false blocking, co-failure rate, cascade depth/action reach, coverage, escalation rate, latency, and monetary cost.

## Required analyses
Same-model vs cross-model verifier co-failure; confidence/calibration; Evidence Gate v1/v2/v3; provenance attacks; model-family holdout; prompt perturbation; document-format OOD split.

## Integrity rule
No policy thresholds may be changed after inspecting test-set results. Any changed policy becomes a new preregistered experiment on a fresh holdout.
