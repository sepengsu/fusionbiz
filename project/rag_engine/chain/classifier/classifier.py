from sentence_transformers import SentenceTransformer, util

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
    return "manual"

_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
_sql_vec = _model.encode("SQL로 데이터를 조회하는 방법")
_manual_vec = _model.encode("기계 고장이나 오류 해결 방법")

def classify_by_embedding(question: str) -> str:
    q_vec = _model.encode(question)
    sql_score = util.cos_sim(q_vec, _sql_vec).item()
    manual_score = util.cos_sim(q_vec, _manual_vec).item()
    return "sql" if sql_score > manual_score else "manual"

def classify_question_type(question: str, mode: str = "keyword", device=None) -> str:
    if mode == "embedding":
        return classify_by_embedding(question)
    else:
        return classify_by_keyword(question)
