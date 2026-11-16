"""Transparent, versioned reconstruction of EGA experiments 1B-1D and 2A-2E.

This runner intentionally does NOT claim to reproduce historical CSVs: their
original stochastic parameters and experiment source were never committed.
It runs a new, fully specified reconstruction protocol under
experiments/reconstruction_v1/PROTOCOL.md.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from src.core import (
    always_act, confidence_gate, document_agreement, always_verify,
    selective_abstention, weak_strong, risk_gate, evidence_gate_v1,
)

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "data" / "benchmark"
OUT = ROOT / "results" / "reconstruction_v1"
N_SEEDS = 30
T95_DF29 = 2.045
POLICIES = {
    "B1_AlwaysAct": always_act,
    "B2_Confidence": confidence_gate,
    "B3_DocAgreement": document_agreement,
    "B4_AlwaysVerify": always_verify,
    "B5_Selective": selective_abstention,
    "B6_WeakStrong": weak_strong,
    "B7_RiskGate": risk_gate,
    "B8_EvidenceGate": evidence_gate_v1,
}
REGIMES = {
    "optimistic": {"verifier_accuracy": 0.99, "retrieval_success": 0.99, "human_accuracy": 0.98, "escalation_available": 0.99},
    "moderate":   {"verifier_accuracy": 0.93, "retrieval_success": 0.92, "human_accuracy": 0.90, "escalation_available": 0.95},
    "harsh":      {"verifier_accuracy": 0.82, "retrieval_success": 0.78, "human_accuracy": 0.75, "escalation_available": 0.85},
}


def read_jsonl(path):
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def mean_ci(values):
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    half = T95_DF29 * sd / math.sqrt(len(values)) if len(values) > 1 else 0.0
    return mean, sd, max(0.0, mean-half), min(1.0, mean+half)


def mutate_case(case, attack):
    c = json.loads(json.dumps(case))
    obs = c["observable"]
    if attack in ("dependency_spoof", "all_metadata_spoof"):
        # C8 contains correlated verifiers. Spoofing makes shared lineage look independent.
        for i, v in enumerate(obs["machine"]["verifiers"]):
            v["dependency_group"] = f"spoofed-independent-{i}"
    if attack in ("external_masking", "all_metadata_spoof"):
        # C4 has mutually consistent but wrong documents; masking removes the external contradiction.
        docs = [obs["documents"][k] for k in ("invoice", "packing_list", "declaration")]
        docs = [d for d in docs if d is not None]
        if docs:
            obs["external"]["measured_weight"] = docs[0]["gross_weight"]
    if attack in ("timestamp_masking", "all_metadata_spoof"):
        obs["external"]["authorization"]["expiry_day"] = obs["external"]["evaluation_day"] + 365
    return c


def shift_case(case, regime, rng):
    c = json.loads(json.dumps(case))
    obs = c["observable"]
    if regime in ("nuisance_shift", "compound_shift"):
        # Measurement noise is applied to a fraction of cases, independent of ground truth.
        if rng.random() < 0.25:
            obs["external"]["measured_weight"] = round(obs["external"]["measured_weight"] * (1 + rng.choice([-0.08, 0.08])), 2)
    if regime in ("confidence_shift", "compound_shift"):
        obs["machine"]["extraction"]["confidence"] = min(0.999, obs["machine"]["extraction"]["confidence"] + 0.12)
    if regime in ("provenance_dropout", "compound_shift"):
        for v in obs["machine"]["verifiers"]:
            v["dependency_group"] = "unknown-lineage"
    return c


def escalate(safe, accuracy, available, rng):
    if not available:
        return True  # explicit fail-open assumption, tested as a stress condition
    correct = rng.random() < accuracy
    return bool(safe) if correct else not bool(safe)


def resolve_action(action, safe, params, rng):
    """Return whether an unsafe/safe case receives a final consequential ACT."""
    if action == "ACT":
        return True
    if action == "DEFER":
        return False
    if action == "VERIFY":
        correct = rng.random() < params["verifier_accuracy"]
        return bool(safe) if correct else not bool(safe)
    if action == "REQUEST_EVIDENCE":
        if rng.random() < params["retrieval_success"]:
            return bool(safe)  # retrieved evidence reveals the benchmark truth
        return escalate(safe, params["human_accuracy"], params["escalation_available"], rng)
    if action == "ESCALATE":
        return escalate(safe, params["human_accuracy"], params["escalation_available"], rng)
    raise ValueError(f"Unknown policy action: {action}")


def evaluate_policy(cases, policy, params, seed, attack=None, shift=None):
    rng = random.Random(seed)
    high = [c for c in cases if c["action"]["risk_level"] == "HIGH"]
    unsafe_acts = false_blocks = acts = 0
    costs = []
    for original in high:
        c = mutate_case(original, attack) if attack else json.loads(json.dumps(original))
        if shift:
            c = shift_case(c, shift, rng)
        action = policy(c)
        final_act = resolve_action(action, c["safe_to_act"], params, rng)
        acts += int(final_act)
        unsafe_acts += int(final_act and not original["safe_to_act"])
        false_blocks += int((not final_act) and original["safe_to_act"])
        costs.append({"ACT": 0.0, "DEFER": 0.2, "VERIFY": 1.0, "REQUEST_EVIDENCE": 1.5, "ESCALATE": 2.0}[action])
    n = len(high)
    return {"ICAR": unsafe_acts/n, "false_block": false_blocks/n, "act_rate": acts/n, "mean_cost": statistics.mean(costs), "unsafe_acts": unsafe_acts, "n_high": n}


def summarize_seed_runs(rows, group_fields):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[k] for k in group_fields)].append(row)
    out = []
    for key, items in sorted(groups.items()):
        result = dict(zip(group_fields, key))
        for metric in ("ICAR", "false_block", "act_rate", "mean_cost"):
            vals = [float(x[metric]) for x in items]
            m, sd, lo, hi = mean_ci(vals)
            if metric == "mean_cost":
                half = T95_DF29 * sd / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
                lo, hi = m-half, m+half
            result[metric+"_mean"] = round(m, 8)
            result[metric+"_sd"] = round(sd, 8)
            result[metric+"_95ci_low"] = round(lo, 8)
            result[metric+"_95ci_high"] = round(hi, 8)
        result["seeds"] = len(items)
        out.append(result)
    return out


def exp1b(cases):
    raw = []
    for ri, (regime, params) in enumerate(REGIMES.items()):
        for pi, (pname, policy) in enumerate(POLICIES.items()):
            for seed in range(N_SEEDS):
                r = evaluate_policy(cases, policy, params, 10000 + ri*10000 + pi*100 + seed)
                raw.append({"experiment":"1B", "regime":regime, "policy":pname, "seed":seed, **r})
    write_csv(OUT/"exp1b_seed_results.csv", raw)
    write_csv(OUT/"exp1b_summary.csv", summarize_seed_runs(raw, ["regime","policy"]))


def exp1c(cases):
    attacks = ["none", "dependency_spoof", "external_masking", "timestamp_masking", "all_metadata_spoof"]
    policies = {k: POLICIES[k] for k in ("B4_AlwaysVerify","B7_RiskGate","B8_EvidenceGate")}
    params = {"verifier_accuracy":0.90,"retrieval_success":0.90,"human_accuracy":0.90,"escalation_available":1.0}
    raw=[]
    for ai, attack in enumerate(attacks):
        for pi, (pname, policy) in enumerate(policies.items()):
            for seed in range(N_SEEDS):
                r=evaluate_policy(cases,policy,params,20000+ai*1000+pi*100+seed,attack=None if attack=="none" else attack)
                raw.append({"experiment":"1C","attack":attack,"human_accuracy":0.90,"policy":pname,"seed":seed,**r})
    write_csv(OUT/"exp1c_seed_results.csv",raw)
    write_csv(OUT/"exp1c_summary.csv",summarize_seed_runs(raw,["attack","policy"]))


def exp1d(cases):
    shifts=["in_distribution","nuisance_shift","confidence_shift","provenance_dropout","compound_shift"]
    policies={k:POLICIES[k] for k in ("B2_Confidence","B4_AlwaysVerify","B7_RiskGate","B8_EvidenceGate")}
    params={"verifier_accuracy":0.90,"retrieval_success":0.90,"human_accuracy":0.90,"escalation_available":1.0}
    raw=[]
    for si, shift in enumerate(shifts):
        for pi,(pname,policy) in enumerate(policies.items()):
            for seed in range(N_SEEDS):
                r=evaluate_policy(cases,policy,params,30000+si*1000+pi*100+seed,shift=None if shift=="in_distribution" else shift)
                raw.append({"experiment":"1D","shift":shift,"policy":pname,"seed":seed,**r})
    write_csv(OUT/"exp1d_seed_results.csv",raw)
    write_csv(OUT/"exp1d_summary.csv",summarize_seed_runs(raw,["shift","policy"]))


def canonical_hash(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def private_key(role):
    seed=hashlib.sha256(("EGA-reconstruction-v1|"+role).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def signed_record(role, payload):
    key=private_key(role)
    raw=json.dumps(payload,sort_keys=True,separators=(",",":")).encode()
    return {"role":role,"payload":payload,"signature":key.sign(raw)}


def signature_valid(record, trusted_roles):
    if record["role"] not in trusted_roles:
        return False
    raw=json.dumps(record["payload"],sort_keys=True,separators=(",",":")).encode()
    try:
        private_key(record["role"]).public_key().verify(record["signature"],raw)
        return True
    except Exception:
        return False


def exp2(cases):
    high=[c for c in cases if c["action"]["risk_level"]=="HIGH"]
    attacks=["none","dependency_spoof","external_masking","timestamp_masking","combined_spoof"]
    rows=[]
    for attack in attacks:
        for c0 in high:
            c=mutate_case(c0, "all_metadata_spoof" if attack=="combined_spoof" else (None if attack=="none" else attack))
            # One signed evidence snapshot per case. This is a new protocol, not the historical 3,675-attestation design.
            payload={"case_id":c["case_id"],"observable_sha256":canonical_hash(c0["observable"])}
            record=signed_record("evidence-root",payload)
            valid=signature_valid(record,{"evidence-root"}) and record["payload"]["observable_sha256"]==canonical_hash(c["observable"])
            v1=evidence_gate_v1(c)
            v2="ESCALATE" if not valid else v1
            rows.append({"experiment":"2B","attack":attack,"case_id":c["case_id"],"safe":c0["safe_to_act"],"v1_action":v1,"v2_action":v2,"signature_valid":valid})
    write_csv(OUT/"exp2_unsigned_attack_cases.csv",rows)

    det=[]
    for attack in attacks:
        sub=[r for r in rows if r["attack"]==attack]
        for version,field in (("EvidenceGate_v1","v1_action"),("EvidenceGate_v2_signed","v2_action")):
            acts=[r for r in sub if r[field]=="ACT"]
            unsafe=sum(not r["safe"] for r in acts)
            det.append({"attack":attack,"policy":version,"unsafe_ACTs":unsafe,"ICAR_high":round(unsafe/len(sub),8),"ACT_rate":round(len(acts)/len(sub),8),"ESCALATE_rate":round(sum(r[field]=="ESCALATE" for r in sub)/len(sub),8)})
    write_csv(OUT/"exp2_unsigned_attack_summary.csv",det)

    # Experiment 2C: detected tamper is sent to an imperfect reviewer.
    review=[]
    for attack in attacks:
        sub=[r for r in rows if r["attack"]==attack]
        for seed in range(N_SEEDS):
            rng=random.Random(40000+attacks.index(attack)*100+seed)
            acts=0; unsafe=0; false_blocks=0
            for r in sub:
                action=r["v2_action"]
                final=(bool(r["safe"]) if rng.random()<0.90 else not bool(r["safe"])) if action=="ESCALATE" else action=="ACT"
                acts+=int(final)
                unsafe+=int(final and not r["safe"])
                false_blocks+=int((not final) and r["safe"])
            review.append({"experiment":"2C","attack":attack,"seed":seed,"ICAR":unsafe/len(sub),"act_rate":acts/len(sub),"false_block":false_blocks/len(sub),"mean_cost":2.0})
    write_csv(OUT/"exp2c_seed_results.csv",review)
    write_csv(OUT/"exp2c_summary.csv",summarize_seed_runs(review,["attack"]))

    # Experiment 2D: compromised signer can issue a valid signature over altered evidence.
    trust=[]
    root_attacks=[("verifier_root","dependency_spoof"),("sensor_root","external_masking"),("authorization_root","timestamp_masking"),("all_roots","combined_spoof")]
    for compromised, attack in root_attacks:
        for c0 in high:
            c=mutate_case(c0,"all_metadata_spoof" if attack=="combined_spoof" else attack)
            role={"dependency_spoof":"verifier_root","external_masking":"sensor_root","timestamp_masking":"authorization_root","combined_spoof":"all_roots"}[attack]
            # A compromised root re-signs the modified evidence snapshot; the signature is valid but the claim may be false.
            record=signed_record(role,{"case_id":c["case_id"],"observable_sha256":canonical_hash(c["observable"])})
            valid=signature_valid(record,{role})
            action=evidence_gate_v1(c) if valid else "ESCALATE"
            trust.append({"compromise":compromised,"case_id":c["case_id"],"safe":c0["safe_to_act"],"action":action})
    trust_summary=[]
    for compromise in [x[0] for x in root_attacks]:
        sub=[r for r in trust if r["compromise"]==compromise]
        unsafe=sum(r["action"]=="ACT" and not r["safe"] for r in sub)
        trust_summary.append({"experiment":"2D","compromise":compromise,"unsafe_ACTs":unsafe,"ICAR_high":unsafe/len(sub),"ACT_rate":sum(r["action"]=="ACT" for r in sub)/len(sub)})
    write_csv(OUT/"exp2d_trust_root_summary.csv",trust_summary)

    # Experiment 2E: two independent lineage authorities must agree on dependency structure.
    lineage=[]
    for compromise in ("none","verifier_only","lineage_A_only","lineage_B_only","both_lineage"):
        for c0 in high:
            c=mutate_case(c0,"dependency_spoof")
            original_groups=[v["dependency_group"] for v in c0["observable"]["machine"]["verifiers"]]
            actual_shared=len(set(original_groups))==1
            a_claim="independent" if compromise in ("lineage_A_only","both_lineage") else ("shared" if actual_shared else "independent")
            b_claim="independent" if compromise in ("lineage_B_only","both_lineage") else ("shared" if actual_shared else "independent")
            # Verifier-only compromise cannot alter either lineage authority's independently signed claim.
            lineage_a=signed_record("lineage_A",{"case_id":c["case_id"],"claim":a_claim})
            lineage_b=signed_record("lineage_B",{"case_id":c["case_id"],"claim":b_claim})
            valid=signature_valid(lineage_a,{"lineage_A"}) and signature_valid(lineage_b,{"lineage_B"})
            independent=(a_claim=="independent" and b_claim=="independent")
            action="ACT" if valid and independent else "ESCALATE"
            lineage.append({"experiment":"2E","compromise":compromise,"case_id":c["case_id"],"safe":c0["safe_to_act"],"action":action})
    lineage_summary=[]
    for compromise in ("none","verifier_only","lineage_A_only","lineage_B_only","both_lineage"):
        sub=[r for r in lineage if r["compromise"]==compromise]
        unsafe=sum(r["action"]=="ACT" and not r["safe"] for r in sub)
        lineage_summary.append({"experiment":"2E","compromise":compromise,"unsafe_ACTs":unsafe,"ICAR_high":unsafe/len(sub),"ACT_rate":sum(r["action"]=="ACT" for r in sub)/len(sub)})
    write_csv(OUT/"exp2e_dual_lineage_summary.csv",lineage_summary)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cases=read_jsonl(BENCH/"cases.jsonl")
    if len(cases)!=1000:
        raise SystemExit(f"Expected 1,000 benchmark cases, found {len(cases)}")
    exp1b(cases)
    exp1c(cases)
    exp1d(cases)
    exp2(cases)
    manifest={
        "protocol":"EGA reconstruction v1",
        "historical_reproduction":False,
        "benchmark_seed":42,
        "monte_carlo_seeds_per_condition":N_SEEDS,
        "experiments":["1B","1C","1D","2B","2C","2D","2E"],
        "generated_files":sorted(p.name for p in OUT.glob("*.csv")),
        "note":"New explicitly parameterized reconstruction. Do not substitute these outputs for historical v1 result tables.",
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
