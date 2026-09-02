import hashlib
import io
import os
import subprocess
import struct
import tempfile
import unittest
import zlib
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from scripts import repository_audit as audit


ROOT = Path(__file__).resolve().parents[1]


class TextPrivacyTests(unittest.TestCase):
    def test_clean_synthetic_text_passes(self):
        findings = audit.scan_text(
            Path("sample.md"),
            "Synthetic Candidate 0001 uses analyst@apexprecision.test.",
        )
        self.assertEqual([], findings)

    def test_phone_and_national_id_patterns_fail(self):
        values = {
            "Indian mobile": "9" + "123456789",
            "Aadhaar": "1234" + " 5678" + " 9012",
            "PAN": "ABCDE" + "1234" + "F",
            "passport": "A" + "1234567",
            "Emirates ID": "784" + "-1999-1234567-1",
            "IFSC": "ABCD" + "0" + "123456",
        }
        for category, value in values.items():
            with self.subTest(category=category):
                findings = audit.scan_text(Path("sample.md"), f"value={value}")
                self.assertIn(category, {finding.category for finding in findings})

    def test_secret_patterns_fail(self):
        values = {
            "private key": "-----BEGIN " + "PRIVATE KEY-----",
            "AWS key": "AKIA" + "A" * 16,
            "GitHub credential": "gh" + "p_" + "A" * 24,
            "GitHub credential fine-grained": "github" + "_pat_" + "A" * 24,
        }
        for label, value in values.items():
            with self.subTest(label=label):
                findings = audit.scan_text(Path("sample.md"), value)
                self.assertIn(label.split(" fine-grained")[0], {f.category for f in findings})

    def test_local_paths_and_username_fail(self):
        values = {
            "macOS local path": "/" + "Users" + "/sample/project",
            "Windows local path": "C:\\" + "Users" + "\\sample\\project",
            "local username": "mac" + "admin",
        }
        for category, value in values.items():
            with self.subTest(category=category):
                findings = audit.scan_text(Path("sample.md"), value)
                self.assertIn(category, {finding.category for finding in findings})

    def test_non_synthetic_email_domain_fails(self):
        email = "reviewer" + "@" + "mail.test"
        findings = audit.scan_text(Path("sample.md"), email)
        self.assertIn("non-synthetic email domain", {finding.category for finding in findings})

    def test_failure_output_does_not_echo_matched_value(self):
        credential = "gh" + "p_" + "B" * 24
        output = audit.format_findings(audit.scan_text(Path("sample.md"), credential))
        self.assertNotIn(credential, output)
        self.assertIn("GitHub credential", output)
        self.assertIn("sample.md", output)


class TrackedPathPolicyTests(unittest.TestCase):
    def test_expected_paths_are_allowed(self):
        for path in (
            Path("README.md"),
            Path("LICENSE"),
            Path("scripts/repository_audit.py"),
            Path(".github/workflows/quality-gates.yml"),
        ):
            with self.subTest(path=path):
                self.assertTrue(audit.is_allowed_tracked_path(path))

    def test_private_hidden_and_binary_paths_fail(self):
        for path in (
            Path(".env"),
            Path(".gstack/cache.json"),
            Path("contract.docx"),
            Path("archive.zip"),
            Path("unexpected-binary"),
        ):
            with self.subTest(path=path):
                self.assertFalse(audit.is_allowed_tracked_path(path))

    def test_only_governed_visual_evidence_png_paths_are_allowed(self):
        governed = Path("docs/audit/visual/desktop-final-pages.png")
        self.assertTrue(audit.is_allowed_tracked_path(governed))
        self.assertFalse(audit.is_allowed_tracked_path(Path("screenshot.png")))

    @staticmethod
    def png_chunk(kind, payload):
        body = kind + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body))

    def test_governed_png_requires_safe_dimensions_and_no_text_metadata(self):
        signature = b"\x89PNG\r\n\x1a\n"
        ihdr = self.png_chunk(b"IHDR", struct.pack(">IIBBBBB", 1200, 900, 8, 2, 0, 0, 0))
        iend = self.png_chunk(b"IEND", b"")
        relative = Path("docs/audit/visual/desktop-final-pages.png")
        self.assertEqual([], audit.png_visual_findings(relative, signature + ihdr + iend))

        metadata = self.png_chunk(b"tEXt", b"Source\x00private workstation path")
        findings = audit.png_visual_findings(relative, signature + ihdr + metadata + iend)
        self.assertEqual(["PNG metadata"], [finding.category for finding in findings])

    def test_tracked_symlink_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("synthetic", encoding="utf-8")
            (root / "linked.md").symlink_to("README.md")
            findings = audit.tracked_path_findings([Path("linked.md")], root=root)
            self.assertEqual(["tracked symlink"], [finding.category for finding in findings])

    def test_binary_payload_with_text_extension_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sample.md").write_bytes(b"synthetic\0payload")
            findings = audit.privacy_findings(root, [Path("sample.md")])
            self.assertEqual(["binary tracked file"], [finding.category for finding in findings])


