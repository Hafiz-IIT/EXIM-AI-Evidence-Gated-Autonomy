# Experiment 2 source recovery and controller reconstruction

## Original archive recovery

On 18 November 2026, the original 12 September 2026 research archives were recovered from the user's Library. The GitHub-ready source snapshot's 32-entry SHA-256 manifest was verified 32/32. The missing seven-row dual-lineage compromise CSV and original 2D trust-root/stochastic outputs were restored with original hashes.

The exact archived v1 `core.py` and generic Ed25519 helper `provenance.py` are preserved under `legacy/experiment2_original/src/`. They do not replace current source files.

## Clearly labeled v2/v3 reconstruction

The archives did not contain the original executable Experiment 2B/2D/2E runner or the exact historical `evidence_gate_v2` / `evidence_gate_v3` functions. The user gave blanket authorization to continue the research and complete the task, so a separately labeled reconstruction was implemented under `legacy/experiment2_reconstruction/`. It is explicitly **not** represented as the original source.

The reconstruction:
- regenerates the 500-case 2A attested dataset and 2B dual-lineage dataset from the archived benchmark and signing helper, matching both archived SHA-256 hashes;
- reproduces the archived 16-branch, 500-case decision cache byte-for-byte (SHA-256 `7f59b47d7b62c1747897feef0cb1adc0f7e5c92f4b671b180ca3317a3c266c33`);
- reproduces the 2B deterministic attack comparison, 2D trust-root compromise table and 2E dual-lineage compromise table byte-for-byte;
- records the reconstruction assumptions and the limits of the historical evidence.

Run `python scripts/reconstruct_exp2.py` to create `results/exp2_reconstruction/`. The original `results/exp2/` artifacts are never overwritten.

## Important security finding / reconstruction assumption

The archived `trust_roots.json` does not list lineage_A or lineage_B. The reconstruction derives their public-key hashes from the archived deterministic test-key helper; these are reconstructed trust anchors, not recovered historical registry entries.

The 2E behavior is consistent with a gate that uses two lineage signatures as the authoritative dependency-group claim but does not bind that claim to the dependency-group field inside the verifier's signed attestation. Under that reconstructed rule, compromising both lineage authorities produces 50 unsafe ACTs (10%) in the 500-case synthetic benchmark, while either one alone fails closed. This is a material common-cause weakness, not evidence that the original missing source had exactly this implementation.

## Stochastic results

The restored 2D 30-seed per-seed CSV recomputes its summary exactly. The 2C stochastic summary remains an archived aggregate; the exact per-seed file remains in the recovered source archive and is not yet checked into this repository.

## Claim boundaries

All cases, keys, identities, signatures and attacks are synthetic. The deterministic keys are test fixtures, not production cryptography. These counts are not real-world probabilities or deployment-security evidence. The reconstructed controllers must not be cited as original historical source.


The manuscript-build workflow now executes `scripts/reconstruct_exp2.py` and uploads the generated case sets, decision cache, reconstructed 2B/2D/2E tables and reconstruction manifest as a CI artifact. This makes the byte-for-byte recovery checks part of the repeatable CI path.
