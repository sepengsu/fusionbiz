from config.config_manager import load_config
from rag_engine.chain.classifier.classifier import classify_question_type
from rag_engine.chain.execution.sql_executor import handle_sql_question
from rag_engine.chain.execution.manual_executor import handle_rag_question

def handle_question(question, vector_dir_map: dict, device):
    """
    입력된 질문을 적절한 실행기로 분기하여 처리하는 라우터 함수
    - 'sql' → handle_sql_question
    - 'rag' → handle_rag_question
    """

    config = load_config()
    mode = config.get("classification_mode", "keyword")

    # 질문 유형 분류
    qtype = classify_question_type(question, mode=mode)

    if qtype == "sql":
        result = handle_sql_question(question, device)
    elif qtype == "rag":
        vector_dir = vector_dir_map.get("manual_vector_dir", "")
        chunk_dir = vector_dir_map.get("manual_chunk_dir", "")
        result = handle_rag_question(question, vector_dir, chunk_dir, device)
    else:
        result = {
            "question_type": "unknown",
            "answer": "❌ 질문 유형을 판별할 수 없습니다.",
            "source_chunks": []
        }

    result["device"] = str(device)
    result["question_type"] = qtype
    return result
