from pathlib import Path

import fitz
from fastapi import FastAPI, File, UploadFile, HTTPException


app = FastAPI(
    title="AI Research Assistant",
    description="An AI-powered research assistant for organizing, searching, summarizing, and querying academic papers.",
    version="0.1.0"
)


UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from all pages of a PDF document."""
    text = []

    with fitz.open(file_path) as document:
        for page in document:
            text.append(page.get_text())

    return "\n".join(text).strip()


@app.get("/")
def root():
    return {
        "message": "AI Research Assistant API is running"
    }


@app.post("/papers/upload")
async def upload_paper(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        buffer.write(await file.read())

    extracted_text = extract_text_from_pdf(file_path)

    return {
        "message": "Paper uploaded successfully",
        "filename": file.filename,
        "text_length": len(extracted_text)
    }