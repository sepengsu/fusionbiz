import openai
import os
from config.config_manager import load_config

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_manual_response(question: str, chunks: list, device=None) -> str:
    config = load_config()
    system_prompt = config.get("system_prompt", "매뉴얼 기반 질문 응답 생성기입니다.")
    user_template = config.get("user_prompt_template", "문서:\n{context}\n\n질문: {query}\n답변:")
    model = config.get("llm_model", "gpt-4o")
    temp = config.get("temperature", 0.4)

    context = "\n\n".join(chunk["text"] for chunk in chunks)
    prompt = user_template.replace("{context}", context).replace("{query}", question)

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=temp
    )
    return response["choices"][0]["message"]["content"].strip()
