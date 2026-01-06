from sqlalchemy import Table, Column, Integer, ForeignKey
from app.config.database import Base

note_category = Table(
    "note_category",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id")),
    Column("category_id", Integer, ForeignKey("categories.id"))
)
