from pydantic import BaseModel
from typing import Optional, List

class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = ""
    summary: Optional[str] = ""
    categories: Optional[List[int]] = [] 

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    categories: Optional[List[int]] = None

class NoteResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = ""
    summary: Optional[str] = ""
    categories: Optional[List[str]] = []
    voice_message: Optional[str] = None

    class Config:
        orm_mode = True
