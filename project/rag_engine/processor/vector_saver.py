from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
from openai import OpenAI

def get_embeddings(chunks, model_name):
    if model_name.startswith("openai/"):
        openai_model = model_name.replace("openai/", "")
        client = OpenAI()  # API 키는 .env 또는 환경변수에서 자동으로 로드됨

        vectors = []
        for chunk in chunks:
            response = client.embeddings.create(
                model=openai_model,
                input=chunk,
            )
            vector = response.data[0].embedding
            vectors.append(vector)

        return np.array(vectors, dtype=np.float32)
    
    else:
        model = SentenceTransformer(model_name)
        return model.encode(chunks, convert_to_numpy=True)

def save_faiss_index(chunks, save_path, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    vectors = get_embeddings(chunks, model_name)
    dim = vectors.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors))
    faiss.write_index(index, save_path)
    print(f"[✅] FAISS 인덱스 저장 완료: {save_path}")
