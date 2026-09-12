from pathlib import Path
import hashlib, json
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
bench=ROOT/'data'/'benchmark'

if not (bench/'cases.jsonl').exists():
    raise SystemExit('Run: python scripts/generate_benchmark.py')

cases=[json.loads(x) for x in open(bench/'cases.jsonl')]

def H(o):
    return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()

assert len(cases)==1000
assert len({r['case_id'] for r in cases})==1000
assert len({r['pair_id'] for r in cases})==500
assert len({r['fingerprint'] for r in cases})==500
fail=0
for pid in {r['pair_id'] for r in cases}:
    p=[r for r in cases if r['pair_id']==pid]
    if len(p)!=2 or {x['action']['risk_level'] for x in p}!={'LOW','HIGH'}:
        fail+=1
    elif H(p[0]['observable'])!=H(p[1]['observable']):
        fail+=1
assert fail==0
counts=Counter(r['family'] for r in cases)
assert set(counts.values())=={100}
print('PASS: 1000 records; 500 unique pairs/fingerprints; 0 pair-integrity failures; 100 records/family.')
