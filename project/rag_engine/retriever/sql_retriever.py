import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def get_top_chunks(
    question: str,
    vector_dir: str,
    chunk_dir: str,
    device=None,
    top_k: int = 5,
    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
) -> list[dict]:
    """
    질문을 벡터화하여 FAISS에서 유사한 chunk를 검색하고
    점수와 함께 반환 (chunk 텍스트 포함)
    """

    # 1. 임베딩 모델 로딩
    model = SentenceTransformer(model_name)

    # 2. 질문 벡터화
    query_vec = model.encode(question)
    query_vec = np.array([query_vec]).astype("float32")

    # 3. 벡터 인덱스 로드
    index_path = os.path.join(vector_dir, "index.faiss")
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"벡터 인덱스가 존재하지 않습니다: {index_path}")
    
    index = faiss.read_index(index_path)

    # 4. 유사도 검색
    D, I = index.search(query_vec, top_k)

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
