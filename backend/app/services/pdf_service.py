from pathlib import Path

import fitz


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from all pages of a PDF document."""
    text = []

    with fitz.open(file_path) as document:
        for page in document:
            text.append(page.get_text())

    return "\n".join(text).strip()