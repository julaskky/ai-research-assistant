import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.database import Base, get_db


@pytest.fixture(scope="session", autouse=True)
def test_database(tmp_path_factory):
    """
    Create an isolated SQLite database for the entire test session.

    A known baseline paper is inserted so tests can safely verify
    paper retrieval and search behavior without relying on the
    development database.
    """
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

    # Create one known baseline paper for tests that need paper ID 1.
    pdf_path = "data/computers-14-00494.pdf"

    with TestClient(app) as client:
        with open(pdf_path, "rb") as pdf_file:
            response = client.post(
                "/papers/upload",
                files={
                    "file": (
                        "computers-14-00494.pdf",
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