from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from backend.services.audio_recorder import AudioRecorderService
from backend.models.recording import RecordingCreate, RecordingResponse

recording_router = APIRouter(prefix="/recordings", tags=["recordings"])

audio_service = AudioRecorderService()

@recording_router.post("/record", response_model=RecordingResponse)
async def start_recording(request: RecordingCreate, background_tasks: BackgroundTasks):
    """
    시스템 오디오 녹음 시작
    """
    try:
        result = audio_service.record_system_audio(
            duration=request.duration,
            sample_rate=request.sample_rate
        )
        return result
    except Exception as e:
        # 프론트에 상세 에러 메시지를 전달
        raise HTTPException(status_code=500, detail=str(e))


@recording_router.get("")
@recording_router.get("/")
async def list_recordings():
    try:
        return audio_service.list_recordings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"녹음 목록을 불러오는 중 오류: {e}")


@recording_router.get("/{filename}")
async def get_recording(filename: str):
    file_path = audio_service.get_recording(filename)
    if not file_path:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    return FileResponse(path=file_path, media_type='audio/wav', filename=filename)
