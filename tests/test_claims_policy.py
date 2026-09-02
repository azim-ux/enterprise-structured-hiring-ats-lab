import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

UNSUPPORTED_IMPLEMENTATION_CLAIMS = (
    "a privacy-first enterprise hiring system",
    "blind automated knockout",
    "transfer + purge",
    "cohorts hidden from screeners and panels",
    "rejected résumés queued for 180-day purge",
    "receive separated permissions",
)


def literal_findings(text):
    lowered = text.casefold()
    return [claim for claim in UNSUPPORTED_IMPLEMENTATION_CLAIMS if claim.casefold() in lowered]


def pdf_text(path):
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


class ClaimsPolicyRedCycleTests(unittest.TestCase):
    def test_current_html_sources_do_not_assert_unimplemented_controls(self):
        findings = []
        for relative in ("slides.html", "mobile-case-study.html"):
            findings.extend(literal_findings((ROOT / relative).read_text(encoding="utf-8")))
        self.assertEqual([], findings)

    def test_current_pdf_text_does_not_assert_unimplemented_controls(self):
        findings = []
        for relative in (
            "Structured_Hiring_and_ATS_Architecture_Case_Study.pdf",
            "Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf",
        ):
            findings.extend(literal_findings(pdf_text(ROOT / relative)))
        self.assertEqual([], findings)


if __name__ == "__main__":
    unittest.main(verbosity=2)
