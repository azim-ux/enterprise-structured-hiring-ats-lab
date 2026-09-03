import hashlib
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLIDES = ROOT / "slides.html"
DESKTOP_PDF = ROOT / "Structured_Hiring_and_ATS_Architecture_Case_Study.pdf"
MOBILE_PDF = ROOT / "Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf"
MOBILE_SHA256 = "4e8b208c0f5d499c9ce2dde3c08b0e2d3cb0a0bc6c2d032818db303cd70429c1"

TYPE_TARGETS = {
    "--print-cover": (54.0, 64.0),
    "--print-title": (32.0, 40.0),
    "--print-eyebrow": (11.0, 14.0),
    "--print-body": (15.0, 18.0),
    "--print-label": (12.0, 14.0),
    "--print-caption": (12.0, 14.0),
    "--print-formula": (20.0, 24.0),
    "--print-kpi": (28.0, 40.0),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def color_luminance(value):
    channels = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(foreground, background):
    first, second = color_luminance(foreground), color_luminance(background)
    return (max(first, second) + 0.05) / (min(first, second) + 0.05)


def custom_properties(source):
    return dict(re.findall(r"(--print-[a-z-]+)\s*:\s*([^;]+);", source))


def pdf_xml():
    completed = subprocess.run(
        ["pdftohtml", "-xml", "-hidden", "-nodrm", "-stdout", str(DESKTOP_PDF)],
        check=True,
        capture_output=True,
        text=True,
    )
    return ET.fromstring(completed.stdout)


class DesktopPrintDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SLIDES.read_text(encoding="utf-8")

    def test_print_typography_tokens_meet_editorial_targets(self):
        properties = custom_properties(self.source)
        for token, (minimum, maximum) in TYPE_TARGETS.items():
            with self.subTest(token=token):
                self.assertTrue(token in properties, f"missing required print token: {token}")
                match = re.fullmatch(r"([0-9.]+)pt", properties[token].strip())
                self.assertIsNotNone(match, f"{token} must use deterministic print points")
                value = float(match.group(1))
                self.assertGreaterEqual(value, minimum)
                self.assertLessEqual(value, maximum)

    def test_print_text_colors_meet_wcag_aa_on_paper(self):
        properties = custom_properties(self.source)
        paper = properties.get("--print-paper")
        self.assertRegex(paper or "", r"^#[0-9a-fA-F]{6}$")
        for token in ("--print-ink-color", "--print-body-color", "--print-muted-color", "--print-teal-color", "--print-amber-color"):
            with self.subTest(token=token):
                color = properties.get(token)
                self.assertRegex(color or "", r"^#[0-9a-fA-F]{6}$")
                self.assertGreaterEqual(contrast_ratio(color, paper), 4.5)

    def test_editorial_structures_replace_pill_and_card_templates(self):
        for required in ("evidence-strip", "evidence-path", "control-register", "executive-scorecard", "action-sequence"):
            with self.subTest(required=required):
                self.assertTrue(
                    f'class="{required}' in self.source,
                    f"missing required editorial structure: {required}",
                )
        for retired in ('class="chips"', 'class="chip"', 'class="grid-3"', 'class="card"', 'class="results"', 'class="result"', 'class="next"'):
            with self.subTest(retired=retired):
                self.assertTrue(retired not in self.source, "retired template structure remains")

    def test_rendered_pdf_has_five_nonempty_pages_and_required_text(self):
        expected = {
            1: ("Evidence over instinct", "100% synthetic", "Not for real applicant data"),
            2: ("Six design stages", "PROPOSED", "MODELED", "TESTED"),
            3: ("0.40", "4.60", "3.92", "+0.68"),
            4: ("624 / 2,400", "362 / 1,600", "0.87", "indicator, not proof"),
            5: ("4,000", "91.8%", "Explore", "Inspect", "Challenge", "Not suitable for real applicant data"),
        }
        for page, snippets in expected.items():
            completed = subprocess.run(
                ["pdftotext", "-f", str(page), "-l", str(page), "-layout", str(DESKTOP_PDF), "-"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue(completed.stdout.strip(), f"desktop PDF page {page} is empty")
            self.assertNotIn("\ufffd", completed.stdout, f"desktop PDF page {page} contains a replacement glyph")
            for snippet in snippets:
                with self.subTest(page=page, snippet=snippet):
                    self.assertIn(snippet, completed.stdout)

    def test_rendered_text_meets_twelve_point_floor_and_page_bounds(self):
        root = pdf_xml()
        self.assertEqual(5, len(root.findall("page")))
        fonts = {}
        for page in root.findall("page"):
            width = float(page.attrib["width"])
            height = float(page.attrib["height"])
            scale = width / 960.0
            fonts.update({item.attrib["id"]: float(item.attrib["size"]) / scale for item in page.findall("fontspec")})
            visible_sizes = []
            for item in page.findall("text"):
                text_value = "".join(item.itertext()).strip()
                if not text_value:
                    continue
                visible_sizes.append(fonts[item.attrib["font"]])
                left, top = float(item.attrib["left"]), float(item.attrib["top"])
                item_width, item_height = float(item.attrib["width"]), float(item.attrib["height"])
                self.assertGreaterEqual(left, 0)
                self.assertGreaterEqual(top, 0)
                self.assertLessEqual(left + item_width, width + 1)
                self.assertLessEqual(top + item_height, height + 1)
            self.assertTrue(visible_sizes)
            self.assertGreaterEqual(min(visible_sizes), 12.0, f"page {page.attrib['number']} contains undersized text")

    def test_mobile_pdf_matches_reviewed_linkedin_artifact(self):
        self.assertEqual(MOBILE_SHA256, sha256(MOBILE_PDF))


if __name__ == "__main__":
    unittest.main(verbosity=2)
