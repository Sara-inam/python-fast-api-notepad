from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.note_schemas import NoteCreate, NoteUpdate, NoteResponse
from app.services.note_service import NoteService
from app.models.note import Note
from app.models.category import Category
from app.models.note_category import note_category
from typing import List
from app.utilis.token_utilis import verify_token
from pydub import AudioSegment
import io
from fastapi.responses import StreamingResponse
from app.crud.note_crud import get_note_voice
from app.utilis.category_utilis import split_ai_categories
from app.crud.category_crud import assign_categories_to_note


# FFmpeg path
AudioSegment.converter = r"C:\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\ffmpeg-8.0.1-essentials_build\bin\ffprobe.exe"

note_router = APIRouter(prefix="/notes", tags=["Notes"])

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization[7:]
    user_id = verify_token(token)
    return {"id": user_id}



# --- GET NOTES ---
@note_router.get("/get", response_model=list[NoteResponse])
def list_notes(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    service = NoteService(db, current_user["id"])
    notes = service.list_notes()

    response_notes = []
    for note in notes:
        response_notes.append(
            NoteResponse(
                id=note.id,
                title=note.title,
                content=note.content,
                summary=getattr(note, "summary", ""),
                categories=[cat.name for cat in note.categories],  # Convert categories to strings
                voice_message=f"http://127.0.0.1:8000/notes/voice/{note.id}" if note.voice_message else None
            )
        )

    return response_notes

# --- STREAM VOICE ---
@note_router.get("/voice/{note_id}")
def stream_voice(
    note_id: int,
    db: Session = Depends(get_db)
):
    voice_bytes = get_note_voice(db, note_id)

    if not voice_bytes:
        raise HTTPException(status_code=404, detail="Voice not found")

    return StreamingResponse(
        io.BytesIO(voice_bytes),
        media_type="audio/webm"
    )


# --- CREATE NOTE ---
@note_router.post("/create", response_model=NoteResponse)
async def create_new_note(
    title: str = Form(...),
    content: str = Form(None),
    ai_categories: str = Form(None),  # AI generated categories text
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from app.schemas.note_schemas import NoteCreate

    note_create = NoteCreate(title=title, content=content or "")
    service = NoteService(db, current_user["id"])
    db_note = service.create_note(note_create)

    #  Voice upload
    if file:
        file_bytes = await file.read()
        service.upload_voice(db_note.id, file_bytes)
        db_note.voice_message = f"http://127.0.0.1:8000/notes/voice/{db_note.id}"

    # Split AI categories and assign
    if ai_categories:
        category_list = split_ai_categories(ai_categories)
        assign_categories_to_note(db, db_note, category_list)

    #  Return response with category names
    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        summary=getattr(db_note, "summary", ""),
        categories=[cat.name for cat in db_note.categories],
        voice_message=db_note.voice_message
    )


@note_router.put("/update/{note_id}", response_model=NoteResponse)
async def update_existing_note(
    note_id: int,
    title: str = Form(...),
    content: str = Form(...),
    summary: str = Form(None),
    ai_categories: str = Form(None),  # AI generated categories text
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = NoteService(db, current_user["id"])

    note_update = NoteUpdate(
        title=title,
        content=content,
        summary=summary
    )

    db_note = service.update_note(note_id, note_update)

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    #  Voice upload
    if file:
        file_bytes = await file.read()
        service.upload_voice(note_id, file_bytes)
        db_note.voice_message = f"http://127.0.0.1:8000/notes/voice/{note_id}"

    #  Split AI categories and assign
    if ai_categories:
        category_list = split_ai_categories(ai_categories)
        assign_categories_to_note(db, db_note, category_list)

    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        summary=getattr(db_note, "summary", ""),
        categories=[cat.name for cat in db_note.categories],
        voice_message=db_note.voice_message
    )
# --- DELETE NOTE ---
@note_router.delete("/delete/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    service = NoteService(db, current_user["id"])
    db_note = service.delete_note(note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"detail": "Deleted Successfully"}


# --- UPLOAD VOICE ONLY ---
@note_router.post("/upload_voice/{note_id}")
async def upload_voice(note_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    file_bytes = await file.read()
    audio = AudioSegment.from_file(io.BytesIO(file_bytes))
    if len(audio) > 5 * 60 * 1000:  # 5 minutes
        raise HTTPException(status_code=400, detail="Voice message max 5 minutes allowed")
    service = NoteService(db, current_user["id"])
    db_note = service.upload_voice(note_id, file_bytes)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"detail": "Voice uploaded successfully", "voice_message": f"/notes/voice/{note_id}"}



@note_router.get("/search/{category_name}", response_model=List[NoteResponse])
def search_notes_by_category(category_name: str, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.name == category_name).first()
    if not category:
        return []

    notes = (
        db.query(Note)
        .join(note_category, Note.id == note_category.c.note_id)
        .filter(note_category.c.category_id == category.id)
        .all()
    )

    # Convert notes to NoteResponse format
    response_notes = []
    for note in notes:
        response_notes.append(
            NoteResponse(
                id=note.id,
                title=note.title,
                content=note.content,
                summary=getattr(note, "summary", ""),
                categories=[cat.name for cat in note.categories],
                voice_message=f"http://127.0.0.1:8000/notes/voice/{note.id}" if note.voice_message else None
            )
        )
    return response_notes
