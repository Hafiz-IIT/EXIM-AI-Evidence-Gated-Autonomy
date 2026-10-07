# arXiv / Preprint Release Checklist

## Paper identity
**Title:** Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence  
**Author:** Syed Hafiz Ali  
**Current manuscript:** `paper/MANUSCRIPT.md`

## Claims allowed in v1
- 500 unique synthetic evidence states paired into 1,000 LOW/HIGH-consequence cases.
- Evidence Gate deterministic result: 0/500 unsafe HIGH-risk ACT decisions.
- Risk Gate and Always Verify deterministic result: 50/500 each.
- Stochastic Evidence Gate ICAR: 1.86% optimistic, 6.10% moderate, 13.09% harsh.
- Dependency spoofing and external-evidence masking are demonstrated benchmark failure modes.
- 3,675 synthetic Ed25519 attestations were tested.
- Signed provenance blocked several unsigned metadata attacks in the synthetic benchmark.
- Trust-root compromise remained a failure mode.
- Dual-lineage separation of duties raised the compromise threshold in the synthetic benchmark.

## Claims forbidden in v1
- "solves AI safety"
- "safe" or "guarantees safety"
- "production-ready"
- "real-world validated"
- "frontier-proof"
- "works on real customs data"
- "human oversight was validated"
- "external frontier-model evaluation completed"
- "cryptography proves truth"

## Verified before arXiv submission
1. **PASS —** benchmark and tables reproduced in CI:
   - `python scripts/generate_benchmark.py`
   - `python scripts/verify_benchmark.py`
   - `python scripts/reproduce_tables.py`
2. **PASS —** LaTeX source compiled; final CI artifact is 5 pages and page 1, page 3, and page 5 were visually inspected.
3. **PASS —** reported numerical claims were cross-checked against the version-controlled `results/` files.
4. **PASS —** source package boundary is limited to the manuscript compilation inputs; no private client material is part of the intended arXiv package.
5. **READY —** upload only `main.tex` and `references.bib`.
6. **READY —** submit as a preprint, not as a peer-reviewed publication.
7. After arXiv assigns an identifier, add that identifier to README and CITATION.cff.
8. Add the indexed paper to a public Google Scholar profile. If Scholar does not find it, use "Add article manually."

## Versioning
- **v1:** Experiments 1A-2E.
- **v2:** Add Experiment 3 only after the frozen external-model protocol is actually run.
- **Later version/follow-up:** Add the human-oversight study only after real participants and any required ethics review.

## Suggested classification
Candidate categories include **cs.AI**, **cs.LG**, or **cs.CY** depending on final framing and arXiv moderation. Do not treat this suggestion as a guarantee of category acceptance or endorsement.
