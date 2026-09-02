# Test-Coverage Map

## Executed automated suite

The Stage 1A.1 branch has 55 standard-library `unittest` cases. The suite covers the original repository integrity gates plus the identity-policy hotfix. The final fresh-clone result must remain 55 passed, zero failures, and zero skips.

| Area | Positive coverage | Negative and failure coverage |
|---|---|---|
| Tracked-file privacy | Synthetic/public content and permitted file types | Phone and identity patterns, local paths, credentials, binary payloads, hidden/private paths, symlinks, non-synthetic domains |
| Links and scripts | Tracked relative Markdown/HTML targets and self-hosted scripts | Missing targets, repository escape, and external executable scripts |
| PDFs and artifacts | Text, metadata, page geometry, tagging, inactive content, governed hashes, pinned Chart.js marker | Wrong metadata, active PDF content, missing/mutated artifacts, dependency-marker drift |
| Data and KPIs | 5 requisitions, 4,000 candidates, 2,000 interviews, 500 composites, 120 hires, 28.5 days, 1,836 SLA rows, AIR 0.87 | Reconciliation failure is category-only |
| Offline history privacy | User-noreply author/committer; exact platform committer on a two-parent merge; documented legacy exception | Personal author/committer, arbitrary GitHub-domain identity, platform author, single-parent platform committer, adjacent misuse of legacy exception |
| Hosted merge provenance | Sanitized PR #15 merge shape; exact actor; valid verified signature; two parents; merged-PR association | Wrong actor, bad/missing signature, parent mismatch, no/mismatched PR, malformed response, unavailable API, invalid context |
| Redaction | Passing CLIs emit counts | Failures emit only category, path or abbreviated commit; matched identities, secrets, responses, exception details, and tokens are not emitted |
| Workflow | Immutable action pins and push-only hosted provenance job | Contract requires read-only contents and job-scoped pull-request permission |

## Coverage observation

The standard-library `trace` run on 2026-09-02 reports:

- `scripts/github_provenance_audit.py`: 92% line coverage.
- `scripts/repository_audit.py`: 91% line coverage.

This is line execution evidence, not proof that every semantic state or external failure mode has been modeled.

## Test-first evidence

Before policy implementation, the expanded 40-test run produced 2 expected failures and 9 expected errors. The failures represented the existing false positive and missing workflow contract; the errors represented the intentionally absent identity-record and provenance interfaces. After implementation and edge-case hardening, 55 tests pass.

## Remaining Stage 1 gaps

- Exact CSV schemas, nullability, identifier sequencing, foreign keys, enumerations, downstream stage consistency, and per-requisition totals.
- Embedded dashboard JSON-to-CSV parity and five-slide content contracts.
- Browser-verifiable pagination, responsive viewport matrices, keyboard/focus behavior, automated accessibility checks, and performance budgets.
- Continuous dependency advisory monitoring.
- Real-world identity proof beyond metadata reported and signed by GitHub.
- Availability of the hosted provenance check when GitHub's API or token permission is unavailable; the control intentionally fails closed.

Passing this suite establishes repository consistency for the current synthetic demonstration. It does not establish production readiness, legal compliance, selection validity, accessibility conformance, or security certification.
