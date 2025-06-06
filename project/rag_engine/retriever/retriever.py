import os
import faiss
import numpy as np
from .utils import load_index_and_model_with_meta, verify_query_vector_dim

def get_top_chunks(
    question: str,
    vector_dir: str,
    chunk_dir: str,
    device=None,
    top_k: int = 5
) -> list[dict]:
    """
    질문을 벡터화하여 FAISS에서 유사한 chunk를 검색하고 점수와 함께 반환
    """

    # 1. 메타 정보 기반으로 모델, 인덱스, 차원 불러오기
    model, index, expected_dim = load_index_and_model_with_meta(vector_dir)

    # 2. 질문 벡터화
    query_vec = model.encode([question])  # shape: (1, d)
    verify_query_vector_dim(query_vec, expected_dim)
    query_vec = query_vec.astype("float32")

    # 3. 유사도 검색
    D, I = index.search(query_vec, top_k)

    # 4. 결과 조합
    results = []
    for i, score in zip(I[0], D[0]):
        chunk_file = os.path.join(chunk_dir, f"chunk_{i}.txt")
        if os.path.exists(chunk_file):
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunk_text = f.read()
                results.append({
                    "text": chunk_text,
                    "score": float(score),
                    "index": i
                })

    return results
