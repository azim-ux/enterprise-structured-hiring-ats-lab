# Stage 0 Baseline Audit

**Audit date:** 2026-09-01

**Baseline commit:** `640406ba742843f99c55ba9f3b8b2f5924291ee9`

**Audit branch:** `audit/stage-0-baseline`

**Scope:** documentation and evidence only; no implementation files changed

Tracking: [delivery epic #1](https://github.com/azim-ux/enterprise-structured-hiring-ats-lab/issues/1) · [Stage 0 issue #7](https://github.com/azim-ux/enterprise-structured-hiring-ats-lab/issues/7)

## Positioning boundary

The repository is a **portfolio simulation today** and is intended to evolve into an **enterprise-oriented structured-hiring reference implementation**. It is not an enterprise-ready ATS, a validated selection instrument, a legal opinion, or an employment-decision service.

## Verified repository inventory

The baseline contains 28 tracked files totaling 9,253,590 bytes:

| Area | Evidence | Baseline result |
|---|---|---|
| Browser application | `index.html`, `dashboard.html` | Both are 3,480,689 bytes and byte-for-byte identical (`SHA-256 51765b…bbbad`) |
| Presentation surfaces | `slides.html`, `mobile-case-study.html`, `mobile-case-study.css` | Five-slide deck and five-page phone source |
| Published PDFs | Two case-study PDFs | Both tagged, five pages, unencrypted, and contain no JavaScript |
| Synthetic data | Three CSV files | 5 requisitions, 4,000 candidates, 2,000 interview competency rows |
| Governance documentation | 11 Markdown files plus `README.md` | Methodology, RACI, validity, fairness, privacy, UAT, and data dictionary |
| Test code | `tests/test_repository_integrity.py` | Four `unittest` cases; no CI workflow |
| Runtime dependency | `vendor/chart.umd.min.js` | Chart.js 4.4.7 with preserved MIT license |
| Repository history | Full remote history | One commit, authored with a GitHub noreply address |

Each dashboard embeds 3,448,439 characters of JSON: requisitions (2,077), candidates (2,432,524), and interviews (1,013,838). Because the two dashboard files are identical, the repository publishes the same large payload twice.

## Baseline verification

| Check | Result | Qualification |
|---|---|---|
| `python3 -m unittest -v tests/test_repository_integrity.py` | 4/4 passed in a clean clone | The privacy test scans untracked and ignored files; a generated `.gstack` file caused a reproducible false failure before local audit artifacts were moved outside the repository |
| Exact-index privacy/link audit | Passed across 28 tracked files | Scanned text, CSV, HTML, PDF text/metadata, file paths, secrets, and internal links |
| Data reconciliation | Passed | 500 composite scores recomputed with 40/40/20 and produced zero errors; all candidate requisition references resolve |
| Live dashboard | HTTP 200; search and scorecard flow passed | Tested at 1440×900 and 375×812; no console errors in tested flow |
| Live slides | Next-slide control passed | No console errors; phone overlap defect recorded |
| Phone case-study HTML | HTTP 200 | 375 px viewport had 375 px document width |
| Dependency advisory query | No GitHub Advisory Database match for `chart.js@4.4.7` on 2026-09-01 | This is a point-in-time query, not continuous monitoring |
| Semantic code graph | Not available | Graphify discovered 3 code files, 16 documents, and 3 PDFs, but its external Gemini request failed with `401 UNAUTHENTICATED`; no generated semantic graph is treated as evidence |

## Material findings

1. **The executable system is a static demonstration.** There is no server, database, authentication, authorization enforcement, durable audit log, queue worker, API, or integration layer.
2. **Documented controls are not implemented controls.** The RBAC, erasure, encryption, backup, incident, and transition controls are design specifications only.
3. **The current README overstates automated coverage.** It says the suite checks exact inventory, schemas, references, scoring arithmetic, pagination, embedded JSON parity, and the slide contract; the four tests do not implement most of those assertions.
4. **The mobile dashboard overflows horizontally.** At a 375 px viewport, the document scroll width is 707 px. The pipeline table and closed drawer geometry are the main contributors.
5. **The slide navigation overlays content on a phone.** On slide two, fixed previous/next controls obscure the lower control card.
6. **The two dashboard entry points are exact multi-megabyte duplicates.** This raises maintenance, review, and transfer cost.
7. **There is no continuous quality gate.** The repository has no `.github/workflows` files and no automated browser, accessibility, dependency, or release validation.
8. **One methodology statement is stale.** `METHODOLOGY_AND_LIMITATIONS.md` says Tailwind CSS and Chart.js use CDNs, while the current dashboard uses custom CSS and self-hosted Chart.js with no Tailwind runtime.

## Stage 0 deliverables

- [Architecture map](ARCHITECTURE_MAP.md)
- [Test-coverage map](TEST_COVERAGE_MAP.md)
- [Claim-versus-evidence matrix](CLAIM_EVIDENCE_MATRIX.md)
- [Privacy and supply-chain assessment](PRIVACY_AND_SUPPLY_CHAIN_ASSESSMENT.md)
- [Mobile and accessibility defect report](MOBILE_ACCESSIBILITY_REPORT.md)
- [Prioritized implementation backlog](IMPLEMENTATION_BACKLOG.md)
- [Do-not-touch list](DO_NOT_TOUCH.md)
- [Production-readiness gap register](../../PRODUCTION_READINESS_GAP.md)

## Decision gate

This audit creates evidence and backlog only. Stage 1 must not begin until this pull request and its linked issues have been reviewed. No merge, release, repository-setting change, or external announcement is authorized by this document.
