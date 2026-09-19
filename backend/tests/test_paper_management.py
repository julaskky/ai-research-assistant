from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def create_test_paper():
    response = client.post(
        "/papers/upload",
        files={
            "file": (
                "computers-14-00494.pdf",
                open("data/computers-14-00494.pdf", "rb"),
                "application/pdf"
            )
        }
    )

    assert response.status_code == 200

    return response.json()["id"]


def test_update_paper():
    paper_id = create_test_paper()

    response = client.put(
        f"/papers/{paper_id}",
        json={
            "title": "Updated Research Paper Title",
            "journal": "Test Journal"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Paper updated successfully"
    assert data["id"] == paper_id
    assert data["title"] == "Updated Research Paper Title"
    assert data["journal"] == "Test Journal"


def test_update_paper_not_found():
    response = client.put(
        "/papers/999999",
        json={
            "title": "Updated Title"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Paper not found."


def test_update_paper_partial_update():
    paper_id = create_test_paper()

    response = client.put(
        f"/papers/{paper_id}",
        json={
            "keywords": "artificial intelligence; software engineering"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["keywords"] == (
        "artificial intelligence; software engineering"
    )


def test_delete_paper():
    paper_id = create_test_paper()

    response = client.delete(f"/papers/{paper_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Paper deleted successfully"
    assert data["id"] == paper_id

    get_response = client.get(f"/papers/{paper_id}")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Paper not found."


def test_delete_paper_not_found():
    response = client.delete("/papers/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Paper not found."