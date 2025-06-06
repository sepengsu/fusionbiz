import os
import re
from datetime import datetime

def parse_date(text):
    # "1월 29일" → 0129 / 또는 "2021년 1월 29일"
    match = re.search(r'(\d{4})?[년\s]*(\d{1,2})월\s*(\d{1,2})일', text)
    if match:
        year = int(match.group(1)) if match.group(1) else 2021  # default year
        month = int(match.group(2))
        day = int(match.group(3))
        return datetime(year, month, day)
    return None

def guess_sql_db_path(question: str, db_root="data/factory") -> str:
    q = question.lower()

    machine = 'log' # 그냥 파일 하나로 하기 
    target_date = parse_date(q)

    candidates = []
    for fname in os.listdir(db_root):
        if not fname.endswith(".db"):
            continue

        parts = fname.replace(".db", "").split("_")
        if len(parts) < 3:
            continue

        mname, start_str, end_str = parts[0], parts[1], parts[2]
        start_dt = datetime.strptime(start_str, "%Y%m%d")
        end_dt = datetime.strptime(end_str, "%Y%m%d")

        # 기계 이름이 없거나 일치해야 함
        if machine and not mname.lower().startswith(machine.lower()):
            continue

        # 날짜가 포함되면 가산점
        score = 0
        if not machine:
            score += 1  # fallback 용도
        if not target_date or (start_dt <= target_date <= end_dt):
            score += 2

        candidates.append((score, fname))

    if candidates:
        best = max(candidates, key=lambda x: x[0])[1]
        return os.path.join(db_root, best)

    return os.path.join(db_root, "default.db")
