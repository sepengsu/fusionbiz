import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def parse_datetime_from_line(line: str):
    pattern = r"(\d{4})년 (\d{1,2})월 (\d{1,2})일 (\d{1,2})시 (\d{1,2})분"
    match = re.search(pattern, line)
    if match:
        year, month, day, hour, minute = map(int, match.groups())
        return datetime(year, month, day, hour, minute)
    return None

def preprocess_log_file(filepath: str, chunk_dir: str, vector_dir: str, device=None):
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device=device)

    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    entries = [(parse_datetime_from_line(line), line) for line in lines if parse_datetime_from_line(line)]
    entries.sort(key=lambda x: x[0])

    chunks = []
    current_chunk = []
    chunk_start = None

    for dt, line in entries:
        if chunk_start is None:
            chunk_start = dt
        if dt - chunk_start > timedelta(minutes=10):
            chunks.append(current_chunk)
            current_chunk = []
            chunk_start = dt
        current_chunk.append(line)
    if current_chunk:
        chunks.append(current_chunk)

    os.makedirs(chunk_dir, exist_ok=True)
    os.makedirs(vector_dir, exist_ok=True)

    embeddings = []
    for i, chunk in enumerate(chunks):
        content = "\n".join(chunk)
        with open(os.path.join(chunk_dir, f"chunk_{i}.txt"), "w", encoding="utf-8") as f:
            f.write(content)
        emb = model.encode(content)
        embeddings.append(emb)

    if embeddings:
        dim = len(embeddings[0])
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings).astype('float32'))
        faiss.write_index(index, os.path.join(vector_dir, "index.faiss"))
        print(f"[INFO] Saved FAISS index with {len(embeddings)} chunks")
