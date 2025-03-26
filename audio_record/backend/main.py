from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routes.recording import recording_router

# FastAPI 애플리케이션 초기화
app = FastAPI(
    title="Windows System Audio Recorder",
    description="윈도우 시스템 오디오 녹음 애플리케이션",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 라우터 먼저 등록
app.include_router(recording_router, include_in_schema=True)

# ✅ 그 다음에 정적 파일 mount
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# uvicorn 실행 코드
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
