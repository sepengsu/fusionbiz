from openai import OpenAI
import os
from config.config_manager import load_config

openai_api_key = os.getenv("OPENAI_API_KEY")
# OpenAI client 객체 생성 (API 키는 .env 또는 환경변수에서 자동 인식)
client = OpenAI(api_key=openai_api_key)

def generate_manual_response(question: str, chunks: list, device=None) -> str:
    config = load_config()
    system_prompt = config.get("manual_system_prompt", "매뉴얼 기반 질문 응답 생성기입니다.")
    user_template = config.get("user_prompt_template", "문서:\n{context}\n\n질문: {query}\n답변:")
    model = config.get("llm_model", "gpt-4o-mini")
    temp = config.get("temperature", 0.4)

    # context 구성
    context = "\n\n".join(chunk["text"] for chunk in chunks)
    prompt = user_template.replace("{context}", context).replace("{query}", question)

    # OpenAI Chat 호출 (v1.0 이상)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=temp
    )

    return response.choices[0].message.content.strip()
