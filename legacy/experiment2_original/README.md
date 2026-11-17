# Recovered original Experiment 2 artifacts

The 12 September 2026 GitHub-ready snapshot was recovered from the user's Library. Its 32-entry SHA-256 manifest was verified against all 32 extracted files with zero mismatches. The original Experiment 2 provenance archive was also recovered.

- `src/core.py` is the archived original v1 evidence-gate implementation.
- `src/provenance.py` is the archived original deterministic Ed25519 helper.
- `2A_attestation/trust_roots.json` and `sample_attestation.json` preserve the original trust-root and sample-attestation artifacts.
- Original 2D compromise CSVs and stochastic per-seed output are restored under `results/exp2/`.

## Historical source versus reconstruction

The recovered archives did not contain the original executable Experiment 2B/2D/2E runner or the frozen `evidence_gate_v2` / `evidence_gate_v3` controller source. The user authorized us to continue with a clearly labeled reconstruction rather than stop at the missing source. That reconstruction lives in `legacy/experiment2_reconstruction/`; it does not replace or masquerade as the original historical source.

The reconstruction regenerates the original 500-case attestation datasets, reproduces the 16-branch per-case decision cache byte-for-byte by SHA-256, and exactly matches the archived 2B, 2D and 2E result tables. See `docs/EXP2_SOURCE_RECOVERY.md` and `legacy/experiment2_reconstruction/README.md`.

## Important limitation

The original archived trust-root file contains document, external-sensor, authorization and verifier roots, but not lineage_A/lineage_B roots. The reconstruction derives those two public-key hashes from the archived deterministic test-key helper and records them as reconstructed roots. The historical v3 behavior also treats the dual-lineage group as authoritative without binding it to the verifier attestation's dependency-group field. This is an explicit reconstruction assumption and a security weakness demonstrated by the dual-lineage-compromise results.

All keys and cases are synthetic; deterministic test keys are not production cryptography.
