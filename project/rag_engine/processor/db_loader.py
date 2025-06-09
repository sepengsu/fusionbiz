import os
import sqlite3
import pandas as pd

def load_log_file_to_sqlite(uploaded_file, save_dir="data/raw_file", db_dir_path="data/factory"):
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
    # 3.1. 컬럼 이름 정리
    df.columns = df.columns.str.strip()
    # 4. DB 이름 생성
    db_name = generate_db_name_from_machine_data(file_path)
    db_path = os.path.join(db_dir_path, db_name)
    # 5. SQLite 저장
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        Name = "logs"  # 테이블 이름 고정
        cursor.execute(f"DROP TABLE IF EXISTS {Name}")
        df.to_sql(Name, conn, index=False)
        row_count = cursor.execute(f"SELECT COUNT(*) FROM {Name}").fetchone()[0]
        conn.commit()
        conn.close()
    except Exception as e:
        return {"error": f"DB 저장 실패: {str(e)}"}

    return {
        "message": "✅ 로그 파일이 SQLite DB로 저장되었습니다.",
        "filename": filename,
        "row_count": row_count
    }

def generate_db_name_from_machine_data(txt_path: str) -> str:
    df = pd.read_csv(txt_path, sep="\t")

    # 기계 이름 추출 (모든 행 동일하다고 가정)
    machinename = 'log'

    # 시작 및 종료 시간 추출
    start = df.iloc[0]
    end = df.iloc[-1]

    def to_datetime_str(row):
        return f"{row['Year']:04}{row['Month']:02}{row['Day']:02}"
    
    print(f"Start: {start}, End: {end}")
    start_str = to_datetime_str(start)
    end_str = to_datetime_str(end)

    db_name = f"{machinename}_{start_str}_{end_str}.db"
    return db_name

