# Stage 0 Evidence Manifest

**Evidence date:** 2026-09-02

**Baseline input:** `640406ba742843f99c55ba9f3b8b2f5924291ee9`

**PR input:** `audit/stage-0-baseline` checked out at `HEAD`. Because this manifest is part of the PR commit, the exact immutable input is obtained with `git rev-parse HEAD` after checkout and is also displayed by PR #8.

Commands use `<repo>` or `<fresh-clone>` as neutral placeholders. Run them from the repository root unless stated otherwise. Local screenshots were inspected but are not public repository artifacts.

## Tool record

| Tool | Version used |
|---|---|
| Git | 2.50.1 (Apple Git-155) |
| Python | 3.9.6 |
| ripgrep | 15.2.0 |
| shasum | 6.02 |
| Poppler `pdftotext` / `pdfinfo` | 26.04.0 |
| GitHub CLI | 2.97.0 |
| Browser | HeadlessChrome 151.0.7922.34 via the local gstack browser wrapper |

## Evidence index

| Evidence ID | Claim verified | Exact command or method | Tool/version | Input commit | Expected result | Automated/manual |
|---|---|---|---|---|---|---|
| E01 | Baseline tracked-file count | `git ls-tree -r --name-only 640406ba742843f99c55ba9f3b8b2f5924291ee9 \| wc -l` | Git 2.50.1 | Baseline | `28` | Automated |
| E02 | Corrected PR tracked-file count | `git ls-files \| wc -l` | Git 2.50.1 | PR `HEAD` | `38` | Automated |
| E03 | Tracked PDF count on both inputs | `git ls-tree -r --name-only 640406ba742843f99c55ba9f3b8b2f5924291ee9 \| rg -c '\.pdf$'` and `git ls-files \| rg -c '\.pdf$'` | Git 2.50.1; ripgrep 15.2.0 | Baseline and PR `HEAD` | `2` and `2` | Automated |
| E04 | Major-artifact integrity | `shasum -a 256 <files listed below>` | shasum 6.02 | Baseline and PR `HEAD` | Exact hashes in the artifact table | Automated |
| E05 | Reachable history and identities | `git rev-list --all --count` and `git log --format='%H %an <%ae> %cn <%ce> %s' --all` | Git 2.50.1 | Corrected PR `HEAD` | Three reachable commits after the correction commit; author and committer addresses use the approved GitHub noreply domain | Automated plus manual domain review |
| E06 | Existing test suite | From a fresh clone: `python3 -m unittest discover -s tests -p 'test_repository_integrity.py' -v` | Python 3.9.6 | PR `HEAD` | Four tests run; four pass; zero failures/skips | Automated |
| E07 | Exact-index privacy scan | Run Appendix A | Python 3.9.6; Poppler 26.04.0 | PR `HEAD` | `PASS tracked privacy scan: 38 files` | Automated |
| E08 | High-confidence secret/credential scan | `git grep -nI -E -e '-----BEGIN ([A-Z]+ )?PRIVATE KEY-----' -e 'gh[pousr]_[A-Za-z0-9_]{20,}' -e 'github_pat_[A-Za-z0-9_]{20,}' -e 'AKIA[0-9A-Z]{16}' -- .` | Git 2.50.1 | PR `HEAD` | No output; exit status `1` means no match | Automated |
| E09 | Local-path scan | `git grep -nIF -e "$(printf '/%s/' Users)" -e "$(printf 'C:\\%s\\' Users)" -e "$(printf '%s%s' mac admin)" -- .` | Git 2.50.1 | PR `HEAD` | No output; exit status `1` means no match | Automated |
| E10 | PDF visible text | For each tracked PDF: `pdftotext -layout "$pdf" -` and render with `pdftoppm -png -r 96 "$pdf" <neutral-output-prefix>`; inspect all ten rendered pages | Poppler 26.04.0 | Baseline PDFs | Two five-page documents; no private contact details, IDs, credentials, or local paths; portfolio-owner name is intentional public attribution; pages are readable without clipping or overlap | Automated extraction plus manual visual review |
| E11 | PDF metadata and active content | For each tracked PDF: `pdfinfo "$pdf"` | Poppler 26.04.0 | Baseline PDFs | Five pages each; tagged; unencrypted; `JavaScript: no`; sizes 960×540 pt and 420×720 pt | Automated plus manual metadata review |
| E12 | Markdown links | Run Appendix B | Python 3.9.6 | PR `HEAD` | All relative Markdown links resolve to tracked paths within the repository | Automated |
| E13 | HTML relative links | `python3 -m unittest tests.test_repository_integrity.RepositoryIntegrityTests.test_relative_html_links_resolve_inside_repository -v` | Python 3.9.6 | PR `HEAD` | One test run; one pass | Automated |
| E14 | Dataset row counts | Run Appendix C | Python 3.9.6 | Baseline data | 5 requisitions, 4,000 candidates, and 2,000 interview rows | Automated |
| E15 | Composite-score recomputation | Run Appendix C | Python 3.9.6 | Baseline data | 500 populated composite scores; zero arithmetic differences using 40/40/20 | Automated |
| E16 | Governed KPI reconciliation | Run Appendix C | Python 3.9.6 | Baseline data | 120 hires; 28.5 mean days; 1,836 SLA-met rows; AIR `0.87` | Automated |
| E17 | Browser desktop width | `B=<qa-browser>; $B goto <live-url>; $B viewport 1440x900; $B js '({viewport:innerWidth,document:document.documentElement.scrollWidth})'` | HeadlessChrome 151.0.7922.34 | Live `main` at baseline commit | Viewport `1440`; document width `1440` | Automated DOM measurement |
| E18 | Browser phone overflow | `B=<qa-browser>; $B viewport 375x812; $B js '({viewport:innerWidth,document:document.documentElement.scrollWidth,overflow:document.documentElement.scrollWidth>innerWidth})'` | HeadlessChrome 151.0.7922.34 | Live `main` at baseline commit | Viewport `375`; document width `707`; overflow `true` | Automated DOM measurement plus manual screenshot review |
| E19 | Slide-control overlap | At 375×812, open `slides.html`, activate “Next slide,” and compare `.controls` with the first slide-two `.card` using `getBoundingClientRect()` | HeadlessChrome 151.0.7922.34 | Live `main` at baseline commit | Controls top/bottom `746/790`; card top/bottom `669/811`; rectangles intersect | Automated geometry plus manual screenshot review |
| E20 | Console errors | After dashboard load and slide navigation: `$B console --errors` | HeadlessChrome 151.0.7922.34 | Live `main` at baseline commit | No console errors in the tested flows | Automated inspection |
| E21 | Chart.js version and integrity | `rg -o -m1 'Chart\.js v[0-9.]+' vendor/chart.umd.min.js` and `shasum -a 256 vendor/chart.umd.min.js` | ripgrep 15.2.0; shasum 6.02 | Baseline and PR `HEAD` | Version `4.4.7`; hash `206b6e8bb00fc7bba2c7ee80ca41db3e9e05ba7be0aa35abeba9cfd5357f5d0e` | Automated |
| E22 | Dependency-advisory query | `gh api --method GET /advisories -f ecosystem=npm -f affects='chart.js@4.4.7' -f per_page=100` | GitHub CLI 2.97.0 | GitHub Advisory Database on 2026-09-02 | `[]` | Automated point-in-time query |

