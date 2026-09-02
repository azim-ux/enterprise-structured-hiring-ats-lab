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

The history gate records one exact legacy exception: GitHub's Stage 0 merge commit contains a pre-existing non-noreply author address in raw metadata. The value is never printed. No later commit is excepted.

## Stage 1A.1 identity-policy evidence

The post-merge quality gate for PR #15 exposed a policy false positive: the human author used the protected user-noreply form, while GitHub's web merge service used its exact non-personal platform identity as committer. The original policy incorrectly treated those two roles as equivalent.

Stage 1A.1 separates deterministic privacy classification from hosted provenance verification. The offline audit permits the exact platform service identity only as committer on a two-parent merge and keeps the existing immutable legacy exception. The push-to-main provenance job independently requires the exact `web-flow` actor, a verified signature with valid reason, two parents, and association with a merged pull request.

Test-first evidence was captured before the implementation: 40 tests ran with 2 expected failures and 9 expected errors because the new contracts and module did not yet exist. The completed suite runs 55 tests, including positive, negative, malformed-evidence, unavailable-API, sanitized PR #15-shape, and redaction cases. Standard-library trace observation reports at least 92% line coverage for the provenance module and 91% for the repository auditor.

An authenticated, field-filtered hosted verification confirmed two reachable platform-generated merge commits. The command emitted only the verified count; no address or API response body was logged. See the [identity privacy and provenance method](IDENTITY_PRIVACY_AND_PROVENANCE_METHOD.md).

## Stage 1B data-contract evidence

Stage 1B adds [`scripts/data_contracts.py`](../../scripts/data_contracts.py) as the single executable source for synthetic-data contracts and delegates the repository auditor's existing `data` gate to it. No CSV, dashboard, slide, PDF, dependency, workflow, route, or repository setting is changed.

Test-first evidence was captured in two red cycles: the focused suite first failed to import the intentionally absent validator, then three added mutations failed for temporal, per-requisition cohort, and displayed-KPI rules before those checks were implemented. The completed branch runs 92 tests with zero skips. Standard-library line tracing reports 95.4% for the new validator, 92% for the repository auditor, and 92% for the hosted-provenance module.

## Stage 1C truthful PDF-artifact evidence

The untouched Stage 1B baseline passed 92 tests and the complete 47-file audit. Before regeneration, both PDFs had five pages, extractable text, tagging, no encryption, no JavaScript, and their intended dimensions. The earlier desktop PDF was 374,276 bytes with SHA-256 `40d08a823387f81e35a36aac07b10c6cae3ac2940a014d8570bb31f0394b5c14`; the earlier phone PDF was 408,388 bytes with SHA-256 `11fae9a47a056a2ccd5b6dda97535935237e042cea86e114ade78d91da08cc86`.

The initial test-first claims cycle produced two expected failures against the unchanged source HTML and extracted PDF text. It detected affirmative wording that implied an enterprise runtime, operational knockout and erasure, implemented demographic isolation, and active role permissions. A later focused red cycle proved that a qualified mention could not be allowed to hide a second affirmative claim and that only two exact, metadata-free visual-evidence PNG paths may be tracked.

The revised sources qualify modeled results, design proposals, and absent controls in context. The full reasoning is recorded in the [claim-evidence matrix](CLAIM_EVIDENCE_MATRIX.md). The source-to-output contract is:

| Source | Generated output | Pages | Page size |
|---|---|---:|---:|
| `slides.html` | `Structured_Hiring_and_ATS_Architecture_Case_Study.pdf` | 5 | 960 × 540 points |
| `mobile-case-study.html` + `mobile-case-study.css` | `Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf` | 5 | 420 × 720 points |

Regeneration is automated and local; the generated PDFs are not manually edited:

```bash
python3 scripts/regenerate_pdfs.py
```

The command uses local Chrome or Chromium, disables background networking, suppresses browser print headers/footers, and replaces only browser-generated creation and modification dates with a fixed neutral timestamp. Two consecutive runs at the recorded tool versions produced the same final SHA-256 values.

