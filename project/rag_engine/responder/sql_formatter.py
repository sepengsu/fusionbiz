from openai import OpenAI
import os
from config.config_manager import load_config

# OpenAI 클라이언트 초기화 (환경 변수에서 키 자동 로딩)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_sql_prompt_response(question: str, chunks: list, device=None) -> str:
    config = load_config()
    system_prompt = config.get("sql_system_prompt", "SQL 생성 도우미입니다.")
    user_template = config.get("user_prompt_template", "예제:\n{context}\n\n질문: {query}\nSQL:")
    model = config.get("llm_model", "gpt-4o-mini")
    temp = config.get("temperature", 0.3)

    context = "\n\n".join(c["text"] for c in chunks)
    prompt = user_template.replace("{context}", context).replace("{query}", question)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=temp
    )

    raw_output = response.choices[0].message.content.strip()
    print(f"Raw SQL Output: {raw_output}")  # 디버깅용 출력
    return clean_sql_output(raw_output)  # ✨ SQL 코드만 추출


def clean_sql_output(raw_output: str) -> str:
    if "```" in raw_output:
        raw_output = raw_output.split("```")[1] if "sql" in raw_output else raw_output

    start_keywords = ["SELECT", "WITH", "INSERT", "UPDATE", "DELETE"]
    lines = raw_output.splitlines()
    for i, line in enumerate(lines):
        if any(line.strip().upper().startswith(k) for k in start_keywords):
            return "\n".join(lines[i:]).strip()

    return raw_output.strip()


def generate_sql_answer(question: str, sql_code: str, columns: list, rows: list) -> str:
    config = load_config()
    system_prompt = config.get("system_prompt", "SQL 결과를 설명하는 도우미입니다.")
    model = config.get("llm_model", "gpt-4o")
    temp = config.get("temperature", 0.4)

    preview = "\n".join([str(dict(zip(columns, r))) for r in rows[:5]])
    summary = f"질문: {question}\nSQL:\n{sql_code}\n결과 샘플:\n{preview}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": summary}
        ],
        temperature=temp
    )
    return response.choices[0].message.content.strip()