# Data Dictionary

## Conventions

CSV files are UTF-8 with a header row and comma delimiter. Dates use ISO `YYYY-MM-DD`. Empty strings represent not applicable or not reached; they are never interpreted as zero. IDs are unique within their entity. All records are synthetic.

## `synthetic_requisitions.csv`

| Column | Type | Definition | Valid values / rule |
|---|---|---|---|
| Requisition_ID | String | Stable requisition-family key | One of the five approved `REQ-2026-{team}-{grade}` values |
| Job_Title | String | Approved public role title | Non-empty |
| Department | String | Owning function | Engineering; People & Culture; Quality; Supply Chain |
| Grade | String | APD internal synthetic grade | APD-G1; APD-G2; APD-G3; APD-G4 |
| Hiring_Manager_ID | String | Pseudonymous accountable manager | `APD-MGR-01` to `APD-MGR-05` |
| Target_Headcount | Integer | Approved positions | 10; 15; 25; or 60; sum 120 |
| Open_Date | Date | Approved opening date | On or before Close_Date |
| Close_Date | Date | Filled closure date | On or after Open_Date |
| Days_to_Fill | Decimal | Governed elapsed-day KPI | Positive; one decimal |
| Status | Enum | Requisition state | Filled |
| Sourcing_Channel_Primary | Enum | Largest planned source | LinkedIn Recruiter; Direct Career Portal; Employee Referral; Skills Academy; Regional Hiring Drive |
| Total_Applicants | Integer | Applications received | Non-negative; reconciles to candidates |
| Shortlisted | Integer | Narrow operational shortlist count | Between Interviewed and Total_Applicants |
| Interviewed | Integer | Structured finalist count | Between Offered and Shortlisted |
| Offered | Integer | Approved offers issued | Between Hired and Interviewed |
| Hired | Integer | Accepted and started hires | 0 to Target_Headcount |

## `synthetic_candidates.csv`

| Column | Type | Definition | Valid values / rule |
|---|---|---|---|
| Candidate_ID | String | Stable candidate alias | Unique; `CAND-2026-0001` to `CAND-2026-4000` |
| Full_Name | String | Explicitly synthetic display label | `Synthetic Candidate NNNN`; no contact data |
| Gender | Enum | Synthetic monitoring attribute | Male; Female; restricted from decision roles |
| Demographic_Cohort | Enum | Fairness-analysis grouping | Reference Group; Focal Group; compliance-only |
| Requisition_ID | Foreign key | Applied requisition | Must exist in requisitions |
| Applied_Date | Date | Application receipt | Within the synthetic campaign |
| Source_Channel | Enum | Candidate source | LinkedIn Recruiter; Direct Career Portal; Employee Referral; Skills Academy; Regional Hiring Drive |
| Current_Stage | Enum | Furthest completed stage at closure | Application Review; Shortlisted; Interview Complete; Hired |
| Disposition_Reason | String | Controlled plain-language outcome | Required for every closed candidacy |
| Resume_Screen_Score | Decimal | Evidence screen on 1–5 scale | 1.00–5.00; required |
| Phone_Screen_Score | Decimal / empty | Knockout-progression evidence score | 1.00–5.00 for exactly 986 progressed candidates; empty otherwise |
| Work_Sample_Score | Decimal / empty | Two-hour simulation score | 1.00–5.00 for finalists |
| Structured_Interview_Score | Decimal / empty | Mean governed BARS score | 1.00–5.00 for finalists |
| Job_Knowledge_Score | Decimal / empty | Blueprint knowledge score | 1.00–5.00 for finalists |
| Composite_Score | Decimal / empty | Weighted 40/40/20 result | Two decimals; finalists only |
| Subjective_Impression_Score | Decimal / empty | Diagnostic intuition rating | 1.00–5.00; zero decision weight |
| Bias_Variance_Gap | Decimal / empty | Impression minus composite | Signed decimal; two decimals |
| Offer_Extended | Boolean enum | Offer event | Yes; No |
| Offer_Accepted | Boolean enum | Acceptance event | Yes only when offer extended |
| Hired_Date | Date / empty | Synthetic start/closure date | Required only for Hired |

## `synthetic_interviews.csv`

| Column | Type | Definition | Valid values / rule |
|---|---|---|---|
| Interview_ID | String | Stable evaluation event key | Unique; `INT-2026-0001` to `INT-2026-2000` |
| Candidate_ID | Foreign key | Evaluated candidate | Must exist in candidates |
| Requisition_ID | Foreign key | Governing role | Must match candidate requisition |
| Stage_Name | Enum | Controlled event type | Work Sample Review; Structured Interview A; Structured Interview B; Calibration Review |
| Interviewer_ID | String | Pseudonymous evaluator | `APD-INT-001` to `APD-INT-060` |
| Interviewer_Role | Enum | Evaluation capacity | Technical Assessor; Hiring Manager; Cross-functional Panelist; Talent Acquisition Partner |
| Scheduled_Date | Date | Evaluation date | ISO date |
| Feedback_Submitted_Date | Date | Submission date | On or after Scheduled_Date |
| Turnaround_Hours | Decimal | Hours from event end to feedback | Non-negative; SLA threshold 48.0 |
| SLA_Met | Boolean enum | Timeliness result | Yes when Turnaround_Hours ≤ 48.0; No otherwise |
| BARS_Score_1 | Decimal | Technical Problem Solving & Quality Mindset | 1.0–5.0 |
| BARS_Score_2 | Decimal | Stakeholder Collaboration & Conflict Resolution | 1.0–5.0 |
| BARS_Score_3 | Decimal | Process Optimization & Continuous Improvement | 1.0–5.0 |
| BARS_Score_4 | Decimal | Adaptability & Ethical Governance | 1.0–5.0 |
| Mean_BARS_Score | Decimal | Arithmetic mean of four ratings | Two decimals; 1.00–5.00 |
| Notes_Summary | String | Short job-evidence statement | No sensitive inference or demographic data |

## Cross-file validation

- Requisition applicant totals equal candidate counts by Requisition_ID.
- Hired candidates reconcile to requisition Hired totals.
- Interview Candidate_ID and Requisition_ID pairs match the candidate file.
- Composite equals `0.40 × work sample + 0.40 × structured interview + 0.20 × job knowledge`.
- Bias gap equals subjective impression minus composite.
- Exactly 4,000 candidates partition into 2,400 Reference and 1,600 Focal records.
- Knockout progression contains 624 Reference and 362 Focal candidates; AIR rounds to 0.87.
- Exactly 500 scored candidates each have four evaluation events.
- Exactly 1,836 interview rows have SLA_Met Yes and 164 have No, producing 91.8%.
- Source-identical JSON arrays in `index.html` and `dashboard.html` preserve every CSV field as a string.
