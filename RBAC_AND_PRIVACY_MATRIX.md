# RBAC and Privacy Matrix

## Privacy architecture

The ATS separates candidate identity, assessment evidence, demographic monitoring, automation services, and system administration. Access follows **least privilege**, purpose limitation, time-bound assignment, and deny-by-default rules across 4,000 candidate records. Demographic cohorts are inaccessible to every person or service that screens, scores, calibrates, or approves offers.

The design references India’s [Digital Personal Data Protection Act, 2023](https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf) and GDPR [Article 17](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016R0679) as governance sources. Applicability, commencement, lawful basis, retention duties, and jurisdiction require production legal review. The 180-day rejected-resume schedule is an APD minimization control, not a universal statutory period.

## Permission matrix

Legend: **C** create, **R** read, **U** update, **A** aggregate only, **X** no access.

| Data object | Candidate Support | Talent Acquisition | Hiring Manager | Interviewer | People Operations | HRIS/ATS Admin | Privacy & Compliance |
|---|---|---|---|---|---|---|---|
| Contact identity | R/U assigned | R assigned | X | X | R hired only | R support case | X unless request case |
| Redacted application | X | C/R/U assigned | R shortlisted | R assigned | X | R support case | X |
| Accommodation logistics | C/R/U assigned | Need-to-know flag | X | Delivery instruction only | R/U assigned | X | A |
| Assessment content | X | R assigned | R assigned | C/R assigned | X | R version support | A |
| Locked scores | X | R assigned | R assigned | Own score before lock; panel after calibration | X | System calculation only | A / audited case |
| Subjective impression | X | R after lock | C own after lock | C own after lock | X | X | A |
| Demographic cohort | Candidate self-service | X | X | X | X | Technical custody without query | A only |
| Offer data | X | C/R assigned | R/approve assigned | X | R/U hired only | Support metadata | A |
| Audit log | X | Own actions | Own actions | Own actions | Own actions | R system events | R/A |
| Retention and deletion queue | Request status | X | X | X | C legal hold request | R/execute | R/approve |
| Knockout rule configuration | X | Test cases only | X | X | C | C/U deploy | R/approve |
| Batch-worker retry queue | X | Aggregate status | X | X | X | R/U | R incident case |

No role may export both demographic cohort and individual assessment scores. Administrative custody does not authorize business use.

## Data lifecycle

| Event | Minimum record | Retention action | Control evidence |
|---|---|---|---|
| Application received | Identity, contact route, requisition, notice event, job evidence | Active during selection | Notice version and timestamp |
| Rejected | Decision, reason, evidence, communication | Resume and direct identifiers queued for purge after **180 days** | Deletion due date |
| Talent-pool opt-in | Separate explicit preference and expiry | Retain only for the stated period | Preference history |
| Hired | Minimum identity and employment-start data | Transfer approved fields to HRIS; remove assessment-panel access | Transfer manifest |
| Legal hold | Hold reason, scope, approver, review date | Suspend only affected deletion | Hold register |
| Purged | Candidate alias, requisition, irreversible aggregate measures | Delete identity, resume, attachments, free text, and search index copies | Deletion certificate |

Backups follow the same expiry through cryptographic erasure or bounded backup rotation. Search indexes, exports, email attachments, and processor copies are included in deletion scope.

## Right to be Forgotten workflow

1. Candidate submits a request through the privacy channel, such as `privacy@apexprecision.test`.
2. Candidate Support verifies identity using proportionate information and creates a restricted request ID.
3. Privacy & Compliance records jurisdiction, request scope, receipt date, and response due date.
4. HRIS/ATS Admin discovers live records, attachments, exports, search indexes, processors, and backups.
5. Privacy & Compliance assesses applicable erasure rights, legal obligations, legal claims, and documented exceptions.
6. Approved deletion removes or irreversibly de-identifies data; denied or partial actions record the legal reason and appeal route.
7. Processors receive scoped deletion instructions and return completion evidence.
8. The candidate receives a plain-language completion response; the ATS retains only the minimum request audit record.

The workflow also supports DPDP correction and erasure requests and GDPR Article 17 requests where applicable. Request details are never exposed to interviewers or Hiring Managers.

## Security controls

- SSO with multi-factor authentication for workforce users.
- Quarterly access recertification and immediate leaver revocation.
- Time-bound requisition assignment; no standing interviewer access.
- Encryption in transit and at rest with managed key rotation.
- Immutable event history for score, threshold, permission, export, and deletion changes.
- Free-text warnings and automated scanning for sensitive or inappropriate notes.
- Processor inventory, contractual deletion terms, incident notification, and subprocessor review.
- Export watermarking, row limits, purpose code, and approval for sensitive aggregates.
- Service accounts scoped to one queue and transition; no interactive login or demographic query permission.
- Idempotency keys, signed rule versions, bounded batch size, retry limits, dead-letter review, and daily count reconciliation.
- Pagination and field-level projection so routine recruiter views never load or export the full 4,000-row dataset unnecessarily.

## Incident response

Suspected unauthorized access triggers containment, log preservation, impact assessment, credential review, data-principal risk analysis, processor coordination, and legally required notifications. Affected hiring decisions are frozen when the incident may have exposed demographic data or altered evidence.
