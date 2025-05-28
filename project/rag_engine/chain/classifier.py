from rag_engine.retriever import get_top_chunks

def classify_question_type(question, device, top_k=1):
    """
    질문을 'sql' 또는 'rag'으로 분류합니다.
    벡터 유사도를 기준으로 가장 유사한 문서군을 판단합니다.
    """
    sql_chunks = get_top_chunks(
        question, 
        vector_dir="data/vector_store/sql_guide", 
        chunk_dir="data/sql_guide_chunks", 
        device=device, 
        top_k=top_k
    )
    rag_chunks = get_top_chunks(
        question, 
        vector_dir="data/vector_store/log_chunks", 
        chunk_dir="data/processed_chunks", 
        device=device, 
        top_k=top_k
    )

    sql_score = sql_chunks[0]['score'] if sql_chunks else 0
    rag_score = rag_chunks[0]['score'] if rag_chunks else 0

    if sql_score == 0 and rag_score == 0:
        return "unknown"
    return "sql" if sql_score >= rag_score else "rag"