class LinkAndScriptTests(unittest.TestCase):
    def write(self, root, relative, content):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_markdown_relative_links_resolve_to_tracked_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write(root, "README.md", "[Guide](docs/guide.md#usage)")
            self.write(root, "docs/guide.md", "# Guide")
            tracked = {Path("README.md"), Path("docs/guide.md")}
            self.assertEqual([], audit.markdown_link_findings(root, tracked))

    def test_markdown_missing_and_escape_links_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write(root, "README.md", "[Missing](missing.md) [Escape](../outside.md)")
            findings = audit.markdown_link_findings(root, {Path("README.md")})
            self.assertEqual(2, len(findings))
            self.assertEqual({"Markdown link"}, {finding.category for finding in findings})

    def test_html_relative_links_resolve_to_tracked_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write(root, "index.html", '<a href="docs/help.html">Help</a><script src="app.js"></script>')
            self.write(root, "docs/help.html", "Help")
            self.write(root, "app.js", "console.log('synthetic')")
            tracked = {Path("index.html"), Path("docs/help.html"), Path("app.js")}
            self.assertEqual([], audit.html_link_findings(root, tracked))

    def test_html_missing_and_escape_links_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write(root, "index.html", '<a href="missing.html">Missing</a><img src="../outside.png">')
            findings = audit.html_link_findings(root, {Path("index.html")})
            self.assertEqual(2, len(findings))
            self.assertEqual({"HTML link"}, {finding.category for finding in findings})

    def test_external_executable_script_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write(root, "index.html", '<script src="https://cdn.example.test/app.js"></script>')
            findings = audit.external_script_findings(root, {Path("index.html")})
            self.assertEqual(1, len(findings))
            self.assertEqual("external executable script", findings[0].category)


class PdfAndArtifactTests(unittest.TestCase):
    def test_pdf_metadata_contract_accepts_expected_values(self):
        metadata = audit.parse_pdfinfo(
            "Pages: 5\nTagged: yes\nEncrypted: no\nJavaScript: no\nForm: none\nPage size: 420 x 720 pts\n"
        )
        findings = audit.pdf_metadata_findings(
            Path("phone.pdf"), metadata, expected_size="420 x 720 pts"
        )
        self.assertEqual([], findings)

    def test_pdf_metadata_contract_rejects_active_or_wrong_document(self):
        metadata = audit.parse_pdfinfo(
            "Pages: 4\nTagged: no\nEncrypted: yes\nJavaScript: yes\nForm: AcroForm\nPage size: 420 x 720 pts\n"
        )
        findings = audit.pdf_metadata_findings(
            Path("phone.pdf"), metadata, expected_size="420 x 720 pts"
        )
        self.assertEqual(
            {"PDF pages", "PDF tagging", "PDF encryption", "PDF JavaScript", "PDF forms"},
            {finding.category for finding in findings},
        )

    def test_artifact_hash_mismatch_fails_without_printing_content(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "artifact.txt").write_text("synthetic", encoding="utf-8")
            findings = audit.artifact_hash_findings(root, {"artifact.txt": "0" * 64})
            self.assertEqual(1, len(findings))
            self.assertEqual("artifact checksum", findings[0].category)

    def test_chart_artifact_requires_the_pinned_version_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "vendor/chart.umd.min.js"
            path.parent.mkdir(parents=True)
            path.write_text("synthetic chart bundle", encoding="utf-8")
            checksum = hashlib.sha256(path.read_bytes()).hexdigest()
            findings = audit.artifact_hash_findings(
                root, {"vendor/chart.umd.min.js": checksum}
            )
            self.assertEqual(["dependency version"], [f.category for f in findings])


