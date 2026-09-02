import subprocess
import unittest
from pathlib import Path

from scripts import claims_policy


ROOT = Path(__file__).resolve().parents[1]


def pdf_text(path):
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


class ClaimsPolicyRedCycleTests(unittest.TestCase):
    def test_policy_rejects_affirmative_unsupported_claims(self):
        cases = {
            "production-system": "A privacy-first enterprise hiring system for global use.",
            "implemented-rbac": "Recruiters receive separated permissions.",
            "implemented-sensitive-control": "The application implements encryption.",
            "operational-erasure": "Rejected résumés queued for 180-day purge.",
            "legal-compliance": "The selection process is legally compliant.",
            "validated-fairness": "This is a bias-free selection model.",
            "predictive-validity": "Predictive validity was established locally.",
            "accessibility-conformance": "The artifact is WCAG compliant.",
        }
        for expected, text in cases.items():
            with self.subTest(expected=expected):
                self.assertIn(expected, {item.rule for item in claims_policy.evaluate_claims(text)})

    def test_policy_allows_qualified_design_and_limitation_language(self):
        allowed = (
            "An enterprise-oriented reference implementation under development.",
            "Proposed control design: production RBAC and encryption are required.",
            "This static artifact does not implement access enforcement or erasure.",
            "The indicator is not proof of compliance or absence of bias.",
            "The rule is not proof that a process is legally compliant or free from bias.",
            "Independent legal, security, accessibility and validation review is required.",
        )
        for text in allowed:
            with self.subTest(text=text):
                self.assertEqual([], claims_policy.evaluate_claims(text))

    def test_qualified_mention_does_not_hide_a_later_affirmative_claim(self):
        text = (
            "The proposal is not proof of validated fairness. "
            "The released selection model is bias-free."
        )
        self.assertIn(
            "validated-fairness",
            {item.rule for item in claims_policy.evaluate_claims(text)},
        )

    def test_current_html_sources_do_not_assert_unimplemented_controls(self):
        findings = []
        for relative in ("slides.html", "mobile-case-study.html"):
            findings.extend(claims_policy.evaluate_claims((ROOT / relative).read_text(encoding="utf-8")))
        self.assertEqual([], findings)

    def test_current_pdf_text_does_not_assert_unimplemented_controls(self):
        findings = []
        for relative in (
            "Structured_Hiring_and_ATS_Architecture_Case_Study.pdf",
            "Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf",
        ):
            findings.extend(claims_policy.evaluate_claims(pdf_text(ROOT / relative)))
        self.assertEqual([], findings)


if __name__ == "__main__":
    unittest.main(verbosity=2)
