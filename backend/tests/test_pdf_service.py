from pathlib import Path

from backend.app.services.pdf_service import extract_text_from_pdf


def test_extract_text_from_pdf():
    pdf_path = Path("data/computers-14-00494.pdf")

    text = extract_text_from_pdf(pdf_path)

    assert isinstance(text, str)
    assert len(text) > 0