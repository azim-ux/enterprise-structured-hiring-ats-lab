import csv
import re
import unittest
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def read_csv(name):
    with (ROOT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, _tag, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.links.append(value)


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
        requisitions = read_csv("synthetic_requisitions.csv")
        candidates = read_csv("synthetic_candidates.csv")
        interviews = read_csv("synthetic_interviews.csv")
        self.assertEqual((5, 4_000, 2_000), (len(requisitions), len(candidates), len(interviews)))
        self.assertEqual(120, sum(row["Current_Stage"] == "Hired" for row in candidates))
        self.assertEqual(Decimal("28.5"), sum(Decimal(row["Days_to_Fill"]) for row in requisitions) / 5)
        self.assertEqual(1_836, sum(row["SLA_Met"] == "Yes" for row in interviews))
        reference = [row for row in candidates if row["Demographic_Cohort"] == "Reference Group"]
        focal = [row for row in candidates if row["Demographic_Cohort"] == "Focal Group"]
        ref_rate = Decimal(sum(bool(row["Phone_Screen_Score"]) for row in reference)) / len(reference)
        focal_rate = Decimal(sum(bool(row["Phone_Screen_Score"]) for row in focal)) / len(focal)
        self.assertEqual(Decimal("0.87"), (focal_rate / ref_rate).quantize(Decimal("0.01")))

    def test_no_pii_secrets_or_local_paths(self):
        patterns = {
            "Indian mobile": re.compile(r"(?<!\d)[6-9]\d{9}(?!\d)"),
            "Aadhaar": re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b"),
            "PAN": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
            "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
            "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
        }
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or path.suffix.lower() == ".pdf":
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            self.assertNotIn("/" + "Users" + "/", text, path)
            self.assertNotIn("C:\\" + "Users" + "\\", text, path)
            for label, pattern in patterns.items():
                self.assertIsNone(pattern.search(text), f"{label} pattern in {path}")

    def test_relative_html_links_resolve_inside_repository(self):
        for path in ROOT.glob("*.html"):
            parser = LinkCollector()
            parser.feed(path.read_text(encoding="utf-8"))
            for raw_link in parser.links:
                parsed = urlsplit(raw_link)
                if parsed.scheme or raw_link.startswith(("//", "#", "data:")):
                    continue
                target = (path.parent / unquote(parsed.path)).resolve()
                self.assertTrue(target.is_relative_to(ROOT), (path.name, raw_link))
                self.assertTrue(target.exists(), (path.name, raw_link))


if __name__ == "__main__":
    unittest.main(verbosity=2)
