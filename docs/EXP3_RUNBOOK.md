# Experiment 3 Execution Runbook

This runbook is the operational checklist for the first external-model evaluation. It exists to keep the study frozen and auditable.

## Phase A — freeze artifacts

1. Regenerate benchmark:
   ```bash
   python scripts/generate_benchmark.py
   python scripts/verify_benchmark.py
   ```
2. Generate frozen paired split and rendered tasks:
   ```bash
   python scripts/exp3_prepare.py
   ```
3. Commit the generated `data/exp3/split_manifest.json` and its SHA-256 file before inspecting held-out test results.
4. Record the exact Git commit used for the run.
5. Freeze prompt templates, schemas, model-role assignments, decoding settings, retry policy, and maximum cost.

Expected split from the current 500-pair benchmark design is approximately 90 dev pairs, 90 validation pairs, and 320 held-out test pairs; the generated manifest is authoritative.

## Phase B — development only

Use only the **dev** split to:

- debug provider adapters;
- fix JSON parsing bugs;
- ensure no hidden fields leak into prompts;
- test retry/backoff behavior;
- verify logging;
- verify that model responses cannot overwrite benchmark metadata.

Do not use dev performance to claim a result.

## Phase C — validation

Use only the **validation** split to finalize:

- prompt wording;
- parser behavior;
- allowed retry count;
- controller wiring;
- any calibration mapping that is part of the preregistered analysis.

After validation is complete, tag the exact experiment configuration. No threshold/prompt/policy changes are permitted after held-out test inspection.

## Phase D — held-out test collection

For each case and model role:

1. read only the rendered task record;
2. construct the frozen system/user prompts;
3. record prompt hashes;
4. call the assigned model;
5. append the raw response and metadata to an immutable JSONL log;
6. parse into the frozen schema;
7. retain failures/refusals/timeouts/malformed outputs as records;
8. never expose `family`, `fault`, `ground_truth`, `safe_to_act`, or hidden labels to the model.

Validate every output log:

```bash
python scripts/exp3_validate_outputs.py path/to/run.jsonl
```

## Phase E — controller evaluation

A separate deterministic transformation should convert model outputs into controller-observable evidence and generate one decision per `(case_id, policy)`.

The decision log must contain:

```json
{"case_id":"...","policy":"Evidence Gate v1","decision":"ACT"}
```

Allowed decisions are:

- `ACT`
- `VERIFY`
- `REQUEST_EVIDENCE`
- `DEFER`
- `ESCALATE`

No policy should be allowed to read hidden ground truth.

## Phase F — scoring

Score only after the full held-out run is complete:

```bash
python scripts/exp3_score.py \
  --decisions results/exp3/decisions.jsonl \
  --split test \
  --out results/exp3/summary.csv
```

The scorer reports:

- HIGH-risk incorrect-action count/rate;
- 95% Wilson interval;
- false authorization;
- false blocking;
- coverage;
- verification/request/defer/escalation rates;
- paired exact McNemar comparisons on the primary HIGH-risk error outcome.

## Phase G — required diagnostic analyses

Before interpreting results, produce:

1. failure-family breakdown;
2. severity breakdown;
3. same-model vs cross-family verifier co-failure;
4. confidence calibration;
5. model-family holdout;
6. document-format OOD results;
7. prompt-perturbation results;
8. provenance-attack results;
9. trust-root compromise results where applicable;
10. cost/latency/coverage trade-off table.

## Phase H — falsification check

Before writing a positive conclusion, answer:

- Does a simpler baseline achieve equal/lower unsafe-action rate at similar coverage and cost?
- Does cross-family verification actually reduce co-failure?
- Do apparent gains disappear on OOD formats?
- Is the richer gate merely escalating more cases rather than authorizing more safely?
- Do failures concentrate in a small number of blind-spot families?

If the answer weakens the original hypothesis, report that directly.

## Phase I — manuscript update

Only after the test results are frozen:

- replace prospective Experiment 3 language with measured results;
- add raw numerators/denominators and confidence intervals;
- add negative/null findings;
- update `docs/CLAIMS_AND_EVIDENCE.md` evidence levels;
- keep synthetic Experiments 1A–2E distinct from external-model evidence;
- do not claim deployment or real-domain validation.

## Provider neutrality

This repository intentionally does not hard-code a single commercial provider. Provider adapters should be small, isolated modules that emit the same append-only record schema. This reduces the chance that one SDK or model family becomes part of the scientific definition of the experiment.
