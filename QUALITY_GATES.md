# Repository Quality Gates

This guide defines the executable checks for this enterprise-oriented structured-hiring reference implementation in development. Local privacy and integrity checks use `scripts/repository_audit.py`; GitHub-hosted merge provenance uses the deliberately separate `scripts/github_provenance_audit.py`.

Passing these gates establishes consistency for the current synthetic demonstration. It does not establish production readiness, security certification, regulatory compliance, selection validity, legal sufficiency, or accessibility conformance.

## Prerequisites

- Git
- Python 3.9 or newer; CI uses Python 3.11
- Poppler command-line tools: `pdfinfo` and `pdftotext`

Install Poppler with `brew install poppler` on macOS or `sudo apt-get install poppler-utils` on Ubuntu.

## Run the gates locally

From the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/repository_audit.py --all
git diff --check
```

A successful audit ends with `PASS repository audit` and exits with status 0. A failed audit exits with status 1 and reports only the finding category and file or abbreviated commit identifier. It deliberately does not echo matched credentials, personal identifiers, or email addresses.

Run a narrower check by repeating `--check` as needed:

```bash
python3 scripts/repository_audit.py --check privacy --check history
```

Supported checks are `paths`, `privacy`, `markdown-links`, `html-links`, `external-scripts`, `pdfs`, `artifacts`, `data`, and `history`.

For a standard-library coverage observation without adding a dependency:

```bash
python3 -m trace --count --missing --summary --coverdir ../repository-audit-coverage --module unittest discover -s tests
```

## Gate matrix

| Gate | Enforced contract |
|---|---|
| Tracked paths | Only documented text, web, data, Python, PDF, and workflow file types are tracked; hidden files and symbolic links are denied except the root ignore file and workflow definitions. |
| Privacy | Tracked text and extracted PDF content contain no binary payloads or matched phone, national-ID, local-path, private-key, credential, or non-synthetic email-domain patterns. |
| Links | Relative Markdown and HTML targets stay inside the repository and resolve to tracked files. |
| Executable scripts | HTML does not load executable JavaScript from an external host. |
| PDFs | Exactly two governed PDFs exist; each has extractable text, five pages, tagging, no encryption, no JavaScript, and its expected page size. |
| Artifacts | Governed HTML, data, PDF, CSS, and Chart.js files match recorded SHA-256 values; the Chart.js 4.4.7 marker is present. |
| Data | Row counts, all 500 composite calculations, hires, time to fill, SLA rows, and adverse-impact ratio reconcile to the governed values. |
| History privacy | A human author must use a user-specific GitHub noreply identity. A committer must use that form too, except that the exact GitHub generic platform service identity is allowed only on a two-parent merge commit. Arbitrary GitHub-domain identities and the platform identity as author are rejected. |
| Hosted provenance | Every reachable commit using the platform service committer must be attributed by GitHub to the exact `web-flow` actor, have a verified signature with a valid reason, have exactly two parents, and be associated with a merged pull request. |

## Identity model

Git stores an **author** and a **committer**. The author identifies who created the change; the committer identifies who created that Git commit object. They can legitimately differ when GitHub's web merge service creates a pull-request merge commit.

Privacy classification and provenance are separate controls:

- The deterministic offline history audit classifies identity metadata. It permits user-specific noreply identities and, only for the committer of a two-parent merge, GitHub's exact generic platform service identity. That service identity represents GitHub infrastructure rather than a person's contact address.
- The hosted provenance audit then proves the platform-shaped commit came from GitHub. It does not trust the metadata string alone.

The policy never allowlists every address from a broad domain. Such a rule would admit arbitrary or attacker-chosen identities that merely look GitHub-related. The platform service identity is also never valid as a human author.

Both CLIs fail with category-only diagnostics and an abbreviated commit identifier. They do not echo identity values, matched secrets, API response bodies, exception strings, or tokens. Tests use constructed synthetic values and sanitized API metadata without address fields.

## CI design

`.github/workflows/quality-gates.yml` runs the deterministic repository-audit job on every pull request and push to `main`. It has read-only contents permission, disables persisted checkout credentials, retrieves full history for identity checks, installs only Poppler from the Ubuntu package repository, runs the Python suite and audit CLI, and checks the changed range for whitespace errors.

A second provenance job runs only after a successful repository audit on pushes to `main`, because that is when GitHub-generated merge commits enter the protected history. That job has only `contents: read` and `pull-requests: read`, does not install runtime dependencies, and fails closed if API evidence is unavailable, incomplete, malformed, or inconsistent. Pull-request code is never given the provenance job's pull-request token permission.

The official GitHub actions are pinned to immutable commit identifiers. Updating either pin requires checking the corresponding official release and commit verification before changing the workflow.

## Known history behavior

Stage 0 was merged by GitHub as commit `e410482fbb50e757ae4a6487eee0eae85eabbc8c`. GitHub placed the account's pre-existing non-noreply address in that merge commit's raw author metadata. The audit permits only that exact immutable commit and does not print the address. This exception documents an existing exposure; it does not remove it or authorize another exception.

PR #15 established the normal GitHub web-merge shape: a protected user-noreply author and GitHub's non-personal platform identity as committer. This is a reusable policy classification, not a one-commit exception. Its provenance must still pass the separate hosted checks.

Future human-authored commits remain subject to the user-noreply requirement. The legacy exception cannot be used by an adjacent commit, and no platform-committer commit is accepted solely because its committer metadata looks trusted.

## Updating governed artifacts

Do not edit the checksum table merely to make a failure disappear. First review the artifact change in its dedicated issue, regenerate or modify it through the documented source workflow, inspect its visible output, rerun privacy and PDF checks, and then update the expected SHA-256 value in `scripts/repository_audit.py` in the same reviewed pull request. PDF regeneration belongs to the separate PDF workstream, not this CI stage.

## Limitations and rollback

The offline audit cannot prove a GitHub actor, signature state, or pull-request association and intentionally does not make those claims. The hosted check depends on GitHub API availability and read permissions; it fails rather than silently downgrading when evidence cannot be established. Neither control proves the real-world identity of a contributor beyond GitHub's reported metadata.

These gates do not run a browser, perform assistive-technology testing, scan dependencies continuously, validate employment-law compliance, test production access control, or certify the synthetic selection model. The Stage 1 issue plan tracks those concerns separately.

Reverting a merge adds a new commit; it does not remove the original commit object from reachable published history. If this identity-policy hotfix is defective, revert the focused hotfix rather than rewriting or force-pushing history.

If the workflow itself causes an unexpected failure, revert the focused CI commit. Do not bypass a failing check or add a new privacy exception without a reviewed root-cause record.
