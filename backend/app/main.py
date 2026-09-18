from fastapi import FastAPI

app = FastAPI(
title="AI Research Assistant",
description="An AI-powered research assistant for organizing, searching, summarizing, and querying academic papers.",
version="0.1.0"
)

@app.get("/")
def root():
return {
"message": "AI Research Assistant API is running"
}
