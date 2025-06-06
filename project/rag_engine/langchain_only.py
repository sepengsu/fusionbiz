from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableMap
import os

# 🔹 LLM 구성
llm = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo",
    api_key=os.getenv("OPENAI_API_KEY")
)

# 🔹 질문 분류 프롬프트 + 체인
classifier_prompt = PromptTemplate.from_template("""
다음 질문을 분류해줘: "{question}"
- SQL 관련이면 "sql"
- 고장 대응 관련이면 "manual"
- 전체 요약이면 "summary"
정답만 말해줘.
""")
classifier_chain = classifier_prompt | llm | RunnableLambda(lambda x: x.content.strip().lower())

# 🔹 SQL 분석기 (예시)
def run_sql_analysis(question):
    # (실제 구현에서는 SQL 생성 + DuckDB 실행)
    return ["CNC", "MCT"]
sql_chain = RunnableLambda(lambda d: {"machines": run_sql_analysis(d["question"])})

# 🔹 메뉴얼 검색기 (예시)
def retrieve_manual_chunks(machines):
    return [
        {"machine": m, "status": "에러 3회, 정지 5회", "manual_chunk": f"[{m}] 점검 항목: 센서, 윤활유"}
        for m in machines
    ]
manual_chain = RunnableLambda(lambda d: {"chunks": retrieve_manual_chunks(d["machines"])})

# 🔹 응답 생성 프롬프트
manual_prompt = PromptTemplate.from_template("""
기계: {machine}
상태 요약: {status}
매뉴얼 내용:
{manual_chunk}

위 내용을 기반으로 점검 항목을 정리해줘.
""")
def generate_final_response(data):
    outputs = []
    for item in data["chunks"]:
        prompt = manual_prompt.format(**item)
        res = llm.invoke(prompt)
        outputs.append(f"🛠️ {item['machine']}\n{res.content.strip()}\n")
    return {"response": "\n".join(outputs)}
response_chain = RunnableLambda(generate_final_response)

# 🔹 summary 응답기
summary_prompt = PromptTemplate.from_template("""
오늘의 기계 로그 상태를 요약해줘. 주요 오류 기계, 작동률, 점검 필요 기계 등을 정리해줘.
질문: {question}
""")
summary_chain = summary_prompt | llm | RunnableLambda(lambda x: {"response": x.content.strip()})

# 🔹 최종 라우터 체인
full_chain = RunnableMap({
    "type": classifier_chain,
    "question": lambda q: q
}) | (lambda d: {
    "sql": sql_chain | manual_chain | response_chain,
    "manual": manual_chain | response_chain,
    "summary": summary_chain
}[d["type"]])

# 🔹 실행 예시
if __name__ == "__main__":
    question = "오늘 어떤 기계를 점검해야 하고 어떻게 점검해야 해?"
    result = full_chain.invoke(question)
    print("\n=== 응답 ===\n")
    print(result["response"])
