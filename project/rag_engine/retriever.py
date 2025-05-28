import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

def load_chunks(chunk_dir):
    chunks = []
    paths = sorted(Path(chunk_dir).glob("chunk_*.txt"))
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            chunks.append(f.read())
    return chunks

def get_top_chunks(query: str, vector_dir: str, chunk_dir: str = "data/processed_chunks", top_k: int = 3, device=None):
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device=device)

    index_path = os.path.join(vector_dir, "index.faiss")
    if not os.path.exists(index_path):
        raise FileNotFoundError("FAISS index not found. Run preprocess_log_file first.")

    index = faiss.read_index(index_path)
    query_vec = model.encode(query)
    query_vec = np.array([query_vec]).astype("float32")

    distances, indices = index.search(query_vec, top_k)
    chunks = load_chunks(chunk_dir)
    return [chunks[i] for i in indices[0] if i < len(chunks)]
