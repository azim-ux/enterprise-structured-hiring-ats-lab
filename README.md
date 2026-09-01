# Enterprise-Oriented Structured Hiring & ATS Reference Implementation

An audit-oriented portfolio simulation for Apex Precision Dynamics Ltd. (APD), a fictional 70-person precision-manufacturing firm in Aligarh, India. It is the static demonstration layer of an **enterprise-oriented structured-hiring reference implementation** in development. It demonstrates how structured selection, automation design, privacy requirements, fairness monitoring, and recruiter operations can remain traceable across **4,000 synthetic candidates**.

## Standalone release

- [Launch the live interactive lab](https://azim-ux.github.io/enterprise-structured-hiring-ats-lab/)
- [Review the source and automated checks](https://github.com/azim-ux/enterprise-structured-hiring-ats-lab)
- [Explore the complete People Operations & HRIS portfolio](https://azim-ux.github.io/people-operations-hris-portfolio/)

This repository is an independently deployable, open-source release of the Structured Hiring & ATS Architecture Lab. Original code and documentation are licensed under MIT; third-party frameworks and cited research retain their own terms.

## Executive summary

The deterministic simulation contains five requisition families, 4,000 applications, 986 modeled knockout progressions, 500 fully assessed finalists, and 120 modeled hires. Its evidence model uses a 40/40/20 composite of work sample, structured BARS interview, and job-knowledge evidence. The reconciled synthetic view is **3.0% conversion**, **28.5 average days to fill**, **91.8% feedback-SLA adherence**, and a **0.87 adverse-impact ratio** at the knockout-progression gate.

Candidate CAND-2026-0013 is the halo-effect control. A subjective impression of 4.60 did not override a governed composite of 3.92; the +0.68 gap triggered evidence review and the candidate was not hired.

All people, identifiers, dates, scores, and events are fictional. Demographic cohort fields are not displayed in individual decision views, but the static public demonstration delivers the complete synthetic dataset to the browser. This is not access control, and the architecture must never be used with real applicant data.

## Explore the lab

- [Open the reference-implementation experience](index.html)
- [Open the high-volume analytics dashboard](dashboard.html)
- [Open the five-slide case presentation](slides.html)
- [Download the five-page PDF case study](Structured_Hiring_and_ATS_Architecture_Case_Study.pdf)
- [Open the responsive phone case-study source](mobile-case-study.html)
- [Read the five-page phone-friendly portrait edition](Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf)

Both dashboard pages embed all three source datasets as JSON. Search, filtering, 25/50-row pagination, charts, and scorecards run directly from the local file. Chart.js 4.4.7 is pinned and self-hosted in `vendor/`, so page rendering does not depend on a third-party JavaScript request.

## Governed KPIs

| KPI | Reconciled value | Source of truth |
|---|---:|---|
| Candidates evaluated | 4,000 | Candidate row count |
| Applied-to-hired conversion | 3.0% | 120 hires / 4,000 applicants |
| Average time to fill | 28.5 days | Mean of 34.0, 22.0, 30.0, 26.0, and 30.5 |
| Interviewer SLA adherence | 91.8% | 1,836 of 2,000 evaluations at or below 48 hours |
| Knockout-progression AIR | 0.87 | (362/1,600) / (624/2,400) = 0.870 |

The 4/5ths result is a monitoring signal rather than proof of fairness or lawful practice. The larger cohort improves precision but does not repair invalid criteria, biased measurement, job-family confounding, or poor data quality.

## Requisition families

| Requisition | Applicants | Shortlisted | Assessed | Hired |
|---|---:|---:|---:|---:|
| Senior Precision Engineer · G4 | 800 | 197 | 100 | 10 |
| CNC Precision Machinist Trainee · G1 | 1,600 | 395 | 200 | 60 |
| Quality Assurance Specialist · G3 | 600 | 148 | 75 | 15 |
| People Operations Specialist · G2 | 400 | 98 | 50 | 10 |
| Supply Chain & Logistics Associate · G2 | 600 | 148 | 75 | 25 |
| **Total** | **4,000** | **986** | **500** | **120** |

## Repository map

### Data

- [Synthetic requisitions](synthetic_requisitions.csv)
- [Synthetic candidates](synthetic_candidates.csv)
- [Synthetic interviews](synthetic_interviews.csv)

### Evidence, design, and governance

- [Research foundation](RESEARCH_FOUNDATION.md)
- [Requisitions and roles](REQUISITIONS_AND_ROLES.md)
- [Structured interview rubrics](STRUCTURED_INTERVIEW_RUBRICS.md)
- [ATS workflow and RACI](ATS_WORKFLOW_AND_RACI.md)
- [Selection validity model](SELECTION_VALIDITY_MODEL.md)
- [Compliance and fairness matrix](COMPLIANCE_AND_FAIRNESS_MATRIX.md)
- [RBAC and privacy matrix](RBAC_AND_PRIVACY_MATRIX.md)
- [UAT test register](UAT_TEST_REGISTER.md)
- [Methodology and limitations](METHODOLOGY_AND_LIMITATIONS.md)
- [Data dictionary](DATA_DICTIONARY.md)

## Reproduction

1. Clone or download this repository.
2. Open `index.html`, `dashboard.html`, or `slides.html` in a modern browser.
3. Inspect the three CSV files for row-level evidence.
4. Run `python3 -m unittest tests/test_repository_integrity.py` from the repository root.

The four-test acceptance suite checks ten required assets, selected row counts and governed KPI values, a limited set of privacy/secret/local-path patterns in non-PDF files, and relative `href`/`src` targets in top-level HTML files. It does not currently verify the exact inventory, full schemas and foreign keys, every composite calculation, embedded JSON/CSV parity, browser behavior, PDF contents, or the five-slide contract; those gaps are tracked in the [Stage 0 test-coverage map](docs/audit/TEST_COVERAGE_MAP.md).

## Interpretation boundary

This is a systems-design and analytics work sample, not a validated production selection instrument, legal opinion, or employment recommendation. Production use requires local job analysis, candidate accessibility review, criterion validation, security and load testing, employment-law review, recruiter-capacity planning, and ongoing subgroup monitoring.
