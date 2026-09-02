# Repository Quality Gates

This guide defines the executable checks for this enterprise-oriented structured-hiring reference implementation in development. Local runs and CI call the same Python entry point: `scripts/repository_audit.py`.

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
| History | New author and committer addresses must use the GitHub noreply domain. |

## CI design

`.github/workflows/quality-gates.yml` runs on every pull request and push to `main`. It has read-only repository permission, disables persisted checkout credentials, retrieves full history for identity checks, installs only Poppler from the Ubuntu package repository, runs the Python suite and audit CLI, and checks the PR diff for whitespace errors.

The official GitHub actions are pinned to immutable commit identifiers. Updating either pin requires checking the corresponding official release and commit verification before changing the workflow.

## Known history exception

Stage 0 was merged by GitHub as commit `e410482fbb50e757ae4a6487eee0eae85eabbc8c`. GitHub placed the account's pre-existing non-noreply address in that merge commit's raw author metadata. The audit permits only that exact immutable commit and does not print the address. This exception documents an existing exposure; it does not remove it or authorize another exception.

Before any later pull request is merged, enable GitHub's email-privacy setting and verify that the merge identity will use a noreply address. Every other reachable commit is rejected if either author or committer identity is not noreply.

## Updating governed artifacts

Do not edit the checksum table merely to make a failure disappear. First review the artifact change in its dedicated issue, regenerate or modify it through the documented source workflow, inspect its visible output, rerun privacy and PDF checks, and then update the expected SHA-256 value in `scripts/repository_audit.py` in the same reviewed pull request. PDF regeneration belongs to the separate PDF workstream, not this CI stage.

## Limitations and rollback

These deterministic gates do not run a browser, perform assistive-technology testing, scan dependencies continuously, validate employment-law compliance, test production access control, or certify the synthetic selection model. The Stage 1 issue plan tracks those concerns separately.

If the workflow itself causes an unexpected failure, revert the focused CI commit. Do not bypass a failing check or add a new privacy exception without a reviewed root-cause record.
