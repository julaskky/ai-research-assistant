from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from sqlalchemy.orm import relationship


from backend.app.database.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)

    # File information
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    # Bibliographic metadata
    title = Column(Text, nullable=True)
    authors = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)
    publication_year = Column(Integer, nullable=True)
    doi = Column(String, nullable=True)
    journal = Column(String, nullable=True)
    keywords = Column(Text, nullable=True)

    # Extracted document content
    extracted_text = Column(Text, nullable=False)

    # System metadata
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    research_notes = relationship(
        "ResearchNote",
        back_populates="paper",
        cascade="all, delete-orphan"
    )



class ResearchNote(Base):
    __tablename__ = "research_notes"

    id = Column(Integer, primary_key=True, index=True)

    paper_id = Column(
        Integer,
        ForeignKey("papers.id"),
        nullable=False,
        index=True
    )

    paper = relationship(
        "Paper",
        back_populates="research_notes"
    )



    note = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )