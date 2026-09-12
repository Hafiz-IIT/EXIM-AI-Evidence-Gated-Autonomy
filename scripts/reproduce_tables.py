from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
s1=pd.read_csv(ROOT/'results/exp1/summary.csv')
s2=pd.read_csv(ROOT/'results/exp2/deterministic_attack_comparison.csv')
s3=pd.read_csv(ROOT/'results/exp2/dual_lineage_compromise.csv')

print('\nExperiment 1A main table')
print(s1[['policy','ICAR_high','MeanCost','FinalActRate']].to_string(index=False))
print('\nExperiment 2B provenance attacks')
print(s2[['attack','policy','ICAR_high','ACT_rate','ESCALATE_rate']].to_string(index=False))
print('\nExperiment 2E dual-lineage compromise')
print(s3.to_string(index=False))