| PDF check | Desktop | Phone |
|---|---|---|
| Final SHA-256 | `0541bee04409a6ca2fa416644fa6df38496eaf6d07867371a3b199066e021626` | `d9c875aba042fc56da6feaf8aa33c5938d22505b28632718cf73851c080c4824` |
| File size | 397,296 bytes | 459,050 bytes |
| Searchable text | Present | Present |
| Tagged / encrypted | Yes / no | Yes / no |
| JavaScript / forms | No / none | No / none |
| Embedded files | 0 | 0 |
| External URL annotations | 0 | 2 intended links on page 5 |
| Local paths or private identifiers in text/metadata | None detected | None detected |

All ten final pages were rendered with Poppler at 144 DPI and inspected individually. The two optimized contact sheets are included as governed evidence: [desktop pages 1–5](visual/desktop-final-pages.png) and [phone pages 1–5 at a 390-pixel-wide simulation](visual/mobile-final-pages.png).

| Page | Visual inspection result |
|---|---|
| Desktop 1 | Complete title, qualification, and chips; no clipping, overlap, or broken glyphs observed. |
| Desktop 2 | Six-stage architecture and three control cards remain inside printable bounds. |
| Desktop 3 | Formula and halo-control card are complete after print spacing correction. |
| Desktop 4 | Fairness metrics and qualification list are complete and visually separated. |
| Desktop 5 | Five modeled metrics and three action blocks remain legible with no footer collision. |
| Phone 1 | Use boundary and modeled KPI labels are visible without horizontal scrolling. |
| Phone 2 | Header and all five architecture steps are complete after print pagination correction. |
| Phone 3 | Six evidence cards and interpretation qualification remain legible. |
| Phone 4 | Full header, six control statements, limitation language, and footer are visible after targeted print-only spacing. |
| Phone 5 | Four decision cards, research qualification, and two intended links remain complete. |

The phone pages were also resampled to a representative 390-pixel width and reviewed at normal fit-to-width. They require no horizontal scrolling; page 4 remains deliberately denser than the other pages but its qualification text is legible. This is a visual observation, not accessibility-conformance evidence.

The completed local suite runs 107 tests with zero failures and zero skips. Full-suite standard-library tracing reports 100.0% for the claims policy, 92.1% for PDF regeneration, 91.2% for the repository auditor, 95.4% for the unchanged data-contract validator, 92.9% for hosted provenance, and 93.8% across all five first-party script modules.

## Tool record

| Tool | Version used for Stage 0 |
|---|---|
| Git | 2.50.1 (Apple Git-155) |
| Python | 3.9.6 |
| ripgrep | 15.2.0 |
| shasum | 6.02 |
| Poppler `pdftotext` / `pdfinfo` | 26.04.0 |
| GitHub CLI | 2.97.0 |
| Browser | Google Chrome 151.0.7922.109 / HeadlessChrome 151 |

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
| E23 | Stage 1A.1 test-first baseline | Unittest before implementation | 40 ran; 2 expected failures and 9 expected errors |
| E24 | Final identity/provenance contracts | Complete unittest suite | 55 passed; zero failures and zero skips |
| E25 | Offline repository audit | Executable audit | 45 tracked files passed after documentation commit |
| E26 | Hosted platform provenance | GitHub API field allowlist | Two reachable merges verified; category/count output only |
| E27 | Changed audit-module coverage | Standard-library trace | Provenance 92%; repository audit 91% |
| E28 | Stage 1B test-first baseline | Focused unittest before implementation | Validator import failed as expected; no source artifact changed |
| E29 | Stage 1B second red cycle | Three focused mutation tests | Temporal, requisition-cohort, and displayed-KPI mutations failed before implementation |
| E30 | Complete data contracts | Standard-library unittest | 92 passed; zero failures and zero skips |
| E31 | Data-contract coverage | Module-filtered standard-library line tracing | Data contracts 95.4%; repository audit 92%; provenance 92% |
| E32 | Source artifact immutability | Git diff and governed SHA-256 audit | CSV, dashboard, slide, PDF, dependency, workflow, and public route content unchanged |
| E33 | Stage 1C baseline | Unittest and repository audit before source edits | 92 passed, zero skips; 47 tracked files passed |
| E34 | Claims red cycle | Source HTML and extracted-PDF assertions | Two expected failures on unsupported wording before correction |
| E35 | Contextual claims policy | Positive qualification and negative mutation tests | Every match is evaluated; rule identifiers only; current HTML and PDF text pass |
| E36 | Deterministic PDF regeneration | Two consecutive local builds and SHA-256 comparison | Both output hashes repeated exactly |
| E37 | PDF structure and privacy | `pdfinfo`, `pdftotext`, `pdfdetach`, URL inventory, and repository audit | Five pages each; intended sizes; no encryption, JavaScript, forms, embedded files, private paths, or unsupported governed claims detected |
| E38 | Ten-page visual review | 144-DPI page renders plus 390-pixel phone simulation | All ten pages inspected; no clipping, overlap, missing glyphs, or horizontal overflow observed after targeted fixes |
| E39 | Visual-evidence governance | Exact path, SHA-256, size, dimensions, metadata-chunk, and privacy review | Two optimized contact sheets; full-resolution page renders remain untracked |
| E40 | Stage 1C complete local gate | Full unittest, audit, whitespace, workflow, and trace runs | 107 passed, zero skips; 53 tracked files passed; 93.8% aggregate first-party script coverage |

