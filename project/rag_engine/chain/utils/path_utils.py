import re
import os
from datetime import datetime
from typing import Optional

def extract_first_date(question: str, reference_date: Optional[datetime] = None) -> Optional[datetime]:
    today = reference_date or datetime.today()
    question = re.sub(r"\s+", " ", question.strip())  # 공백 정리

    # 1. 'X월Y일', 'X월 Y일'
    match = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", question)
    if match:
        return datetime(year=today.year, month=int(match[1]), day=int(match[2]))

    # 2. YYYY-MM-DD / YYYY.MM.DD / YYYY/MM/DD
    match = re.search(r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})", question)
    if match:
        return datetime(year=int(match[1]), month=int(match[2]), day=int(match[3]))

    # 3. MM/DD or M.D
    match = re.search(r"\b(\d{1,2})[./](\d{1,2})\b", question)
    if match:
        return datetime(year=today.year, month=int(match[1]), day=int(match[2]))

    # 4. only 일: e.g., 30일
    match = re.search(r"\b(\d{1,2})\s*일\b", question)
    if match:
        return datetime(year=today.year, month=today.month, day=int(match[1]))

    return None

REFER= datetime(2021,1,1)  # 예시: 기준 날짜 설정
def infer_existing_db_path(
    question: str,
    db_dir: str = "data/factory",
    reference_date: Optional[datetime] = None
) -> Optional[str]:
    reference_date = REFER  # 예: datetime(2021, 1, 1)로 기준 고정
    target_date = extract_first_date(question, reference_date)
    if not target_date:
        return None

    target_str = target_date.strftime("%Y%m%d")
    closest_path = None
    closest_gap = float('inf')

    for fname in os.listdir(db_dir):
        if not fname.startswith("log_") or not fname.endswith(".db"):
            continue

        try:
            date_range_str = fname[len("log_"):-len(".db")]
            start_str, end_str = date_range_str.split("_")
            start = datetime.strptime(start_str, "%Y%m%d")
            end = datetime.strptime(end_str, "%Y%m%d")

            # ✅ 직접 포함되는 경우 즉시 반환
            if start <= target_date <= end:
                return os.path.join(db_dir, fname)

            # ❗ 포함 안 되는 경우 → 가장 가까운 범위 추적
            gap = min(abs((start - target_date).days), abs((end - target_date).days))
            if gap < closest_gap:
                closest_gap = gap
                closest_path = os.path.join(db_dir, fname)

        except Exception:
            continue

    return closest_path


import re
from datetime import datetime

def extract_reference_date_from_question(question: str, reference_date: Optional[datetime] = None) -> datetime:
    """
    질문 내 날짜 패턴에서 기준 날짜를 추출합니다.
    내부적으로 extract_first_date 재사용.
    """
    reference_date = REFER
    result = extract_first_date(question, reference_date)
    return result or (reference_date or datetime.today())