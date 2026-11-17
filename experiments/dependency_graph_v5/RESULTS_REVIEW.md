# Dependency-Graph v5 Results Review

**Validation run:** [GitHub Actions #44167634191](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44167634191)  
**Benchmark:** v0.4, 700 HIGH-risk cases per scenario  
**Scenarios:** 16  
**Policies:** 4  
**Rows:** 44,800 case-policy-scenario rows  
**Artifact:** `ega-dependency-graph-v5` (artifact ID `14365958156`)

## 1. Aggregate policy comparison

| Policy | Threshold | Unsafe ACT | Safe-ACT coverage across 1,600 safe cases | Graph-validation rejections |
|---|---:|---:|---:|---:|
| K2 key-unique | 2-of-3 | 700 | 100% | 0 |
| F2 field-distinct | 2-of-3 | 650 | 100% | 0 |
| F3 field-distinct | 3-of-3 | 50 | 93.75% | 0 |
| G2 graph-aware | 2-of-3 | 150 | 87.5% | 1,800 |

The aggregate counts are deterministic results over 16 × 700 synthetic cases. The 1,600 safe cases are the 100 safe cases in each scenario; the scenario transformations do not change the safe-case denominator for v5.

## 2. Scenario findings

- **Honest baseline and one witness compromised:** all four policies produce zero unsafe ACT and 100% safe-case coverage.
- **Two witnesses compromised:** K2, F2 and G2 each produce 50 unsafe ACT decisions in C4 consistent-but-wrong; F3 rejects the two-witness false quorum and retains 100% safe coverage.
- **All three witnesses compromised:** every policy produces 50 unsafe ACT decisions in C4. A 3-of-3 threshold cannot protect against full-roster compromise.
- **Direct shared administrative domain:** K2 produces 50 unsafe ACT decisions. F2 and G2 detect the shared administrative field and block the C4 false quorum. F3 rejects all cases because its all-three-supporter rule cannot establish three distinct administrative domains, producing 100% false blocking in this scenario.
- **Seven hidden shared-dependency scenarios** (parent/control, identity provider, KMS, firmware/build, acquisition gateway, physical measurement source, upstream feed): K2 and F2 each produce 50 unsafe ACT decisions per scenario because direct labels are distinct. F3 rejects the two-witness false quorum. G2 rejects the 50 matching C4 cases because the signed graph declares the common ancestor, while retaining 100% safe-case coverage by selecting a different independent matching pair when all three witnesses agree.
- **Incomplete dependency manifest:** G2 rejects the 50 C4 cases that depend on the incomplete witness manifest and retains safe coverage by using the remaining valid pair.
- **Missing/cyclic graph structure and graph-signature tampering:** G2 fails closed on all 700 cases in each scenario (700 graph-validation rejections per scenario), causing 100% false blocking there. K2/F2 do not consume the graph and each produces 50 unsafe C4 ACT decisions; F3 rejects those two-witness cases.
- **Registry signing-key compromise:** the attacker obtains the existing registry private key while the verifier retains the original pinned public key. Two colluding witnesses share a true parent, the third witness remains honest, and the attacker signs a graph that omits the shared parent. K2/F2/G2 each produce 50 unsafe ACT decisions in C4; F3 blocks those false actions and retains 100% safe-case coverage. The graph-aware policy cannot recover a dependency that its compromised graph authority has hidden.

## 3. Graph rejection accounting

G2 records 1,800 graph-validation rejections across the benchmark:
- 7 declared shared-ancestor scenarios × 50 C4 cases = 350;
- incomplete dependency manifest = 50;
- unresolved/cyclic graph structure = 700;
- invalid graph signature/schema = 700.

The case-level CSV separately records the ground-truth shared dependency identifier, whether the signed graph declares that dependency, and whether the registry-root scenario omits it. This prevents the signed graph's statement from being confused with the synthetic ground-truth attack label.

## 4. Interpretation

The experiment supports a narrow result: **direct identity-field diversity is insufficient when witnesses share a declared transitive dependency; graph-aware admission blocks those modeled collusions when the signed graph is accurate.** It also exposes the graph's trust assumption: a compromised registry signing key can sign a graph that omits a true shared parent, allowing a graph-aware 2-of-3 policy to be fooled.

The 3-of-3 policy is a useful threshold sensitivity comparator, not a universal solution. It blocks two-witness collusion but cannot stop full-roster compromise and can reduce availability when all three supporters must be mutually distinct. G2 preserves safe coverage across the declared hidden-dependency scenarios, but loses availability under graph-structure and graph-integrity failures.

## 5. Claim boundary and limitations

- All identities, dependency graphs, source values and attacks are synthetic.
- A signed dependency graph authenticates registry assertions, not their real-world completeness or truth.
- Distinct dependency nodes do not prove independent ownership, operation, hardware or data.
- The registry signing-key scenario assumes compromise of the existing issuer private key while the original public key remains pinned; the attacker can enroll two attacker-controlled witness keys and sign a graph omitting a true common parent.
- The graph is a declared static dependency model; it does not discover hidden dependencies from operational telemetry.
- The experiment does not implement production PKI, KMS/HSM, hardware attestation, distributed graph reconciliation, durable revocation, or atomic commit.
- Deterministic counts are not real-world probabilities or production-security evidence.

## 6. Integrity and reproduction

Pinned manifest: [results/dependency_graph_v5/manifest-44167634191.json](../../results/dependency_graph_v5/manifest-44167634191.json).

Output hashes:
- `dependency_graph_v5_cases.csv`: `7b2f0c9b25e95a7fded1b58bf7dbca78553694e7a307b4018c3ac859700e4816`
- `dependency_graph_v5_summary.csv`: `3171c16490ed59aa0fcea21bc59af0a34d18f036da0a758488f8c7ce88bdfdcd`

Reproduce with:

```bash
python -m unittest tests.test_dependency_graph_v5 -v
python scripts/run_dependency_graph_v5.py
```

The full workflow also regenerates benchmark v0.4, runs v1/v2/v3/v4 and document-root-attestation experiments, reproduces publication tables from checked-in historical result files, and compiles the manuscript.
