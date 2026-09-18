from pathlib import Path

from backend.app.services.pdf_service import extract_text_from_pdf


def test_extract_text_from_pdf():
    pdf_path = Path("data/computers-14-00494.pdf")

    text = extract_text_from_pdf(pdf_path)

    assert isinstance(text, str)
    assert len(text) > 0



from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_upload_rejects_non_pdf():
    response = client.post(
        "/papers/upload",
        files={
            "file": (
                "test.txt",
                b"This is not a PDF file.",
                "text/plain"
            )
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed."