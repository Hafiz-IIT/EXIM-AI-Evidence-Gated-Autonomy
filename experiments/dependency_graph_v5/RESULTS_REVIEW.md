# Dependency-Graph v5 Results Review

**Validation run:** [GitHub Actions #44163544687](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/actions/runs/44163544687)  
**Experiment status:** v5 regression tests, experiment runner and artifact upload passed; the full manuscript/reconstruction workflow was still running when this review was prepared.  
**Benchmark:** v0.4, 700 HIGH-risk cases per scenario  
**Policies:** 4  
**Scenarios:** 14  
**Rows:** 14 × 4 × 700 = 39,200  
**Artifact:** `ega-dependency-graph-v5`  
**Artifact ID:** `14363334448`  
**Source commit:** `35f136e0f5ccf587a888582943e56fc91af2cc48`

## 1. Main results

Unsafe ACT counts by policy:

| Scenario | K2 key-unique | F2 field-distinct 2-of-3 | F3 field-distinct 3-of-3 | G2 graph-aware 2-of-3 |
|---|---:|---:|---:|---:|
| Honest baseline | 0 | 0 | 0 | 0 |
| One witness compromised | 0 | 0 | 0 | 0 |
| Two witnesses compromised | 50 | 50 | 0 | 50 |
| All witnesses compromised | 50 | 50 | 50 | 50 |
| Direct shared admin | 50 | 0 | 0 | 0 |
| Hidden shared parent | 50 | 50 | 0 | 0 |
| Hidden shared identity provider | 50 | 50 | 0 | 0 |
| Hidden shared KMS | 50 | 50 | 0 | 0 |
| Hidden shared firmware/build | 50 | 50 | 0 | 0 |
| Hidden shared upstream feed | 50 | 50 | 0 | 0 |
| Incomplete dependency manifest | 50 | 50 | 0 | 0 |
| Missing dependency parent | 50 | 50 | 0 | 0 |
| Graph signature tampering | 50 | 50 | 0 | 0 |
| Registry-root compromise | 50 | 50 | 50 | 50 |

Safe-ACT coverage for the same scenarios:

| Scenario | K2 | F2 | F3 | G2 |
|---|---:|---:|---:|---:|
| Honest baseline | 100% | 100% | 100% | 100% |
| One witness compromised | 100% | 100% | 100% | 100% |
| Two witnesses compromised | 100% | 100% | 100% | 100% |
| All witnesses compromised | 100% | 100% | 100% | 100% |
| Direct shared admin | 100% | 100% | 0% | 100% |
| Hidden shared parent / IDP / KMS / firmware / upstream | 100% | 100% | 100% | 100% |
| Incomplete dependency manifest | 100% | 100% | 100% | 100% |
| Missing dependency parent | 100% | 100% | 100% | 0% |
| Graph signature tampering | 100% | 100% | 100% | 0% |
| Registry-root compromise | 100% | 100% | 100% | 100% |

The benchmark has 100 safe cases per scenario. In hidden-dependency scenarios, graph-aware admission preserves safe coverage because a third witness with disjoint ancestry remains available; in C4 consistent-but-wrong, only the two compromised witnesses match the false document-derived value, and their shared ancestor prevents them forming a graph-aware quorum.

## 2. Findings

### 2.1 Flat labels miss transitive common dependencies

K2 and F2 authorize 50 unsafe C4 actions in each hidden shared-parent, shared-IDP, shared-KMS, shared-firmware and shared-upstream scenario. The witness IDs, keys and direct source/admin/gateway labels are distinct, but the signed dependency graph contains a common ancestor.

G2 blocks those unsafe actions by checking transitive ancestor intersections among the matching supporters. It preserves 100% safe-ACT coverage in these scenarios because the third witness remains independent and agrees on the safe cases.

### 2.2 Strict 3-of-3 and graph-aware 2-of-3 solve different problems

F3 blocks two-witness collusion even when the two compromised witnesses have disjoint ancestry. However, it requires all three witnesses to agree and loses all safe coverage in the direct shared-admin scenario, where a valid pair involving the third witness exists.

G2 permits a 2-of-3 quorum when it can select two directly distinct supporters with disjoint transitive ancestry. It therefore detects declared common dependencies while retaining the ability to select a valid independent pair. It does **not** prevent independent two-witness collusion: G2 still produces 50 unsafe ACTs in the ordinary two-witness-compromise scenario.

### 2.3 Graph integrity and trust-root compromise remain critical

G2 fails closed when a dependency parent is unresolved or the graph signature is tampered with. In both scenarios it blocks all 100 safe cases (100% false-block rate). This is a deliberate fail-closed result, not an acceptable availability target.

When the registry root is compromised, the attacker can sign source credentials and a graph that omits the true shared dependency. G2 then produces 50 unsafe ACTs, just like the flat-field policies. A signed graph authenticates the registry's assertion; it does not prove that the graph is complete or true.

### 2.4 Full-roster compromise remains unsolved

All policies authorize 50 unsafe C4 actions when all three witnesses are compromised and agree on the false value. No threshold or ancestry policy can recover truth if every accepted source and the trust metadata are controlled by the attacker.

## 3. Aggregate comparison

Across 9,800 case-policy-scenario rows per policy (14 scenarios × 700 cases):

| Policy | Unsafe ACT total | Safe-ACT coverage over 1,400 safe case-scenario instances |
|---|---:|---:|
| K2 key-unique | 600 | 100.0% |
| F2 field-distinct 2-of-3 | 550 | 100.0% |
| F3 field-distinct 3-of-3 | 100 | 92.9% |
| G2 graph-aware 2-of-3 | 150 | 85.7% |

These aggregate counts intentionally repeat the same 700 benchmark cases across attack scenarios; they are comparison totals, not estimates of deployment risk. G2's lower aggregate safe coverage is driven by fail-closed rejection of all cases when the graph itself is structurally incomplete or its signature is invalid. In the hidden shared-dependency scenarios, G2 has 100% safe coverage.

## 4. Claim boundary and limitations

- All identities, dependency graphs, source values, signatures and attacks are synthetic.
- The graph is signed by the same registry trust root as source credentials; registry compromise can falsify both.
- Dependency nodes and edges are registry assertions. Their signature does not prove actual corporate ownership, operational control, hardware/software ancestry or upstream data lineage.
- The graph-aware rule checks pairwise ancestor intersection; it does not implement the EFD structural-cut metric and does not claim a new general quorum theory.
- The graph-aware policy only detects shared dependencies that are represented in the graph.
- Independent collusion, full-roster compromise, semantic falsehood by an otherwise independent source, and trust-root compromise remain residual risks.
- The experiment uses a v1 action gate and v3 bounded recovery as the downstream policy. It is not a standalone controller.
- No production PKI, KMS/HSM custody, cloud-provider audit, hardware attestation, SBOM/build provenance verification, secure acquisition or atomic commit is implemented.
- Counts are deterministic synthetic outcomes, not real-world probabilities or production-security evidence.

## 5. Reproduction and integrity

Run:

```bash
python -m unittest discover -s tests -v
python scripts/run_dependency_graph_v5.py
```

The artifact manifest records:

- `dependency_graph_v5_cases.csv`: `b7b7e141fb7e89ad90384242024dd4113f853fbc9f440e16a48084a068d5f4ca`
- `dependency_graph_v5_summary.csv`: `63ab93fe9fe70208f92f68fd056ec8d59e7d4ca7daa3a260c82cf1aa4341b891`

## 6. Interpretation

The experiment supports a narrow, falsifiable result: **direct identity and administrative-domain diversity can miss declared transitive common dependencies; a signed dependency-ancestry check detects those modeled overlaps when the graph is complete and the trust root is honest.** It does not prove real-world independence. EFD and ARP already address the general theory, so the contribution is an EXIM-specific benchmark comparison across key-only, field-distinct and graph-aware admission policies.
