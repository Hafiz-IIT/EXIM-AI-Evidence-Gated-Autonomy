# Preregistered Human-Oversight Study Protocol — H8

## Research question
Does a structured evidence packet improve human review of escalated AI-workflow cases relative to raw model output?

## Status
Protocol only. No human-subject result exists yet.

## Design
Randomized within-subject crossover.

Each participant reviews an equal number of cases in two conditions:
1. **Raw escalation:** proposed action, model output, generic uncertainty notice.
2. **Evidence packet:** proposed action plus evidence provenance, source dependencies, conflicts, missing evidence, verifier history, freshness, and reason for escalation.

Case assignment and condition order are randomized. The same participant never sees the same underlying case in both conditions.

## Participants
Target 60 reviewers, stratified where feasible:
- 30 technical/data/AI participants;
- 30 operations/domain participants.

If formal institutional ethics review is required, recruitment begins only after approval/exemption.

## Cases
40 cases per participant:
- 10 clean/false-positive cases;
- 10 document-conflict or missing-evidence cases;
- 10 consistent-but-wrong/external-conflict cases;
- 10 verifier/correlation/cascade cases.

High-risk and reversible actions are balanced.

## Primary outcome
Correct authorization decision: ACT vs BLOCK/ESCALATE according to hidden benchmark truth.

## Secondary outcomes
Decision time, calibration/confidence, false authorization, false blocking, evidence items inspected, ability to identify the decisive conflict, and perceived workload.

## Hypothesis
Evidence packets improve correct authorization without an unacceptable increase in decision time.

## Analysis
Primary comparison: paired participant-level accuracy difference between conditions.
Report effect size and 95% confidence interval, not significance alone.
Predefined subgroup analysis: technical vs domain reviewers.

## Failure criterion
H8 is not supported if the evidence packet does not improve accuracy, or if any accuracy gain is accompanied by operationally prohibitive review time/workload.

## Integrity constraints
No participant may see hidden fault-family labels or oracle truth.
No result will be claimed until actual participants complete the study.
