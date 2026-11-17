# Experiment 2 controller reconstruction (not original source)

The original Experiment 2B/2D/2E runner was absent from both recovered archives. After the user authorized continued work with a clearly labeled reconstruction, this module was derived from:

- the archived v1 controller and deterministic signing helper;
- the original 500-case benchmark;
- exact archived 2A/2B attestation outputs;
- the 16-branch per-case decision cache;
- the 2B, 2D and 2E result tables.

First generate the benchmark with `python scripts/generate_benchmark.py`, then run `python scripts/reconstruct_exp2.py`. The runner writes to `results/exp2_reconstruction/` and never overwrites archived results.

The tests require exact SHA-256 matches for the regenerated 2A/2B case files and decision cache, plus byte-for-byte matches for the 2B, 2D and 2E CSV tables.

## Reconstruction caveat discovered

The archived v3 lineages are signed by lineage_A and lineage_B, but these signers are absent from the archived `trust_roots.json`. Their public-key hashes are reconstructed from `deterministic_test_key`, not recovered from an original trust registry.

Further, the v3 behavior reproduced by the archived 2E table uses the dual-lineage attestations as the authoritative dependency-group claim but does not bind that claim to the dependency-group field in the verifier's signed attestation. Consequently, collusion of both lineage authorities can make a false dependency group appear valid and yields 50 unsafe ACTs in the 500-case synthetic benchmark. This is not proof that the original source had exactly this implementation; it is the minimal clearly labeled reconstruction consistent with the archived case records and result tables.

Do not cite this reconstruction as the historical original source or as production security evidence.
