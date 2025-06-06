import os
from dotenv import load_dotenv
# ------------------------- 환경 설정 -------------------------
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
print("env 파일 있음" if os.path.exists(os.path.join(os.path.dirname(__file__), ".env")) else "env 파일 없음")
print(f"환경 변수 openai_api_key 로딩 완료" if os.getenv("OPENAI_API_KEY") else "환경 변수 openai_api_key 없음")

from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil, torch, random

from rag_engine.processor.chunker import chunk_file
from rag_engine.processor.vector_saver import save_faiss_index, get_embeddings, save_meta_config
from config.config_manager import save_config, load_config
from rag_engine.chain.routing.chat_router import handle_question
from rag_engine.processor.db_loader import load_log_file_to_sqlite

app = FastAPI()

# ------------------------- 디렉토리 경로 -------------------------
BASE_DIR = "frontend"
PREPROCESSOR_DIR = os.path.join(BASE_DIR, "preprocessor")
CHATBOT_DIR = os.path.join(BASE_DIR, "chatbotsetting")
CHATTING_DIR = os.path.join(BASE_DIR, "chatting")

DATA_BASE = "data"
RAW_DIR = os.path.join(DATA_BASE, "raw_file")
CHUNK_BASE = {
    "manual": os.path.join(DATA_BASE, "manual", "processed_chunks"),
    "sql": os.path.join(DATA_BASE, "sqlguide", "processed_chunks")
}
VECTOR_BASE = {
    "manual": os.path.join(DATA_BASE, "manual", "vector_store"),
    "sql": os.path.join(DATA_BASE, "sqlguide", "vector_store")
}

os.makedirs(RAW_DIR, exist_ok=True)
for path in list(CHUNK_BASE.values()) + list(VECTOR_BASE.values()):
    os.makedirs(path, exist_ok=True)

# ------------------------- 정적 파일 마운트 -------------------------
app.mount("/frontend", StaticFiles(directory=BASE_DIR), name="frontend")
app.mount("/config", StaticFiles(directory="config"), name="config")
# ------------------------- 디바이스 설정 -------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] Using device: {device}")

# ------------------------- 설정 API -------------------------

@app.get("/chat_config")
def get_chat_config():
    return load_config()

@app.post("/chat_config")
async def set_chat_config(request: Request):
    config = await request.json()
    save_config(config)
    return {"message": "✅ 설정이 저장되었습니다."}

# ------------------------- 메인 화면 -------------------------

@app.get("/")
def serve_main():
    return RedirectResponse(url="/frontend/index.html")


# ------------------------- 데이터 업로드 및 벡터 저장 -------------------------

@app.post("/upload_log")
def upload_log(
    file: UploadFile = File(...),
    chunk_size: int = Form(200),
    chunk_overlap: int = Form(0),
    embedding_model: str = Form("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
    vector_type: str = Form("FAISS"),
    process_type: str = Form("manual")
):
    filename = file.filename
    file_path = os.path.join(RAW_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 청크 및 벡터 저장 경로
    chunk_dir = CHUNK_BASE.get(process_type)
    vector_dir = VECTOR_BASE.get(process_type)

    # 텍스트 chunk 처리
    chunks = chunk_file(file_path, chunk_dir, chunk_size, chunk_overlap)

    # FAISS 인덱스 저장
    index_path = os.path.join(vector_dir, "index.faiss")
    save_faiss_index(chunks, index_path, model_name=embedding_model)

    # 메타 정보 저장
    vector_dim = len(get_embeddings(["임시"], embedding_model)[0])
    save_meta_config(
        save_dir=vector_dir,
        embedding_model=embedding_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        vector_type=vector_type,
        process_type=process_type,
        vector_dim=vector_dim,
        filename=filename
    )

    # 샘플 텍스트 미리보기
    sample_text = ""
    try:
        chunk_files = [f for f in os.listdir(chunk_dir) if f.endswith(".txt")]
        if chunk_files:
            random_file = random.choice(chunk_files)
            with open(os.path.join(chunk_dir, random_file), "r", encoding="utf-8") as f:
                sample_text = f.read()
    except Exception as e:
        sample_text = f"미리보기 오류: {str(e)}"

    return {
        "status": "uploaded and processed",
        "filename": filename,
        "device": str(device),
        "sample": sample_text.strip()
    }

# ------------------------- 질문 응답 API -------------------------

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(query: QueryRequest):
    result = handle_question(
        question=query.question,
        vector_dir_map=VECTOR_BASE,
        device=device
    )
    return result

# ------------------------- 벡터 상태 확인 -------------------------

@app.get("/api/vector_status")
def get_vector_status():
    import glob

    result = {}

    # ✅ LOG: .db 파일 기준
    log_db_files = glob.glob("data/factory/*.db")
    result["log"] = {
        "loaded": len(log_db_files) > 0,
        "doc_count": len(log_db_files)
    }

    # ✅ SQL, MANUAL은 기존 방식 유지
    for key in ["manual", "sql"]:
        try:
            index_path = os.path.join(VECTOR_BASE[key], "index.faiss")
            loaded = os.path.exists(index_path)

            chunk_dir = CHUNK_BASE.get(key, "")
            chunk_files = os.listdir(chunk_dir) if os.path.isdir(chunk_dir) else []
            doc_count = len([f for f in chunk_files if f.endswith(".txt")])

            result[key] = {
                "loaded": loaded,
                "doc_count": doc_count
            }
        except Exception as e:
            result[key] = {
                "loaded": False,
                "doc_count": 0,
                "error": str(e)
            }

    return JSONResponse(content=result)



# ------------------------- db 생성 -------------------------
@app.post("/upload_log_to_db")
def upload_log_to_sqlite(file: UploadFile = File(...)):
    return load_log_file_to_sqlite(file)
