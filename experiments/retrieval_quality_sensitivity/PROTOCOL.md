# Retrieval Quality and Escalation Fallback Sensitivity v1

**Status:** New exploratory synthetic sensitivity experiment. It is not a preregistered confirmatory study and does not replace reconstruction v1/v2 results.

## Motivation

The earlier reconstruction models successful evidence retrieval as if it reveals benchmark ground truth. It also treats unavailable escalation as fail-open (the final outcome is ACT). Both are explicit simplifying assumptions, but either can materially affect the apparent performance of an evidence-gated policy.

This experiment separates retrieval availability from retrieval correctness and compares fail-open with fail-closed fallback when human escalation is unavailable.

## Research question

How sensitive are the relative unsafe-action and safe-action-coverage outcomes of Evidence Gate versus Risk Gate to retrieval availability, retrieval accuracy, human-review accuracy, escalation availability and escalation-unavailability fallback?

## Experimental design

- Benchmark: v0.4, HIGH-risk subset (700 synthetic cases).
- Policies: Evidence Gate and Risk Gate.
- Seeds: 30.
- Parameter grid:
  - retrieval availability: 0.50, 0.75, 0.95;
  - retrieval accuracy conditional on availability: 0.50, 0.75, 0.95;
  - human-review accuracy: 0.75, 0.90, 0.98;
  - escalation availability: 0.80, 0.95, 1.00;
  - unavailable escalation fallback: ACT (fail-open) or DEFER (fail-closed).
- Verifier accuracy is held at 0.93.
- This produces 162 parameter conditions and 30 seed replications per condition.

Parameter values are illustrative stress-test settings, not empirical estimates of real retrieval systems or human reviewers. Retrieval, verifier and human-review errors are modelled as symmetric binary errors: an incorrect resolution flips the benchmark safe/unsafe label. This is intentionally simple and should be replaced with empirically estimated error structures before any real-world interpretation.

## Coupled randomness

For each seed and case, event-specific random draws are generated from a deterministic case-indexed seed. The same event draws are reused across Evidence Gate and Risk Gate. This common-random-numbers design improves the interpretability of paired policy differences without assuming that sequential RNG consumption is identical across policies.

## Outcome metrics

- Unsafe ACT / all HIGH-risk cases.
- Unsafe ACT / all final ACT decisions.
- Safe ACT coverage among safe cases.
- False-block rate among safe cases.
- Overall final ACT rate.
- Paired Evidence Gate minus Risk Gate differences across seeds, with t-based 95% intervals.
- Scenario-family summaries for all 14 v0.4 families.

## Interpretation boundaries

The benchmark is constructed and synthetic. The sensitivity parameters are not calibrated from field data. These outputs can reveal which assumptions drive policy comparisons within this simulator; they cannot estimate deployed-agent incident rates, prove the gate is safer in production, or establish real-world retrieval/human-review performance.

## Reproduction

The GitHub Actions manuscript workflow runs the following command:

    python scripts/run_retrieval_quality_sensitivity.py

Outputs are written to results/retrieval_quality_sensitivity/ and uploaded as a workflow artifact. The manifest records the benchmark digest, parameter grid, seed count and output hashes.