## Full SHA-256 artifact hashes

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

## Appendix A: exact-index privacy scan

```bash
python3 - <<'PY'
import re
import subprocess
from pathlib import Path

root = Path.cwd()
tracked = [Path(p.decode()) for p in subprocess.check_output(
    ["git", "ls-files", "-z"]
).split(b"\0") if p]
allowed_suffixes = {"", ".css", ".csv", ".html", ".js", ".md", ".pdf", ".py"}
allowed_email_domains = {"apexprecision.test", "example.com"}
patterns = {
    "Indian mobile": re.compile(r"(?<!\d)[6-9]\d{9}(?!\d)"),
    "Aadhaar": re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b"),
    "PAN": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
    "passport": re.compile(r"\b[A-Z][1-9]\d{6}\b"),
    "Emirates ID": re.compile(r"\b784[ -]?\d{4}[ -]?\d{7}[ -]?\d\b"),
    "IFSC": re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),
    "macOS local path": re.compile("/" + "Users" + "/", re.I),
    "Windows local path": re.compile(r"C:\\" + "Users" + r"\\", re.I),
    "local username": re.compile(r"\b" + "mac" + "admin" + r"\b", re.I),
    "private key": re.compile("-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub credential": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
}
email = re.compile(r"\b[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})\b", re.I)
failures = []
for relative in tracked:
    path = root / relative
    if path.suffix.lower() not in allowed_suffixes:
        failures.append(f"unexpected file type: {relative}")
    if any(part.startswith(".") for part in relative.parts) and relative.name != ".gitignore":
        failures.append(f"unexpected hidden path: {relative}")
    if path.suffix.lower() == ".pdf":
        text = subprocess.check_output(["pdftotext", str(path), "-"], text=True, errors="replace")
        text += subprocess.check_output(["pdfinfo", str(path)], text=True, errors="replace")
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
    for label, pattern in patterns.items():
        if pattern.search(text):
            failures.append(f"{label}: {relative}")
    domains = {match.group(1).lower() for match in email.finditer(text)}
    if domains - allowed_email_domains:
        failures.append(f"non-synthetic email domain: {relative}: {sorted(domains - allowed_email_domains)}")
if failures:
    raise SystemExit("FAIL\n" + "\n".join(failures))
print(f"PASS tracked privacy scan: {len(tracked)} files")
PY
```

