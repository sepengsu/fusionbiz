import os
from pathlib import Path

class Settings:
    # 프로젝트 루트 디렉토리
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # 녹음 파일 저장 디렉토리
    RECORDINGS_DIR = BASE_DIR / 'recordings'
    
    # 기본 녹음 설정
    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_CHANNELS = 2
    MAX_RECORDING_DURATION = 300  # 최대 녹음 시간 (초)

    # 디렉토리 생성
    RECORDINGS_DIR.mkdir(exist_ok=True)

settings = Settings()