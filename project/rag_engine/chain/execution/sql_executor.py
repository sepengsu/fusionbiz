import sqlite3
from rag_engine.retriever.retriever import get_top_chunks
from rag_engine.responder.sql_formatter import (
    generate_sql_prompt_response,
    generate_sql_answer
)

DEFAULT_SQL_DB_PATH = "data/factory/log.db"

def handle_sql_question(question: str, device=None, db_path: str = None) -> dict:
    """
    자연어 질문을 기반으로:
    1. 관련 SQL 예제 검색
    2. GPT로 SQL 생성
    3. SQLite DB 실행
    4. 결과를 자연어 응답으로 반환

    Args:
        question (str): 사용자 질문
        device (str): 임베딩 디바이스
        db_path (str): 사용할 SQLite DB 경로 (기본값 사용 가능)
    """
    db_path = db_path or DEFAULT_SQL_DB_PATH

    # 1. 관련 SQL 예제 청크 검색 (벡터 기반 RAG)
    top_chunks = get_top_chunks(
        question=question,
        vector_dir="data/sqlguide/vector_store",
        chunk_dir="data/sqlguide/processed_chunks",
        device=device,
        top_k=5
    )

    # 2. GPT에게 SQL 생성 요청
    sql_code = generate_sql_prompt_response(
        question=question,
        chunks=top_chunks,
        device=device
    )

    # 3. SQL 실행 (sqlite3 기준)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_code)
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()
    except Exception as e:
        return {
            "question_type": "sql",
            "answer": f"❌ SQL 실행 오류: {str(e)}",
            "sql": sql_code,
            "source_chunks": [c["text"] for c in top_chunks]
        }

    # 4. 자연어 응답 생성
    answer = generate_sql_answer(
        question=question,
        sql_code=sql_code,
        columns=col_names,
        rows=rows
    )

    return {
        "question_type": "sql",
        "answer": answer,
        "sql": sql_code,
        "source_chunks": [
            {"text": c["text"], "score": float(c["score"])} for c in top_chunks
        ]
    }
