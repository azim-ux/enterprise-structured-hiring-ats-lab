# Methodology and Limitations

## Build method

The portfolio simulation was generated from a fixed mathematical contract rather than an employer dataset. APD, all names, IDs, requisitions, dates, scores, events, decisions, and notes are fictional.

### 1. Define five requisition families

Five job specifications spanning G1–G4 were translated into required competencies, knockout rules, standardized assessments, BARS anchors, stage gates, capacity limits, proposed privacy partitions, and audit-evidence requirements. Applicant blocks are fixed at 800, 1,600, 600, 400, and 600 records. The privacy partitions and audit controls are reference designs, not runtime enforcement in the static browser demonstration.

### 2. Generate the 4,000-candidate cohort

Candidate IDs run sequentially from `CAND-2026-0001` to `CAND-2026-4000`. Within every five sequential records, three are assigned to the Reference Group and two to the Focal Group. Because every requisition block is divisible by five, each family preserves the overall 60/40 partition: 2,400 Reference and 1,600 Focal candidates.

Names use the explicit pattern `Synthetic Candidate NNNN` to avoid invented contact information or accidental claims about real individuals. Applied dates, source channels, and screening values are deterministic functions of the sequence number and requisition start date, making the dataset reproducible.

### 3. Allocate stage progression

The knockout progression quotas are specified by requisition and cohort:

| Requisition | Reference progressed | Focal progressed | Total shortlisted |
|---|---:|---:|---:|
| ENG-G4 | 125 | 72 | 197 |
| ENG-G1 | 250 | 145 | 395 |
| QUA-G3 | 94 | 54 | 148 |
| PNC-G2 | 62 | 36 | 98 |
| SCM-G2 | 93 | 55 | 148 |
| **Total** | **624** | **362** | **986** |

Presence of `Phone_Screen_Score` encodes knockout progression. Of the 986 shortlisted candidates, 500 receive all three governed assessment scores: 300 Reference and 200 Focal. The remaining 486 stop at Shortlisted. Non-progressors stop at Application Review.

### 4. Calculate composite evidence and hires

All 500 assessed finalists receive deterministic work-sample, four-component BARS, and job-knowledge scores. Candidate-level structured score is the mean of the four BARS components.

```text
Composite = 0.40 × Work Sample
          + 0.40 × Structured Interview
          + 0.20 × Job Knowledge

Bias Gap = Subjective Impression − Composite
```

Arithmetic is performed with decimal values and round-half-up to two places; binary floating-point is not used for reconciliation. Within each requisition, deterministic score ordering is descending by exact composite and uses ascending `Candidate_ID` only to resolve an exact tie.

Exactly 120 scored candidates are marked Hired according to preallocated requisition and cohort quotas: 10, 60, 15, 10, and 25. Candidate CAND-2026-0013 is explicitly set to work sample 4.00, structured interview 3.80, knowledge 4.00, composite 3.92, subjective impression 4.60, and gap +0.68; the candidate is not hired.

### 5. Generate 2,000 evaluation events

Every one of 500 scored candidates has four events: Work Sample Review, Structured Interview A, Structured Interview B, and Calibration Review. Interview IDs run from `INT-2026-0001` through `INT-2026-2000`.

A deterministic permutation rule distributes 164 late records through the sequence: an evaluation is late when `(event sequence × 37) mod 2,000 < 164`. Late turnaround is 49–72 hours; all other events are 12–48 hours. This produces exactly 1,836 on-time events and 164 late events, or 91.8% adherence.

### 6. Reconcile, qualify claims, and publish

The current 107-test suite and executable repository audit verify required assets, governed artifact hashes, PDF text and metadata contracts, contextual capability claims, reviewed contact-sheet policy, tracked-file privacy, relative Markdown and HTML links, self-hosted executable scripts, exact schemas and nullability, IDs and foreign keys, enumerations and stage progression, all 500 composite calculations, per-requisition and cohort totals, SLA boundaries, governed KPIs, both dashboard JSON payloads, the halo control, five-slide structure, deterministic pagination rules, history identity privacy, workflow pins, and GitHub platform-merge provenance behavior. Both dashboard files must preserve every normalized CSV field and value; drift fails the `data` gate.

