#!/usr/bin/env python3
"""Executable repository audit gates for the synthetic hiring reference project."""

import argparse
import hashlib
import re
import subprocess
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    from scripts import claims_policy, data_contracts
except ModuleNotFoundError:  # Direct execution places scripts/ on sys.path.
    import claims_policy
    import data_contracts


ROOT = Path(__file__).resolve().parents[1]

ALLOWED_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".js",
    ".md",
    ".pdf",
    ".py",
    ".yaml",
    ".yml",
}
ALLOWED_EMAIL_DOMAINS = {
    "apexprecision.test",
    "example.com",
    "users.noreply.github.com",
}
EXPECTED_VISUAL_EVIDENCE = {
    Path("docs/audit/visual/desktop-final-pages.png"),
    Path("docs/audit/visual/mobile-final-pages.png"),
}
MAX_VISUAL_EVIDENCE_BYTES = 1_000_000
EXPECTED_PDFS = {
    "Structured_Hiring_and_ATS_Architecture_Case_Study.pdf": "960 x 540 pts",
    "Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf": "420 x 720 pts",
}
CLAIM_SOURCES = ("slides.html", "mobile-case-study.html")
EXPECTED_ARTIFACT_HASHES = {
    "index.html": "51765b742caae8ea61c7bb465e01762e9fe987e6ee308d61e11f79ccad9bbbad",
    "dashboard.html": "51765b742caae8ea61c7bb465e01762e9fe987e6ee308d61e11f79ccad9bbbad",
    "slides.html": "c7cad18ca4dc9f49e052902cc49fb1baccb8098f90c7fc32ede8444e3a91a978",
    "mobile-case-study.html": "4bdb3869340c0fba5e8a41016e78d0e39a4c9886b5402252ae1e6d9745ab0778",
    "mobile-case-study.css": "b9abc45c1d475bfa7c2ede5d1a8ed9d2fc93926cfde93769094f99a605907c17",
    "synthetic_requisitions.csv": "a5857a0bd2fb824288406611f0afd929f428c40ebe143c1f982e25ed79d20bab",
    "synthetic_candidates.csv": "2e9cb4153172b7cf83349b8f49498a8598c621c81c5cfe14441a3fd6fbb57359",
    "synthetic_interviews.csv": "07857ea73dbde578b5ead86b16536a967c9193a113b3e0387ee454b0ebb83a36",
    "Structured_Hiring_and_ATS_Architecture_Case_Study.pdf": "6a90cc75ef1d4a4ba334a76b50bb12250c2201384eaf6fc97d90bc93c9a47586",
    "Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf": "bf22457062981dfd348ea3c403563d2996e050772328459c55053cee78a6fbd6",
    "docs/audit/visual/desktop-final-pages.png": "0071bb1876852f3617d01b8dbf0236b050deb296ad10cfd63fca497814272d79",
    "docs/audit/visual/mobile-final-pages.png": "4276410bf1a23e0c7f7890065b275774fdb34e3743e53a856eeb0aee314ba070",
    "vendor/chart.umd.min.js": "206b6e8bb00fc7bba2c7ee80ca41db3e9e05ba7be0aa35abeba9cfd5357f5d0e",
}
KNOWN_IDENTITY_EXCEPTIONS = {
    # GitHub-generated Stage 0 merge commit. Raw metadata contains the account's
    # pre-existing non-noreply address. Do not add another exception; fix the
    # GitHub email-privacy setting before any later merge.
    "e410482fbb50e757ae4a6487eee0eae85eabbc8c",
}

TEXT_PATTERNS = {
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
    "GitHub credential": re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"
    ),
}
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})\b", re.I)
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
USER_NOREPLY_PATTERN = re.compile(r"^[^@\s]+@users\.noreply\.github\.com$", re.I)
GITHUB_PLATFORM_IDENTITY = "noreply" + "@" + "github.com"


@dataclass(frozen=True)
class Finding:
    category: str
    path: str
    message: str = "prohibited or inconsistent content detected"


@dataclass(frozen=True)
class CommitIdentity:
    commit: str
    parents: tuple
    author: str
    committer: str


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        for key in ("href", "src"):
            value = attributes.get(key)
            if value:
                self.links.append(value)
        if tag.lower() == "script" and attributes.get("src"):
            self.scripts.append(attributes["src"])


def _git(root, *args):
    return subprocess.check_output(
        ["git", *args], cwd=root, text=False, stderr=subprocess.DEVNULL
    )


def tracked_files(root=ROOT):
    return [
        Path(item.decode())
        for item in _git(root, "ls-files", "-z").split(b"\0")
        if item
    ]


