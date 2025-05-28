from rag_engine.chain.classifier import classify_question_type
from rag_engine.chain.sql_executor import handle_sql_question
from rag_engine.chain.rag_executor import handle_rag_question

def handle_question(question, vector_dir, chunk_dir, device):
    """
    입력된 질문을 적절한 실행기로 분기하여 처리하는 라우터 함수
    - 'sql' → handle_sql_question
    - 'rag' → handle_rag_question
    """

    # 질문 유형 분류 (벡터 기반 or 키워드 기반 구현 가능)
    qtype = classify_question_type(question, device=device)

    if qtype == "sql":
        result = handle_sql_question(question, device)
    elif qtype == "rag":
        result = handle_rag_question(question, vector_dir, chunk_dir, device)
    else:
        result = {
            "question_type": "unknown",
            "answer": "❌ 질문 유형을 판별할 수 없습니다.",
            "source_chunks": []
        }

    result["device"] = str(device)
    return result
