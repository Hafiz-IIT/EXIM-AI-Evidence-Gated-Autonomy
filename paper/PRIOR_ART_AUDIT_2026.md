# Prior-Art Audit — EGA v1

## Core adjacent areas reviewed

### AI control
Greenblatt et al., *AI Control: Improving Safety Despite Intentional Subversion* (ICML 2024), evaluates protocols designed to remain safe against intentional model subversion. EGA differs by treating the evidence chain and action-authorization state as the experimental object rather than evaluating untrusted-model coding behavior.

### Scalable oversight
Kenton et al., *On scalable oversight with weak LLMs judging strong LLMs* (2024), evaluates debate, consultancy and direct judging under capability asymmetry. EGA differs by making evidence completeness, source dependence and provenance explicit variables before authorization.

### Oversight communication and disagreement
Recent work studies collaborative disagreement resolution and strategic communication in oversight. These results reinforce the need to examine how evidence is elicited and presented, not only whether the final verdict is correct.

### Provenance
in-toto and SLSA provide established provenance/attestation mechanisms. EGA uses the same broad integrity principle as an experimental tool but studies the separate failure mode where a trusted signer can attest to a false claim.

## Novelty boundary

The manuscript should **not** claim invention of:
- AI control
- scalable oversight
- cryptographic provenance
- signed attestations
- separation of duties

The defensible contribution is the **synthetic benchmark and experimental framing that jointly varies evidence sufficiency, source independence, provenance integrity, trust-root compromise and escalation reliability for consequential action authorization**.

## Submission requirement

Before arXiv submission, perform one final literature search immediately before freezing v1 so the related-work section reflects the current state of the field.


## Dependency-aware witness ancestry — v5 novelty boundary

The v5 protocol cites He and Yu's *The Illusion of Independent Quorums: Epistemic Fault Domains and Correlated Cognitive Failures in Agentic Quorums* (arXiv:2609.02925), which introduces Epistemic Fault Domains, the Structural Epistemic Cut, and a Dependency-Aware Quorum Controller. It also cites Hillier's *Attestation Reconciliation Protocol* draft -06 (23 October 2026), which specifies witness quorum requirements including pairwise distinct operating-party identifiers and verification methods, and Kahn's 1998 work on independent corroboration.

Accordingly, v5 must not claim invention of epistemic fault domains, structural cuts, dependency-aware quorum admission, or witness diversity. Its contribution is restricted to an EXIM-inspired deterministic benchmark comparison of key uniqueness, direct-field diversity, strict thresholding, and transitive-ancestry intersection, including measured security/availability costs and a registry-root omission attack. The graph-aware mechanism is a prototype implementation of a known design direction, not a new theory.
