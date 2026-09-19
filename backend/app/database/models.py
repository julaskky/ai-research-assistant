from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

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