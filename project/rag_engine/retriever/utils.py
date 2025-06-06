from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os, json

def load_index(index_path):
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"❌ 인덱스가 존재하지 않습니다: {index_path}")
    return faiss.read_index(index_path)

def embed_query(query, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
    model = SentenceTransformer(model_name)
    return model.encode([query])[0]

def load_index_and_model_with_meta(vector_dir):
    meta_path = os.path.join(vector_dir, "meta.json")
    index_path = os.path.join(vector_dir, "index.faiss")

    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    model_name = meta["embedding_model"]
    expected_dim = meta["vector_dim"]

    model = SentenceTransformer(model_name)
    index = faiss.read_index(index_path)

    return model, index, expected_dim

def verify_query_vector_dim(query_vec, expected_dim):
    if query_vec.shape[1] != expected_dim:
        raise ValueError(f"❌ 쿼리 벡터 차원 {query_vec.shape[1]} ≠ 인덱스 차원 {expected_dim}")