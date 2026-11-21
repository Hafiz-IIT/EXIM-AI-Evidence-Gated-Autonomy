# Experiment 3 controller recovery — source audit

Status: historical policy logic recovered; direct C0–C14 adapter remains blocked pending a versioned mapping amendment.

## Authoritative code recovered

The repository's pre-Experiment-3 deterministic controller is implemented in `src/core.py` at blob SHA `4700f68570eb3179c6baa35213304a5fb42bfc43`.

The functions are:
- `always_act`
- `confidence_gate`
- `document_agreement`
- `always_verify`
- `selective_abstention`
- `weak_strong`
- `risk_gate`
- `evidence_gate_v1`

This is concrete executable historical source, not a prose reconstruction. The frozen Experiment 3 protocol reuses the B1–B8 names but describes B3 and B6 at a higher level. Therefore, the source functions are a recovered reference, not automatically an exact implementation of every Experiment 3 baseline.

## Recovered B1–B8 logic from `src/core.py`

| ID | Historical function | Exact rule |
|---|---|---|
| B1 | `always_act` | Always return `ACT`. |
| B2 | `confidence_gate` | `ACT` iff extraction confidence ≥ 0.90; otherwise `DEFER`. |
| B3 | `document_agreement` | `ACT` iff all three documents are present and agree on quantity, gross weight and HS; otherwise `DEFER`. |
| B4 | `always_verify` | Always return `VERIFY`. |
| B5 | `selective_abstention` | `ACT` iff confidence ≥ 0.90 and no verifier rejects; otherwise `DEFER`. |
| B6 | `weak_strong` | Define weak support as document agreement and accepting verifiers ≥ ceil(verifier count / 2). Return `ACT` iff confidence ≥ 0.94 and weak support; return `DEFER` iff confidence < 0.75; otherwise `VERIFY`. |
| B7 | `risk_gate` | `VERIFY` for HIGH risk; for LOW risk, `ACT` iff confidence ≥ 0.90, else `DEFER`. |
| B8 | `evidence_gate_v1` | See ordered rule below. |

### Exact historical B8 order

The order is material; the first matching condition wins:

1. LOW risk → `ACT`.
2. Duplicate document kind or invalid provenance envelope → `ESCALATE`.
3. Incomplete document set, absent authorization, or expired authorization → `REQUEST_EVIDENCE`.
4. Document disagreement → `VERIFY`.
5. External measured-weight conflict → `ESCALATE`.
6. Extraction mismatch against invoice → `VERIFY`.
7. Any verifier rejection or fewer than two distinct verifier dependency groups → `ESCALATE`.
8. Otherwise → `ACT`.

The B8 input features are computed by `visible_features` in the same source file. In particular, the historical controller expects three source documents, an explicit authorization record with expiry/evaluation dates, external measured weight, extraction values, verifier accept flags and dependency groups, document-instance duplication metadata, and an optional provenance hash envelope.

## Why this cannot be copied directly into the frozen C0–C14 run

The C0–C14 Prompt Pack v1 and model-facing case schema do not expose all of those historical input fields:
- The real-model roles produce proposer/V1/V2 judgments, not the old invoice/packing-list/declaration extraction object.
- There is no explicit positive freshness-validity field in the prompt schema. An empty `freshness_failures` array is not proof of freshness.
- The prompts expose provenance concerns but do not provide a deterministic authenticated provenance-integrity result or document-set hash.
- The prompt schema does not expose the old measured-weight/extraction-to-invoice comparison.
- The C0–C14 registry currently has no frozen reversibility descriptions, despite the frozen Prompt Pack requiring them.
- The frozen Experiment 3 protocol describes B3 as an output-agreement gate and B6 as a strong-verifier gate; the recovered historical functions are document agreement and a weak/strong confidence band. These labels are related, but not equivalent by definition.

Consequently, relabeling the old functions as the exact C0–C14 B1–B8 controller would change the operational meaning of the frozen experiment. Filling the missing fields from model silence would also violate the parser/feature-map rule.

## Frozen Experiment 3 descriptions vs recovered source

The frozen protocol defines:
- B1 Always Act.
- B2 Confidence Threshold.
- B3 Agreement Gate: act if two or more outputs agree.
- B4 Always Verify.
- B5 Selective Confidence: verify only in a confidence band.
- B6 Strong-Verifier Gate: act when a designated stronger verifier accepts.
- B7 Risk Gate: consequence-aware but evidence-structure-light.
- B8 Evidence Gate: full typed EGA policy.

The frozen protocol does not provide exact numeric thresholds, designated-strong-verifier identity/rotation, agreement tie handling, or complete C0–C14 feature-to-action mapping for these labels. The historical source supplies 0.90, 0.94 and 0.75 thresholds, but those values belong to the historical functions described above; they must not be silently assumed to be frozen Experiment 3 values.

## Safe implementation decision

- Preserve `src/core.py` unchanged as the historical controller source.
- Do not reuse its B8 directly against C0–C14 model outputs.
- Do not report B1–B8 C0–C14 scores until a versioned protocol amendment defines the mapping/thresholds and the missing evidence fields.
- Keep the 630-call plan and all raw model outputs blocked from execution until that amendment, reversibility source, dry-run acceptance and account-level zero-cost checks are satisfied.

## Source anchors

- Frozen Experiment 3 protocol: https://app.notion.com/p/3de0a218bb3d8117a22cf31b037d5306
- Frozen primary run manifest: https://app.notion.com/p/3de0a218bb3d81789fe8d731007dc2e5
- Frozen Prompt Pack v1: https://app.notion.com/p/3de0a218bb3d81689cfdfb876d2051c7
- Statistical Analysis Plan v1: https://app.notion.com/p/3de0a218bb3d816db032d6ec1ee8070b
- Historical implementation: `src/core.py` (blob SHA above)
