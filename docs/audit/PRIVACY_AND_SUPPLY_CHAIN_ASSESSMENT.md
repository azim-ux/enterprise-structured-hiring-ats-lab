# Privacy and Supply-Chain Assessment

## Privacy exposure

### Verified public boundary

- Reachable human-authored commits are checked for user-specific GitHub noreply identities. GitHub platform-committed merges are classified separately and require hosted actor, signature, parent, and merged-PR provenance.
- An exact-index scan covered all 28 baseline files and all 38 corrected PR-branch files, including extracted PDF text and metadata.
- No personal phone number, Aadhaar, PAN, passport, Emirates ID, private email, credential, secret key, macOS home-directory path, hidden artifact, or broken internal link was detected.
- Candidate names follow the synthetic pattern `Synthetic Candidate ####`; APD is explicitly fictional.
- Published PDFs are unencrypted but contain synthetic/public material only. They contain no JavaScript.

The baseline findings apply to commit `640406b`; the 38-file result applies to the corrected PR branch. Every later change requires the same tracked-file and history checks.

### Exposure that is safe only because the data is synthetic

Both dashboard files deliver all 4,000 candidate rows, including demographic cohort values, to every browser. Hiding cohort fields in the UI is not access control. This architecture must never receive real candidate or employee data.

### Gaps

- No runtime authentication, authorization, consent, retention, deletion, encryption-at-rest, audit logging, or incident workflow exists.
- The checked-in privacy test omits several identifiers and file formats and is sensitive to ignored local tooling artifacts.
- No data classification file or machine-enforced “synthetic only” schema marker exists.
- Hosted provenance depends on GitHub API availability and reports; it fails closed but cannot independently prove a contributor's real-world identity.
- GitHub secret scanning and push protection are enabled, but non-provider patterns and validity checks are disabled; repository settings were observed only and were not changed.

## Dependency and supply chain

| Item | Baseline | Assessment |
|---|---|---|
| Client runtime | Vendored Chart.js 4.4.7 | Version is pinned and license preserved |
| Network-loaded scripts | None in the dashboard | Reduces CDN/runtime dependency risk |
| Package manifest/lockfile | None | No provenance, checksum, automated update, or reproducible dependency installation workflow |
| Advisory query | GitHub Advisory Database returned no match for `chart.js@4.4.7` on 2026-09-02 | Point-in-time only; not a guarantee |
| Upstream release | Chart.js v4.5.1 is the latest official release observed (published 2025-10-13) | Vendored version is behind upstream; upgrade impact is unassessed |
| CI dependency scan | None | No continuous detection |
| Licenses | Repository MIT plus Chart.js MIT notice | Present; research/OpenCATS are referenced but not redistributed |

## Required Stage 1 controls

- Scan `git ls-files` rather than every local file and extend PII/secret patterns and PDF checks.
- Verify commit author domains and forbidden paths across full reachable history.
- Add a cryptographic checksum and provenance note for vendored Chart.js.
- Add scheduled/admission dependency advisory checks.
- Fail CI if externally hosted executable scripts are introduced without review.
- Keep all datasets demonstrably synthetic and prevent real contact/identity fields from entering the public repository.

## Limit

This is a repository-level privacy and supply-chain baseline, not a GDPR/DPDP compliance opinion, penetration test, or professional security assessment.
