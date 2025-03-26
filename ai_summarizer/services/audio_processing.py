from faster_whisper import WhisperModel
from models.summarization import gpt_summarize

def transcribe_audio(audio_path: str):
    model = WhisperModel("base")  # 또는 "small", "medium", "large"
    segments, info = model.transcribe(audio_path)

    # segments는 generator이므로 텍스트만 추출
    full_text = " ".join([segment.text for segment in segments])
    return full_text

def summarize_text(text: str):
    return gpt_summarize(text)
