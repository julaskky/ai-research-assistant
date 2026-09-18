from pathlib import Path

from backend.app.database.init_db import initialize_database

from fastapi import FastAPI, File, UploadFile, HTTPException

from backend.app.services.pdf_service import extract_text_from_pdf


from fastapi import Depends
from sqlalchemy.orm import Session

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

    paper = Paper(
        filename=file.filename,
        file_path=str(file_path),
        extracted_text=extracted_text
    )

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return {
        "message": "Paper uploaded successfully",
        "filename": file.filename,
        "text_length": len(extracted_text)
    }


@app.get("/papers")
def get_papers(db: Session = Depends(get_db)):
    papers = db.query(Paper).all()

    return [
        {
            "id": paper.id,
            "filename": paper.filename,
            "file_path": paper.file_path
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
        "file_path": paper.file_path,
        "text_length": len(paper.extracted_text)
    }