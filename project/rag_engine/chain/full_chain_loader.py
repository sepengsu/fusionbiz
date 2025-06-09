# rag_engine/chain/full_chain_loader.py
import os
import json
import time
from pathlib import Path
from langchain_openai import ChatOpenAI
from rag_engine.chain.full_chain import build_full_chain

CONFIG_PATH = Path("config/chat_config.json")

# 전역 캐시
_cached_chain = None
_cached_mtime = None
_cached_config = None

def get_cached_full_chain():
    global _cached_chain, _cached_mtime, _cached_config

    try:
        current_mtime = os.path.getmtime(CONFIG_PATH)
    except FileNotFoundError:
        print("[ERROR] chat_config.json 파일이 존재하지 않습니다.")
        return None

    if _cached_chain is None or _cached_mtime != current_mtime:
        print("[INFO] 🔄 Chat config 변경 감지 또는 최초 실행: 체인 재구성 중...")

        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)

            llm = ChatOpenAI(
                model=config.get("llm_model", "gpt-3.5-turbo"),
                temperature=config.get("temperature", 0.0),
                api_key=os.getenv("OPENAI_API_KEY")
            )

            _cached_chain = build_full_chain(llm, config)

            _cached_mtime = current_mtime
            _cached_config = config
        except Exception as e:
            print("[ERROR] 체인 구성 중 오류 발생:", e)
            import traceback
            traceback.print_exc()
            return None

    return _cached_chain

