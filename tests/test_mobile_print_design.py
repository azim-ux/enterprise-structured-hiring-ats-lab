import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "mobile-case-study.html"
STYLES = ROOT / "mobile-case-study.css"
PDF = ROOT / "Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf"

TYPE_TARGETS = {
    "--mobile-cover": (36.0, 44.0),
    "--mobile-title": (25.0, 31.0),
    "--mobile-body": (12.0, 15.0),
    "--mobile-label": (10.0, 12.0),
    "--mobile-caption": (10.0, 12.0),
    "--mobile-kpi": (26.0, 34.0),
}


def color_luminance(value):
    channels = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(foreground, background):
    first, second = color_luminance(foreground), color_luminance(background)
    return (max(first, second) + 0.05) / (min(first, second) + 0.05)


def custom_properties(source):
    return dict(re.findall(r"(--mobile-[a-z-]+)\s*:\s*([^;]+);", source))


def pdf_xml():
    completed = subprocess.run(
        ["pdftohtml", "-xml", "-hidden", "-nodrm", "-i", "-stdout", str(PDF)],
        check=True,
        capture_output=True,
        text=True,
    )
    return ET.fromstring(completed.stdout)


class MobilePrintDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.styles = STYLES.read_text(encoding="utf-8")

    def test_linkedin_narrative_uses_five_distinct_expert_prompts(self):
        expected = (
            "Can 4,000 applications stay auditable?",
            "Six stages. One evidence chain.",
            "A stronger story cannot outrank stronger evidence.",
            "Fairness needs counts, not comfort.",
            "Built to be inspected.",
        )
        for phrase in expected:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.source)
        self.assertEqual(5, self.source.count('<section class="page'))

    def test_editorial_structures_replace_generic_cards_and_pills(self):
        required = (
            "proof-rail",
            "evidence-path",
            "formula-panel",
            "control-case",
            "fairness-equation",
            "review-sequence",
        )
        for class_name in required:
            with self.subTest(class_name=class_name):
                self.assertIn(f'class="{class_name}', self.source)
        for retired in ('class="chips"', 'class="chip"', 'class="metric-grid"', 'class="card-grid"', 'class="card"'):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, self.source)

    def test_mobile_typography_tokens_protect_phone_readability(self):
        properties = custom_properties(self.styles)
        for token, (minimum, maximum) in TYPE_TARGETS.items():
            with self.subTest(token=token):
                self.assertIn(token, properties)
                match = re.fullmatch(r"([0-9.]+)pt", properties[token].strip())
                self.assertIsNotNone(match, f"{token} must use deterministic print points")
                value = float(match.group(1))
                self.assertGreaterEqual(value, minimum)
                self.assertLessEqual(value, maximum)

    def test_mobile_palette_meets_wcag_aa_for_body_and_accents(self):
        properties = custom_properties(self.styles)
        paper = properties.get("--mobile-paper")
        self.assertRegex(paper or "", r"^#[0-9a-fA-F]{6}$")
        for token in ("--mobile-ink", "--mobile-body-color", "--mobile-teal", "--mobile-amber"):
            with self.subTest(token=token):
                color = properties.get(token)
                self.assertRegex(color or "", r"^#[0-9a-fA-F]{6}$")
                self.assertGreaterEqual(contrast_ratio(color, paper), 4.5)

    def test_rendered_pdf_has_five_complete_pages_and_expert_evidence(self):
        expected = {
            1: ("Can 4,000 applications stay auditable?", "100% SYNTHETIC", "OPEN-SOURCE"),
            2: ("Six stages. One evidence chain.", "Authorize", "Knockout", "Calibrate"),
            3: ("0.40", "4.60", "3.92", "+0.68"),
            4: ("624 / 2,400", "362 / 1,600", "22.6% ÷ 26.0% = 0.87", "1,836 / 2,000"),
            5: ("Built to be inspected.", "Explore the live model", "Audit the source", "Not suitable for real applicant data"),
        }
        for page, snippets in expected.items():
            completed = subprocess.run(
                ["pdftotext", "-f", str(page), "-l", str(page), "-layout", str(PDF), "-"],
                check=True,
                capture_output=True,
                text=True,
            )
            normalized = re.sub(r"\s+", " ", completed.stdout).strip()
            self.assertTrue(normalized, f"mobile PDF page {page} is empty")
            self.assertNotIn("\ufffd", normalized, f"mobile PDF page {page} contains a replacement glyph")
            for snippet in snippets:
                with self.subTest(page=page, snippet=snippet):
                    self.assertIn(snippet, normalized)

    def test_decorative_folios_do_not_interrupt_pdf_reading_order(self):
        expected = {
            1: ("Can 4,000 applications stay auditable?", "01"),
            5: ("Built to be inspected.", "05"),
        }
        for page, (headline, decorative_folio) in expected.items():
            completed = subprocess.run(
                ["pdftotext", "-f", str(page), "-l", str(page), "-layout", str(PDF), "-"],
                check=True,
                capture_output=True,
                text=True,
            )
            normalized = re.sub(r"\s+", " ", completed.stdout).strip()
            with self.subTest(page=page):
                self.assertIn(headline, normalized)
                self.assertNotRegex(normalized, rf"(?<!\d){decorative_folio}(?!\d)")

        self.assertNotRegex(
            self.source,
            r'<(?:div|span)[^>]*class="[^"]*cover-index[^"]*"[^>]*>\s*(?:01|05)\s*</(?:div|span)>',
        )
        self.assertNotRegex(self.source, r'<text\b[^>]*>\s*(?:01|05)\s*</text>')

    def test_rendered_text_stays_inside_page_bounds(self):
        root = pdf_xml()
        pages = root.findall("page")
        self.assertEqual(5, len(pages))
        fonts = {}
        for page in pages:
            width = float(page.attrib["width"])
            height = float(page.attrib["height"])
            scale = width / 420.0
            fonts.update({item.attrib["id"]: float(item.attrib["size"]) / scale for item in page.findall("fontspec")})
            visible_sizes = []
            for item in page.findall("text"):
                text_value = "".join(item.itertext()).strip()
                if not text_value:
                    continue
                visible_sizes.append(fonts[item.attrib["font"]])
                left = float(item.attrib["left"])
                top = float(item.attrib["top"])
                item_width = float(item.attrib["width"])
                item_height = float(item.attrib["height"])
                self.assertGreaterEqual(left, 0)
                self.assertGreaterEqual(top, 0)
                self.assertLessEqual(left + item_width, width + 1)
                self.assertLessEqual(top + item_height, height + 1)
            self.assertTrue(visible_sizes)
            self.assertGreaterEqual(min(visible_sizes), 9.0, f"page {page.attrib['number']} contains undersized text")


if __name__ == "__main__":
    unittest.main(verbosity=2)
