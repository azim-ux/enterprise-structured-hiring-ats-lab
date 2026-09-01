# Test-Coverage Map

## Executed automated suite

The repository has one Python module with four `unittest` cases. A fresh-clone run passed 4/4 on 2026-09-02.

| Test | What it actually asserts | Important omissions |
|---|---|---|
| `test_required_assets_exist` | Ten named files exist | Exact inventory, documentation set, licenses, file integrity, PDF page count |
| `test_reconciled_metrics` | 5/4,000/2,000 row counts; 120 hires; 28.5 days; 1,836 SLA rows; 0.87 AIR | Schemas, ID uniqueness, foreign keys, all stage counts, all 500 composite calculations, per-requisition totals, rounding policy |
| `test_no_pii_secrets_or_local_paths` | A small regex set across readable non-PDF files | PDFs, Git history, emails, passports, Emirates IDs, broader credentials, binary/archive inspection; it also scans ignored tooling artifacts |
| `test_relative_html_links_resolve_inside_repository` | Local `href`/`src` targets from top-level HTML exist and stay inside the repo | HTTP status, fragments, Markdown links, case-sensitive deployment behavior, download semantics, external links |

## Claim mismatch

At the audited baseline, the README said the acceptance suite checked “exact inventory, schemas, row counts, references, scoring arithmetic, KPI reconciliation, privacy patterns, enterprise pagination controls, embedded JSON parity, and five-slide contract.” The current implementation verifies only part of row counts, KPI reconciliation, basic privacy patterns, required assets, and local HTML link existence. The Stage 0 branch corrects the README to match those four implemented tests.

## Manual/live baseline coverage

| Surface | Coverage performed | Result |
|---|---|---|
| Dashboard desktop | Load, viewport width, screenshot | Passed; 1440 px document width at 1440 px viewport |
| Dashboard phone | Load, screenshot, horizontal-overflow measurement | Failed layout check; 707 px document width at 375 px viewport |
| Candidate search | Search for synthetic ID `CAND-2026-0013` | Passed; one expected row |
| Scorecard drawer | Open on phone, inspect accessible close control, close | Passed in tested path |
| Slide deck | Next control on phone, screenshot, console | Functional; content overlap observed |
| Phone case study | Load and width check at 375×812 | Passed; no document-level overflow |
| Console | Tested dashboard and slide interactions | No console errors observed |
| Basic semantics | Page language/title, headings, landmarks, control names, dialog metadata | Present in sampled dashboard state |

## Coverage gaps for Stage 1

- No CI workflow or branch quality gate.
- No repeatable browser/E2E suite.
- No automated viewport matrix or overflow assertion.
- No automated accessibility engine, keyboard-flow suite, focus-trap assertion, contrast check, reduced-motion check, or screen-reader verification.
- No test for dashboard/CSV parity or prevention of duplicate application sources.
- No full schema, foreign-key, uniqueness, enumerated-value, or formula contract.
- No tests for every documented UAT scenario; the UAT register is a specification, not an execution record.
- No PDF text, metadata, page-count, link, or rendering regression test.
- No dependency integrity/hash check, update automation, or advisory scan in CI.
- No performance budget.

## Stage 1 quality-gate contract

The first implementation stage should convert the evidence above into deterministic CI checks: clean-clone unit tests, exact tracked-file privacy scanning, schema and KPI contracts, link validation, browser smoke tests, phone-width assertions, accessibility automation, dependency checks, and a documented performance budget. Passing tests must not be described as production readiness.
