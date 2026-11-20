# Experiment 3 — zero-cost provider qualification (protocol amendment candidate)

**Status: research-only qualification note; no provider is frozen and no API call has been made.**

## Non-negotiable constraints
- API spend must remain USD 0. No billing activation, paid plan, prepaid credits, card, or automatic fallback to a paid model.
- Preserve raw request/response records, exact model IDs, provider identity, prompt hashes, task hashes, usage, latency, retry history, and provider errors.
- Do not silently substitute a model or provider in an already frozen run.
- A provider is eligible only after its exact model is confirmed available to this account on a genuinely free tier, the API-compatible request is smoke-tested, and the account's effective limits are recorded.
- A free-tier quota is not a guarantee of availability or throughput.

## Candidate assessment (checked 2026-11-21)

| Provider / model family | Public evidence | Decision |
|---|---|---|
| Google Gemini Developer API | Google's pricing page lists eligible Gemini models with free input and output tokens on the Free tier. The free tier has limited model access and quotas. | **Candidate A.** Confirm exact model availability, key/project Free-tier status, and quota in AI Studio before freeze. Do not enable grounding or any separately billed tool. |
| Groq-hosted OpenAI GPT-OSS 120B | Groq's public rate-limit page lists openai/gpt-oss-120b and a base table of 30 RPM, 1,000 RPD, 8K TPM and 200K TPD. The model page lists paid per-token pricing, so the rate-limit table alone does not prove this account has free access. | **Candidate B, conditional.** Verify the account dashboard explicitly shows Free access and no billing requirement before use. |
| OpenRouter free model variants | OpenRouter lists model variants with $0 token prices. Free variants are capped at 20 RPM and 50 requests/day without a credit purchase; failed requests count toward the daily cap. The model catalog can change. | **Candidate C, fallback only.** Use only an exact pinned model ID ending in :free. At 50 requests/day, 630 requests require at least 13 quota days before retries or other usage. |
| Cerebras Inference | Cerebras advertises a $0 Free tier with lower rate limits. Public documentation does not provide a sufficiently clear, current quota/model-entitlement guarantee for the exact candidate model. | **Unqualified.** Do not freeze until exact model availability, free entitlement, quota, and request behavior are confirmed for this account. |
| Mistral API | Mistral states Free mode does not include API access; API keys and API usage require billing activation and pay-as-you-go. | **Excluded** under the zero-spend constraint. |

## Candidate model-family separation
The intended three-family design is Google Gemini (Google), OpenAI GPT-OSS (OpenAI model family hosted by Groq), and a third independently versioned family provisionally selected from an exact OpenRouter :free model only if it can be pinned and remain available throughout the run. Provider count is not model-family count. Groq and OpenRouter are inference providers, not model families. Different family labels do not prove independent training data, ownership, infrastructure or failure modes.

## Required qualification gate before freezing
For each candidate, perform only one minimal development smoke request:
1. Confirm the account's current plan/tier and that billing is not activated or required.
2. Confirm exact model ID and model-family owner from the provider's current catalogue.
3. Confirm endpoint, authentication, JSON response mode, context window and output cap.
4. Record published limits and account dashboard's effective limits.
5. Send one short harmless synthetic-input smoke request.
6. Record response, request ID, returned model ID, usage, timestamp and provider headers; do not infer missing usage.
7. Confirm no paid fallback, automatic model routing, search grounding or metered tool is enabled.
8. Only then freeze exact model IDs, endpoint identities, settings and protocol version. Any later substitution requires a new protocol version and fresh holdout.

If a candidate cannot pass these checks, it remains excluded. Do not use a paid fallback.

## Workload and reproducibility caveats
- The 630-call figure is a separate frozen workload estimate from the harness currently in this branch. Reconcile it against the actual condition/task expansion before execution; retries and smoke requests add traffic.
- OpenRouter's 50 requests/day free-variant limit means 630 requests cannot be represented as a one-day run through that route.
- Groq's public rate-limit table is not proof of this account's Free-tier entitlement. Check the account's Limits page and billing state.
- Gemini free-tier quotas are model- and project-specific and may change. Free-tier data-use terms differ from paid-tier terms; synthetic benchmark inputs are required.
- A zero-cost plan is not yet an executable frozen protocol. The exact third family and account entitlements remain to be qualified.

## Scope discrepancy to resolve before a new freeze
The current PROTOCOL.md and harness in this repository branch describe generated benchmark v0.4 with 700 HIGH-risk cases, a 60/20/20 split by pair, and development/validation/final-holdout layouts. The separate historical description of 30 gold cases (C0–C14), 90 proposer calls, 540 verifier calls and a 28-call dry run is not represented by the current example manifest/config files inspected for this note.

These must not be merged into one protocol by assumption. Before any new run, identify the authoritative 30-case task set and exact frozen manifests, or explicitly state that the current 700-case harness is the active Experiment 3 protocol. No holdout or scored model run is authorized by this note.

## Sources checked (2026-11-21)
- Google Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing
- Gemini OpenAI-compatible endpoint: https://ai.google.dev/gemini-api/docs/openai
- Groq rate limits: https://console.groq.com/docs/rate-limits
- Groq GPT-OSS 120B model page: https://console.groq.com/docs/model/openai/gpt-oss-120b
- Cerebras pricing: https://inference-docs.cerebras.ai/support/pricing
- Mistral usage limits: https://docs.mistral.ai/admin/billing-usage/usage-limits
- OpenRouter free models and limits: https://openrouter.ai/collections/free-models/

This is a provider-qualification artifact, not an audit report, benchmark result, or claim that any real-model experiment has run.