class HistoryIdentityTests(unittest.TestCase):
    @staticmethod
    def user_noreply(label="reviewer"):
        return label + "@" + "users.noreply.github.com"

    @staticmethod
    def platform_identity():
        return "noreply" + "@" + "github.com"

    @staticmethod
    def personal_identity():
        return "reviewer" + "@" + "mail.test"

    def record(self, *, author=None, committer=None, parents=("a", "b"), commit="f" * 40):
        return audit.CommitIdentity(
            commit=commit,
            parents=tuple(parents),
            author=author or self.user_noreply("author"),
            committer=committer or self.user_noreply("committer"),
        )

    def init_repo(self, root):
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Synthetic Reviewer"], cwd=root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "reviewer@users.noreply.github.com"],
            cwd=root,
            check=True,
        )
        (root / "README.md").write_text("synthetic", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "test: synthetic baseline"], cwd=root, check=True)

    def test_noreply_history_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.init_repo(root)
            self.assertEqual([], audit.history_identity_findings(root))

    def test_user_noreply_author_and_committer_pass(self):
        self.assertEqual([], audit.identity_findings([self.record()], allowed_exceptions=set()))

    def test_exact_platform_committer_passes_only_for_merge_shape(self):
        record = self.record(committer=self.platform_identity())
        self.assertEqual([], audit.identity_findings([record], allowed_exceptions=set()))

    def test_personal_author_fails_even_with_platform_committer(self):
        record = self.record(
            author=self.personal_identity(), committer=self.platform_identity()
        )
        findings = audit.identity_findings([record], allowed_exceptions=set())
        self.assertEqual(["commit identity"], [finding.category for finding in findings])

    def test_personal_committer_fails(self):
        record = self.record(committer=self.personal_identity())
        findings = audit.identity_findings([record], allowed_exceptions=set())
        self.assertEqual(["commit identity"], [finding.category for finding in findings])

    def test_arbitrary_github_domain_identity_fails(self):
        arbitrary = "reviewer" + "@" + "github.com"
        record = self.record(committer=arbitrary)
        findings = audit.identity_findings([record], allowed_exceptions=set())
        self.assertEqual(["commit identity"], [finding.category for finding in findings])

    def test_platform_identity_as_author_fails(self):
        record = self.record(author=self.platform_identity())
        findings = audit.identity_findings([record], allowed_exceptions=set())
        self.assertEqual(["commit identity"], [finding.category for finding in findings])

    def test_platform_committer_on_single_parent_commit_fails(self):
        record = self.record(committer=self.platform_identity(), parents=("a",))
        findings = audit.identity_findings([record], allowed_exceptions=set())
        self.assertEqual(["commit identity"], [finding.category for finding in findings])

    def test_documented_legacy_exception_remains_narrow(self):
        legacy_commit = next(iter(audit.KNOWN_IDENTITY_EXCEPTIONS))
        excepted = self.record(
            commit=legacy_commit,
            author=self.personal_identity(),
            committer=self.platform_identity(),
        )
        adjacent = self.record(
            commit="e" * 40,
            author=self.personal_identity(),
            committer=self.platform_identity(),
        )
        self.assertEqual([], audit.identity_findings([excepted]))
        self.assertEqual(1, len(audit.identity_findings([adjacent])))

    def test_non_noreply_history_fails_without_echoing_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.init_repo(root)
            (root / "README.md").write_text("synthetic update", encoding="utf-8")
            environment = os.environ.copy()
            private_email = "reviewer" + "@" + "mail.test"
            environment.update(
                {
                    "GIT_AUTHOR_NAME": "Synthetic Reviewer",
                    "GIT_AUTHOR_EMAIL": private_email,
                    "GIT_COMMITTER_NAME": "Synthetic Reviewer",
                    "GIT_COMMITTER_EMAIL": private_email,
                }
            )
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "test: rejected identity"],
                cwd=root,
                check=True,
                env=environment,
            )
            findings = audit.history_identity_findings(root)
            output = audit.format_findings(findings)
            self.assertEqual(1, len(findings))
            self.assertNotIn(private_email, output)
            self.assertIn("commit identity", output)


