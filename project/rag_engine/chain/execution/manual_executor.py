from rag_engine.retriever.manual_retriever import get_top_chunks
from rag_engine.responder.manual_formatter import generate_manual_response 

def handle_rag_question(question, vector_dir, chunk_dir, device, top_k=5):
    """
    매뉴얼 문서 기반 RAG 방식으로 질문에 응답하는 함수
    - 관련 chunk를 벡터 검색으로 찾고
    - GPT로 응답을 생성하여 반환
    """
    # 1. 관련 chunk 검색
    top_chunks = get_top_chunks(
        question=question,
        vector_dir=vector_dir,
        chunk_dir=chunk_dir,
        device=device,
        top_k=top_k
    )

    # 2. GPT 응답 생성
    answer = generate_manual_response(question, top_chunks, device=device)

    return {
        "question_type": "manual",
        "answer": answer,
        "source_chunks": [
            {"text": chunk["text"], "score": float(chunk["score"])}
            for chunk in top_chunks
        ]
    }
