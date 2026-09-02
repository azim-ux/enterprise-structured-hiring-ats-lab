import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from scripts import github_provenance_audit as provenance
from scripts import repository_audit as audit


MERGE_SHA = "3d307cd8ad3946bc195e3ab247f7d0e9c3fd55f9"
REPOSITORY = "azim-ux/enterprise-structured-hiring-ats-lab"


def user_noreply(label="reviewer"):
    return label + "@" + "users.noreply.github.com"


def platform_identity():
    return "noreply" + "@" + "github.com"


def merge_record(parents=("a", "b")):
    return audit.CommitIdentity(
        commit=MERGE_SHA,
        parents=tuple(parents),
        author=user_noreply("author"),
        committer=platform_identity(),
    )


def commit_metadata(*, actor="web-flow", verified=True, reason="valid", parents=2):
    return {
        "sha": MERGE_SHA,
        "committer": {"login": actor},
        "commit": {"verification": {"verified": verified, "reason": reason}},
        "parents": [{"sha": str(index)} for index in range(parents)],
    }


def merged_pr_metadata(*, merge_sha=MERGE_SHA, merged=True):
    return [
        {
            "number": 15,
            "state": "closed",
            "merged_at": "2026-09-02T08:09:31Z" if merged else None,
            "merge_commit_sha": merge_sha,
        }
    ]


class FakeApi:
    def __init__(self, commit=None, pulls=None, error=None):
        self.commit = commit if commit is not None else commit_metadata()
        self.pulls = pulls if pulls is not None else merged_pr_metadata()
        self.error = error
        self.paths = []

    def get(self, path):
        self.paths.append(path)
        if self.error:
            raise self.error
        return self.pulls if path.endswith("/pulls") else self.commit


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.payload


