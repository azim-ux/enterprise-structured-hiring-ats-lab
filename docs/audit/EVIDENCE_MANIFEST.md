# Stage 0 Evidence Manifest

**Evidence date:** 2026-09-02

**Baseline input:** `640406ba742843f99c55ba9f3b8b2f5924291ee9`

**Approved Stage 0 head:** `51455a074db59c8bb87649915e516ca0f58a427f`

**Stage 0 merge:** `e410482fbb50e757ae4a6487eee0eae85eabbc8c`

Commands use neutral placeholders and run from the repository root unless stated otherwise. Local screenshots were inspected but are not public repository artifacts.

## Stage 1A executable source of truth

Stage 0 recorded a point-in-time 38-file review. Stage 1A moves the maintained repository checks into [`scripts/repository_audit.py`](../../scripts/repository_audit.py), with behavior tests in [`tests/test_repository_audit.py`](../../tests/test_repository_audit.py) and operator instructions in the [Repository Quality Gates guide](../../QUALITY_GATES.md).

Run these commands from a fresh clone for the current result:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/repository_audit.py --all
```

The executable gate replaces the former copied command appendices. This manifest explains the Stage 0 evidence and records immutable results; it is not a second implementation of the checks.

The history gate records one exact legacy exception: GitHub's Stage 0 merge commit contains a pre-existing non-noreply author address in raw metadata. The value is never printed. No later commit is excepted, and GitHub email privacy must be enabled before another merge.

## Tool record

| Tool | Version used for Stage 0 |
|---|---|
| Git | 2.50.1 (Apple Git-155) |
| Python | 3.9.6 |
| ripgrep | 15.2.0 |
| shasum | 6.02 |
| Poppler `pdftotext` / `pdfinfo` | 26.04.0 |
| GitHub CLI | 2.97.0 |
| Browser | HeadlessChrome 151.0.7922.34 via the local browser wrapper |

## Stage 0 evidence index

| ID | Claim verified | Method | Immutable result |
|---|---|---|---|
| E01 | Baseline tracked files | Git tree inventory | 28 |
| E02 | Corrected Stage 0 tracked files | Git index inventory | 38 |
| E03 | Tracked PDFs | Git index inventory | 2 |
| E04 | Major-artifact integrity | SHA-256 comparison | Exact values in the artifact table |
| E05 | Reachable history | Git commit and identity review | Three commits at the approved head; identities were noreply before the later GitHub merge |
| E06 | Existing tests | Fresh-clone unittest run | 4 tests passed |
| E07 | Tracked-file privacy | Exact-index text and PDF scan | 38 files passed |
| E08 | High-confidence secrets | Exact-index pattern scan | No findings |
| E09 | Local paths and username | Exact-index pattern scan | No findings |
| E10 | PDF visible content | Text extraction plus all-page render review | Two readable five-page documents; no private content found |
| E11 | PDF metadata and active content | `pdfinfo` | Tagged, unencrypted, no JavaScript; expected sizes |
| E12 | Markdown links | Tracked-target validator | 52 relative links passed |
| E13 | HTML links | Unittest | Relative targets passed |
| E14 | Dataset rows | CSV reconciliation | 5 requisitions, 4,000 candidates, 2,000 interviews |
| E15 | Composite scores | Decimal 40/40/20 recomputation | 500 checked; zero differences |
| E16 | Governed KPIs | CSV reconciliation | 120 hires; 28.5 days; 1,836 SLA rows; AIR 0.87 |
| E17 | Desktop width | Browser DOM measurement at 1440×900 | Document width 1440 |
| E18 | Phone overflow | Browser DOM measurement at 375×812 | Document width 707; overflow reproduced |
| E19 | Slide overlap | Browser rectangle intersection | Controls intersected slide-two card |
| E20 | Tested console flows | Browser console inspection | No errors observed |
| E21 | Chart.js version and integrity | Version marker plus SHA-256 | 4.4.7 and governed hash |
| E22 | Dependency advisory query | GitHub Advisory Database query | No matching advisory at the observation time |

The current executable audit covers E02–E16 and E21 where the claims are deterministic repository properties. Browser observations E17–E20 remain Stage 0 baselines for the later responsive/accessibility workstream. E22 is point-in-time evidence and is not a continuous advisory service.

## Governed SHA-256 artifact hashes

| Artifact | SHA-256 |
|---|---|
| `index.html` | `51765b742caae8ea61c7bb465e01762e9fe987e6ee308d61e11f79ccad9bbbad` |
| `dashboard.html` | `51765b742caae8ea61c7bb465e01762e9fe987e6ee308d61e11f79ccad9bbbad` |
| `slides.html` | `326576edb7ec8e3175996872e55334805ff9f6b595baa87018ec8610fcd8b3d0` |
| `mobile-case-study.html` | `7227193f0b35f0d891756d7ec3d773f5a30b6d5602fbd19be2cfeaf47e0da746` |
| `mobile-case-study.css` | `df7636f62b9275ac70a3a583bb2383f39b4ac6a6760a2834a321739e53d59034` |
| `synthetic_requisitions.csv` | `a5857a0bd2fb824288406611f0afd929f428c40ebe143c1f982e25ed79d20bab` |
| `synthetic_candidates.csv` | `2e9cb4153172b7cf83349b8f49498a8598c621c81c5cfe14441a3fd6fbb57359` |
| `synthetic_interviews.csv` | `07857ea73dbde578b5ead86b16536a967c9193a113b3e0387ee454b0ebb83a36` |
| `Structured_Hiring_and_ATS_Architecture_Case_Study.pdf` | `40d08a823387f81e35a36aac07b10c6cae3ac2940a014d8570bb31f0394b5c14` |
| `Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf` | `11fae9a47a056a2ccd5b6dda97535935237e042cea86e114ade78d91da08cc86` |
| `vendor/chart.umd.min.js` | `206b6e8bb00fc7bba2c7ee80ca41db3e9e05ba7be0aa35abeba9cfd5357f5d0e` |

## Evidence boundary

The browser and advisory results are point-in-time observations. PDF review confirms the current public artifacts, not future regeneration. Passing these checks establishes repository consistency for this synthetic demonstration; it does not establish production readiness, regulatory compliance, security, selection validity, accessibility conformance, or freedom from bias.
