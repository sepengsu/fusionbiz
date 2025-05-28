from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import shutil
import os
import torch

from rag_engine.retriever import get_top_chunks
from rag_engine.responder import generate_response
from rag_engine.processor import preprocess_log_file

app = FastAPI()

DATA_DIR = "data/raw_logs"
CHUNK_DIR = "data/processed_chunks"
VECTOR_DIR = "data/vector_store"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)

# 디바이스 설정 (CUDA 사용 가능 시 GPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] Using device: {device}")

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def health_check():
    return {"status": "OK", "device": str(device)}

@app.post("/upload_log")
def upload_log(file: UploadFile = File(...)):
    filepath = os.path.join(DATA_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 전처리 및 벡터 저장 수행
    preprocess_log_file(filepath, CHUNK_DIR, VECTOR_DIR, device=device)
    return {"status": "uploaded and processed", "filename": file.filename, "device": str(device)}

@app.post("/ask")
def ask_question(query: QueryRequest):
    # top-k chunk 검색
    top_chunks = get_top_chunks(query.question, VECTOR_DIR, device=device)

    # GPT 응답 생성
    answer = generate_response(query.question, top_chunks, device=device)
    return {"answer": answer, "source_chunks": top_chunks, "device": str(device)}
