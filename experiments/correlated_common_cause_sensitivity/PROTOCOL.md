# Correlated Common-Cause Retrieval, Verifier and Human-Review Sensitivity v1

**Status:** Exploratory synthetic sensitivity experiment. Version 2 adds an explicit serial-gate comparator after the first run exposed a limitation in the existing branching policy simulator.

## Research question

At identical marginal retrieval, verifier and human-review accuracies, how does a shared common-cause failure process change unsafe consequential-action rates for Evidence Gate versus Risk Gate?

## Why this experiment is needed

The existing retrieval sensitivity study draws retrieval, verifier and human-review correctness independently. That is a useful baseline, but it cannot represent a single compromised or misleading source contaminating several assurance channels. A shared shock can create correlated failures even when each channel's marginal accuracy remains unchanged.

## Design

- Benchmark: v0.4 HIGH-risk subset (700 cases).
- Policies: Evidence Gate and Risk Gate.
- Seeds: 20, with case-indexed common random numbers shared across policies.
- Conditions: 81 factorial combinations.
- Retrieval accuracy: 0.50, 0.75, 0.95.
- Human-review accuracy: 0.75, 0.90, 0.98.
- Verifier accuracy: 0.85, 0.93, 0.98.
- Common-shock fraction: 0, 0.5, 1.0.
- Fixed retrieval availability: 0.75.
- Fixed escalation availability: 0.95.
- Fixed fallback when escalation is unavailable: DEFER.

## Common-cause model

Let each channel j have marginal error probability e_j = 1 - accuracy_j. Define:

    rho = common_shock_fraction * min(e_retrieval, e_human, e_verifier)

For each case and seed, draw one shared shock Z ~ Bernoulli(rho). If Z=1, every correctness channel that is invoked returns an incorrect result. If Z=0, channel j has residual independent error probability:

    q_j = (e_j - rho) / (1 - rho)

Thus:

    P(error_j) = rho + (1 - rho) q_j = e_j

The model preserves each channel's marginal error rate while inducing positive dependence. At common_shock_fraction=0, errors are independent. At 1.0, the common shock reaches the largest mass compatible with all three marginal error rates. Retrieval and escalation availability remain independent of correctness shocks.

This is a deliberately simple common-cause model. It does not represent source graphs, multiple correlated clusters, adaptive adversaries, or empirically estimated dependencies.

## Two policy structures are evaluated

1. **Existing policy branches.** The repository's current Evidence Gate and Risk Gate choose one terminal correctness channel per case (retrieval, verifier, or human escalation). The shared shock is present in the draw cache, but a single path usually invokes only one correctness channel. With marginals preserved, this branch-only model is expected to be largely insensitive to cross-channel dependence. That is a diagnostic limitation, not evidence that correlated failures are harmless.
2. **SerialEvidenceGate (stylized comparator).** Retrieval and verifier each produce a binary safe/unsafe assessment. If they agree, the gate follows the shared assessment. If they disagree, or retrieval is unavailable, it escalates to human review. A common shock can make retrieval and verifier jointly wrong on an unsafe case, causing agreement on a false-safe assessment and bypassing the human escalation. This is a deliberately simplified composition model, not a claim about the current Evidence Gate implementation.

The serial comparator makes the cross-channel dependence observable. Results for it must be reported separately from the existing policies and must not be described as measured performance of the current EGA implementation.

## Metrics and statistical design

- Unsafe ACT / all HIGH-risk cases.
- Unsafe ACT / all ACT decisions.
- Safe ACT coverage.
- False-block rate among safe cases.
- Final ACT rate.
- Paired Evidence Gate minus Risk Gate differences across 20 seed-level replications, with t-based 95% intervals.
- Per-family summaries across all 14 benchmark families.

The same case-indexed random draws are reused across all three policy structures. Report both marginal accuracies and the actual common-shock mass for every condition. Report the existing branching policies separately from the stylized SerialEvidenceGate.

## Limitations

- All cases and accuracy parameters are synthetic and illustrative.
- The common-shock mechanism is a stylized stress model, not an empirical estimate of dependence in real retrieval or human-review pipelines.
- The model assumes a common shock forces all invoked correctness channels to err; real common-cause failures may be partial, directional or source-specific.
- The study does not use real LLM verifiers, retrieval systems or human reviewers.
- Confidence intervals describe seed variability under this simulator, not uncertainty about deployment incident rates.

## Reproduction

    python -m unittest discover -s tests -p 'test_correlated_common_cause.py' -v
    python scripts/run_correlated_common_cause_sensitivity.py