class PlatformProvenanceTests(unittest.TestCase):
    @patch("scripts.github_provenance_audit.urlopen")
    def test_api_client_parses_json_without_logging_response(self, opener):
        opener.return_value = FakeResponse(b'{"synthetic": true}')
        client = provenance.GitHubApiClient(token="synthetic-token")
        self.assertEqual({"synthetic": True}, client.get("/synthetic"))
        request = opener.call_args.args[0]
        self.assertTrue(request.has_header("Authorization"))

    @patch("scripts.github_provenance_audit.urlopen", side_effect=URLError("offline"))
    def test_api_client_normalizes_transport_failure(self, _opener):
        with self.assertRaises(provenance.ProvenanceUnavailable) as raised:
            provenance.GitHubApiClient().get("/synthetic")
        self.assertEqual("remote evidence unavailable", str(raised.exception))

    def test_sanitized_pr15_merge_shape_passes(self):
        api = FakeApi()
        findings = provenance.platform_provenance_findings(
            [merge_record()], REPOSITORY, api
        )
        self.assertEqual([], findings)
        self.assertNotIn("email", repr(api.commit).lower())
        self.assertEqual(2, len(api.paths))

    def test_wrong_actor_fails(self):
        api = FakeApi(commit=commit_metadata(actor="not-platform"))
        findings = provenance.platform_provenance_findings(
            [merge_record()], REPOSITORY, api
        )
        self.assertIn("platform provenance actor", {item.category for item in findings})

    def test_mismatched_commit_response_fails_before_pr_lookup(self):
        metadata = commit_metadata()
        metadata["sha"] = "f" * 40
        api = FakeApi(commit=metadata)
        findings = provenance.platform_provenance_findings(
            [merge_record()], REPOSITORY, api
        )
        self.assertEqual(
            ["platform provenance response"], [item.category for item in findings]
        )
        self.assertEqual(1, len(api.paths))

    def test_missing_invalid_or_unverifiable_signature_fails(self):
        cases = (
            commit_metadata(verified=False),
            commit_metadata(reason="unknown"),
            {"sha": MERGE_SHA, "committer": {"login": "web-flow"}, "commit": {}, "parents": [{}, {}]},
            {"sha": MERGE_SHA, "committer": {"login": "web-flow"}, "commit": None, "parents": [{}, {}]},
        )
        for metadata in cases:
            with self.subTest(metadata=metadata):
                findings = provenance.platform_provenance_findings(
                    [merge_record()], REPOSITORY, FakeApi(commit=metadata)
                )
                self.assertIn(
                    "platform provenance signature",
                    {item.category for item in findings},
                )

    def test_api_parent_count_must_confirm_merge_shape(self):
        findings = provenance.platform_provenance_findings(
            [merge_record()], REPOSITORY, FakeApi(commit=commit_metadata(parents=1))
        )
        self.assertIn(
            "platform provenance parents", {item.category for item in findings}
        )

    def test_local_single_parent_shape_fails_before_remote_lookup(self):
        api = FakeApi()
        findings = provenance.platform_provenance_findings(
            [merge_record(parents=("a",))], REPOSITORY, api
        )
        self.assertEqual(
            ["platform provenance parents"], [item.category for item in findings]
        )
        self.assertEqual([], api.paths)

    def test_malformed_local_commit_identifier_fails_before_remote_lookup(self):
        record = audit.CommitIdentity(
            commit="not-a-commit",
            parents=("a", "b"),
            author=user_noreply("author"),
            committer=platform_identity(),
        )
        api = FakeApi()
        findings = provenance.platform_provenance_findings([record], REPOSITORY, api)
        self.assertEqual(
            ["platform provenance response"], [item.category for item in findings]
        )
        self.assertEqual([], api.paths)

    def test_unmerged_unassociated_or_mismatched_pr_fails(self):
        cases = (
            [],
            merged_pr_metadata(merged=False),
            merged_pr_metadata(merge_sha="f" * 40),
        )
        for pulls in cases:
            with self.subTest(pulls=pulls):
                findings = provenance.platform_provenance_findings(
                    [merge_record()], REPOSITORY, FakeApi(pulls=pulls)
                )
                self.assertIn(
                    "platform provenance pull request",
                    {item.category for item in findings},
                )

    def test_api_unavailable_fails_closed_with_redacted_output(self):
        prohibited = "private" + "@" + "mail.test"
        api = FakeApi(error=provenance.ProvenanceUnavailable(prohibited))
        findings = provenance.platform_provenance_findings(
            [merge_record()], REPOSITORY, api
        )
        output = provenance.format_findings(findings)
        self.assertIn("platform provenance unavailable", output)
        self.assertNotIn(prohibited, output)

    def test_non_platform_commits_do_not_require_remote_provenance(self):
        record = audit.CommitIdentity(
            commit="a" * 40,
            parents=("b",),
            author=user_noreply("author"),
            committer=user_noreply("committer"),
        )
        api = FakeApi(error=provenance.ProvenanceUnavailable("offline"))
        self.assertEqual(
            [], provenance.platform_provenance_findings([record], REPOSITORY, api)
        )
        self.assertEqual([], api.paths)

    def test_failure_formatter_emits_only_category_and_abbreviated_commit(self):
        prohibited = "private" + "@" + "mail.test"
        finding = provenance.ProvenanceFinding(
            "platform provenance actor", MERGE_SHA, prohibited
        )
        output = provenance.format_findings([finding])
        self.assertEqual(
            f"- platform provenance actor: {MERGE_SHA[:12]} (verification failed)",
            output,
        )
        self.assertNotIn(prohibited, output)

    def test_cli_fails_without_repository_context_and_keeps_output_redacted(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = provenance.main(["--repository", "invalid"])
        self.assertEqual(1, result)
        self.assertEqual("FAIL platform provenance: invalid repository context\n", stderr.getvalue())

    def test_cli_fails_closed_when_local_history_is_unavailable(self):
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as temp, redirect_stderr(stderr):
            result = provenance.main(
                ["--repository", REPOSITORY, "--root", str(Path(temp))]
            )
        self.assertEqual(1, result)
        self.assertEqual("FAIL platform provenance: local history unavailable\n", stderr.getvalue())

    @patch("scripts.github_provenance_audit.GitHubApiClient")
    @patch("scripts.github_provenance_audit.audit.history_identity_records")
    def test_cli_success_reports_count_only(self, records, client):
        records.return_value = [merge_record()]
        client.return_value = FakeApi()
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            result = provenance.main(["--repository", REPOSITORY])
        self.assertEqual(0, result)
        self.assertEqual("PASS platform provenance: 1 verified merge commit(s)\n", stdout.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
