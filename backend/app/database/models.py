from sqlalchemy import Column, Integer, String, Text

from backend.app.database.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    title = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    authors = Column(String, nullable=True)
    extracted_text = Column(Text, nullable=False)
