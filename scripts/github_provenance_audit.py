#!/usr/bin/env python3
"""Verify GitHub provenance for platform-committed merge commits."""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from scripts import repository_audit as audit
except ImportError:  # Direct execution from the scripts directory.
    import repository_audit as audit


API_BASE = "https://api.github.com"
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class ProvenanceUnavailable(RuntimeError):
    """Raised when remote provenance evidence cannot be obtained safely."""


@dataclass(frozen=True)
class ProvenanceFinding:
    category: str
    commit: str
    detail: str = "verification failed"


class GitHubApiClient:
    def __init__(self, token=None, api_base=API_BASE, timeout=20):
        self.token = token
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout

    def get(self, path):
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "repository-platform-provenance-audit",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        request = Request(self.api_base + path, headers=headers)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError, ValueError):
            raise ProvenanceUnavailable("remote evidence unavailable") from None


def _finding(category, record):
    return ProvenanceFinding(category, record.commit)


def _is_merged_association(pulls, commit):
    return isinstance(pulls, list) and any(
        isinstance(item, dict)
        and item.get("state") == "closed"
        and bool(item.get("merged_at"))
        and item.get("merge_commit_sha") == commit
        for item in pulls
    )


def platform_provenance_findings(records, repository, api):
    findings = []
    for record in records:
        if not audit.is_github_platform_identity(record.committer):
            continue
        if not COMMIT_PATTERN.fullmatch(record.commit):
            findings.append(_finding("platform provenance response", record))
            continue
        if len(record.parents) != 2:
            findings.append(_finding("platform provenance parents", record))
            continue
        try:
            metadata = api.get(f"/repos/{repository}/commits/{record.commit}")
        except ProvenanceUnavailable:
            findings.append(_finding("platform provenance unavailable", record))
            continue
        if not isinstance(metadata, dict) or metadata.get("sha") != record.commit:
            findings.append(_finding("platform provenance response", record))
            continue
        committer = metadata.get("committer")
        if not isinstance(committer, dict) or committer.get("login") != "web-flow":
            findings.append(_finding("platform provenance actor", record))
        commit_payload = metadata.get("commit")
        verification = (
            commit_payload.get("verification", {})
            if isinstance(commit_payload, dict)
            else {}
        )
        if not isinstance(verification, dict) or not (
            verification.get("verified") is True and verification.get("reason") == "valid"
        ):
            findings.append(_finding("platform provenance signature", record))
        parents = metadata.get("parents")
        if not isinstance(parents, list) or len(parents) != 2:
            findings.append(_finding("platform provenance parents", record))
        try:
            pulls = api.get(f"/repos/{repository}/commits/{record.commit}/pulls")
        except ProvenanceUnavailable:
            findings.append(_finding("platform provenance unavailable", record))
            continue
        if not _is_merged_association(pulls, record.commit):
            findings.append(_finding("platform provenance pull request", record))
    return list(dict.fromkeys(findings))


def format_findings(findings):
    return "\n".join(
        f"- {finding.category}: {finding.commit[:12]} (verification failed)"
        for finding in findings
    )


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        default=os.environ.get("GITHUB_REPOSITORY", ""),
        help="GitHub owner/repository slug",
    )
    parser.add_argument("--root", type=Path, default=audit.ROOT, help=argparse.SUPPRESS)
    return parser


def main(argv=None):
    arguments = build_parser().parse_args(argv)
    if not REPOSITORY_PATTERN.fullmatch(arguments.repository):
        print("FAIL platform provenance: invalid repository context", file=sys.stderr)
        return 1
    try:
        records = audit.history_identity_records(arguments.root)
    except (OSError, subprocess.SubprocessError, ValueError):
        print("FAIL platform provenance: local history unavailable", file=sys.stderr)
        return 1
    candidates = [
        record for record in records if audit.is_github_platform_identity(record.committer)
    ]
    api = GitHubApiClient(token=os.environ.get("GITHUB_TOKEN"))
    findings = platform_provenance_findings(candidates, arguments.repository, api)
    if findings:
        print("FAIL platform provenance", file=sys.stderr)
        print(format_findings(findings), file=sys.stderr)
        return 1
    print(f"PASS platform provenance: {len(candidates)} verified merge commit(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
