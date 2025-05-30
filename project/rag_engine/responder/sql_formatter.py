import openai
import os
from config.config_manager import load_config

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_sql_prompt_response(question: str, chunks: list, device=None) -> str:
    config = load_config()
    system_prompt = config.get("system_prompt", "SQL 생성 도우미입니다.")
    user_template = config.get("user_prompt_template", "예제:\n{context}\n\n질문: {query}\nSQL:")
    model = config.get("llm_model", "gpt-4o")
    temp = config.get("temperature", 0.3)

    context = "\n\n".join(c["text"] for c in chunks)
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

def generate_sql_answer(question: str, sql_code: str, columns: list, rows: list) -> str:
    config = load_config()
    system_prompt = config.get("system_prompt", "SQL 결과를 설명하는 도우미입니다.")
    model = config.get("llm_model", "gpt-4o")
    temp = config.get("temperature", 0.4)

    preview = "\n".join([str(dict(zip(columns, r))) for r in rows[:5]])
    summary = f"질문: {question}\nSQL:\n{sql_code}\n결과 샘플:\n{preview}"

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": summary}
        ],
        temperature=temp
    )
    return response["choices"][0]["message"]["content"].strip()
