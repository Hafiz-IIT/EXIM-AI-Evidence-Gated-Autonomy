# Experiment 2 reconstruction CI validation

This small validation branch exists only to trigger a fresh pull-request workflow against the current Experiment 2 recovery branch. It does not add or alter any controller behavior.

The CI workflow runs:

```bash
python -m unittest discover -s tests -v
python scripts/reconstruct_exp2.py \
  --benchmark data/benchmark/cases.jsonl \
  --original-results results/exp2 \
  --output results/exp2_reconstruction
```

The expected result is `exact_reconstruction_verified`, with exact hashes for the regenerated 2A/2B case sets and decision cache, and byte-for-byte matches for the archived 2B, 2D and 2E CSV tables. Generated artifacts are written outside `results/exp2/` so archived evidence is never overwritten.
