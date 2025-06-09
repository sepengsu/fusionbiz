from rag_engine.retriever.retriever import get_top_chunks

def search_sqlguide_chunks(
    query: str,
    device=None,
    vector_dir="data/sqlguide/vector_store",
    chunk_dir="data/sqlguide/processed_chunks"
) -> dict:
    """
    SQL 질문에 대해 sqlguide vector/processed_chunks에서 관련 chunk 검색하여 반환

    Returns: dict with keys: question, sql_chunks (str)
    """
    top_chunks = get_top_chunks(
        question=query,
        vector_dir=vector_dir,
        chunk_dir=chunk_dir,
        device=device,
    )

    return {
        "question": query,
        "sql_chunks": "\n---\n".join([chunk["text"] for chunk in top_chunks])
    }
