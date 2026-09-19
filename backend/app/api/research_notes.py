from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.database.models import Paper, ResearchNote
from backend.app.schemas import ResearchNoteCreate, ResearchNoteUpdate


router = APIRouter(
    tags=["Research Notes"]
)

@router.post("/papers/{paper_id}/notes")
def create_research_note(
    paper_id: int,
    note_data: ResearchNoteCreate,
    db: Session = Depends(get_db)
):
    paper = (
        db.query(Paper)
        .filter(Paper.id == paper_id)
        .first()
    )

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found."
        )

    note = ResearchNote(
        paper_id=paper_id,
        note=note_data.note
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return {
        "message": "Research note created successfully",
        "id": note.id,
        "paper_id": note.paper_id,
        "note": note.note,
        "created_at": note.created_at,
        "updated_at": note.updated_at
    }

@router.get("/papers/{paper_id}/notes")
def get_research_notes(
    paper_id: int,
    db: Session = Depends(get_db)
):
    paper = (
        db.query(Paper)
        .filter(Paper.id == paper_id)
        .first()
    )

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found."
        )

    notes = (
        db.query(ResearchNote)
        .filter(ResearchNote.paper_id == paper_id)
        .order_by(ResearchNote.created_at.asc())
        .all()
    )

    return [
        {
            "id": note.id,
            "paper_id": note.paper_id,
            "note": note.note,
            "created_at": note.created_at,
            "updated_at": note.updated_at
        }
        for note in notes
    ]

@router.get("/notes/{note_id}")
def get_research_note(
    note_id: int,
    db: Session = Depends(get_db)
):
    note = (
        db.query(ResearchNote)
        .filter(ResearchNote.id == note_id)
        .first()
    )

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Research note not found."
        )

    return {
        "id": note.id,
        "paper_id": note.paper_id,
        "note": note.note,
        "created_at": note.created_at,
        "updated_at": note.updated_at
    }



@router.put("/notes/{note_id}")
def update_research_note(
    note_id: int,
    note_data: ResearchNoteUpdate,
    db: Session = Depends(get_db)
):
    note = (
        db.query(ResearchNote)
        .filter(ResearchNote.id == note_id)
        .first()
    )

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Research note not found."
        )

    note.note = note_data.note

    db.commit()
    db.refresh(note)

    return {
        "message": "Research note updated successfully",
        "id": note.id,
        "paper_id": note.paper_id,
        "note": note.note,
        "created_at": note.created_at,
        "updated_at": note.updated_at
    }


@router.delete("/notes/{note_id}")
def delete_research_note(
    note_id: int,
    db: Session = Depends(get_db)
):
    note = (
        db.query(ResearchNote)
        .filter(ResearchNote.id == note_id)
        .first()
    )

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Research note not found."
        )

    db.delete(note)
    db.commit()

    return {
        "message": "Research note deleted successfully",
        "id": note_id
    }