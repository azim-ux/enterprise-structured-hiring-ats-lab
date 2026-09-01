# Prioritized Implementation Backlog

This backlog is evidence-derived. Priority is based on privacy risk, claim integrity, evaluator impact, and the dependency order in the approved staged delivery plan.

## Stage 1 — Quality foundation

1. Add CI for unit/integrity checks, exact-index privacy scanning, link validation, browser smoke tests, and documentation claim checks.
2. Expand data contracts for schemas, unique keys, foreign keys, enumerations, all 500 composite calculations, stage counts, per-requisition counts, embedded-data parity, and governed KPI constants.
3. Make privacy tests inspect tracked files and full reachable history while ignoring local tooling artifacts by design.
4. Establish one canonical dashboard source/output path and remove the exact duplicate multi-megabyte application payload.
5. Correct the 375 px document overflow and slide-control overlap; add repeatable viewport assertions.
6. Add automated accessibility checks plus keyboard, focus-return, dialog, heading, control-name, and chart-alternative tests.
7. Correct stale/overstated README and methodology claims.
8. Record vendored dependency provenance/checksum and add a scheduled advisory check.

## Stage 2 — Executable core vertical slice

1. Define a relational schema for requisitions, candidates, applications, assessment versions, scores, stage events, decisions, and audit events.
2. Provide migrations and deterministic synthetic seed data that reproduce the governed KPIs.
3. Implement one end-to-end versioned transition slice with idempotency, reason codes, structured score calculation, and append-only event evidence.
4. Expose a documented role-scoped API with field projection and server-side pagination.
5. Connect a thin dashboard view to the API; retain static demonstration mode only if clearly labelled.
6. Add API, migration, integration, failure-retry, and reconciliation tests.

## Stage 3 — Security, privacy, and responsible-hiring controls

1. Enforce authentication and deny-by-default authorization; test every role/data-object boundary.
2. Separate identity, assessment, and demographic-monitoring data stores/views.
3. Implement retention, deletion, legal hold, export controls, encryption/key handling, and tamper-evident audit evidence.
4. Add threat model, misuse cases, incident response, backup/restore, and disaster-recovery evidence.
5. Implement fairness monitoring with minimum-cell suppression, stratification, version tracking, and explicit human/legal review gates.
6. Add abuse, authorization, privacy, and destructive-workflow tests.

## Stage 4 — Evaluator and contributor experience

1. Add a quick start that works from a clean clone.
2. Publish architecture decision records, data model, API reference, SQL examples, control-to-test traceability, and demo script.
3. Add contribution, issue, pull-request, security-reporting, and support guidance.
4. Ensure every externally visible claim links to executable evidence or is labelled as planned/design-only.

## Stage 5 — Release candidate

1. Run clean-clone install, seed, migration, test, build, browser, accessibility, privacy, dependency, backup/restore, and release checks.
2. Reconcile all governed KPIs from the executable system.
3. Review the final diff, open risks, release notes, and production-readiness gaps.
4. Request explicit human approval before merge, release, Pages change, or external announcement.

## Exit rule

No stage is complete because documents or mocked screens exist. Completion requires the issue acceptance criteria, executable evidence, CI results, privacy impact statement, and reviewed pull-request diff specified for that stage.
