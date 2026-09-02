# Test-Coverage Map

## Executed automated suite

The Stage 1B branch has 92 standard-library `unittest` cases: the 55-test Stage 1A.1 baseline plus 34 focused data-contract tests and 3 repository-audit integration tests. The final fresh-clone result must remain 92 passed, zero failures, and zero skips.

| Area | Positive coverage | Negative and failure coverage |
|---|---|---|
| Tracked-file privacy | Synthetic/public content and permitted file types | Phone and identity patterns, local paths, credentials, binary payloads, hidden/private paths, symlinks, non-synthetic domains |
| Links and scripts | Tracked relative Markdown/HTML targets and self-hosted scripts | Missing targets, repository escape, and external executable scripts |
| PDFs and artifacts | Text, metadata, page geometry, tagging, inactive content, governed hashes, pinned Chart.js marker | Wrong metadata, active PDF content, missing/mutated artifacts, dependency-marker drift |
| CSV structure | Exact ordered schemas, required/nullable fields, types, dates, score ranges and precision | Missing, duplicate, unexpected columns; malformed rows; empty required values; invalid type/date/range/precision |
| Keys and progression | Unique/sequential IDs, foreign keys, candidate/requisition pairs, enums, temporal order, downstream stage fields, offers, dispositions and four-event finalist sets | Duplicate/gapped IDs, orphan/mismatched references, invalid enum, impossible transition, inconsistent date/offer/disposition/event state |
| Arithmetic and totals | All 500 40/40/20 composites, 2,000 BARS means, bias gaps, decimal half-up rounding, deterministic ties, requisition funnels, cohort progression, 120 hires, 28.5 days, 1,836 SLA rows and AIR 0.87 | Independent component/result/gap mutations, missing/corrupt scores, requisition and cohort drift, 48-hour boundary inversion and displayed-KPI drift |
| Published parity | Both routes preserve all three CSVs after string/null normalization; halo values; five slide IDs/order/labels; 25/50 pagination controls and bounded model | Missing/additional/modified JSON records and fields, malformed blocks, every protected halo-field mutation, slide/control drift, invalid page sizes/source/bounds |
| Offline history privacy | User-noreply author/committer; exact platform committer on a two-parent merge; documented legacy exception | Personal author/committer, arbitrary GitHub-domain identity, platform author, single-parent platform committer, adjacent misuse of legacy exception |
| Hosted merge provenance | Sanitized PR #15 merge shape; exact actor; valid verified signature; two parents; merged-PR association | Wrong actor, bad/missing signature, parent mismatch, no/mismatched PR, malformed response, unavailable API, invalid context |
| Redaction | Passing CLIs emit counts | Failures emit only category, path or abbreviated commit; matched identities, secrets, responses, exception details, and tokens are not emitted |
| Workflow | Immutable action pins and push-only hosted provenance job | Contract requires read-only contents and job-scoped pull-request permission |

## Coverage observation

The standard-library `trace` run on 2026-09-02 reports:

- `scripts/github_provenance_audit.py`: 92% line coverage.
- `scripts/repository_audit.py`: 92% line coverage.
- `scripts/data_contracts.py`: 95.4% line coverage (667 of 699 executable lines).

This is line execution evidence, not proof that every semantic state or external failure mode has been modeled.

## Test-first evidence

Before Stage 1B implementation, the focused module failed to import because the validator intentionally did not exist. A second red cycle produced three expected failures for temporal consistency, requisition-level cohort progression, and displayed KPI drift. After implementation and error-path coverage, all 92 tests pass. The 37 Stage 1B additions comprise 11 positive or mixed current-behavior tests and 26 negative mutation/error-path tests; subtests independently mutate every composite component, requisition total, halo-control field, dashboard route, and protected relationship.

## Remaining Stage 1 gaps

- Browser-verifiable pagination, responsive viewport matrices, keyboard/focus behavior, automated accessibility checks, and performance budgets.
- Continuous dependency advisory monitoring.
- Real-world identity proof beyond metadata reported and signed by GitHub.
- Availability of the hosted provenance check when GitHub's API or token permission is unavailable; the control intentionally fails closed.

Passing this suite establishes repository consistency for the current synthetic demonstration. It does not establish production readiness, legal compliance, selection validity, accessibility conformance, or security certification.
