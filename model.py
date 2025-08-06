from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, LargeBinary
import numpy as np

Base = declarative_base()

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500))
    authors = Column(Text)
    abstract = Column(Text)
    url = Column(String(500))
    source = Column(String(50))
    summary = Column(Text, nullable=True)
    topic = Column(Integer, nullable=True)
    embedding = Column(LargeBinary, nullable=True)

    def to_dict(self):
        return {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "url": self.url,
            "source": self.source,
            "summary": self.summary
        }
