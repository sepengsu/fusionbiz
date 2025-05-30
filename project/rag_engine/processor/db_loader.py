import os
import sqlite3
import pandas as pd

def load_log_file_to_sqlite(uploaded_file, save_dir="data/raw_file", db_path="data/factory/log.db"):
    os.makedirs(save_dir, exist_ok=True)

    # 1. 파일 저장
    filename = uploaded_file.filename
    file_path = os.path.join(save_dir, filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.file.read())

    # 2. 파일 형식 파악
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    # 3. pandas로 불러오기 (기본: tab 구분 assumed)
    try:
        if ext in [".csv"]:
            df = pd.read_csv(file_path)  # 콤마 구분
        elif ext in [".txt", ".tsv"]:
            df = pd.read_csv(file_path, sep="\t")  # 탭 구분
        else:
            return {"error": f"지원되지 않는 확장자입니다: {ext}"}
    except Exception as e:
        return {"error": f"파일 파싱 실패: {str(e)}"}

    # 4. SQLite 저장
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS machine_log")
        df.to_sql("machine_log", conn, index=False)
        row_count = cursor.execute("SELECT COUNT(*) FROM machine_log").fetchone()[0]
        conn.commit()
        conn.close()
    except Exception as e:
        return {"error": f"DB 저장 실패: {str(e)}"}

    return {
        "message": "✅ 로그 파일이 SQLite DB로 저장되었습니다.",
        "filename": filename,
        "row_count": row_count
    }