def is_allowed_tracked_path(path):
    path = Path(path)
    if path == Path("LICENSE"):
        return True
    if path.parts[:2] == (".github", "workflows"):
        return len(path.parts) == 3 and path.suffix.lower() in {".yml", ".yaml"}
    if any(part.startswith(".") for part in path.parts):
        return path.name == ".gitignore"
    if path.suffix.lower() == ".png":
        return path in EXPECTED_VISUAL_EVIDENCE
    return path.suffix.lower() in ALLOWED_SUFFIXES


def tracked_path_findings(paths, root=None):
    findings = [
        Finding("unexpected tracked path", str(path))
        for path in paths
        if not is_allowed_tracked_path(path)
    ]
    if root is not None:
        findings.extend(
            Finding("tracked symlink", str(path))
            for path in paths
            if (Path(root) / path).is_symlink()
        )
    return findings


def scan_text(relative, text):
    relative = str(relative)
    findings = []
    for category, pattern in TEXT_PATTERNS.items():
        if pattern.search(text):
            findings.append(Finding(category, relative))
    domains = {match.group(1).lower() for match in EMAIL_PATTERN.finditer(text)}
    if domains - ALLOWED_EMAIL_DOMAINS:
        findings.append(Finding("non-synthetic email domain", relative))
    return findings


def png_visual_findings(relative, payload):
    """Validate the two reviewed contact sheets without decoding image pixels."""
    relative = Path(relative)
    findings = []
    if len(payload) > MAX_VISUAL_EVIDENCE_BYTES:
        findings.append(Finding("PNG size", str(relative)))
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return findings + [Finding("PNG structure", str(relative))]

    offset = 8
    dimensions = None
    text_metadata = False
    structurally_complete = False
    while offset + 12 <= len(payload):
        length = int.from_bytes(payload[offset:offset + 4], "big")
        kind = payload[offset + 4:offset + 8]
        end = offset + 12 + length
        if end > len(payload):
            break
        data = payload[offset + 8:offset + 8 + length]
        if kind == b"IHDR" and len(data) == 13:
            dimensions = (
                int.from_bytes(data[:4], "big"),
                int.from_bytes(data[4:8], "big"),
            )
        if kind in {b"tEXt", b"zTXt", b"iTXt", b"eXIf"}:
            text_metadata = True
        if kind == b"IEND":
            structurally_complete = end == len(payload)
            break
        offset = end

    if not structurally_complete or dimensions is None:
        findings.append(Finding("PNG structure", str(relative)))
    elif not (600 <= dimensions[0] <= 2400 and 400 <= dimensions[1] <= 2400):
        findings.append(Finding("PNG dimensions", str(relative)))
    if text_metadata:
        findings.append(Finding("PNG metadata", str(relative)))
    return findings


def _pdf_text_and_metadata(path):
    visible = subprocess.check_output(
        ["pdftotext", "-layout", str(path), "-"],
        text=True,
        errors="replace",
        stderr=subprocess.DEVNULL,
    )
    metadata = subprocess.check_output(
        ["pdfinfo", str(path)],
        text=True,
        errors="replace",
        stderr=subprocess.DEVNULL,
    )
    return visible, metadata


def privacy_findings(root=ROOT, paths=None):
    paths = list(paths if paths is not None else tracked_files(root))
    findings = []
    for relative in paths:
        path = root / relative
        try:
            if path.suffix.lower() == ".pdf":
                visible, metadata = _pdf_text_and_metadata(path)
                text = visible + metadata
            elif path.suffix.lower() == ".png":
                content = path.read_bytes()
                findings.extend(png_visual_findings(relative, content))
                continue
            else:
                content = path.read_bytes()
                if b"\0" in content:
                    findings.append(Finding("binary tracked file", str(relative)))
                    continue
                text = content.decode(encoding="utf-8", errors="replace")
        except (OSError, subprocess.SubprocessError):
            findings.append(Finding("unreadable tracked file", str(relative)))
            continue
        findings.extend(scan_text(relative, text))
    return findings


def capability_claim_findings(root=ROOT):
    root = Path(root)
    findings = []
    for relative in CLAIM_SOURCES + tuple(EXPECTED_PDFS):
        path = root / relative
        try:
            if path.suffix.lower() == ".pdf":
                text, _ = _pdf_text_and_metadata(path)
            else:
                text = path.read_text(encoding="utf-8")
        except (OSError, subprocess.SubprocessError, UnicodeError):
            findings.append(Finding("capability claims", relative, "artifact is unreadable"))
            continue
        findings.extend(
            Finding("unsupported capability claim", relative, item.rule)
            for item in claims_policy.evaluate_claims(text)
        )
    return _deduplicate(findings)


