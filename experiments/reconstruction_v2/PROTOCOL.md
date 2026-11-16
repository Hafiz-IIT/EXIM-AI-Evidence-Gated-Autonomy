# EGA Benchmark v0.4 and Reconstruction v2 Protocol

**Status:** New synthetic benchmark and experiment protocol. This is not a reproduction of historical experiment outputs. Benchmark v0.3 and all historical result CSVs remain unchanged.

## Benchmark v0.4

- 14 fault families, 50 underlying situations per family.
- 700 unique underlying situations, each paired as LOW- and HIGH-risk cases.
- 1,400 total cases, 100 per family.
- Deterministic generation seed: 42.
- Each case includes normalized document slots, a raw document-instance list, and a synthetic document-set content digest.
- New families:
  - C10 missing invoice.
  - C11 missing packing list.
  - C12 duplicate document kind (two invoice instances with conflicting quantities).
  - C13 corrupted provenance (document-set digest does not match the observed document instances).

The provenance digest is a synthetic integrity field, not a digital signature, trusted timestamp, PKI, or proof that the underlying document is true. A regression test deliberately rewrites all document, extraction and external-weight values consistently, recomputes the unkeyed digest, and confirms the current gate still returns ACT. This is an expected security limitation: an attacker who can rewrite the evidence and recompute a public digest can create a self-consistent false record. The duplicate-document representation intentionally preserves both raw instances while retaining the legacy normalized document map; this makes it possible to test whether a policy checks raw multiplicity rather than silently trusting a normalized slot.

## Policy changes

The existing evidence gate now:
- requests evidence when invoice, packing list, or declaration is missing;
- escalates when a duplicate document kind is present;
- escalates when the explicit v0.4 document-set digest is corrupted;
- remains backward-compatible with v0.3 records, which predate the explicit lineage envelope.

These are policy behaviors under test, not evidence of real customs-system readiness.

## Reconstruction v2

The v2 runner reruns the transparent 1B, 1C, 1D and 2B–2E reconstruction suite against all 700 HIGH-risk v0.4 cases, with 30 Monte Carlo seeds per stochastic condition. Outputs are written separately to `results/reconstruction_v2/`; v0.3 and v1 outputs are not overwritten.

## Parameter sensitivity

One-factor-at-a-time sweeps compare Always Verify, Risk Gate and Evidence Gate while varying one parameter and holding the other parameters at the moderate baseline:

| Parameter | Values |
|---|---|
| Verifier accuracy | 0.75, 0.85, 0.93, 0.99 |
| Retrieval success | 0.70, 0.85, 0.92, 0.99 |
| Human accuracy | 0.70, 0.80, 0.90, 0.98 |
| Escalation availability | 0.70, 0.85, 0.95, 1.00 |

A 3×3 interaction sweep varies human accuracy (0.70, 0.85, 0.98) against escalation availability (0.70, 0.85, 1.00). Each condition has 30 seeds. The same seed is used across the compared policies within a condition to support paired comparisons, although action-dependent random-number consumption means this is not a perfectly coupled simulation.

The output includes per-seed results, means, standard deviations and 95% t intervals. Intervals describe Monte Carlo variation under the specified simulator only; they are not uncertainty intervals for real-world performance.

## Reproducibility and interpretation

Run:
```bash
python -m unittest discover -s tests -v
python scripts/generate_benchmark_v04.py
python scripts/verify_benchmark_v04.py
python scripts/run_reconstruction_v2.py
```

The runner writes source commit, workflow run ID, Python version and SHA-256 hashes for generated CSVs into its manifest. The benchmark generator and verifier are separate commands so integrity can be checked independently.

No result from this protocol should be presented as real customs performance, frontier-model evaluation, human-subject validation, cryptographic proof of truth, or historical reproduction. Manuscript claims must be reconciled against the v2 outputs and independently reviewed before submission.
