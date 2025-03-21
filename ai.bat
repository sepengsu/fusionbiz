@echo off
SETLOCAL
set PYTHONCTYPESLIB=C:\Windows\System32\msvcrt.dll
cd ai_summarizer
call uvicorn main:app --reload
ENDLOCAL
