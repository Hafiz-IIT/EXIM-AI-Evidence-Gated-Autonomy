from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

s1 = pd.read_csv(ROOT / "results/exp1/summary.csv")
s2 = pd.read_csv(ROOT / "results/exp2/deterministic_attack_comparison.csv")

print("\nExperiment 1A main table")
print(s1[["policy", "ICAR_high", "MeanCost", "FinalActRate"]].to_string(index=False))

print("\nExperiment 2B provenance attacks")
print(s2[["attack", "policy", "ICAR_high", "ACT_rate", "ESCALATE_rate"]].to_string(index=False))

exp2e_path = ROOT / "results/exp2/dual_lineage_compromise.csv"
print("\nExperiment 2E dual-lineage compromise")
if exp2e_path.exists():
    s3 = pd.read_csv(exp2e_path)
    print(s3.to_string(index=False))
else:
    print(
        "ARCHIVAL GAP: results/exp2/dual_lineage_compromise.csv is not committed. "
        "Do not reconstruct this table from prose and label it reproduced. "
        "See results/exp2/EXP2_RESULTS.md for the historical summary; recover the "
        "original experiment artifact or regenerate it from the exact frozen code path "
        "before claiming row-level reproducibility for Experiment 2E."
    )
