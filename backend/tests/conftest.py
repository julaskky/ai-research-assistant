from pathlib import Path

import pymupdf
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.database import Base, get_db


TEST_PDF_PATH = Path("data/computers-14-00494.pdf")

TEST_TITLE = (
    "eXplainable AI Framework for Automated Lesson Plan "
    "Generation and Alignment with Bloom’s Taxonomy"
)

TEST_AUTHORS = (
    "Deborah Olaniyan, Julius Olaniyan, "
    "Ibidun C. Obagbuwa and Anthony K. Tsetse"
)

TEST_CITATION_AUTHORS = (
    "Olaniyan, D.; Olaniyan, J.; "
    "Obagbuwa, I.C.; Tsetse, A.K."
)

TEST_TEXT_LENGTH = 56611


def create_test_pdf(pdf_path: Path):
    """Create a deterministic academic-style PDF for automated tests."""
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    document = pymupdf.open()

    page = document.new_page()

    text = (
        "Article\n"
        f"{TEST_TITLE}\n"
        "1\n"
        f"Citation: {TEST_CITATION_AUTHORS}\n"
        "eXplainable AI Framework\n"
        "\n"
        "Abstract\n"
        "This paper presents an artificial intelligence framework "
        "for automated lesson plan generation and alignment with "
        "Bloom's Taxonomy.\n"
        "\n"
        "Keywords\n"
        "artificial intelligence; lesson plan generation; "
        "Bloom's Taxonomy; explainable AI\n"
        "\n"
        "Introduction\n"
        "This test document represents an academic research paper "
        "used only for automated software testing.\n"
        "\n"
        "DOI: 10.3390/computers14040094\n"
        "Published in 2025.\n"
    )

    if len(text) < TEST_TEXT_LENGTH:
        text += " Academic research content for automated testing." * (
            (TEST_TEXT_LENGTH - len(text)) // 49 + 1
        )

    text = text[:TEST_TEXT_LENGTH]

    page.insert_textbox(
        pymupdf.Rect(50, 50, 545, 780),
        text,
        fontsize=8,
    )

    document.set_metadata(
        {
            "title": TEST_TITLE,
            "author": TEST_AUTHORS,
            "subject": "Artificial intelligence research",
            "keywords": (
                "artificial intelligence; lesson plan generation; "
                "Bloom's Taxonomy"
            ),
        }
    )

    document.save(pdf_path)
    document.close()


@pytest.fixture(scope="session", autouse=True)
def test_database(tmp_path_factory):
    """
    Create an isolated SQLite database for the entire test session.

    A deterministic test PDF is created automatically when the real
    development PDF is not available. This keeps CI independent of
    ignored local research files.
    """
    pdf_was_created = False

    if not TEST_PDF_PATH.exists():
        create_test_pdf(TEST_PDF_PATH)
        pdf_was_created = True

    db_directory = tmp_path_factory.mktemp("test_database")
    db_path = db_directory / "test_research_assistant.db"

    test_database_url = f"sqlite:///{db_path}"

    engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False}
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        with open(TEST_PDF_PATH, "rb") as pdf_file:
            response = client.post(
                "/papers/upload",
                files={
                    "file": (
                        TEST_PDF_PATH.name,
                        pdf_file,
                        "application/pdf"
                    )
                }
            )

        assert response.status_code == 200
        assert response.json()["id"] == 1

    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    if pdf_was_created and TEST_PDF_PATH.exists():
        TEST_PDF_PATH.unlink()