def _normalize_tracked(tracked):
    return {Path(path) for path in tracked}


def _relative_target(root, source, raw):
    cleaned = raw.strip().strip("<>").split(maxsplit=1)[0]
    parsed = urlsplit(cleaned)
    if parsed.scheme or parsed.netloc or cleaned.startswith(("#", "//", "data:")):
        return None
    if not parsed.path:
        return None
    return (source.parent / unquote(parsed.path)).resolve()


def markdown_link_findings(root=ROOT, tracked=None):
    root = Path(root).resolve()
    tracked = _normalize_tracked(tracked if tracked is not None else tracked_files(root))
    findings = []
    for relative in sorted(path for path in tracked if path.suffix.lower() == ".md"):
        source = root / relative
        try:
            text = source.read_text(encoding="utf-8")
        except OSError:
            findings.append(Finding("Markdown link", str(relative), "source is unreadable"))
            continue
        for raw in MARKDOWN_LINK_PATTERN.findall(text):
            target = _relative_target(root, source, raw)
            if target is None:
                continue
            try:
                target_relative = target.relative_to(root)
            except ValueError:
                findings.append(Finding("Markdown link", str(relative), "target leaves repository"))
                continue
            if target_relative not in tracked:
                findings.append(Finding("Markdown link", str(relative), "target is not tracked"))
    return findings


def _collect_html(path):
    parser = LinkCollector()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    return parser


def html_link_findings(root=ROOT, tracked=None):
    root = Path(root).resolve()
    tracked = _normalize_tracked(tracked if tracked is not None else tracked_files(root))
    findings = []
    for relative in sorted(path for path in tracked if path.suffix.lower() == ".html"):
        source = root / relative
        try:
            links = _collect_html(source).links
        except OSError:
            findings.append(Finding("HTML link", str(relative), "source is unreadable"))
            continue
        for raw in links:
            target = _relative_target(root, source, raw)
            if target is None:
                continue
            try:
                target_relative = target.relative_to(root)
            except ValueError:
                findings.append(Finding("HTML link", str(relative), "target leaves repository"))
                continue
            if target_relative not in tracked:
                findings.append(Finding("HTML link", str(relative), "target is not tracked"))
    return findings


def external_script_findings(root=ROOT, tracked=None):
    root = Path(root)
    tracked = _normalize_tracked(tracked if tracked is not None else tracked_files(root))
    findings = []
    for relative in sorted(path for path in tracked if path.suffix.lower() == ".html"):
        try:
            scripts = _collect_html(root / relative).scripts
        except OSError:
            continue
        for raw in scripts:
            parsed = urlsplit(raw)
            if parsed.scheme in {"http", "https"} or raw.startswith("//"):
                findings.append(Finding("external executable script", str(relative)))
    return findings


def parse_pdfinfo(text):
    metadata = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata


def pdf_metadata_findings(path, metadata, expected_size):
    checks = {
        "PDF pages": metadata.get("Pages") == "5",
        "PDF tagging": metadata.get("Tagged", "").lower() == "yes",
        "PDF encryption": metadata.get("Encrypted", "").lower().startswith("no"),
        "PDF JavaScript": metadata.get("JavaScript", "").lower() == "no",
        "PDF forms": metadata.get("Form", "").lower() == "none",
        "PDF page size": metadata.get("Page size", "").startswith(expected_size),
    }
    return [Finding(category, str(path)) for category, passed in checks.items() if not passed]


def pdf_findings(root=ROOT):
    root = Path(root)
    try:
        tracked_pdfs = {
            str(path) for path in tracked_files(root) if path.suffix.lower() == ".pdf"
        }
    except subprocess.SubprocessError:
        tracked_pdfs = set()
    findings = []
    if tracked_pdfs != set(EXPECTED_PDFS):
        findings.append(Finding("PDF inventory", "repository"))
    for relative, expected_size in EXPECTED_PDFS.items():
        path = root / relative
        try:
            visible, metadata_text = _pdf_text_and_metadata(path)
        except (OSError, subprocess.SubprocessError):
            findings.append(Finding("PDF tooling", relative))
            continue
        if not visible.strip():
            findings.append(Finding("PDF visible text", relative))
        findings.extend(
            pdf_metadata_findings(Path(relative), parse_pdfinfo(metadata_text), expected_size)
        )
    return findings


