import os
import numpy as np
from sentence_transformers import SentenceTransformer, util
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

# 🔹 키워드 기반 분류 키워드
SQL_KEYWORDS = ["쿼리", "sql","횟수를 알려줘"]
MANUAL_KEYWORDS = ["메뉴얼", "고장 분석 방법","점검 방법","매뉴얼"]
SUMMARY_KEYWORDS = ["요약", "보고서", "로그 요약", "운전 로그 요약","보고서"]

# 🔹 임베딩 기반 대표 문장
prototype_sql = [
    "데이터를 조회하는 SQL 쿼리",
    "운전 로그를 테이블로 보여줘",
    "정지 횟수를 알려줘",
    "에러 로그 개수를 확인하고 싶어",
    "1월 29일 몇 번 정지됐는지 알려줘",
    "SQL 쿼리로 분석해줘",
    "SQL"
]

prototype_manual = [
    "왜 고장났는지 알아봐줘",
    "작동 중 멈춘 이유와 점검 방법",
    "기계가 안 돼. 점검은 어떻게 해?",
    "정비 방법이 어떻게 돼?",
    "메뉴얼이 뭐야?",
    "오류가 발생했어. 어떻게 해야 해?",
    "메뉴얼을 알려줘",
]

prototype_summary = [
    "1월 29일 운전 로그 요약",
    "1월 전체 로그 요약",
    "요약",
    "CNC 운전 1월 30일 로그 요약",
    "로그 분석",
    "보고서 작성해줘"
]


# 🔹 임베딩 모델 초기화
_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# ✅ 키워드 기반 분류
def classify_by_keyword(question: str) -> str:
    q = question.lower()
    for kw in SQL_KEYWORDS:
        if kw in q:
            return "sql"
    for kw in MANUAL_KEYWORDS:
        if kw in q:
            return "manual"
    for kw in SUMMARY_KEYWORDS:
        if kw in q:
            return "summary"
    return None  # 키워드로 분류할 수 없는 경우

# ✅ 임베딩 기반 분류
def classify_by_embedding_pairwise(question: str) -> str:
    q_vec = _model.encode(question)
    sql_vecs = _model.encode(prototype_sql)
    manual_vecs = _model.encode(prototype_manual)
    summary_vecs = _model.encode(prototype_summary)

    sql_score = util.cos_sim(q_vec, sql_vecs).mean().item()
    manual_score = util.cos_sim(q_vec, manual_vecs).mean().item()
    summary_score = util.cos_sim(q_vec, summary_vecs).mean().item()
    print(f"[DEBUG] 임베딩 유사도 - SQL: {sql_score}, Manual: {manual_score}, Summary: {summary_score}")
    if summary_score > max(sql_score, manual_score):
        return "summary"
    if sql_score > max(manual_score, summary_score):
        return "sql"
    if manual_score > max(sql_score, summary_score):
        return "manual"
    # 기본적으로 SQL과 Manual 비교
    if sql_score == manual_score:
        return "manual"  # 동률인 경우 Manual로 처리
    return "sql" if sql_score > manual_score else "manual"

# ✅ LLM 기반 분류기 체인 구성
_llm = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo",
    api_key=os.getenv("OPENAI_API_KEY")
)

_llm_prompt = PromptTemplate.from_template("""
다음 질문을 "sql", "manual", "summary" 중 하나로 분류해줘.

질문: "{question}"
답변 (sql/manual/summary 중 하나):
""")

_llm_chain = _llm_prompt | _llm | RunnableLambda(lambda x: x.content.strip().lower())

# ✅ LLM 기반 분류
def classify_by_llm(question: str) -> str:
    try:
        result = _llm_chain.invoke({"question": question})
        if result in ["sql", "manual", "summary"]:
            return result
    except Exception as e:
        print(f"[ERROR] LLM 분류 실패: {e}")
    return "manual"

# ✅ 최종 하이브리드 분류기
def classify_question_type(question: str, mode: str = "embedding") -> str:
    """
    mode = "keyword" | "embedding" | "llm"
    """
    if mode not in ["keyword", "embedding", "llm"]:
        raise ValueError(f"지원하지 않는 분류 모드: {mode}. 'keyword', 'embedding', 'llm' 중 하나를 선택하세요.")
    
    if not question:
        raise ValueError("질문이 비어있습니다. 유효한 질문을 입력하세요.")
    
    print(f"[INFO] 분류 모드: {mode}, 질문: {question}")
    question = question.strip()
    if mode == "keyword":
        return classify_by_keyword(question)

    if mode == "embedding":
        keyword = classify_by_keyword(question)
        if keyword:
            return keyword
        return classify_by_embedding_pairwise(question)

    if mode == "llm":
        return classify_by_llm(question)

    return "manual"