The public case-study sources distinguish implemented calculations and tests from modeled outcomes and proposed controls. A contextual claims policy rejects affirmative assertions of unimplemented production, access-control, erasure, compliance, fairness, predictive-validity, and accessibility capabilities while allowing clearly labelled design requirements and limitations. This is a regression guard for governed wording, not a comprehensive natural-language verifier.

The PDF build uses local Chrome or Chromium with background networking disabled. `slides.html` maps to the 960 × 540 point desktop PDF; `mobile-case-study.html` plus `mobile-case-study.css` maps to the 420 × 720 point phone PDF. Browser-generated creation and modification dates are normalized to a fixed neutral value, so repeated builds with the same browser and inputs are byte-stable. Toolchain upgrades can legitimately change PDF bytes and require a new reviewed hash update.

## Statistical assumptions

- Scores are on a common 1.00–5.00 scale and higher values represent stronger constructed evidence.
- Empty downstream fields mean the stage was not reached; they are not zero.
- Cohort allocation and progression are engineered to the contract, not sampled from a population.
- Chi-square results describe the constructed 2×2 table and do not estimate a real employer effect.
- Requisition-level time to fill is an authoritative reporting value, including the fractional 30.5-day record.
- Feedback hours are authoritative even though date-only fields cannot reconstruct time-of-day.
- Offer and acceptance totals equal hires in this simulation.

## Limitations

### Synthetic evidence

No distribution, relationship, significance test, operational result, or utility estimate generalizes to a real employer. The deterministic generator is designed to make controls and reconciliation inspectable, not to mimic every feature of applicant behavior.

### No local criterion validation

The validity coefficients are literature-informed inputs, not APD estimates. There are no real performance criteria, reliability estimates, outcome follow-ups, confidence intervals for predictor validity, or cross-validation samples. Composite validity cannot be inferred by averaging component validities.

### Scale does not cure bias

A 4,000-row dataset increases statistical power but cannot repair a non-job-related rule, inaccessible assessment, misclassified group, biased criterion, or hidden job-family composition. Statistical significance and the four-fifths ratio answer different questions and require practical interpretation.

### Engineered parity after assessment

The assessed and hired stages intentionally have proportional cohort allocation. This makes reconciliation clear but is not evidence that a real process would produce parity. Production monitoring must examine applicant availability, qualifications, withdrawals, rule versions, accommodations, and job-level outcomes.

### Automation risk

High-volume knockout logic can multiply an error quickly. Production controls require human review for ambiguity, candidate appeal, idempotent transitions, load testing, kill switch, rollback, replay safety, and post-batch reconciliation.

### Construct and accessibility risk

Structured assessments can still measure irrelevant language fluency, test familiarity, device access, or time pressure. Real deployment needs accessible delivery, accommodations, candidate-reaction evidence, and proof that alternative modes preserve the job-related construct.

### Legal scope

DPDP, GDPR, and EEOC sources are governance benchmarks. Applicability varies by jurisdiction and processing context. This project is not legal advice, and the 180-day rejected-resume rule is a design choice requiring local review.

### Browser delivery

The source data and application logic are embedded. Chart.js 4.4.7 is pinned and self-hosted in `vendor/`; no Tailwind runtime is present, and the dashboard does not request externally hosted executable scripts. Very large inline JSON increases file size and parse cost. The public browser receives the complete synthetic dataset, including cohort fields, even though individual decision views do not display those fields. UI hiding is not access control. Any later API-backed reference implementation would require authenticated server-side pagination and field projection, and this static architecture must never be used with real applicant data.

### PDF and claims boundary

The five-page exports are readable portfolio documents, not conformance reports. Tagging and searchable text do not establish a correct semantic tag tree, assistive-technology usability, or accessibility conformance. The visual review checks visible layout at the recorded render resolution and a 390-pixel-wide phone simulation; it is not device-lab coverage. The claims gate recognizes governed patterns and contextual qualifiers but cannot prove every future sentence is true.

## Ethical boundaries

Do not use the synthetic thresholds, scores, cohort labels, or candidate sequence for real employment decisions. Do not infer protected characteristics. Do not train an automated selection model on this constructed dataset. Candidates require notice, accommodation, human review, correction routes, and proportionate retention.

## Change control

Any source-data change must propagate to both embedded JSON payloads and reconciled documentation. Changes to a rule, threshold, weight, assessment, permission, or retention schedule require a version, rationale, approver, fairness review, UAT evidence, and release record.
