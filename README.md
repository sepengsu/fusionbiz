### 서비스 만들기 
```
/ai_summarizer
│── main.py
│── config.py
│
├── /routes
│   ├── text_summary.py
│   ├── audio_summary.py
│   ├── health_check.py
│
├── /services
│   ├── text_processing.py
│   ├── audio_processing.py
│
├── /models
│   ├── summarization.py
│   ├── stt.py
│
├── /templates       # HTML 템플릿 폴더 (Jinja2 사용)
│   ├── index.html   # 메인 페이지
│   ├── result.html  # 요약 결과 페이지
│
└── /static          # CSS, JS, 이미지 폴더
    ├── style.css
    ├── script.js
```


### 1. ffmpeg 설치 
```
소스코드로 설치하고 path 지정하는 것을 추천함 

  libc_name = None
  if platform.uname()[0] == 'Windows':
    libc_name = 'msvcrt'
  else:
    libc_name = ctypes.util.find_library('c')

    추가 
```