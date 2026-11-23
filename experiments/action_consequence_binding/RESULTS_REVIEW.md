# Action Consequence Binding — Results Review v1

**Workflow run:** 45085431233  
**Source commit:** a16451839efb663e907f5eef785f7203256cfbdc  
**Benchmark:** v0.4 HIGH-risk subset  
**Cases:** 700 (600 unsafe-to-act, 100 safe-to-act)  
**Experiment type:** deterministic synthetic policy test

## Main result

The existing v1 gate trusts the proposed action's risk_level field. When that field is downgraded from HIGH to LOW, v1 returns ACT before applying its normal evidence checks. In this 700-case synthetic set, that produces 700 ACT decisions, including 600 unsafe ACT decisions.

The new v2 gate binds the proposed action name and consequence metadata to a separately supplied trusted action ID and action catalog. Any mismatch returns ESCALATE. In these attacks, v2 returns no ACT decisions, preventing unsafe ACTs but also blocking all 100 safe cases pending review.

## Aggregate results

| Variant | Policy | Unsafe ACT | Unsafe ACT / all cases | Unsafe ACT / ACT | Safe ACT coverage | False-block rate | Escalation rate |
|---|---|---:|---:|---:|---:|---:|---:|
| Unmodified | v1 | 0/700 | 0.00% | 0.00% | 50.00% | 50.00% | 35.71% |
| Unmodified | v2 | 0/700 | 0.00% | 0.00% | 50.00% | 50.00% | 35.71% |
| Risk-level downgrade | v1 | 600/700 | 85.71% | 85.71% | 100.00% | 0.00% | 0.00% |
| Risk-level downgrade | v2 | 0/700 | 0.00% | Not defined (no ACT) | 0.00% | 100.00% | 100.00% |
| Reversibility spoof | v1 | 0/700 | 0.00% | 0.00% | 50.00% | 50.00% | 35.71% |
| Reversibility spoof | v2 | 0/700 | 0.00% | Not defined (no ACT) | 0.00% | 100.00% | 100.00% |
| External-effect spoof | v1 | 0/700 | 0.00% | 0.00% | 50.00% | 50.00% | 35.71% |
| External-effect spoof | v2 | 0/700 | 0.00% | Not defined (no ACT) | 0.00% | 100.00% | 100.00% |
| Action-identity substitution | v1 | 600/700 | 85.71% | 85.71% | 100.00% | 0.00% | 0.00% |
| Action-identity substitution | v2 | 0/700 | 0.00% | Not defined (no ACT) | 0.00% | 100.00% | 100.00% |

## Interpretation

1. **Risk metadata is a security boundary in v1.** A single HIGH-to-LOW downgrade bypasses the normal evidence path.
2. **v1 does not use reversibility or external_effect in its decision logic.** Those fields can be altered without changing v1 decisions.
3. **Action identity also needs an independent binding.** If the proposed action name is changed to a known low-risk action, v1 accepts the low-risk branch. v2 rejects it when the trusted action ID remains the original high-risk action.
4. **v2 trades unsafe authorisation for intervention.** It prevents ACT under the tested mismatches, but escalates every case, including safe cases. This is a conservative gate, not a complete resolution workflow.
5. **The 85.71% value is not an incident probability.** It is the proportion of unsafe-to-act cases in this constructed 700-case benchmark under a deterministic metadata-spoof transformation.

## Threat-model and implementation limitations

- The trusted action ID is supplied independently by the experiment. The implementation does not authenticate the authorization context that supplies it.
- The catalog is local synthetic configuration, not a signed or centrally governed production registry.
- The code does not enforce that the eventual external tool invocation matches the trusted action ID.
- The experiment tests metadata mismatch, not compromise of the trusted catalog or authorization service.
- No human-resolution outcome is modelled after ESCALATE; therefore the 100% false-block rate is an authorization-stage result, not an end-to-end service failure rate.
- The action catalog covers two synthetic action types.
- Results are deterministic and do not estimate deployment prevalence or stochastic model behaviour.

## Required next experiment

Test compromise and recovery of the trusted action catalog itself: catalog tampering, stale catalog versions, action-ID aliasing, tool-name substitution after authorization, and policy/catalog version mismatch. Add a signed catalog manifest and verify that the executor consumes the same action ID that the gate authorized. Only then can the action-identity binding claim extend beyond the policy function boundary.
