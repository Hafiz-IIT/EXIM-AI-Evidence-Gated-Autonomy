# Experiment 2 reconstruction CI validation

This validation branch triggers a fresh pull-request workflow against the current Experiment 2 recovery branch. It adds only this reproducibility note; it does not alter controller behavior.

The CI run checks the normalized historical benchmark schema, regenerated 2A/2B case hashes, the 16-branch decision-cache hash, and byte-for-byte 2B/2D/2E result tables. Generated files remain under `results/exp2_reconstruction/`, separate from the archived results.
