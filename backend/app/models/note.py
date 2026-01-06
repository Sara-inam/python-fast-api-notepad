from sqlalchemy import Column, Integer, String, Text, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from app.config.database import Base
from app.models.note_category import note_category

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    voice_message = Column(LargeBinary, nullable=True)

    user = relationship("User", back_populates="notes")
    categories = relationship("Category", secondary=note_category, back_populates="notes")