def artifact_hash_findings(root=ROOT, expected=None):
    root = Path(root)
    expected = expected or EXPECTED_ARTIFACT_HASHES
    findings = []
    for relative, wanted in expected.items():
        path = root / relative
        try:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            findings.append(Finding("artifact checksum", relative, "artifact is missing"))
            continue
        if actual != wanted:
            findings.append(Finding("artifact checksum", relative))
        if relative == "vendor/chart.umd.min.js":
            try:
                marker_present = "Chart.js v4.4.7" in path.read_text(
                    encoding="utf-8", errors="replace"
                )
            except OSError:
                marker_present = False
            if not marker_present:
                findings.append(Finding("dependency version", relative))
    return findings


def data_kpi_findings(root=ROOT):
    return [
        Finding(
            f"data {item.category}",
            f"{item.record_key}:{item.field}",
        )
        for item in data_contracts.validate_repository(root)
    ]


def is_user_noreply_identity(value):
    return bool(USER_NOREPLY_PATTERN.fullmatch(value))


def is_github_platform_identity(value):
    return value == GITHUB_PLATFORM_IDENTITY


def history_identity_records(root=ROOT):
    output = _git(root, "log", "--format=%H%x00%P%x00%ae%x00%ce", "--all").decode(
        errors="replace"
    )
    records = []
    for line in output.splitlines():
        parts = line.split("\0")
        if len(parts) != 4:
            raise ValueError("malformed history identity record")
        commit, parents, author, committer = parts
        records.append(
            CommitIdentity(
                commit=commit,
                parents=tuple(parent for parent in parents.split() if parent),
                author=author,
                committer=committer,
            )
        )
    return records


def identity_findings(records, allowed_exceptions=None):
    allowed_exceptions = set(
        KNOWN_IDENTITY_EXCEPTIONS if allowed_exceptions is None else allowed_exceptions
    )
    findings = []
    for record in records:
        if record.commit in allowed_exceptions:
            continue
        author_allowed = is_user_noreply_identity(record.author)
        committer_allowed = is_user_noreply_identity(record.committer)
        restricted_platform_merge = (
            is_github_platform_identity(record.committer) and len(record.parents) == 2
        )
        if not author_allowed or not (committer_allowed or restricted_platform_merge):
            findings.append(Finding("commit identity", record.commit[:12]))
    return findings


def history_identity_findings(root=ROOT, allowed_exceptions=None):
    try:
        records = history_identity_records(root)
    except (subprocess.SubprocessError, ValueError):
        return [Finding("commit identity", "git history", "history is unavailable")]
    return identity_findings(records, allowed_exceptions)


def _deduplicate(findings):
    return list(dict.fromkeys(findings))


def run_checks(root, names):
    root = Path(root).resolve()
    tracked = tracked_files(root)
    checks = {
        "paths": lambda: tracked_path_findings(tracked, root),
        "privacy": lambda: privacy_findings(root, tracked),
        "claims": lambda: capability_claim_findings(root),
        "markdown-links": lambda: markdown_link_findings(root, tracked),
        "html-links": lambda: html_link_findings(root, tracked),
        "external-scripts": lambda: external_script_findings(root, tracked),
        "pdfs": lambda: pdf_findings(root),
        "artifacts": lambda: artifact_hash_findings(root),
        "data": lambda: data_kpi_findings(root),
        "history": lambda: history_identity_findings(root),
    }
    findings = []
    for name in names:
        findings.extend(checks[name]())
    return _deduplicate(findings)


def run_all(root=ROOT):
    return run_checks(
        root,
        (
            "paths",
            "privacy",
            "claims",
            "markdown-links",
            "html-links",
            "external-scripts",
            "pdfs",
            "artifacts",
            "data",
            "history",
        ),
    )


def format_findings(findings):
    return "\n".join(
        f"- {finding.category}: {finding.path} ({finding.message})" for finding in findings
    )


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="run every repository audit gate")
    parser.add_argument(
        "--check",
        action="append",
        choices=(
            "paths",
            "privacy",
            "claims",
            "markdown-links",
            "html-links",
            "external-scripts",
            "pdfs",
            "artifacts",
            "data",
            "history",
        ),
        help="run one named gate; repeat for multiple gates",
    )
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    return parser


def main(argv=None):
    parser = build_parser()
    arguments = parser.parse_args(argv)
    if not arguments.all and not arguments.check:
        parser.error("choose --all or at least one --check")
    names = arguments.check or (
        "paths",
        "privacy",
        "claims",
        "markdown-links",
        "html-links",
        "external-scripts",
        "pdfs",
        "artifacts",
        "data",
        "history",
    )
    findings = run_checks(arguments.root, names)
    if findings:
        print("FAIL repository audit", file=sys.stderr)
        print(format_findings(findings), file=sys.stderr)
        return 1
    count = len(tracked_files(arguments.root))
    print(f"PASS repository audit: {count} tracked files; checks={','.join(names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
