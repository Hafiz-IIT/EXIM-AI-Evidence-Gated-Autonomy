# Publication Path — EGA v1

## Current state

**Research artifact:** READY  
**Manuscript:** substantially prepared  
**LaTeX:** under automated compilation check  
**arXiv:** requires the author's account/submission action  
**Google Scholar:** follows public dissemination/indexing; it is not the publication venue

## 1. Freeze the research artifact

Before submission, freeze the exact v1 benchmark/results state:

- 500 underlying synthetic evidence situations
- 1,000 LOW/HIGH consequence cases
- Experiments 1A–2E
- 3,675 synthetic Ed25519 attestations
- deterministic and stochastic result tables
- adversarial/provenance/trust-root experiments
- claims ledger
- limitations and threats-to-validity

No new experiment should silently change v1 after submission.

## 2. arXiv preprint

**Status: READY FOR FINAL AUTHOR-SIDE SUBMISSION CHECK**

The repository contains:

- `paper/main.tex`
- `paper/references.bib`
- `paper/MANUSCRIPT.md`
- `paper/RESULTS_AND_DISCUSSION.md`
- `paper/ARXIV_METADATA.md`
- `paper/ARXIV_SUBMISSION_CHECKLIST.md`
- reproducibility materials and result CSVs

The author must still submit through the arXiv account, select the final subject classification/license, review the generated PDF, and accept arXiv's submission terms. Do not represent a manuscript as an arXiv preprint until an arXiv identifier exists.

For the initial release, upload only the clean source needed to compile the manuscript. Do not expose private notes, credentials, client records, irrelevant files, or repository history.

**Candidate category:** `cs.AI`. Cross-listing can be considered after checking the final manuscript framing and arXiv's current classification options.

## 3. Google Scholar

Google Scholar is an indexing/discovery system rather than the publication venue.

Google Scholar states that it indexes scholarly articles, preprints, technical reports and other scholarly literature when the content is accessible and technically crawlable. It recommends a separate searchable PDF/HTML per paper, a clear title and author line, an abstract/full text accessible without login, and a bibliography.

Practical sequence:

1. Make the arXiv record public.
2. Search the exact title + author in Google Scholar.
3. If Scholar has indexed it, add/confirm it in the author's Scholar profile.
4. If it has not appeared yet, add the paper manually to the profile while waiting for automatic indexing.
5. Keep the public arXiv PDF stable and searchable.
6. When additional versions exist, let Scholar group them rather than creating unnecessary duplicate records.

Google Scholar says new papers are normally added several times a week, but indexing is not guaranteed immediately.

## 4. Author/profile identity

Use one consistent author identity everywhere:

**Syed Hafiz Ali**

Use the same title, author ordering, affiliation wording and email across:

- manuscript
- arXiv metadata
- GitHub
- Google Scholar
- CV

Do not claim an IIT Madras institutional research affiliation beyond what is actually accurate. The current manuscript uses:

**Independent Researcher; BS in Data Science and Applications, IIT Madras**

## 5. Citation and versioning

### v1
Experiments 1A–2E; current synthetic benchmark and provenance study.

### v2
External-model evaluation only after the frozen protocol is actually executed.

### Later study
Human-oversight evaluation only after actual participants and any required ethics/consent process.

## 6. CV wording

Before arXiv:
> Working paper / research manuscript: *Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence.*

After arXiv:
> Preprint: *Evidence-Gated Autonomy: A Synthetic Benchmark for Consequential Action Authorization Under Uncertain and Compromised Evidence.* arXiv, 2026.

Never use:

- peer-reviewed publication
- accepted paper
- production validation
- real-world safety proof
- completed human-subject study
- completed frontier-model evaluation

until those claims are independently true.
