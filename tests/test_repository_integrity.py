import unittest
from pathlib import Path

from scripts import repository_audit as audit


ROOT = Path(__file__).resolve().parents[1]

class RepositoryIntegrityTests(unittest.TestCase):
    def test_required_assets_exist(self):
        required = {
            "index.html", "dashboard.html", "slides.html", "README.md", "LICENSE",
            "synthetic_requisitions.csv", "synthetic_candidates.csv",
            "synthetic_interviews.csv", "Structured_Hiring_and_ATS_Architecture_Case_Study.pdf",
            "Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf",
        }
        self.assertEqual(set(), {name for name in required if not (ROOT / name).is_file()})

    def test_reconciled_metrics(self):
        self.assertEqual([], audit.data_kpi_findings(ROOT))

    def test_no_pii_secrets_or_local_paths(self):
        tracked = audit.tracked_files(ROOT)
        self.assertEqual([], audit.tracked_path_findings(tracked, ROOT))
        self.assertEqual([], audit.privacy_findings(ROOT, tracked))

    def test_relative_html_links_resolve_inside_repository(self):
        self.assertEqual([], audit.html_link_findings(ROOT))


if __name__ == "__main__":
    unittest.main(verbosity=2)
