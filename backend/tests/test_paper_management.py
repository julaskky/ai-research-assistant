from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_update_paper():
    response = client.put(
        "/papers/3",
        json={
            "title": "Updated Research Paper Title",
            "journal": "Test Journal"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Paper updated successfully"
    assert data["id"] == 3
    assert data["title"] == "Updated Research Paper Title"
    assert data["journal"] == "Test Journal"


def test_update_paper_not_found():
    response = client.put(
        "/papers/999",
        json={
            "title": "Updated Title"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Paper not found."


def test_update_paper_partial_update():
    response = client.put(
        "/papers/3",
        json={
            "keywords": "artificial intelligence; software engineering"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["keywords"] == (
        "artificial intelligence; software engineering"
    )
    assert data["title"] == "Updated Research Paper Title"
    assert data["journal"] == "Test Journal"





def test_delete_paper():
    response = client.delete("/papers/3")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Paper deleted successfully"
    assert data["id"] == 3

    get_response = client.get("/papers/3")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Paper not found."


def test_delete_paper_not_found():
    response = client.delete("/papers/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Paper not found."