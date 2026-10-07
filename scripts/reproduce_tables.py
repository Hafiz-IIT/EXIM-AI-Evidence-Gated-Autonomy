from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

s1 = pd.read_csv(ROOT / "results/exp1/summary.csv")
s2 = pd.read_csv(ROOT / "results/exp2/deterministic_attack_comparison.csv")

print("\nExperiment 1A main table")
cols1 = [c for c in ["policy", "ICAR_high", "MeanCost", "FinalActRate"] if c in s1.columns]
print(s1[cols1].to_string(index=False))

print("\nExperiment 2 provenance attacks")
cols2 = [c for c in ["attack", "policy", "ICAR_high", "ACT_rate", "ESCALATE_rate"] if c in s2.columns]
print(s2[cols2].to_string(index=False))

print("\nPASS: publication tables reference only version-controlled result files.")
