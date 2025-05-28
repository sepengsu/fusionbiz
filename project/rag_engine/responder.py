import openai
import os
OPEN_API_KEY = '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'  # 여기에 OpenAI API 키를 입력하세요

def load_api_key():
    api_key = os.getenv("OPENAI_API_KEY", OPEN_API_KEY) # 환경변수에서 API 키를 가져오거나 기본값 사용
    if not api_key:
        print("[⚠️] OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        api_key = input("🔑 OpenAI API Key를 입력하세요: ").strip()
    openai.api_key = api_key

load_api_key()  # 실행 시 즉시 확인

def generate_response(question: str, context_chunks: list, device=None) -> str:
    context = "\n\n".join(context_chunks)

    prompt = f"""
너는 공장 기계 로그 분석 전문가야.
다음 문서를 참고해서 사용자의 질문에 정확히 응답해줘.

[문서]
{context}

[질문]
{question}

[답변]
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 산업 로그 전문가야. 주어진 문서를 기반으로 정답만 요약해서 말해."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response["choices"][0]["message"]["content"].strip()
