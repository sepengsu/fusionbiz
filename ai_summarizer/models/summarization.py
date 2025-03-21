import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def gpt_summarize(text: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Summarize the following text briefly."},
                  {"role": "user", "content": text}]
    )
    return response["choices"][0]["message"]["content"]
