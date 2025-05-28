from rag_engine.chain.classifier import classify_question_type
from rag_engine.chain.count_executor import handle_count_question
from rag_engine.retriever import get_top_chunks
from rag_engine.responder import generate_response

def handle_question(question, vector_dir, chunk_dir, device):
    qtype = classify_question_type(question)

    if qtype == "count":
        answer = handle_count_question(question)
        return {
            "question_type": qtype,
            "answer": answer,
            "source_chunks": []
        }

    top_chunks = get_top_chunks(question, vector_dir, chunk_dir, device)
    answer = generate_response(question, top_chunks, device)

    return {
        "question_type": qtype,
        "answer": answer,
        "source_chunks": [
            {"text": chunk["text"], "score": float(chunk["score"])}
            for chunk in top_chunks
        ]
    }
