# UAT Test Register

## Test governance

**Entry criteria:** approved workflow version; all 4,000 synthetic candidates and five requisitions loaded; roles provisioned; batch workers and notification service available; assessment versions locked; privacy partition enabled.

**Exit criteria:** all Critical and High scenarios pass; no unresolved privacy, score-integrity, or unauthorized-transition defect; reconciled KPI report matches source records; business and Privacy & Compliance owners sign the release record.

**Defect Severity:** Critical = privacy breach or invalid decision; High = broken control or material reconciliation; Medium = recoverable workflow defect; Low = cosmetic or documentation issue.

### UAT-001 — Requisition approval gate

- **Role:** Hiring Manager and People Operations approver
- **Precondition:** Draft requisition lacks assessment blueprint approval.
- **Action:** Attempt to publish and source candidates.
- **Expected:** Publication is blocked; missing approval is named; event is logged. After approval, status changes once to Open.
- **Evidence:** Requisition history and approval record.
- **Severity if failed:** High

### UAT-002 — High-volume idempotency and duplicate controls

- **Role:** HRIS/ATS Owner and Talent Acquisition
- **Precondition:** Five open requisitions; 4,000 queued applications; one duplicate alias; one incomplete response; fixed batch idempotency keys.
- **Action:** Run the import and knockout worker twice with an injected mid-batch retry.
- **Expected:** Exactly 4,000 candidate records and one transition per rule version remain; the duplicate and incomplete response route to human review; no candidate is rejected twice.
- **Evidence:** Batch manifest, queue metrics, duplicate event, and state-count reconciliation.
- **Severity if failed:** Critical

### UAT-003 — Demographic field isolation

- **Role:** Screener, Interviewer, and Hiring Manager
- **Precondition:** Candidate has a compliance-monitoring cohort value.
- **Action:** Search views, exports, API responses, and scorecard for cohort data.
- **Expected:** No demographic field or proxy value is returned; the denied query is logged.
- **Evidence:** Role screenshots and access log.
- **Severity if failed:** Critical

### UAT-004 — Blind automated knockout decision

- **Role:** Talent Acquisition
- **Precondition:** Redacted application with required-criteria evidence.
- **Action:** Pass, reject, and submit an ambiguous response through the versioned rule.
- **Expected:** Clear cases receive the approved reason and rule version; ambiguity routes to human review; identity, source channel, and demographic fields remain hidden.
- **Evidence:** Stage events, rule version, and redacted-view capture.
- **Severity if failed:** High

### UAT-005 — Controlled stage transition

- **Role:** Talent Acquisition
- **Precondition:** Candidate has no phone-screen evidence.
- **Action:** Attempt direct transition from application review to interview.
- **Expected:** Transition is blocked. Completing the phone-screen checklist enables only the configured next stage.
- **Evidence:** Denial and successful-transition events.
- **Severity if failed:** High

### UAT-006 — Standardized work-sample version

- **Role:** Technical Assessor
- **Precondition:** Candidate assigned to assessment version ENG-WS-2026-01.
- **Action:** Open, time, submit, and score the work sample.
- **Expected:** Correct brief and scoring key load; timer and accommodation adjustment are recorded; post-submit content cannot be altered.
- **Evidence:** Version ID, timestamps, and locked score.
- **Severity if failed:** High

### UAT-007 — Independent BARS score locking

- **Role:** Two Interviewers
- **Precondition:** Same candidate assigned to both assessors.
- **Action:** Assessor A submits while Assessor B remains open.
- **Expected:** B cannot view A’s scores or subjective impression. Both see panel results only after independent lock and calibration release.
- **Evidence:** Permission trace and lock events.
- **Severity if failed:** Critical

### UAT-008 — Composite arithmetic

- **Role:** HRIS/ATS Owner
- **Precondition:** Work sample 4.00, structured interview 3.80, and knowledge 4.00.
- **Action:** Trigger composite calculation.
- **Expected:** Composite is 3.92 using 40/40/20; component versions and unrounded values remain traceable.
- **Evidence:** Calculation event and displayed score.
- **Severity if failed:** Critical

### UAT-009 — Subjective override prevention

- **Role:** Hiring Manager
- **Precondition:** CAND-2026-0013 has impression 4.60 and composite 3.92.
- **Action:** Attempt to promote the candidate using impression alone.
- **Expected:** Direct override is blocked; +0.68 gap is shown; any exception requires evidence, People & Culture approval, and Privacy & Compliance review.
- **Evidence:** Block event and calibration record.
- **Severity if failed:** Critical

### UAT-010 — 24-hour reminder

- **Role:** Interviewer and Talent Acquisition
- **Precondition:** Feedback remains open 24 hours after evaluation.
- **Action:** Run notification job.
- **Expected:** Assessor receives one reminder; TA receives status; SLA remains open rather than breached.
- **Evidence:** Notification event.
- **Severity if failed:** Medium

### UAT-011 — 48-hour breach and 72-hour hold

- **Role:** Interviewer and Hiring Manager
- **Precondition:** Feedback remains missing through both thresholds.
- **Action:** Advance time past 48 and 72 hours and attempt candidate progression.
- **Expected:** At 48 hours a breach is logged; at 72 hours the decision hold blocks progression until a recovery owner is assigned.
- **Evidence:** Breach, hold, assignment, and release events.
- **Severity if failed:** High

### UAT-012 — Adverse-impact aggregate

- **Role:** Privacy & Compliance
- **Precondition:** 2,400 Reference and 1,600 Focal applicants; 624 and 362 progress.
- **Action:** Generate the screening-progression fairness report.
- **Expected:** Rates show 26.000% and 22.625%; AIR rounds to 0.87; Chi-square output and counts appear; business users receive aggregate output only.
- **Evidence:** Signed report and permission trace.
- **Severity if failed:** High

### UAT-013 — Disposition and communication

- **Role:** Talent Acquisition
- **Precondition:** Candidate is rejected at shortlist.
- **Action:** Choose a reason, record evidence, send communication, and attempt to edit the locked reason.
- **Expected:** Approved reason and communication timestamp are required; edit needs authorized reopen and preserves the original.
- **Evidence:** Candidate timeline and audit history.
- **Severity if failed:** High

### UAT-014 — Retention purge and erasure request

- **Role:** HRIS/ATS Owner and Privacy & Compliance
- **Precondition:** Rejected candidate reaches 180 days with no legal hold; separate candidate has a verified erasure request.
- **Action:** Run purge and approved Right to be Forgotten workflows.
- **Expected:** Identity, resume, attachments, search copies, and processor records are removed or irreversibly de-identified; minimum audit evidence and aggregate metrics remain; completion is communicated.
- **Evidence:** Discovery manifest, approval, processor confirmations, and deletion certificate.
- **Severity if failed:** Critical

## Execution record

Each run records environment, workflow and assessment versions, tester, date, observed result, evidence link, pass/fail, defect ID, retest result, and approver. Synthetic UAT data is reset between scenarios to keep tests independent.