class RepositoryIntegrationTests(unittest.TestCase):
    def test_current_data_and_kpis_reconcile(self):
        self.assertEqual([], audit.data_kpi_findings(ROOT))

    def test_data_contract_failures_are_mapped_without_values(self):
        contract_finding = audit.data_contracts.Finding("schema", "synthetic-key", "field")
        with mock.patch.object(
            audit.data_contracts,
            "validate_repository",
            return_value=[contract_finding],
        ):
            findings = audit.data_kpi_findings(ROOT)
        self.assertEqual("data schema", findings[0].category)
        self.assertEqual("synthetic-key:field", findings[0].path)

    def test_current_pdfs_pass_text_and_metadata_checks(self):
        self.assertEqual([], audit.pdf_findings(ROOT))

    def test_current_repository_passes_all_audits(self):
        self.assertEqual([], audit.run_all(ROOT))


class CommandLineTests(unittest.TestCase):
    def test_cli_returns_nonzero_and_redacts_prohibited_content(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            credential = "gh" + "p_" + "C" * 24
            (root / "README.md").write_text(credential, encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                result = audit.main(["--check", "privacy", "--root", str(root)])

            self.assertEqual(1, result)
            self.assertIn("GitHub credential", stderr.getvalue())
            self.assertNotIn(credential, stderr.getvalue())

    def test_cli_success_reports_tracked_count(self):
        stdout = io.StringIO()
        with mock.patch.object(audit, "run_checks", return_value=[]), mock.patch.object(
            audit, "tracked_files", return_value=[Path("README.md")]
        ), redirect_stdout(stdout):
            result = audit.main(["--check", "privacy", "--root", str(ROOT)])
        self.assertEqual(0, result)
        self.assertIn("1 tracked files", stdout.getvalue())

    def test_malformed_history_record_fails_closed(self):
        with mock.patch.object(audit, "_git", return_value=b"malformed"):
            findings = audit.history_identity_findings(ROOT)
        self.assertEqual("commit identity", findings[0].category)


class WorkflowContractTests(unittest.TestCase):
    def test_official_actions_use_verified_node24_release_commits(self):
        workflow = (ROOT / ".github/workflows/quality-gates.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
            workflow,
        )
        self.assertIn(
            "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0",
            workflow,
        )

    def test_platform_provenance_runs_only_for_main_push_with_read_permissions(self):
        workflow = (ROOT / ".github/workflows/quality-gates.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("contents: read", workflow)
        self.assertIn("pull-requests: read", workflow)
        self.assertIn("github-platform-provenance:", workflow)
        self.assertIn("Run GitHub merge provenance audit", workflow)
        self.assertIn("if: github.event_name == 'push'", workflow)
        self.assertIn("python3 scripts/github_provenance_audit.py", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
