from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.services.pdf_service import (
    extract_text_from_pdf,
    extract_title_from_pdf,
    extract_authors_from_pdf
)
from backend.app.services.metadata_service import extract_metadata

from backend.app.database.init_db import initialize_database
from backend.app.database.database import get_db
from backend.app.database.models import Paper, ResearchNote
from pydantic import BaseModel
from backend.app.schemas import ResearchNoteCreate, ResearchNoteUpdate


app = FastAPI(
    title="AI Research Assistant",
    description="An AI-powered research assistant for organizing, searching, summarizing, and querying academic papers.",
    version="0.1.0"
)

class PaperUpdate(BaseModel):
    title: str | None = None
    authors: str | None = None
    abstract: str | None = None
    publication_year: int | None = None
    doi: str | None = None
    journal: str | None = None
    keywords: str | None = None





UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {
        "message": "AI Research Assistant API is running"
    }


@app.post("/papers/upload")
async def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        buffer.write(await file.read())

    extracted_text = extract_text_from_pdf(file_path)

    metadata = extract_metadata(file_path)

    title = (
        metadata.get("title")
        or extract_title_from_pdf(file_path)
        or file.filename
    )

    authors = (
        metadata.get("authors")
        or extract_authors_from_pdf(file_path)
    )

    paper = Paper(
        filename=file.filename,
        title=title,
        file_path=str(file_path),
        authors=authors,
        abstract=metadata.get("abstract"),
        publication_year=metadata.get("publication_year"),
        doi=metadata.get("doi"),
        journal=metadata.get("journal"),
        keywords=metadata.get("keywords"),
        extracted_text=extracted_text
    )

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return {
        "message": "Paper uploaded successfully",
        "id": paper.id,
        "filename": paper.filename,
        "title": paper.title,
        "authors": paper.authors,
        "text_length": len(paper.extracted_text)
    }


@app.get("/papers")
def get_papers(db: Session = Depends(get_db)):
    papers = db.query(Paper).all()

    return [
        {
            "id": paper.id,
            "filename": paper.filename,
            "title": paper.title,
            "authors": paper.authors,
            "abstract": paper.abstract,
            "publication_year": paper.publication_year,
            "doi": paper.doi,
            "journal": paper.journal,
            "keywords": paper.keywords,
            "file_path": paper.file_path,
            "created_at": paper.created_at,
            "updated_at": paper.updated_at
        }
        for paper in papers
    ]


@app.put("/papers/{paper_id}")
def update_paper(
    paper_id: int,
    paper_update: PaperUpdate,
    db: Session = Depends(get_db)
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found."
        )

    update_data = paper_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(paper, field, value)

    db.commit()
    db.refresh(paper)

    return {
        "message": "Paper updated successfully",
        "id": paper.id,
        "filename": paper.filename,
        "title": paper.title,
        "authors": paper.authors,
        "abstract": paper.abstract,
        "publication_year": paper.publication_year,
        "doi": paper.doi,
        "journal": paper.journal,
        "keywords": paper.keywords,
        "updated_at": paper.updated_at
    }




@app.get("/papers/search")
def search_papers(q: str, db: Session = Depends(get_db)):
    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty."
        )

    search_term = f"%{q}%"

    papers = (
        db.query(Paper)
        .filter(
            or_(
                Paper.title.ilike(search_term),
                Paper.authors.ilike(search_term),
                Paper.abstract.ilike(search_term),
                Paper.journal.ilike(search_term),
                Paper.keywords.ilike(search_term),
                Paper.extracted_text.ilike(search_term)
            )
        )
        .all()
    )

    return [
        {
            "id": paper.id,
            "filename": paper.filename,
            "title": paper.title,
            "authors": paper.authors
        }
        for paper in papers
    ]


@app.get("/papers/{paper_id}")
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found."
        )

    return {
        "id": paper.id,
        "filename": paper.filename,
        "title": paper.title,
        "authors": paper.authors,
        "abstract": paper.abstract,
        "publication_year": paper.publication_year,
        "doi": paper.doi,
        "journal": paper.journal,
        "keywords": paper.keywords,
        "file_path": paper.file_path,
        "text_length": len(paper.extracted_text),
        "created_at": paper.created_at,
        "updated_at": paper.updated_at
    }


@app.get("/papers/{paper_id}/text")
def get_paper_text(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found."
        )

    return {
        "id": paper.id,
        "filename": paper.filename,
        "extracted_text": paper.extracted_text
    }



@app.delete("/papers/{paper_id}")
def delete_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found."
        )

    file_path = Path(paper.file_path)

    other_papers = (
        db.query(Paper)
        .filter(
            Paper.file_path == paper.file_path,
            Paper.id != paper.id
        )
        .count()
    )

    db.delete(paper)
    db.commit()

    if other_papers == 0 and file_path.exists():
        file_path.unlink()

    return {
        "message": "Paper deleted successfully",
        "id": paper_id
    }



@app.post("/papers/{paper_id}/notes")
def create_research_note(
    paper_id: int,
    note_data: ResearchNoteCreate,
    db: Session = Depends(get_db)
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()

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



@app.get("/papers/{paper_id}/notes")
def get_research_notes(
    paper_id: int,
    db: Session = Depends(get_db)
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()

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




@app.get("/notes/{note_id}")
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



@app.put("/notes/{note_id}")
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



@app.delete("/notes/{note_id}")
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