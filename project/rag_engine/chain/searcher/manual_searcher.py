from rag_engine.retriever.qa import get_qa_chunks

def search_manual_chunks(
    machines: list[str],
    device=None,
    vector_dir="data/manual/vector_store",
    chunk_dir="data/manual/processed_chunks"
) -> list[dict]:
    """
    여러 기계 이름을 받아 각 기계에 대해 관련 manual chunk를 검색하여 반환

    Returns: list of dict with keys: machine, status, manual_chunk
    """
    results = []
    for machine in machines:
        question = f"{machine}의 고장 원인과 점검 방법"
        top_chunks = get_qa_chunks(
            question=question,
            what="manual",
            device=device,
        )
        context = top_chunks.get("text", "")
        results.append({
            "machine": machine,
            "status": "최근 고장 다수 발생",
            "manual_chunk": context
        })
    return results