from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil
import os
import torch
import random
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
print("env 파일 있음" if os.path.exists(os.path.join(os.path.dirname(__file__), ".env")) else "env 파일 없음")
print(f"환경 변수 openai_api_key 로빙 완료" if os.getenv("OPENAI_API_KEY") else "환경 변수 openai_api_key 없음")
from rag_engine.retriever import get_top_chunks
from rag_engine.responder import generate_response
from rag_engine.processor import preprocess_log_file
from rag_engine.config_manager import save_config, load_config
from rag_engine.chain.chat_router import handle_question


# 환경 변수 로드

app = FastAPI()

# 디렉토리 설정
BASE_DIR = "frontend"
PREPROCESSOR_DIR = os.path.join(BASE_DIR, "preprocessor")
CHATBOT_DIR = os.path.join(BASE_DIR, "chatbot")
CHATTING_DIR = os.path.join(BASE_DIR, "chatting")
DATA_DIR = "data/raw_logs"
CHUNK_DIR = "data/processed_chunks"
VECTOR_DIR = "data/vector_store"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)

# 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] Using device: {device}")

print("[INFO] 환경 변수 로드 완료")

@app.get("/chat_config")
def get_chat_config():
    return load_config()

@app.post("/chat_config")
async def set_chat_config(request: Request):
    config = await request.json()
    save_config(config)
    return {"message": "✅ 설정이 저장되었습니다."}

class QueryRequest(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
def serve_main():
    return FileResponse(path=os.path.join(BASE_DIR, "index.html"))

@app.get("/preprocessor", response_class=HTMLResponse)
def serve_preprocessor():
    return FileResponse(path=os.path.join(PREPROCESSOR_DIR, "index.html"))

@app.get("/chatbot", response_class=HTMLResponse)
def serve_chatbot():
    return FileResponse(path=os.path.join(CHATBOT_DIR, "index.html"))

@app.get("/chatting", response_class=HTMLResponse)
def serve_chatting():
    return FileResponse(path=os.path.join(CHATTING_DIR, "index.html"))

@app.post("/upload_log")
def upload_log(
    file: UploadFile = File(...),
    chunk_size: int = Form(200),
    chunk_overlap: int = Form(0),
    embedding_model: str = Form("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
    vector_type: str = Form("FAISS")
):
    filepath = os.path.join(DATA_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    preprocess_log_file(filepath, CHUNK_DIR, VECTOR_DIR, device=device)

    # 랜덤 청크 미리보기
    sample_text = ""
    try:
        chunk_files = [f for f in os.listdir(CHUNK_DIR) if f.endswith(".txt")]
        if chunk_files:
            random_file = random.choice(chunk_files)
            with open(os.path.join(CHUNK_DIR, random_file), "r", encoding="utf-8") as f:
                sample_text = f.read()
    except Exception as e:
        sample_text = f"미리보기 오류: {str(e)}"

    return {
        "status": "uploaded and processed",
        "filename": file.filename,
        "device": str(device),
        "sample": sample_text.strip()
    }


from rag_engine.chain.chat_router import handle_question

@app.post("/ask")
def ask_question(query: QueryRequest):
    result = handle_question(query.question, VECTOR_DIR, CHUNK_DIR, device)
    return result



import faiss

@app.get("/api/vector_status")
def get_vector_status():
    try:
        # 실제 인덱스 불러보기를 시도
        index_path = os.path.join(VECTOR_DIR, "index.faiss")
        loaded = False
        if os.path.exists(index_path):
            try:
                _ = faiss.read_index(index_path)
                loaded = True
            except:
                loaded = False

        # 문서 수 확인
        chunk_files = [f for f in os.listdir(CHUNK_DIR) if f.endswith(".txt")]
        doc_count = len(chunk_files)

        return JSONResponse(content={
            "loaded": loaded,
            "doc_count": doc_count
        })

    except Exception as e:
        return JSONResponse(content={
            "loaded": False,
            "doc_count": 0,
            "error": str(e)
        }, status_code=500)
