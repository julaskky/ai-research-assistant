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


def test_create_research_note():
    paper_id = create_test_paper()

    response = client.post(
        f"/papers/{paper_id}/notes",
        json={
            "note": "This paper provides a useful approach for automated lesson plan generation."
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Research note created successfully"
    assert data["id"] is not None
    assert data["paper_id"] == paper_id
    assert data["note"] == (
        "This paper provides a useful approach for automated lesson plan generation."
    )
    assert data["created_at"] is not None
    assert data["updated_at"] is not None



def test_create_research_note_paper_not_found():
    response = client.post(
        "/papers/999999/notes",
        json={
            "note": "This note should not be created."
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Paper not found."


def test_get_research_notes():
    paper_id = create_test_paper()

    first_note = "This paper presents an interesting research methodology."
    second_note = "The methodology could be adapted for future research."

    first_response = client.post(
        f"/papers/{paper_id}/notes",
        json={"note": first_note}
    )

    second_response = client.post(
        f"/papers/{paper_id}/notes",
        json={"note": second_note}
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    response = client.get(f"/papers/{paper_id}/notes")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["paper_id"] == paper_id
    assert data[0]["note"] == first_note

    assert data[1]["paper_id"] == paper_id
    assert data[1]["note"] == second_note


def test_get_research_notes_paper_not_found():
    response = client.get("/papers/999999/notes")

    assert response.status_code == 404
    assert response.json()["detail"] == "Paper not found."



def test_get_research_note():
    paper_id = create_test_paper()

    create_response = client.post(
        f"/papers/{paper_id}/notes",
        json={
            "note": "This is an important observation from the paper."
        }
    )

    assert create_response.status_code == 200

    created_note = create_response.json()

    note_id = created_note["id"]

    response = client.get(f"/notes/{note_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == note_id
    assert data["paper_id"] == paper_id
    assert data["note"] == (
        "This is an important observation from the paper."
    )
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_get_research_note_not_found():
    response = client.get("/notes/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Research note not found."


def test_update_research_note():
    paper_id = create_test_paper()

    create_response = client.post(
        f"/papers/{paper_id}/notes",
        json={
            "note": "Original research observation."
        }
    )

    assert create_response.status_code == 200

    note_id = create_response.json()["id"]

    response = client.put(
        f"/notes/{note_id}",
        json={
            "note": "Updated research observation."
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Research note updated successfully"
    assert data["id"] == note_id
    assert data["paper_id"] == paper_id
    assert data["note"] == "Updated research observation."
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_update_research_note_not_found():
    response = client.put(
        "/notes/999999",
        json={
            "note": "This note does not exist."
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Research note not found."



def test_delete_research_note():
    paper_id = create_test_paper()

    create_response = client.post(
        f"/papers/{paper_id}/notes",
        json={
            "note": "This note will be deleted."
        }
    )

    assert create_response.status_code == 200

    note_id = create_response.json()["id"]

    response = client.delete(f"/notes/{note_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Research note deleted successfully"
    assert data["id"] == note_id

    get_response = client.get(f"/notes/{note_id}")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Research note not found."


def test_delete_research_note_not_found():
    response = client.delete("/notes/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Research note not found."