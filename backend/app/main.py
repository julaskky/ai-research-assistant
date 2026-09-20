from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.papers import router as papers_router
from backend.app.api.research_notes import router as research_notes_router
from backend.app.api.ai import router as ai_router


app = FastAPI(
    title="AI Research Assistant",
    description="An AI-powered research assistant for organizing, searching, summarizing, and querying academic papers.",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(papers_router)
app.include_router(research_notes_router)
app.include_router(ai_router)


@app.get("/")
def root():
    return {
        "message": "AI Research Assistant API is running"
    }