## Appendix B: Markdown relative-link validation

```bash
python3 - <<'PY'
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

root = Path.cwd().resolve()
tracked = {Path(p.decode()).resolve() for p in subprocess.check_output(
    ["git", "ls-files", "-z"]
).split(b"\0") if p}
broken = []
checked = 0
for path in sorted(p for p in tracked if p.suffix.lower() == ".md"):
    for raw in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        parsed = urlsplit(raw.strip("<>"))
        if parsed.scheme or raw.startswith("#"):
            continue
        checked += 1
        target = (path.parent / unquote(parsed.path)).resolve()
        if not target.is_relative_to(root) or target not in tracked:
            broken.append((str(path.relative_to(root)), raw))
if broken:
    raise SystemExit(f"FAIL broken Markdown links: {broken}")
print(f"PASS Markdown links: {checked}")
PY
```

## Appendix C: data and KPI reconciliation

```bash
python3 - <<'PY'
import csv
from decimal import Decimal, ROUND_HALF_UP

def rows(name):
    with open(name, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

requisitions = rows("synthetic_requisitions.csv")
candidates = rows("synthetic_candidates.csv")
interviews = rows("synthetic_interviews.csv")
errors = []
for row in candidates:
    if not row["Composite_Score"]:
        continue
    expected = (
        Decimal(row["Work_Sample_Score"]) * Decimal("0.40")
        + Decimal(row["Structured_Interview_Score"]) * Decimal("0.40")
        + Decimal(row["Job_Knowledge_Score"]) * Decimal("0.20")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if Decimal(row["Composite_Score"]) != expected:
        errors.append(row["Candidate_ID"])
reference = [r for r in candidates if r["Demographic_Cohort"] == "Reference Group"]
focal = [r for r in candidates if r["Demographic_Cohort"] == "Focal Group"]
reference_rate = Decimal(sum(bool(r["Phone_Screen_Score"]) for r in reference)) / len(reference)
focal_rate = Decimal(sum(bool(r["Phone_Screen_Score"]) for r in focal)) / len(focal)
result = {
    "requisitions": len(requisitions),
    "candidates": len(candidates),
    "interviews": len(interviews),
    "composites_checked": sum(bool(r["Composite_Score"]) for r in candidates),
    "composite_errors": len(errors),
    "hires": sum(r["Current_Stage"] == "Hired" for r in candidates),
    "mean_days_to_fill": str(sum(Decimal(r["Days_to_Fill"]) for r in requisitions) / len(requisitions)),
    "sla_met": sum(r["SLA_Met"] == "Yes" for r in interviews),
    "air": str((focal_rate / reference_rate).quantize(Decimal("0.01"))),
}
expected = {"requisitions": 5, "candidates": 4000, "interviews": 2000,
            "composites_checked": 500, "composite_errors": 0, "hires": 120,
            "mean_days_to_fill": "28.5", "sla_met": 1836, "air": "0.87"}
if result != expected:
    raise SystemExit(f"FAIL {result}")
print(f"PASS {result}")
PY
```

## Evidence boundary

The browser and advisory results are point-in-time observations. The PDF review confirms the current public artifacts, not their future regeneration. Passing these checks establishes repository consistency for this synthetic demonstration; it does not establish production readiness, regulatory compliance, security, selection validity, accessibility conformance, or freedom from bias.
