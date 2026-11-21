# Real-Model Experiment Protocol — Experiment 3

Status: harness and blinded task preparation implemented; no external model/API run is claimed.

The frozen protocol and executable harness now live in experiments/exp3_real_models/. The harness supports OpenAI-compatible Chat Completions endpoints and evaluates Evidence Gate v1 only. It constructs public model tasks without case IDs, pair IDs, family labels, fault labels, ground truth, safe_to_act or fingerprints. The private evaluation map is stored separately and never sent to providers.

The deterministic split is by underlying pair ID within family (60% development, 20% validation, 20% final holdout). Final holdout has both in-distribution and document-layout OOD renderings. The harness preserves exact model IDs and family labels for extractor and two verifier roles; family labels are not treated as proof of independence.

Final holdout requires frozen benchmark, prompt and model/condition hashes plus explicit CLI confirmation. The exact historical v2/v3 controller source remains unavailable; no v2/v3 model evaluation is implemented until issue #3 is resolved.

See experiments/exp3_real_models/PROTOCOL.md and README.md for execution and artifact requirements.