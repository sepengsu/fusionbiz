from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

class LogPreprocessor:
    """
    GPT 문맥 이해를 돕기 위한 로그 전처리 클래스
    - 시간 기준 그룹화
    - 상태 전이 요약 생성
    - 반복 패턴 요약
    - 자연어 서술형 문장 생성
    """

    def __init__(self, filepath: str, interval_minutes: int = 10):
        self.filepath = Path(filepath)
        self.interval = timedelta(minutes=interval_minutes)
        self.df = self._load_and_parse()

    def _load_and_parse(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        logs = []
        for line in lines:
            try:
                time_part = line.split("에")[0].strip()
                timestamp = datetime.strptime(time_part, "%Y년 %m월 %d일 %H시 %M분")
                logs.append({"timestamp": timestamp, "text": line.strip()})
            except Exception:
                continue
        return pd.DataFrame(logs).sort_values("timestamp")

    def group_by_time(self):
        grouped = []
        current_chunk = []
        current_start = self.df.iloc[0]["timestamp"]

        for _, row in self.df.iterrows():
            if row["timestamp"] - current_start > self.interval:
                grouped.append(current_chunk)
                current_chunk = []
                current_start = row["timestamp"]
            current_chunk.append(row)
        if current_chunk:
            grouped.append(current_chunk)
        return grouped

    def summarize_block(self, block):
        texts = [row["text"] for row in block]
        summary = []
        last_op = None
        for text in texts:
            if "작동" in text:
                current_op = "작동"
            elif "정지" in text:
                current_op = "정지"
            elif "오류" in text:
                current_op = "오류"
            else:
                current_op = "기타"

            if last_op and last_op != current_op:
                summary.append(f"{last_op} → {current_op} 전환 발생")
            last_op = current_op

        return summary + texts

    def format_blocks_as_text(self):
        blocks = self.group_by_time()
        lines = []
        for i, block in enumerate(blocks):
            lines.append(f"[이벤트 블록 {i + 1}]")
            summarized = self.summarize_block(block)
            for line in summarized:
                lines.append(f"- {line}")
            lines.append("")
        return "\n".join(lines)