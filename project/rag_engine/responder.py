import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

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
