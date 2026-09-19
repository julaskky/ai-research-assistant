from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.database.models import Paper
from backend.app.services.ai_service import (
    answer_from_context,
    retrieve_relevant_chunks,
    summarize_text,
)


router = APIRouter(
    prefix="/papers",
    tags=["AI"]
)


class QuestionRequest(BaseModel):
    question: str


@router.post("/{paper_id}/summarize")
def summarize_paper(
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

    summary = summarize_text(
        paper.extracted_text,
        max_sentences=5
    )

    return {
        "paper_id": paper.id,
        "title": paper.title,
        "summary": summary
    }


@router.post("/{paper_id}/ask")
def ask_question(
    paper_id: int,
    question_data: QuestionRequest,
    db: Session = Depends(get_db)
):
    if not question_data.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

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

    chunks = retrieve_relevant_chunks(
        paper.extracted_text,
        question_data.question,
        top_k=3
    )

    if not chunks:
        return {
            "paper_id": paper.id,
            "question": question_data.question,
            "answer": (
                "I could not find relevant information "
                "in the paper."
            ),
            "sources": []
        }

    context = "\n\n".join(chunks)

    answer = answer_from_context(
        question_data.question,
        context
    )

    return {
        "paper_id": paper.id,
        "question": question_data.question,
        "answer": answer,
        "sources": chunks
    }