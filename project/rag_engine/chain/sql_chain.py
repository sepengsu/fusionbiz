from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import RunnableMap
from rag_engine.chain.utils.path_utils import infer_existing_db_path
from rag_engine.chain.searcher.sql_searcher import search_sqlguide_chunks
import sqlite3

def get_sql_chain(llm, config):
    # 날짜 추청 함수 

    guess_date_chain = RunnableLambda(guess_date)

    # 🔹 프롬프트 구성
    system_prompt = SystemMessagePromptTemplate.from_template(config.get("sql_system_prompt", ""))
    user_prompt = HumanMessagePromptTemplate.from_template(config.get("sql_user_prompt", ""))

    prompt_template = ChatPromptTemplate.from_messages([
        system_prompt,
        user_prompt
    ])

    sqlguide_chunk_chain = RunnableLambda(sqlguide_chunk_searcher)
    # 🔹 SQL 생성 함수
    def generate_sql_only(d):
        question = d["question"]
        try:
            # 올바른 메시지 포맷 생성
            messages = prompt_template.format_messages(
                question=question,
                sql_chunks=d.get("sqlguide_chunks", ""),
                chat_history=d.get("chat_history", ""),
                context=d.get("context", ""),
                date=d.get("date", TODAY),  # 기본값 TODAY 사용
                query=question
            )

            # LLM 호출
            raw_output = llm.invoke(messages)
            sql_code = clean_sql_code(raw_output.content)

        except Exception as e:
            sql_code = f"-- ❌ SQL 생성 실패: {str(e)}"

        inferred_path = infer_existing_db_path(question, db_dir=config.get("db_dir", "data/factory"))

        return {
            "question": question,
            "sql_code": sql_code,
            "db_path": inferred_path
        }

    sql_generate_chain = RunnableLambda(generate_sql_only)
    run_sql_chain = RunnableLambda(run_sql)

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", config.get("sql_result_system_prompt", "")),
        ("user", config.get("sql_result_user_prompt","{question}\n\n{table}"))
    ])
    format_result_chain = (
    RunnableMap({
        "question": lambda d: d["question"],
        "table": lambda d: format_table(d["columns"], d["rows"])
    })
    | chat_prompt
    | llm
    | RunnableLambda(lambda m: m.content)  # ✅ output에서 .content만 추출
    )


    return guess_date_chain | sqlguide_chunk_chain | sql_generate_chain | run_sql_chain | format_result_chain

# ------------------------- SQL 관련 함수 -------------------------
def guess_date(d):
    """
    질문에서 날짜를 추출하여 YYYY-MM-DD 형식으로 반환
    """
    question = d["question"]
    date = extract_first_date(question)
    return {
        **d,
        "date": date.strftime("%Y-%m-%d") if date else None
    }
# ------------------------- SQL 가이드 청크 검색 -------------------------
def sqlguide_chunk_searcher(d):
    question = d["question"]
    print(f"[DEBUG] 🧠 SQL 가이드 청크 검색 대상 질문: {question}")

    chunk_result = search_sqlguide_chunks(
        query=question,
        device=d.get("device"),
        vector_dir="data/sqlguide/vector_store",
        chunk_dir="data/sqlguide/processed_chunks"
    )

    print(f"[DEBUG] 📘 SQL 가이드 chunk 검색 완료 (길이: {len(chunk_result['sql_chunks'])})")

    return {
        **d,
        "sqlguide_chunks": chunk_result["sql_chunks"]
    }


# ------------------------- SQL 실행 -------------------------
def run_sql(d):
    sql_code = d["sql_code"]
    db_path = d["db_path"]

    rows, columns, error = run_sql_code(sql_code, db_path)

    if error:
        return {
            "question_type": "sql",
            "response": f"❌ SQL 실행 오류: {error}",
            "sql_code": sql_code,
            "db_path": db_path
        }

    return {
        "question": d["question"],
        "question_type": "sql",
        "rows": rows,
        "columns": columns,
        "sql_code": sql_code,
        "db_path": db_path
    }

# ------------------------- SQL 결과 포맷팅 -------------------------
def format_table(columns, rows):
    if not rows:
        return "결과 없음"

    col_line = " | ".join(columns)
    sep_line = "-+-".join(['-' * len(col) for col in columns])
    row_lines = [" | ".join(str(cell) for cell in row) for row in rows]
    return "\n".join([col_line, sep_line] + row_lines)


# 🔹 SQLite 실행 함수
def run_sql_code(sql_code: str, db_path: str = None) -> tuple:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_code)
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()
        return rows, col_names, None
    except Exception as e:
        return [], [], str(e)


# 결과 및 질문 기반
import os, re, traceback
from datetime import datetime, timedelta
from typing import Optional
TODAY = '2021-01-29' # 예시 날짜, 실제로는 현재 날짜로 대체 필요

# 날짜 추출 함수 
def extract_first_date(question: str, reference_date: Optional[datetime] = None) -> Optional[datetime]:
    """
    질문에서 첫 번째 날짜를 추출합니다.
    """
    today = reference_date or datetime.strptime(TODAY, "%Y-%m-%d")

    # 1. 오늘 날짜
    if "오늘" in question:
        return today

    # 2. 어제 날짜
    if "어제" in question:
        return today - timedelta(days=1)

    # 3. 특정 날짜: e.g., 2021년 1월 1일
    match = re.search(r"\b(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일\b", question)
    if match:
        return datetime(year=int(match[1]), month=int(match[2]), day=int(match[3]))

    # 4. 월/일 조합: e.g., 1월 1일
    match = re.search(r"\b(\d{1,2})\s*월\s*(\d{1,2})\s*일\b", question)
    if match:
        return datetime(year=today.year, month=int(match[1]), day=int(match[2]))
    # 5. 월만: e.g., 1월
    match = re.search(r"\b(\d{1,2})\s*월\b", question)
    if match:
        return datetime(year=today.year, month=int(match[1]), day=1)
    

def clean_sql_code(raw_output: str) -> str:
    """
    자연어 설명이 포함된 응답에서 SQL 쿼리만 추출하고, 쿼리 형식을 정리한다.
    """
    # 백틱 블럭 내 SQL 추출
    if "```" in raw_output:
        parts = raw_output.split("```")
        for i in range(len(parts)):
            if "sql" in parts[i]:
                parts[i] = parts[i].replace("sql", "").strip()
                break
        raw_output =  parts[i]
    
    # SELECT, INSERT 등 SQL 시작 키워드부터 끝까지 추출
    match = re.search(r"(SELECT|WITH|INSERT|UPDATE|DELETE)[\s\S]*", raw_output, re.IGNORECASE)
    if not match:
        raw_output = parts[i]
        match = re.search(r"(SELECT|WITH|INSERT|UPDATE|DELETE)[\s\S]*", raw_output, re.IGNORECASE)
        return "-- ❌ 유효한 SQL 시작 키워드 없음"

    sql_code = match.group(0).strip()

    # 세미콜론이 없으면 추가
    if not sql_code.endswith(";"):
        sql_code += ";"

    return sql_code



