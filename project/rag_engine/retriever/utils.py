from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os

def load_index(index_path):
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"❌ 인덱스가 존재하지 않습니다: {index_path}")
    return faiss.read_index(index_path)

def embed_query(query, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
    model = SentenceTransformer(model_name)
    return model.encode([query])[0]
