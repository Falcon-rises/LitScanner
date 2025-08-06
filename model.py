from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, LargeBinary

Base = declarative_base()

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    authors = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    source = Column(String(50), nullable=True)
    summary = Column(Text, nullable=True)
    topic = Column(Integer, nullable=True)
    embedding = Column(LargeBinary, nullable=True)

    def to_dict(self):
        """
        Convert SQLAlchemy model instance to dictionary for API responses.
        """
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "url": self.url,
            "source": self.source,
            "summary": self.summary,
            "topic": self.topic
        }
