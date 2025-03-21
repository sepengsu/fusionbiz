from fastapi import APIRouter, UploadFile, File
from services.text_processing import summarize_text

router = APIRouter()

@router.post("/summarize/")
async def summarize_text_api(file: UploadFile = File(...)):
    text = await file.read()
    summary = summarize_text(text.decode("utf-8"))
    return {"summary": summary}
