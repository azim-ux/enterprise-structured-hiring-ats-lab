# Production Readiness Gap

## Current status

This repository is a static portfolio simulation and documentation set. The intended destination is an **enterprise-oriented structured-hiring reference implementation**, not a claim of production readiness. No real applicant data or employment decision should be processed here.

| Area | Baseline status | Evidence required before any production-readiness discussion |
|---|---|---|
| Authentication | Absent | Identity provider integration, MFA policy, session controls, account lifecycle, and tests |
| Authorization | Design matrix only | Deny-by-default enforcement, object/field scope, separation of duties, and negative tests |
| Privacy | Synthetic-data boundary plus design documents | Data inventory, lawful-basis analysis, notices, consent where applicable, rights workflows, DPIA, processor controls, and jurisdiction review |
| Encryption | GitHub/browser transport only; no application data store | In-transit and at-rest design, managed keys, rotation, secrets management, and recovery procedures |
| Monitoring | Absent | Service, security, privacy, data-quality, fairness, and business-control telemetry with alert ownership |
| Backups | Absent | Backup scope, encryption, retention, restore tests, deletion propagation, and evidence |
| Disaster recovery | Absent | RTO/RPO, dependency failure modes, failover/runbook, and exercised recovery test |
| Performance | One local browser timing; no budget/load test | Representative workload, capacity model, latency/error budgets, soak tests, and regression gates |
| Availability | Static GitHub Pages only; no application SLO | Service architecture, SLO/SLI, dependency plan, graceful degradation, and incident evidence |
| Integrations | Conceptual OpenCATS/Frappe/HRIS references only | Versioned contracts, sandbox integration, retries, idempotency, reconciliation, and ownership |
| Regulatory review | Educational DPDP/GDPR references only | Qualified employment/privacy counsel review for each jurisdiction and documented decisions |
| Accessibility | Basic semantics and partial manual review | WCAG target, automated/manual audit, assistive-technology testing, accommodations process, and remediation evidence |
| Support | Absent | Support model, service ownership, escalation, maintenance windows, user guidance, and deprecation policy |
| Incident response | Narrative only | Approved plan, roles, detection sources, notification criteria, tabletop exercise, and post-incident process |
| Hiring validity and fairness | Research rationale and synthetic monitoring | Local job analysis, content/criterion evidence, reliability, candidate-reaction evidence, accommodation validation, subgroup monitoring, and qualified review |
| Auditability | Static traceability documents | Authenticated append-only events, time synchronization, retention, integrity protection, access review, and reproducible reports |
| Data quality | Selected metrics tested | Full schema/lineage contracts, source ownership, change control, anomaly handling, and reconciliation |
| Secure delivery | No CI/CD workflow | Protected review path, CI security/privacy gates, artifact provenance, dependency policy, deployment approval, rollback, and audit trail |

## Decision boundary

Closing a code task or passing a test does not close these organizational, legal, operational, or validation gaps. Any future production use would require a separate risk acceptance process led by accountable business, security, privacy, legal, accessibility, and industrial-organizational specialists.
