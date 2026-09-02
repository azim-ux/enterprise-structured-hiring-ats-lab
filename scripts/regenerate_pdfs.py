#!/usr/bin/env python3
"""Regenerate the two governed PDFs from local HTML/CSS without network assets."""

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = (
    ("slides.html", "Structured_Hiring_and_ATS_Architecture_Case_Study.pdf"),
    ("mobile-case-study.html", "Structured_Hiring_and_ATS_Architecture_Mobile_Case_Study.pdf"),
)
FIXED_PDF_DATE = b"D:20000101000000+00'00'"
DATE_FIELDS = (b"CreationDate", b"ModDate")


def find_browser(explicit=None):
    if explicit:
        candidate = Path(explicit)
        if candidate.is_file():
            return candidate
        raise RuntimeError("requested browser executable is unavailable")
    for command in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        resolved = shutil.which(command)
        if resolved:
            return Path(resolved)
    macos_candidate = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if macos_candidate.is_file():
        return macos_candidate
    raise RuntimeError("Chrome or Chromium executable was not found")


def normalize_metadata(payload):
    """Replace volatile browser timestamps as part of the deterministic build."""
    normalized = payload
    for field in DATE_FIELDS:
        pattern = rb"/" + field + rb" \(D:\d{14}\+00'00'\)"
        replacement = b"/" + field + b" (" + FIXED_PDF_DATE + b")"
        normalized, count = re.subn(pattern, replacement, normalized, count=1)
        if count != 1:
            raise RuntimeError("expected PDF metadata field was not generated")
    return normalized


def render_pdf(browser, source, output):
    with tempfile.TemporaryDirectory(prefix="ats-pdf-build-") as directory:
        temporary_output = Path(directory) / output.name
        command = (
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--disable-background-networking",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={temporary_output}",
            source.resolve().as_uri(),
        )
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0 or not temporary_output.is_file():
            raise RuntimeError("browser PDF rendering failed")
        output.write_bytes(normalize_metadata(temporary_output.read_bytes()))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", help="path to a local Chrome or Chromium executable")
    return parser


def main(argv=None):
    arguments = build_parser().parse_args(argv)
    browser = find_browser(arguments.browser)
    for source_name, output_name in OUTPUTS:
        render_pdf(browser, ROOT / source_name, ROOT / output_name)
    print("Regenerated 2 governed PDF artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
