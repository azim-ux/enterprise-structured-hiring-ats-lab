import unittest
import subprocess
import tempfile
from pathlib import Path
from unittest import mock

from scripts import regenerate_pdfs


class PdfRegenerationTests(unittest.TestCase):
    def test_normalization_replaces_only_volatile_browser_dates(self):
        payload = (
            b"prefix /CreationDate (D:20260902131445+00'00') "
            b"/ModDate (D:20260902131445+00'00') suffix"
        )
        normalized = regenerate_pdfs.normalize_metadata(payload)
        self.assertEqual(2, normalized.count(regenerate_pdfs.FIXED_PDF_DATE))
        self.assertNotIn(b"20260902131445", normalized)

    def test_normalization_fails_closed_when_metadata_is_incomplete(self):
        with self.assertRaisesRegex(RuntimeError, "metadata field"):
            regenerate_pdfs.normalize_metadata(
                b"/CreationDate (D:20260902131445+00'00')"
            )

    def test_source_to_output_mapping_is_stable_and_local(self):
        expected = (
            ("slides.html", "Structured_Hiring_and_ATS_Architecture_Case_Study.pdf"),
            ("mobile-case-study.html", "Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf"),
        )
        self.assertEqual(expected, regenerate_pdfs.OUTPUTS)
        for source, output in regenerate_pdfs.OUTPUTS:
            self.assertEqual(Path(source).name, source)
            self.assertEqual(Path(output).name, output)

    def test_explicit_browser_must_be_an_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            browser = Path(directory) / "browser"
            browser.touch()
            self.assertEqual(browser, regenerate_pdfs.find_browser(str(browser)))
            with self.assertRaisesRegex(RuntimeError, "browser executable"):
                regenerate_pdfs.find_browser(str(browser.with_name("missing")))

    def test_path_browser_lookup_returns_the_first_available_command(self):
        with mock.patch.object(regenerate_pdfs.shutil, "which") as which:
            which.side_effect = lambda command: "/synthetic/chrome" if command == "chromium" else None
            self.assertEqual(Path("/synthetic/chrome"), regenerate_pdfs.find_browser())

    def test_render_writes_only_normalized_browser_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.html"
            output = root / "output.pdf"
            source.write_text("synthetic", encoding="utf-8")
            raw = (
                b"/CreationDate (D:20260902131445+00'00') "
                b"/ModDate (D:20260902131445+00'00')"
            )

            def fake_run(command, **_kwargs):
                destination = next(item.split("=", 1)[1] for item in command if item.startswith("--print-to-pdf="))
                Path(destination).write_bytes(raw)
                return subprocess.CompletedProcess(command, 0, "", "")

            with mock.patch.object(regenerate_pdfs.subprocess, "run", side_effect=fake_run):
                regenerate_pdfs.render_pdf(Path("/synthetic/chrome"), source, output)
            self.assertEqual(2, output.read_bytes().count(regenerate_pdfs.FIXED_PDF_DATE))

    def test_render_failure_is_redacted_and_fails_closed(self):
        completed = subprocess.CompletedProcess(["browser"], 1, "private", "private")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.html"
            source.write_text("synthetic", encoding="utf-8")
            with mock.patch.object(regenerate_pdfs.subprocess, "run", return_value=completed):
                with self.assertRaisesRegex(RuntimeError, "browser PDF rendering failed"):
                    regenerate_pdfs.render_pdf(Path("/synthetic/chrome"), source, root / "output.pdf")

    def test_main_builds_both_governed_pairs(self):
        with mock.patch.object(regenerate_pdfs, "find_browser", return_value=Path("browser")), mock.patch.object(
            regenerate_pdfs, "render_pdf"
        ) as render:
            self.assertEqual(0, regenerate_pdfs.main([]))
        self.assertEqual(2, render.call_count)


if __name__ == "__main__":
    unittest.main(verbosity=2)
