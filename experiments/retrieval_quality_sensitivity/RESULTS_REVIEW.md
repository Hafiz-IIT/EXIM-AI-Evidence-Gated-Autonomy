# Retrieval Quality and Escalation Fallback — Results Review v1

**Workflow run:** 45085233806  
**Source commit:** 1db4b147149a3786143a332db7b9e9ce2dba261c  
**Artifact:** ega-retrieval-quality-sensitivity-v1  
**Benchmark:** v0.4 HIGH-risk subset  
**Cases:** 700 (600 unsafe-to-act, 100 safe-to-act)  
**Replications:** 30 seeds per condition  
**Conditions:** 162  
**Scenario families:** 14  
**Study type:** exploratory synthetic sensitivity analysis

## Executive result

The Evidence Gate's relative performance is highly dependent on retrieval quality and the fallback used when escalation is unavailable. Across the 162 prespecified parameter combinations, Evidence Gate had a higher unsafe-ACT rate than Risk Gate in 145 conditions and a lower rate in 17.

Across the paired seed-level differences, the t-based 95% intervals were entirely above zero in 141 conditions, entirely below zero in 14, and crossed zero in 7. Positive differences mean Evidence Gate had a higher unsafe-ACT rate.

This is a negative result for any broad claim that the evidence gate is intrinsically safer than a verification baseline. The evidence gate can outperform Risk Gate under high retrieval accuracy, high human-review accuracy and conservative escalation fallback, but it can perform substantially worse when retrieval or review is unreliable and escalation failure is fail-open.

## Range across the parameter grid

| Metric | Evidence Gate | Risk Gate |
|---|---:|---:|
| Unsafe ACT / all HIGH-risk cases, across conditions | 3.48%–28.02% | 6.00% (constant) |
| Conditions with lower unsafe-ACT rate | 17/162 | 145/162 |
| Conditions with higher unsafe-ACT rate | 145/162 | 17/162 |

The Risk Gate result is constant because verifier accuracy is held fixed at 0.93 and Risk Gate verifies every HIGH-risk action. This is an explicit limitation of the comparison, not evidence that real verifiers have constant performance.

## Best and worst tested conditions for Evidence Gate

| Setting | Best tested condition | Worst tested condition |
|---|---:|---:|
| Retrieval availability | 0.50 | 0.95 |
| Retrieval accuracy conditional on availability | 0.95 | 0.50 |
| Human-review accuracy | 0.98 | 0.75 |
| Escalation availability | 0.80 | 0.80 |
| Fallback when escalation unavailable | DEFER | ACT |
| Evidence Gate unsafe-ACT rate | 3.48% | 28.02% |
| Risk Gate unsafe-ACT rate | 6.00% | 6.00% |
| Paired difference (Evidence Gate − Risk Gate) | −2.52 percentage points | +22.02 percentage points |
| Paired 95% interval | [−2.83, −2.21] pp | [+21.46, +22.59] pp |
| Evidence Gate safe-ACT coverage | 90.43% | 89.37% |
| Risk Gate safe-ACT coverage | 92.90% | 92.90% |

These are grid extrema, not recommended operating points. In particular, the best condition has only 50% retrieval availability but very high conditional retrieval accuracy and human-review accuracy; when retrieval is unavailable, the escalation/fallback assumptions dominate.

## Scenario-family findings

The following are unweighted averages across the 162 parameter conditions of the family-level unsafe-ACT-rate difference (Evidence Gate minus Risk Gate). They describe this constructed grid, not real-world failure prevalence.

| v0.4 family | Mean difference |
|---|---:|
| C3 missing critical evidence | +17.56 pp |
| C5 stale evidence | +17.48 pp |
| C10 missing invoice | +16.41 pp |
| C11 missing packing list | +16.09 pp |
| C8 correlated verifier failure | +9.18 pp |
| C4 consistent but wrong evidence | +9.12 pp |
| C12 duplicate document kind | +9.09 pp |
| C13 corrupted provenance | +7.58 pp |
| C0 clean | 0.00 pp |
| C1 extraction error | 0.00 pp |
| C2 cross-document conflict | 0.00 pp |
| C6 verifier false accept | 0.00 pp |
| C7 verifier false reject | 0.00 pp |
| C9 cascading error | 0.00 pp |

The strongest weaknesses arise where Evidence Gate requests evidence or escalates and then relies on downstream retrieval or human resolution. This aligns with the central dependency concern: a gate cannot compensate for poor downstream evidence acquisition or unreliable review simply by requesting more evidence.

## Method and limitations

- The experiment uses the 700 HIGH-risk cases in a constructed synthetic benchmark, containing 600 unsafe-to-act and 100 safe-to-act cases.
- Retrieval availability and retrieval accuracy are separate parameters.
- Retrieval, verifier and human-review errors are symmetric binary errors: an incorrect resolution flips the benchmark safe/unsafe label.
- Retrieval availability, retrieval correctness, escalation availability and human-review correctness are modelled as event-specific draws.
- The same case-indexed draws are shared across policies within each seed, enabling paired comparisons.
- Verifier accuracy is fixed at 0.93; it is not varied across the grid.
- The parameter values are illustrative and not calibrated using field data.
- The model does not represent actual retrieval rankings, semantic relevance, source lineage, correlated retrieval/reviewer errors, queue capacity, reviewer fatigue, intervention delays or operational costs.
- The confidence intervals describe seed variability under this simulator, not uncertainty about real-world incident rates.
- No external model API or human reviewer was used.

## Required next experiments

1. Sweep verifier accuracy and calibration rather than fixing it at 0.93.
2. Add correlated retrieval/verifier/human errors, including shared upstream source dependence.
3. Model evidence retrieval as source selection with stale, incomplete, duplicated and misleading records—not only a binary correct/incorrect outcome.
4. Add human-review capacity, queue delays, fatigue and intervention costs.
5. Test action-family-specific fallback policies and reversible versus irreversible actions.
6. Independently review benchmark labels and the assumed cost/accuracy ranges before making any policy recommendation.

## Conclusion

The evidence-gated policy is not uniformly superior to a simple verification baseline. Its benefit is conditional on retrieval quality, reviewer quality and escalation reliability. Any paper or application claim must state that dependency and report the failure regions, not only the best-performing settings.
