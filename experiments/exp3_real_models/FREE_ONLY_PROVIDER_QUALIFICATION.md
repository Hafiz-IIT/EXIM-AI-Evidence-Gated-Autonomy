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

## Authoritative source recovery and correction (2026-11-21)

The original frozen Experiment 3 documents have now been recovered from the Notion research workspace:

- Frozen Real-Model Protocol: https://app.notion.com/p/3de0a218bb3d8117a22cf31b037d5306
- Primary Deterministic Run Manifest: https://app.notion.com/p/3de0a218bb3d81789fe8d731007dc2e5
- Dry-Run Manifest v1 — 28 Calls: https://app.notion.com/p/3de0a218bb3d81699d46e0b0ded894f3
- Prompt Pack v1: https://app.notion.com/p/3de0a218bb3d81689cfdfb876d2051c7
- Model & Provider Matrix v1 — Zero-Cost First: https://app.notion.com/p/3de0a218bb3d81259811e9e6d12a1a65
- Execution Harness Contract v1: https://app.notion.com/p/3de0a218bb3d81898fded057b1e38aad
- Statistical Analysis Plan v1: https://app.notion.com/p/3de0a218bb3d816db032d6ec1ee8070b

The Experiment 3 Case Registry was queried directly. It contains exactly 30 frozen rows: one LOW and one HIGH case for each of C0–C14 (15 condition families × 2 consequence regimes). Every condition/consequence cell has exactly one row and its Frozen field is checked. The original case bank is therefore confirmed, not merely remembered.

### Corrected primary workload

| Stage | Frozen unit | Calls |
|---|---|---:|
| 3A Proposers | 30 cases × 3 proposer families | 90 |
| 3B Same-family single verifier | 30 × 3 | 90 |
| 3C Cross-family single verifier | 30 × 3 | 90 |
| 3D Same-family verifier pair | 30 × 3 × 2 roles | 180 |
| 3E Heterogeneous verifier pair | 30 × 3 × 2 non-proposer families | 180 |
| **Primary total** | **90 proposer + 540 verifier** | **630** |

Proposer outputs are generated once per (case, proposer family) and reused across verifier setups. Controller comparisons B1–B8 reuse identical raw outputs and add no model calls.

### Dry-run manifest compatibility warning

The recovered 28-call DR-01…DR-06 manifest is disposable mechanical validation only and is never part of the 630 scored calls. However, its historical provider codes are G = Gemini, M = Mistral, O = Groq, and its rows explicitly route calls through Mistral. **Do not execute this manifest as written.** Mistral API requires billing activation under the currently checked policy, which violates the zero-spend constraint. Preserve historical v1; create a versioned replacement dry-run manifest and provider matrix only after a third genuinely free model family is qualified. Do not silently remap Mistral rows to another provider.

### The GitHub branch contains a different benchmark design

The current `experiments/exp3_real_models/PROTOCOL.md` and harness in this branch implement generated benchmark v0.4: 700 HIGH-risk cases across 14 synthetic failure families, pair-stratified 60/20/20 splits, extractor + verifier A/B roles, and an Evidence Gate v1 extraction/verifier schema.

The recovered frozen Notion Experiment 3 is a distinct study: 30 gold cases across C0–C14 × LOW/HIGH, 90 proposer + 540 verifier calls, proposer/V1/V2/recovery prompts, and B1–B8 policy comparisons. The current GitHub harness does not implement that recovered manifest or prompt contract. These designs must not be combined or described as the same run. Keep the 700-case v0.4 harness separate unless a deliberate, versioned scientific decision supersedes one design. Do not overwrite the frozen Notion v1 source assets.

### Current zero-cost qualification status

Gemini and Groq-hosted GPT-OSS remain conditional candidates. Mistral is excluded. OpenRouter is only a possible fallback route, not yet a qualified third family: an exact :free model ID, family owner, account access, stability, and no-paid-fallback behavior have not been established. Cerebras also remains unqualified. Therefore the frozen three-family requirement is **not yet satisfied**, and no scored run or 28-call dry run should start.

### Revised next steps

1. Identify and qualify an exact third model family on a truly free account tier.
2. Create a versioned zero-cost provider matrix and replacement 28-call dry-run manifest with no Mistral dependency; leave historical v1 unchanged.
3. Implement a dedicated C0–C14 proposer/V1/V2/recovery runner with zero-spend fail-closed behavior. Do not relabel the existing 700-case harness.
4. Run the replacement dry run only after all three providers are demonstrably free for this account and all mechanical checks are ready.
5. Freeze and execute the 630-call primary manifest only after dry-run acceptance, exact model identities, prompt hashes, quota evidence, and zero-cost safeguards are verified.

This reconciliation is a research protocol artifact, not a portfolio audit, benchmark result, or claim that real-model calls have occurred.


