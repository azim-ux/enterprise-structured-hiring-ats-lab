# Test-Coverage Map

## Executed automated suite

The current branch has 119 standard-library `unittest` cases: the 92-test Stage 1B baseline plus five contextual-claims tests, eight deterministic-regeneration tests, two visual-evidence/PDF-metadata policy tests, six desktop print-design tests, and six LinkedIn mobile print-design tests. The final fresh-clone result must remain 119 passed, zero failures, and zero skips.

| Area | Positive coverage | Negative and failure coverage |
|---|---|---|
| Tracked-file privacy | Synthetic/public content, permitted file types, and two exact visual-evidence paths | Phone and identity patterns, local paths, credentials, binary payloads, hidden/private paths, symlinks, non-synthetic domains, arbitrary PNGs, oversized or metadata-bearing contact sheets |
| Links and scripts | Tracked relative Markdown/HTML targets and self-hosted scripts | Missing targets, repository escape, and external executable scripts |
| Claims | Current HTML and extracted PDF text; clearly labelled proposals, absent controls, and review requirements | Affirmative production, runtime access, erasure, compliance, fairness, validity, and accessibility mutations; qualified first mention followed by prohibited later claim |
| PDFs and artifacts | Text, metadata, page geometry, tagging, inactive content, no forms, governed source/output/contact-sheet hashes, pinned Chart.js marker | Wrong metadata, active PDF content, forms, missing/mutated artifacts, dependency-marker drift, incomplete volatile-date normalization |
| Desktop print design | Print type targets, WCAG-AA color tokens, five editorial structures, five nonempty pages, required claims/KPIs, 12-point visible-text floor, text bounds, and reviewed mobile-artifact hash | Missing/invalid typography or color tokens, low contrast, retired pill/card structures, empty/missing text, undersized or out-of-bounds text, mobile hash drift |
| LinkedIn mobile print design | Five expert-facing prompts, editorial proof rail, evidence path, formula panel, halo-control case, fairness equation, review sequence, deterministic print tokens, WCAG-AA light-page palette, five nonempty pages, required evidence, and page bounds | Missing narrative step, generic card/pill regression, missing or invalid print tokens, low-contrast light-page text, missing evidence, undersized text, and out-of-bounds content |
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

The full 113-test standard-library trace reports:

- `scripts/claims_policy.py`: 100.0% (40 of 40 executable lines).
- `scripts/regenerate_pdfs.py`: 92.1% (58 of 63).
- `scripts/repository_audit.py`: 91.2% (404 of 443).
- `scripts/data_contracts.py`: 95.4% (667 of 699), unchanged above the Stage 1B target.
- `scripts/github_provenance_audit.py`: 92.9% (118 of 127).
- All five first-party script modules combined: 93.8% (1,287 of 1,372).

## Test-first evidence

Before Stage 1B implementation, the focused module failed to import because the validator intentionally did not exist. A second red cycle produced three expected failures for temporal consistency, requisition-level cohort progression, and displayed KPI drift. After implementation and error-path coverage, all 92 tests pass. The 37 Stage 1B additions comprise 11 positive or mixed current-behavior tests and 26 negative mutation/error-path tests; subtests independently mutate every composite component, requisition total, halo-control field, dashboard route, and protected relationship.

Stage 1C began with source and extracted-PDF assertions that failed on the earlier unsupported wording. The implementation adds two current-artifact positive tests, qualified-language cases, affirmative mutation cases across eight claim categories, a regression proving one qualified occurrence cannot mask a later claim, deterministic metadata normalization tests, stable local source/output mapping, and positive/negative PNG governance checks.

## Remaining Stage 1 gaps

- Browser-verifiable pagination, responsive viewport matrices, keyboard/focus behavior, automated accessibility checks, and performance budgets.
- Continuous dependency advisory monitoring.
- Formal PDF tag-tree, assistive-technology, and accessibility-conformance testing.
- General natural-language truth verification beyond the explicit governed claims policy.
- Cross-browser deterministic PDF output; a browser/toolchain upgrade can change byte output and requires review.
- Real-world identity proof beyond metadata reported and signed by GitHub.
- Availability of the hosted provenance check when GitHub's API or token permission is unavailable; the control intentionally fails closed.

Passing this suite establishes repository consistency for the current synthetic demonstration. It does not establish production readiness, legal compliance, selection validity, accessibility conformance, or security certification.