The current executable audit covers E02–E16 and E21 where the claims are deterministic repository properties. Browser observations E17–E20 remain Stage 0 baselines for the later responsive/accessibility workstream. E22 is point-in-time evidence and is not a continuous advisory service.

## Governed SHA-256 artifact hashes

| Artifact | SHA-256 |
|---|---|
| `index.html` | `51765b742caae8ea61c7bb465e01762e9fe987e6ee308d61e11f79ccad9bbbad` |
| `dashboard.html` | `51765b742caae8ea61c7bb465e01762e9fe987e6ee308d61e11f79ccad9bbbad` |
| `slides.html` | `6a94bf0651578231195856a41d0f7ba3f038a11b0ac9bcdcf669bd830e93ac79` |
| `mobile-case-study.html` | `b58d8cd5ab743bacbf93d166e163e8b2d6a66764ad5bbf2807d39919c9c64c31` |
| `mobile-case-study.css` | `96ef26afcc038f329efb46b0395b7db299c83712cc9ff7e054f6d7a768316872` |
| `synthetic_requisitions.csv` | `a5857a0bd2fb824288406611f0afd929f428c40ebe143c1f982e25ed79d20bab` |
| `synthetic_candidates.csv` | `2e9cb4153172b7cf83349b8f49498a8598c621c81c5cfe14441a3fd6fbb57359` |
| `synthetic_interviews.csv` | `07857ea73dbde578b5ead86b16536a967c9193a113b3e0387ee454b0ebb83a36` |
| `Structured_Hiring_and_ATS_Architecture_Case_Study.pdf` | `0541bee04409a6ca2fa416644fa6df38496eaf6d07867371a3b199066e021626` |
| `Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf` | `d9c875aba042fc56da6feaf8aa33c5938d22505b28632718cf73851c080c4824` |
| `docs/audit/visual/desktop-final-pages.png` | `9f912e5006e87820378777a016d47aaa74035e0c309f5282c96c8fa9ea41be51` |
| `docs/audit/visual/mobile-final-pages.png` | `4ac1764391146fe31ab4e0b9aa3bec376a72c1b4c40cd5271f94733725934109` |
| `vendor/chart.umd.min.js` | `206b6e8bb00fc7bba2c7ee80ca41db3e9e05ba7be0aa35abeba9cfd5357f5d0e` |

## Evidence boundary

The browser and advisory results are point-in-time observations. PDF review confirms the current public artifacts, not future regeneration. Passing these checks establishes repository consistency for this synthetic demonstration; it does not establish production readiness, regulatory compliance, security, selection validity, accessibility conformance, or freedom from bias.