## Third-family candidate qualification — Cloudflare Workers AI / Z.ai GLM-4.7-Flash (2026-11-21)

**Decision: public-policy qualified candidate C; account-level qualification remains pending.** This is the strongest third-family candidate found in this pass and is preferable to a dynamic OpenRouter :free route for reproducibility.

### Exact identity and endpoint

- Model developer/family: Z.ai (Zhipu AI), GLM family.
- Exact pinned model ID: `@cf/zai-org/glm-4.7-flash`.
- Inference provider: Cloudflare Workers AI.
- OpenAI-compatible base URL: `https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1`.
- Chat endpoint: `/chat/completions`.
- Model documentation lists a 131,072-token context window, text generation, and OpenAI-compatible Chat Completions support.
- Do not confuse this with GLM-5.2/5.3 variants; the official Cloudflare changelog explicitly lists GLM-4.7-Flash among models still accessible on Workers Free when certain larger models were moved behind Workers Paid.

### Zero-cost evidence

Cloudflare's official Workers AI pricing page (updated 2026-11-18) states:
- Workers Free includes 10,000 Neurons per day at no charge.
- Limits reset daily at 00:00 UTC.
- On Workers Free, exceeding the free allocation causes further operations to fail; it does not automatically charge for overage.
- Exceeding the free allowance requires upgrading to Workers Paid for paid overage. **Do not upgrade.**
- The pricing page lists GLM-4.7-Flash at approximately 5,500 Neurons per million input tokens and 36,400 Neurons per million output tokens (pricing page's current model table; verify exact live values again before execution).

Cloudflare's official July 28, 2026 model-access changelog explicitly says `@cf/zai-org/glm-4.7-flash` remains available on Workers Free, while `glm-5.2` and selected other large models require Workers Paid. This is the critical free-plan eligibility evidence.

### Qualification result

| Gate | Result |
|---|---|
| Distinct model family from Google Gemini | **Pass** — Z.ai / GLM |
| Distinct model family from OpenAI GPT-OSS | **Pass** — Z.ai / GLM |
| Exact stable model ID published | **Pass** — `@cf/zai-org/glm-4.7-flash` |
| Officially listed on Workers Free | **Pass (public policy)** |
| OpenAI-compatible Chat Completions documented | **Pass** |
| Published free daily allowance | **Pass** — 10,000 Neurons/day |
| User's Cloudflare account is on Workers Free | **Not yet verified** |
| User's account has no paid billing/usage mode | **Not yet verified** |
| Minimal synthetic smoke call and returned model identity | **Not run** |
| No-paid-fallback behavior verified on user's account | **Not yet verified** |

Thus the study now has three public-policy candidate families: Google Gemini, OpenAI GPT-OSS (hosted by Groq), and Z.ai GLM-4.7-Flash (hosted by Cloudflare). This resolves the *public provider/model-family discovery* blocker, but does not authorize a dry run until the account checks and smoke tests pass.

### Account-side safety gate before first request

In Cloudflare dashboard, confirm Workers plan is **Free**, not Paid; do not add a payment method, switch plans, or enable paid AI Gateway credits. Confirm Workers AI is enabled and the account shows the free daily neuron allowance. Record the account's usage/billing mode privately. Use only the exact model ID above. Set a strict short output cap, disable tools and streaming for the initial smoke, and send only synthetic text. If the account prompts for an upgrade or payment method, stop immediately. Do not retry through a different model or provider automatically.

The Cloudflare token should be stored locally in an environment variable and scoped to the minimum Workers AI permissions needed. Never paste the token into chat or commit it. The account ID and token remain private.

### Remaining compatibility work

The current GitHub harness assumes a generic OpenAI-compatible Chat Completions endpoint with an API key environment variable. Cloudflare's documented endpoint is compatible, but requires an account-specific base URL. Before integrating it into the dedicated C0–C14 runner, test that the provider adapter preserves the returned exact model ID, usage fields, response IDs, errors and relevant headers. Record Cloudflare's account-specific endpoint separately from the model-family label.

### Official sources

- Cloudflare Workers AI pricing (updated 2026-11-18): https://developers.cloudflare.com/workers-ai/platform/pricing/
- Cloudflare model access changelog (2026-07-28): https://developers.cloudflare.com/changelog/post/2026-07-28-models-require-workers-paid/
- Cloudflare GLM-4.7-Flash model page: https://developers.cloudflare.com/workers-ai/models/glm-4.7-flash/
- Cloudflare OpenAI-compatible API endpoints: https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/
- Z.ai model family identity and Cloudflare's provider attribution are shown on the official model page.

**Updated status:** three distinct model-family candidates are now identified and publicly documented. Account entitlement, smoke validation, replacement dry-run manifest, and the dedicated 630-call runner remain pending. No API request was made and no spend occurred in this qualification pass.
