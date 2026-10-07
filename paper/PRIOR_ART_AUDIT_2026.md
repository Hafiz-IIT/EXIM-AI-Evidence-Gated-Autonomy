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
