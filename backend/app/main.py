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
from backend.app.database.init_db import initialize_database
from backend.app.database.database import get_db
from backend.app.database.models import Paper


app = FastAPI(
    title="AI Research Assistant",
    description="An AI-powered research assistant for organizing, searching, summarizing, and querying academic papers.",
    version="0.1.0"
)


initialize_database()


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
    title = extract_title_from_pdf(file_path)
    authors = extract_authors_from_pdf(file_path)

    paper = Paper(
        filename=file.filename,
        title=title or file.filename,
        file_path=str(file_path),
        authors=authors,
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