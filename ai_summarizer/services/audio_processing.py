import whisper
from models.summarization import gpt_summarize

def transcribe_audio(audio_path: str):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def summarize_text(text: str):
    return gpt_summarize(text)
