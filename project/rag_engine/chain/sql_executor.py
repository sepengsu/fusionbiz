import pandas as pd
import pandasql as ps
from rag_engine.retriever import get_top_chunks
from rag_engine.responder import generate_response

# 전제: logs_df는 메모리 상의 DataFrame으로 저장된 로그 데이터셋
# 추후 실제 로그를 DB나 CSV로부터 로딩하는 방식도 고려 가능
LOG_DATA_PATH = "data/raw_logs/machine_data.txt"

def load_log_dataframe():
    df = pd.read_csv(LOG_DATA_PATH, sep="\t")
    return df

def generate_sql_query(question, top_chunks, device):
    # GPT로 SQL 문 생성
    context = "\n\n".join([chunk["text"] for chunk in top_chunks])
    prompt = f"""
    아래는 로그 테이블입니다:

    {context}

    위 정보를 참고하여 다음 질문에 대한 SQL을 생성하세요:

    질문: "{question}"

    SQL:
    """
    return generate_response(prompt, top_chunks, device=device)

def execute_sql_on_logs(sql_query, df):
    try:
        result = ps.sqldf(sql_query, locals())
        return result.to_string(index=False)
    except Exception as e:
        return f"❌ SQL 실행 중 오류 발생: {str(e)}"

def handle_sql_question(question, device):
    # 1. 로그 DataFrame 불러오기
    df = load_log_dataframe()

    # 2. SQL 가이드 문서에서 유사한 chunk 검색
    top_chunks = get_top_chunks(question, "data/vector_store/sql_guide", "data/sql_guide_chunks", device=device)

    # 3. GPT를 통해 SQL 문 생성
    sql_query = generate_sql_query(question, top_chunks, device)

    # 4. SQL 실행
    result = execute_sql_on_logs(sql_query, df)

    return {
        "question_type": "sql",
        "generated_sql": sql_query.strip(),
        "answer": result,
        "source_chunks": top_chunks
    }
