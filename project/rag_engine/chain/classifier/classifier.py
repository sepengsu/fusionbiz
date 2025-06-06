from sentence_transformers import SentenceTransformer, util
import numpy as np

# 🔸 키워드 기반 분류
SQL_KEYWORDS = ["쿼리", "sql", "select", "insert", "delete", "테이블", "where", "join"]
MANUAL_KEYWORDS = ["에러", "오류", "정지", "고장", "작동", "멈춤", "대응", "매뉴얼", "운전"]

def classify_by_keyword(question: str) -> str:
    q = question.lower()
    for kw in SQL_KEYWORDS:
        if kw in q:
            return "sql"
    for kw in MANUAL_KEYWORDS:
        if kw in q:
            return "manual"
    return "manual"  # default fallback

# 🔸 임베딩 기반 대표 문장
prototype_sql = [
    "데이터를 조회하는 SQL 쿼리",
    "운전 로그를 테이블로 보여줘",
    "정지 횟수를 알려줘",
    "에러 로그 개수를 확인하고 싶어",
    "1월 29일 몇 번 정지됐는지 알려줘"
]

prototype_manual = [
    "왜 고장났는지 알아봐줘",
    "정지 이유가 뭐야?",
    "작동 중 멈춘 이유는?",
    "기계가 안 돼. 점검은 어떻게 해?",
    "정비 방법이 어떻게 돼?"
]

_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def classify_by_embedding_pairwise(question: str) -> str:
    q_vec = _model.encode(question)
    sql_vecs = _model.encode(prototype_sql)
    manual_vecs = _model.encode(prototype_manual)

    sql_score = util.cos_sim(q_vec, sql_vecs).mean().item()
    manual_score = util.cos_sim(q_vec, manual_vecs).mean().item()

    return "sql" if sql_score > manual_score else "manual"

# 🔸 최종 하이브리드 분류기
def classify_question_type(question: str) -> str:
    kw_label = classify_by_keyword(question)
    if kw_label != "manual":  # 키워드로 sql로 확신되면 그대로 사용
        return kw_label
    return classify_by_embedding_pairwise(question)

def classify_question_type(question: str, use_llm: bool = False) -> str:
    """
    기본적으로 키워드 + 임베딩 기반 하이브리드 분류를 수행.
    use_llm=True일 경우, LLM (예: GPT) 기반 분류기로 대체 가능 (나중에 확장용)
    """
    if not use_llm:
        kw_label = classify_by_keyword(question)
        if kw_label != "manual":  # 키워드로 sql로 확신되면 그대로 사용
            return kw_label
        return classify_by_embedding_pairwise(question)

    # ✳️ 향후 LLM 사용 시 (예: langchain 기반)
    return classify_by_llm(question)

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
import os

# 🔹 프롬프트 템플릿
prompt = PromptTemplate.from_template("""
다음 질문을 "sql", "manual", "summary" 중 하나로 분류해줘.

질문: "{question}"
답변 (sql/manual/summary 중 하나):
""")

# 🔹 LLM 모델 정의
llm = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo",
    api_key=os.getenv("OPENAI_API_KEY")
)

# 🔹 체인 구성: prompt → LLM
chain = prompt | llm | RunnableLambda(lambda x: x.content.strip().lower())

# 🔹 분류 함수 정의
def classify_by_llm(question: str) -> str:
    try:
        result = chain.invoke({"question": question})
        if result in ["sql", "manual", "summary"]:
            return result
    except Exception as e:
        print(f"[ERROR] LLM 분류 실패: {e}")
    return "manual"


