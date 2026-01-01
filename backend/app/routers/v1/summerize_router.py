from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.logger import logger
from app.services.summerize_service import summarize_text_and_category

summarize_router = APIRouter(prefix="/summarize", tags=["Summarize"])

class SummarizeRequest(BaseModel):
    text: str

@summarize_router.post("")
async def summarize(request: SummarizeRequest):
    logger.info(f"Received summarize request, text length: {len(request.text)}")
    try:
        result = summarize_text_and_category(request.text)
        logger.info(f"Summarization successful, summary length: {len(result.get('summary', ''))}")

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
