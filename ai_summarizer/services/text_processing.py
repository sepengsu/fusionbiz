from models.summarization import gpt_summarize

def summarize_text(text: str):
    return gpt_summarize(text)
