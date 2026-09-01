# Compliance and Fairness Matrix

## Scope and separation

Demographic cohorts in this synthetic lab exist only for aggregated monitoring. Screeners, interviewers, Hiring Managers, automation workers, and offer approvers cannot view cohort fields. Privacy & Compliance receives minimum-cell aggregate outputs through a separate permission path. Individual scores are never adjusted because of cohort membership.

## Four-fifths calculation

The automated-knockout progression gate contains 2,400 Reference Group and 1,600 Focal Group applicants.

```text
Reference selection rate = 624 / 2,400 = 0.26000 = 26.000%
Focal selection rate     = 362 / 1,600 = 0.22625 = 22.625%
AIR                      = 0.22625 / 0.26000 = 0.87019 ≈ 0.87
Percentage-point gap     = 26.000% − 22.625% = 3.375 points
```

Because `0.87 ≥ 0.80`, the gate does not trigger the four-fifths rule-of-thumb flag. It does not establish fairness, statistical equivalence, business necessity, or legal compliance. The [EEOC’s Uniform Guidelines explanation](https://www.eeoc.gov/laws/guidance/questions-and-answers-clarify-and-provide-common-interpretation-uniform-guidelines) describes four-fifths as a practical rule of thumb rather than a legal definition.

## Chi-square explanation

A Pearson **Chi-square** test asks whether progression status and cohort are independent in the observed 2×2 table:

| Cohort | Progressed | Did not progress | Total |
|---|---:|---:|---:|
| Reference Group | 624 | 1,776 | 2,400 |
| Focal Group | 362 | 1,238 | 1,600 |
| **Total** | **986** | **3,014** | **4,000** |

For these constructed counts, Pearson χ² is approximately **5.89** with 1 degree of freedom, producing an illustrative p-value near **.015**. A conventional significance threshold would flag association even though the 0.87 impact ratio passes the 0.80 rule. This is not a contradiction: four-fifths is an effect-size rule of thumb, while Chi-square is sensitive to sample size. Both must be interpreted with job relevance, practical magnitude, confidence intervals, data quality, and legal context.

The test is descriptive because the cohort is synthetic. Production analysis would predeclare withdrawal handling, minimum expected-cell rules, multiplicity treatment across stages, and whether Fisher’s exact test or regression stratified by requisition is more suitable.

## Stage-by-stage enterprise audit

| Gate | Reference progressed / pool | Focal progressed / pool | Reference rate | Focal rate | Lower-to-higher ratio | Flag |
|---|---:|---:|---:|---:|---:|---|
| Application received | 2,400 / 2,400 | 1,600 / 1,600 | 100.0% | 100.0% | 1.00 | No |
| Automated knockout progression | 624 / 2,400 | 362 / 1,600 | 26.000% | 22.625% | 0.87 | No under 4/5ths |
| Work sample and interview | 300 / 2,400 | 200 / 1,600 | 12.5% | 12.5% | 1.00 | No |
| Offer and hire | 72 / 2,400 | 48 / 1,600 | 3.0% | 3.0% | 1.00 | No |

Aggregate parity can hide a job-family problem. The production report therefore repeats this table by requisition, rule version, assessment version, source route, and accommodation status with minimum-cell suppression.

## Control matrix

| Risk | Preventive control | Detective control | Owner | Response |
|---|---|---|---|---|
| Protected data influences automation | Separate compliance partition and deny-by-default service account | Access-query and feature-input audit | Privacy & Compliance | Disable rule; preserve logs; review affected decisions |
| Knockout rule is not job-related | Job-analysis trace and approved minimum criterion | Rule-version outcome review | People Operations | Roll back; route affected candidates to human review |
| Partial batch creates duplicate decisions | Idempotency key and state validation | Event-count reconciliation | HRIS/ATS Owner | Stop worker; replay safe events |
| Missing evidence becomes rejection | Ambiguous or missing responses route to review | Reason-code and appeal analysis | Talent Acquisition | Correct state; reassess |
| Inconsistent interviews | Standard prompts and assessor capacity limits | Note quality, duration, and severity review | Talent Acquisition | Retrain or reassign assessor |
| Accessibility barrier | Accommodation route with construct preservation | Candidate-reaction and outcome review | People Operations | Provide equivalent accessible mode |
| Threshold manipulation | Pre-approved versioned thresholds | Change-log and exception report | HRIS/ATS Owner | Restore version; reprocess impacted cases |
| AIR below .80 or significant association | Counts, ratios, intervals, and test plan | Stage and requisition dashboard | Privacy & Compliance | Freeze rule expansion; investigate root cause |
| Large-sample overreaction | Practical-significance standard | Effect-size review with legal context | Privacy & Compliance | Prioritize material, job-related remediation |

## Mitigation playbook

1. **Validate the event:** confirm denominators, duplicates, withdrawals, stage timestamps, missing values, and rule version.
2. **Contain automation:** pause the affected rule or assessment version when a control failure could alter decisions.
3. **Segment responsibly:** inspect requisition, criterion, assessor, source, assessment version, and accommodation route without exposing individuals.
4. **Test job relevance:** map the flagged gate to critical work and identify less exclusionary alternatives with comparable validity.
5. **Inspect execution:** review appeals, ambiguous-response routing, question consistency, assessor severity, score changes, and exceptions.
6. **Remediate:** revise the rule, retrain staff, provide reassessment where appropriate, and document decision ownership.
7. **Revalidate:** run UAT, accessibility checks, subgroup analysis, and authorized release approval.

## Interpretation guardrails

- Do not rank, penalize, or correct an individual using demographic membership.
- Do not pool unlike requisitions merely to produce a comfortable ratio.
- Do not treat 0.80 as a safe harbor or statistical significance as proof of discrimination.
- Do not ignore a practically material gap because a significance test is inconclusive.
- Escalate production decisions to qualified employment counsel and industrial-organizational expertise.

