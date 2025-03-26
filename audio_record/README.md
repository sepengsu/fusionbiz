# 시스템 오디오 녹음 FastAPI 애플리케이션

## 프로젝트 소개
이 프로젝트는 FastAPI를 사용하여 시스템 오디오를 녹음하고 관리하는 웹 애플리케이션입니다.

## 주요 기능
- 시스템 오디오 녹음
- 녹음 파일 관리
- RESTful API 엔드포인트

## 프로젝트 구조
```
system-audio-recorder/
│
├── main.py                # FastAPI 메인 애플리케이션
├── services/
│   ├── __init__.py
│   └── audio_recorder.py  # 오디오 녹음 서비스
├── models/
│   ├── __init__.py
│   └── recording.py       # 데이터 모델
├── routes/
│   ├── __init__.py
│   └── recording.py       # API 라우트
├── config.py              # 애플리케이션 설정
├── requirements.txt       # 의존성 파일
└── README.md              # 프로젝트 설명서
```

## 설치 방법
1. 가상 환경 생성
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 애플리케이션 실행
```bash
uvicorn main:app --reload
```

## API 엔드포인트
- `POST /record/`: 시스템 오디오 녹음 시작
- `GET /recordings/`: 녹음 파일 목록 조회
- `GET /recordings/{file_id}`: 특정 녹음 파일 다운로드
