# ATS Workflow and RACI

## OpenCATS configuration intent

This is a platform-neutral control design expressed as a six-stage OpenCATS workflow for 4,000 applications across five requisition families. Configuration uses role-scoped views, required fields, immutable event history, controlled reason codes, score locking, capacity queues, idempotent automation, and timed notifications. A production implementation would be load- and security-tested against the deployed OpenCATS version.

## High-volume state machine

```text
DRAFT → APPROVED → OPEN → APPLICATION_RECEIVED
→ KNOCKOUT_PENDING → KNOCKOUT_PASSED | KNOCKOUT_REJECTED | HUMAN_REVIEW
→ PHONE_SCREEN → SHORTLISTED → ASSESSMENT_SCHEDULED
→ SCORES_LOCKED → CALIBRATION → OFFERED | REJECTED
→ HIRED → CLOSED → PURGE_DUE → PURGED
```

Every transition accepts an idempotency key, validates the current state, writes the rule or assessment version, and emits one audit event. Batch workers use bounded queues and retries with dead-letter review; they never skip a required state after partial failure.

## Six-stage funnel

### 1. Requisition authorization

Hiring Manager drafts the business need, outcomes, grade, required criteria, panel, and target dates. Finance validates the synthetic band; People & Culture validates job relevance and duplicate headcount; the accountable approver releases the requisition. No sourcing begins before approval.

**Exit controls:** approved job specification, assessment blueprint, panel conflict declarations, requisition ID, retention schedule, and fairness-monitoring plan.

### 2. Application and blind eligibility screen

The ATS stores direct identifiers in a restricted identity partition. Screeners see an application alias, job-related evidence, and accommodation status only where action is required. Demographic-monitoring fields are written to a separate compliance partition that screening and hiring roles cannot query.

**Exit controls:** consent/lawful-purpose notice, required-criteria decision, reason code, evidence note, duplicate-candidate check, and screening-progression event.

### Automated knockout safeguards

- Questions map only to approved minimum requirements and display the rule version.
- Protected characteristics, inferred proxies, résumé keywords, and source channel cannot drive the rule.
- Missing or ambiguous evidence routes to human review rather than automatic rejection.
- Candidates receive the relevant job criterion and a correction/appeal route.
- Rules are shadow-tested on synthetic cases before release and reconciled after every batch.
- Kill switch, rollback version, retry queue, and duplicate-event protection are owned by the HRIS/ATS Owner.

### 3. Standardized phone screen and shortlist

Talent Acquisition asks the same role-specific questions, records evidence against a checklist, confirms practical expectations, and applies a published progression threshold. Hiring Managers can review redacted evidence only after TA submits the independent recommendation.

**Exit controls:** locked phone score, shortlist reason, accommodation handoff, and candidate communication date.

### 4. Work sample and structured assessment

Candidates receive a standardized two-hour work sample and job-knowledge test. Trained panelists administer common behavioral questions and the four BARS competencies. Panelists cannot see demographic fields, subjective impressions, referral source, or peer scores before locking.

**Exit controls:** assessment version, candidate acknowledgment, assessor identity, four BARS scores, work-sample score, knowledge score, evidence notes, and feedback timestamp.

### 5. Calibration, decision, and offer

The ATS calculates the 40/40/20 composite. A calibration view shows locked evidence, score distributions, and bias-variance gaps. The subjective impression is diagnostic only and has zero decision weight. Offer approval requires the highest defensible composite, required-criteria pass, documented exceptions, and fairness review.

**Exit controls:** final disposition, approved exception or none, offer approvals, communication, and audit log.

### 6. Hire transfer, closure, and retention

Only the minimum onboarding record transfers to HRIS. Rejected applications enter the 180-day purge queue unless a documented legal hold or renewed talent-pool consent applies. Aggregate de-identified metrics persist separately. Access is removed when the requisition closes.

**Exit controls:** transfer manifest, access revocation, deletion due date, reconciliation report, and close approval.

## Twenty-activity RACI

Roles: **TA** Talent Acquisition; **HM** Hiring Manager; **PA** Panel Assessors; **PO** People Operations; **HO** HRIS/ATS Owner; **PC** Privacy & Compliance. R = Responsible, A = Accountable, C = Consulted, I = Informed.

| ID | Activity | TA | HM | PA | PO | HO | PC |
|---|---|---|---|---|---|---|---|
| RACI-01 | Draft outcome-based requisition | C | R/A | I | C | I | I |
| RACI-02 | Validate grade and compensation band | C | C | I | R/A | I | I |
| RACI-03 | Approve job-related criteria | R | A | C | C | I | C |
| RACI-04 | Configure requisition and stage gates | C | I | I | C | R/A | C |
| RACI-05 | Publish privacy notice and consent route | I | I | I | C | C | R/A |
| RACI-06 | Source and acknowledge applicants | R/A | I | I | I | C | I |
| RACI-07 | Execute blind eligibility screen | R/A | I | I | I | C | C |
| RACI-08 | Run standardized phone screen | R/A | C | I | I | I | I |
| RACI-09 | Approve shortlist from redacted evidence | R | A | I | I | I | C |
| RACI-10 | Manage accommodation logistics | C | I | I | R/A | C | C |
| RACI-11 | Administer standardized work sample | C | I | R/A | I | C | I |
| RACI-12 | Conduct structured BARS interview | C | A | R | I | I | I |
| RACI-13 | Submit feedback within 48 hours | C | A | R | I | I | I |
| RACI-14 | Escalate overdue feedback | R/A | I | I | I | C | I |
| RACI-15 | Calculate and lock composite | C | I | I | I | R/A | C |
| RACI-16 | Facilitate evidence calibration | R | A | C | I | I | C |
| RACI-17 | Run stage-level fairness review | I | I | I | C | C | R/A |
| RACI-18 | Approve and issue offer | R | A | I | C | I | I |
| RACI-19 | Transfer minimum hire data to HRIS | I | I | I | R/A | C | C |
| RACI-20 | Purge rejected records and close access | I | I | I | C | R | A |

## Feedback SLA and escalation

- **24-hour reminder:** the ATS reminds the assessor and copies TA when a locked evaluation is still missing.
- **48-hour deadline:** the evaluation becomes overdue; TA and the Hiring Manager receive a breach event, and the candidate cannot advance on incomplete evidence.
- **72-hour hold:** the requisition enters a decision hold; the assessor’s access is suspended for that evaluation and the accountable Hiring Manager must assign a recovery owner.

SLA is measured from the end of the scheduled evaluation to feedback submission. Exactly 1,836 of 2,000 synthetic evaluations meet the at-or-below-48-hour rule; 164 are late, producing exactly 91.8% adherence. Department and assessor views show counts with rates so a small team is not misread from percentages alone.

## Stage-transition rules

Transitions are unidirectional unless HO reopens a stage with an approved reason. A reject action requires a valid reason code and candidate communication. A candidate cannot reach calibration until required assessment fields are complete. No user may approve their own access, alter a locked score without history, or export demographic and score-level data in the same file.

## Operational service levels

| Queue | Target | Breach action |
|---|---:|---|
| New applications awaiting knockout | 4 hours | Pause campaign expansion; inspect worker and rule version |
| Human-review exceptions | 1 business day | Rebalance trained screener capacity |
| Candidate accommodation request | 1 business day acknowledgment | Escalate to People Operations |
| Assessment scheduling | 2 business days | Open additional controlled wave |
| Panel feedback | 48 hours | Apply reminder, breach, and hold protocol |
| Rejected-record purge | Daily after 180 days | Open privacy incident if overdue |
