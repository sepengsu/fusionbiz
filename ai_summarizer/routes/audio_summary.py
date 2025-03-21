from fastapi import APIRouter, UploadFile, File
from services.audio_processing import transcribe_audio, summarize_text

router = APIRouter()

@router.post("/transcribe/")
async def transcribe_audio_api(file: UploadFile = File(...)):
    audio_path = f"temp/{file.filename}"
    with open(audio_path, "wb") as buffer:
        buffer.write(await file.read())

    text = transcribe_audio(audio_path)
    summary = summarize_text(text)
    
    return {"transcription": text, "summary": summary}
