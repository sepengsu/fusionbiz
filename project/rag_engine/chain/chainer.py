# ✅ LangChain-Only 기반 챗봇 구조 (SQL + 메뉴얼 + 요약)

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableMap
import os

# ✅ 기존 모듈 불러오기
from rag_engine.chain.classifier.classifier import classify_question_type
from rag_engine.chain.execution.sql_executor import run_sql_analysis
from rag_engine.chain.execution.manual_executor import search_manual_chunks

# 🔹 LLM 구성
llm = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo",
    api_key=os.getenv("OPENAI_API_KEY")
)

# 🔹 질문 분류기 (하이브리드 분류기 그대로 사용)
classifier_chain = RunnableLambda(lambda q: {"question": q, "type": classify_question_type(q)})

# 🔹 SQL 분석기 (기존 함수 연결)
sql_chain = RunnableLambda(lambda d: {"machines": run_sql_analysis(d["question"])})

# 🔹 메뉴얼 검색기 (기존 함수 연결)
manual_chain = RunnableLambda(lambda d: {"chunks": search_manual_chunks(d["machines"])})

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

# 🔹 summary 응답기 (예시용)
def generate_summary(question):
    return {"response": "요약 기능은 현재 준비 중입니다."}
summary_chain = RunnableLambda(generate_summary)

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
