# Correlated Common-Cause Sensitivity — Results Review v2

**Workflow run:** [45151733036](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/45151733036)  
**PR head commit used for the artifact:** `23cc5f287d349032daf96b1ed9bb670402dafd1e`  
**Workflow checkout commit recorded in manifest:** `14238c6a44a2e360142f012d6094df5759631a37`  
**Artifact:** [ega-correlated-common-cause-sensitivity-v2](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/45151733036/artifacts/14807765067)  
**Benchmark:** v0.4 HIGH-risk subset (700 cases)  
**Design:** 81 parameter conditions × 20 seeds; three policy structures  
**Study type:** exploratory synthetic sensitivity analysis

## Design correction

The first version applied a common shock to channel draws but evaluated the repository's existing policies through branching paths that generally invoke only one correctness channel per decision. With marginal accuracies held constant, this does not meaningfully exercise cross-channel joint failure. Version 2 therefore reports those existing policies as a branch-only diagnostic and adds a separate **SerialEvidenceGate** comparator.

SerialEvidenceGate is a stylized two-source pipeline: retrieval and verifier produce safe/unsafe assessments; agreement determines the decision; disagreement or retrieval unavailability triggers human review. A common shock can make retrieval and verifier jointly wrong and agree on a false-safe assessment, bypassing human review. This is an analytical comparator, **not the current EvidenceGate implementation**.

## Main results

### Existing branching policies

Averaged equally over the 27 accuracy combinations:

| Common-shock fraction | EvidenceGate unsafe-ACT rate | RiskGate unsafe-ACT rate |
|---:|---:|---:|
| 0.0 (independent) | 12.50% | 6.78% |
| 0.5 | 12.21% | 6.58% |
| 1.0 (maximum allowed by marginals) | 12.07% | 6.54% |

The branch-only EvidenceGate result does not rise under the common-shock sweep. Its paired unsafe-ACT change from independent to maximum shock is negative in all 27 conditions, but 12 of those 27 intervals cross zero. This is **not evidence that cross-channel correlation is harmless**; it demonstrates that this branching simulator does not put multiple correctness channels on the same decision path.

EvidenceGate has a higher unsafe-ACT rate than RiskGate in 23/27 accuracy combinations at all three shock levels. For the maximum-shock condition, paired 95% intervals are entirely worse for EvidenceGate in 21/27 conditions, entirely better in 4/27, and cross zero in 2/27.

### Stylized serial gate

Averaged equally over the 27 accuracy combinations:

| Common-shock fraction | SerialEvidenceGate unsafe-ACT rate | SerialEvidenceGate safe-ACT coverage |
|---:|---:|---:|
| 0.0 (independent) | 6.34% | 89.81% |
| 0.5 | 6.39% | 89.29% |
| 1.0 (maximum allowed by marginals) | 6.79% | 88.90% |

For the paired change from independent errors to maximum common shock:

- Mean unsafe-ACT change across the 27 accuracy combinations: **+0.45 percentage points**.
- Unsafe-ACT rate increases in 16/27 combinations, decreases in 10/27, and is unchanged in 1/27.
- Paired 95% intervals are entirely positive in 13/27 combinations, entirely negative in 5/27, and cross zero in 9/27.
- Largest increase: **+2.71 percentage points** (paired 95% interval +1.86 to +3.57 pp) at retrieval accuracy 0.75, human accuracy 0.75, verifier accuracy 0.85.
- Other notable increases include +2.06 pp at (0.75, 0.90, 0.85) and +1.95 pp at (0.95, 0.90, 0.93).

The direction is not universal. Several combinations show lower unsafe-ACT rates under maximum shock, especially where retrieval accuracy is 0.50. The result supports a conditional statement: **a common-cause failure can materially increase unsafe actions in some serial-gate configurations, but the effect depends on marginal accuracies and routing.** It does not support a general claim that correlation always increases risk.

## Statistical outputs

The artifact includes:
- `overall_summary.csv`: 81 conditions, policy-level seed means and paired policy comparisons.
- `scenario_family_summary.csv`: results by scenario family.
- `seed_level_results.csv`: all 20 seed-level outcomes for each condition and policy.
- `paired_shock_effects.csv`: within-seed contrasts for shock fraction 0.5 and 1.0 versus independent errors, with t-based 95% intervals.

The same case-indexed random draws are reused across policies and shock conditions. Each channel's marginal error probability is preserved by the mixture construction; the common-shock mass is the selected fraction of the smallest marginal error rate.

## Limitations and claim boundary

- The benchmark is synthetic; all accuracy and common-shock parameters are illustrative, not empirically calibrated.
- The shared shock is a stylized all-channel failure event, not a fitted dependency model from real retrieval, verifier or human-review data.
- The serial comparator is hypothetical and not an implementation-level measurement of the repository's current EvidenceGate.
- Seed-level confidence intervals describe simulator variability, not deployment uncertainty or real-world incident rates.
- The model does not include multiple source clusters, adaptive attackers, queue capacity, intervention delay, cost, hidden tool hooks or external side effects.

## Next work

1. Calibrate dependence using independent annotations or empirical retrieval/verifier/human-review traces.
2. Replace the single shared shock with source-graph and partial-common-cause models.
3. Model human-review capacity, delay, workload-induced error and intervention cost.
4. Bind the serial-gate decision to a real executor and record canonical tool, arguments, target resource and resulting side effects.
5. Treat any claim of general correlation harm as unproven until these extensions and external replication are complete.
