# Prior-Art / Design Source Notes

The provenance experiments deliberately do not claim cryptographic attestation as novel.

Relevant established patterns:
- **in-toto Attestation Framework:** signed statements bind subjects/artifact hashes to typed provenance claims and are used by SLSA, Sigstore attestations, and related software supply-chain systems.
- **CNCF supply-chain security guidance:** clients should verify both signatures and the contents/policy implications of provenance metadata; signed provenance does not by itself make a claim true.
- **IETF Internet-Draft (July 2026), Compliance Profile of Signed Action Receipts for AI Agents:** proposes signed action/decision receipts and links to SLSA/in-toto-style provenance, illustrating that signed accountability records for agent actions are an active standards direction.

The research contribution being tested here is narrower:
whether attested provenance and separated lineage authority repair specific evidence-independence failures observed in the Evidence-Gated Autonomy benchmark.
