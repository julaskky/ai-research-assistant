from pydantic import BaseModel


class ResearchNoteCreate(BaseModel):
    note: str


class ResearchNoteUpdate(BaseModel):
    note: str