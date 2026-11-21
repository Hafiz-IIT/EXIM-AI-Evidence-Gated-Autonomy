# C0–C14 controller mapping gap register v1

Status: SOURCE RECOVERY COMPLETE FOR HISTORICAL BASELINES; FROZEN E3 MAPPING NOT FULLY SPECIFIED.
This document is an additive audit. It does not amend the frozen Experiment 3 protocol, change its baselines, or authorize scoring.

## What is authoritative

The frozen Experiment 3 protocol defines the decision space as ACT, VERIFY, REQUEST EVIDENCE, DEFER, ESCALATE and gives the following baseline descriptions:
- B1 Always Act.
- B2 Confidence Threshold.
- B3 Agreement Gate: act if two or more outputs agree.
- B4 Always Verify.
- B5 Selective Confidence: verify only in a confidence band.
- B6 Strong-Verifier Gate: act when a designated stronger verifier accepts.
- B7 Risk Gate: consequence-aware but evidence-structure-light.
- B8 Evidence Gate: full typed EGA policy.

Historical executable functions are available in `src/core.py` (blob SHA `4700f68570eb3179c6baa35213304a5fb42bfc43`). Their exact rules and regression tests are recorded in `CONTROLLER_RECOVERY.md`. Historical thresholds are not automatically Experiment 3 thresholds.

## Per-baseline mapping status

| Baseline | Frozen E3 description | Historical source evidence | Missing E3 specification | Status |
|---|---|---|---|---|
| B1 | Always Act | `always_act` always returns ACT | None for this baseline | Directly implementable |
| B2 | Confidence Threshold | Historical `confidence_gate` uses 0.90 | E3 confidence field choice (proposer self-confidence vs extraction confidence), exact threshold and equality handling | Not frozen |
| B3 | Agreement Gate; act if 2+ outputs agree | Historical `document_agreement` checks three source documents, not model-output votes | Which outputs vote; whether vote means exact action enum or binary ACT; handling missing/invalid output | Partially specified |
| B4 | Always Verify | Historical `always_verify` always returns VERIFY | None for this baseline | Directly implementable |
| B5 | Selective Confidence; verify only in a confidence band | Historical `selective_abstention` is not a confidence-band policy; it acts at >=0.90 absent verifier rejection, otherwise defers | Lower/upper confidence bounds, out-of-band action, and verifier interaction | Not frozen |
| B6 | Act when designated stronger verifier accepts | Historical `weak_strong` uses 0.94/0.75 confidence bands and verifier majority | Identity/selection of stronger verifier, acceptance schema, behavior when unavailable or conflicts | Not frozen |
| B7 | Consequence-aware, evidence-structure-light | Historical `risk_gate`: HIGH→VERIFY; LOW→ACT at confidence >=0.90, else DEFER | Whether E3 adopts this exact rule and which confidence field/threshold | Candidate only; not frozen |
| B8 | Full typed EGA policy | Historical `evidence_gate_v1` has ordered checks over legacy document/authorization/provenance fields | Complete mapping from E3 feature schema to typed predicates, freshness validity, provenance validity, independent-source evidence, grounding, reversibility, precedence and action outcomes | Not frozen |

## Feature availability audit

The current E3 proposer/V1/V2 prompt schema provides explicit fields for missing evidence, conflicts, freshness concerns/failures, provenance concerns, dependency concerns, authorization evidence/sufficiency, grounding sufficiency, verifier support and common-mode concerns.

It does not currently provide deterministic positive attestations for:
- source freshness validity and the governing time window;
- authenticated provenance-envelope validity / trust-root status;
- independently verified source identity and independence groups;
- external-grounding verification result and authoritative source identity;
- tested reversibility / rollback validity for all cases;
- the full legacy document-instance and extraction-comparison fields consumed by historical B8.

A model saying that it sees no concern is not a positive attestation. Missing or malformed fields remain unknown; they must not be converted to true.

## Required versioned amendment before B1–B8 scoring

A protocol amendment must define, in a machine-readable table:
1. Exact input fields per baseline, with source and provenance.
2. Confidence field and numeric thresholds, including equality and missing-value behavior.
3. B3 vote set, vote normalization, tie/invalid-output behavior.
4. B5 confidence band and behavior below/above it.
5. B6 designated verifier selection, acceptance condition and failure behavior.
6. B7 consequence-to-action mapping and whether it uses confidence.
7. B8 ordered predicates, positive attestations, precedence and all five possible outputs.
8. Treatment of the 12 cases whose frozen registry does not explicitly establish reversibility.
9. A versioned prompt/manifest/schema hash and paired analysis plan amendment.

## Safe implementation decision

Do not implement guessed B2/B5/B6/B7/B8 rules as if they were frozen. Do not substitute historical B3/B6/B8 semantics. Keep the existing feature mapper as an explicit-field extractor only. Keep the 630-call primary run plan-only and blocked until the protocol amendment is independently reviewed and frozen.

## Sources

- Frozen Experiment 3 protocol: https://app.notion.com/p/3de0a218bb3d8117a22cf31b037d5306
- Prompt Pack v1: https://app.notion.com/p/3de0a218bb3d81689cfdfb876d2051c7
- Execution Harness Contract v1: https://app.notion.com/p/3de0a218bb3d81898fded057b1e38aad
- Historical executable implementation: `src/core.py`, blob SHA above
- Historical rule extraction: `CONTROLLER_RECOVERY.md`
- Case reversibility source audit: `reversibility_assessment_v1.json`


## Versioned amendment draft

An additive proposal is now available at [CONTROLLER_PROTOCOL_AMENDMENT_v1_DRAFT.md](CONTROLLER_PROTOCOL_AMENDMENT_v1_DRAFT.md). It does not close this gap register: it proposes deterministic B1–B8 mappings, explicit unknown-value behavior, and Prompt Pack v2 tri-state attestations while keeping source-supported facts separate from new design choices. The proposal remains unapproved and unfrozen. Do not implement or score its candidate rules until the scientific decisions and acceptance tests listed in that draft are resolved.
