```
project/
├── main.py               # FastAPI 서버
├── rag_engine/
│   ├── retriever.py      # Vector 검색기
│   ├── responder.py      # GPT 응답기
│   ├── processor.py      # 로그 전처리
│   └── utils.py          # 시간 파싱 등 유틸
├── data/
│   ├── raw_logs/         # 업로드된 원본
│   ├── processed_chunks/ # 전처리된 chunk
│   └── vector_store/     # FAISS or Chroma 저장
└── requirements.txt
```