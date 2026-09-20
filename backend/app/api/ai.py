from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.database.models import Paper


from backend.app.services.ai_service import (
    answer_from_context,
    answer_with_gemini,
    retrieve_relevant_chunks,
    summarize_text,
    summarize_with_gemini,
    AI_PROVIDER,
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

    if AI_PROVIDER == "gemini":
        try:
            summary = summarize_with_gemini(
                paper.extracted_text
            )
        except Exception:
            summary = summarize_text(
                paper.extracted_text,
                max_sentences=5
            )
    else:
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

    if AI_PROVIDER == "gemini":
        try:
            answer = answer_with_gemini(
                question_data.question,
                context
            )
        except Exception:
            answer = answer_from_context(
                question_data.question,
                context
            )
    else:
        answer = answer_from_context(
            question_data.question,
            context
        )

    source_excerpts = []

    for chunk in chunks:
        excerpt = chunk.strip()

        if len(excerpt) > 700:
            excerpt = excerpt[:700]

            # Avoid ending the source in the middle of a word.
            last_space = excerpt.rfind(" ")

            if last_space > 0:
                excerpt = excerpt[:last_space]

            excerpt += "..."

        source_excerpts.append(excerpt)


    return {
        "paper_id": paper.id,
        "question": question_data.question,
        "answer": answer,
        "sources": source_excerpts
    }