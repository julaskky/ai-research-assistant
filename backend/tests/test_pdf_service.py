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



def test_get_papers():
    response = client.get("/papers")

    assert response.status_code == 200

    papers = response.json()

    assert isinstance(papers, list)
    assert len(papers) >= 1
    assert papers[0]["filename"] == "computers-14-00494.pdf"



def test_get_paper():
    response = client.get("/papers/1")

    assert response.status_code == 200

    paper = response.json()

    assert paper["id"] == 1
    assert paper["filename"] == "computers-14-00494.pdf"
    assert paper["title"] == "computers-14-00494.pdf"
    assert paper["text_length"] == 56611


def test_get_paper_not_found():
    response = client.get("/papers/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Paper not found."



def test_get_paper_text():
    response = client.get("/papers/1/text")

    assert response.status_code == 200

    paper = response.json()

    assert paper["id"] == 1
    assert paper["filename"] == "computers-14-00494.pdf"
    assert len(paper["extracted_text"]) > 0


def test_get_paper_text_not_found():
    response = client.get("/papers/999/text")

    assert response.status_code == 404
    assert response.json()["detail"] == "Paper not found."



def test_search_papers():
    response = client.get("/papers/search?q=AI")

    assert response.status_code == 200

    papers = response.json()

    assert isinstance(papers, list)
    assert len(papers) >= 1
    assert papers[0]["filename"] == "computers-14-00494.pdf"


def test_search_papers_no_results():
    response = client.get("/papers/search?q=xyznonexistent123")

    assert response.status_code == 200
    assert response.json() == []


def test_search_papers_empty_query():
    response = client.get("/papers/search?q=")

    assert response.status_code == 400
    assert response.json()["detail"] == "Search query cannot be empty."