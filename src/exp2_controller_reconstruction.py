"""Public entry points for the artifact-constrained Experiment 2 controller reconstruction.

These names are intentionally suffixed _reconstructed: the original historical
v2/v3 executable source was not present in either recovered archive.
"""
from legacy.experiment2_reconstruction.controller import (
    evidence_gate_v2_attested,
    evidence_gate_v3_dual_lineage,
)

RECONSTRUCTION_NOTICE = (
    "Reconstructed from archived v1/provenance code, benchmark cases, signed "
    "attestations, decision cache and result tables; not the original historical source."
)


def evidence_gate_v2_reconstructed(case: dict) -> str:
    return evidence_gate_v2_attested(case)


def evidence_gate_v3_reconstructed(case: dict) -> str:
    return evidence_gate_v3_dual_lineage(case)
