import re, sqlite3
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from rag_engine.chain.searcher.manual_searcher import search_manual_chunks
from rag_engine.chain.utils.path_utils import infer_existing_db_path
from datetime import datetime, timedelta
from rag_engine.chain.utils.path_utils import infer_existing_db_path, extract_reference_date_from_question 
from rag_engine.chain.utils.window_selector import extract_window_days
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from rag_engine.chain.sql_chain import extract_first_date, clean_sql_code, run_sql
TODAY = '2021-01-29' # 예시 날짜, 실제로는 현재 날짜로 대체 필요

def get_manual_chain(llm, config):
    max_history = config.get("max_history", 5)
    window_system_prompt = SystemMessagePromptTemplate.from_template(config.get("manual_window_prompt",""))
    window_user_prompt = HumanMessagePromptTemplate.from_template(config.get("manual_window_user_prompt",""))
    window_prompt = ChatPromptTemplate.from_messages([
        window_system_prompt,
        window_user_prompt
    ])

    fallback_gpt_window_chain = window_prompt | llm | RunnableLambda(lambda x: {
        "window_days": int(x.content.strip())
    })


    def get_window_info_with_fallback(question: str) -> dict:
        days = extract_window_days(question)
        print(f"[DEBUG] ⏳ window_days 추출됨 (정규식): {days}")
        db_path = infer_existing_db_path(question)
        ref_date = extract_reference_date_from_question(question)  # 신규 유틸 함수 필요

        if days is not None:
            print(f"[DEBUG] ⏳ window_days 추출됨 (정규식): {days}")
            print(f"[DEBUG] 🗂️ DB 경로 추론됨 (정규식 기반): {db_path}")
            print(f"[DEBUG] 📅 기준일 추론됨: {ref_date}")
            return {"window_days": days, "db_path": db_path, "reference_date": ref_date}

        try:
            res = fallback_gpt_window_chain.invoke({"question": question})
            print(f"[DEBUG] ⏳ window_days 추출됨 (LLM): {res['window_days']}")
            print(f"[DEBUG] 🗂️ DB 경로 추론됨 (LLM 기반): {db_path}")
            print(f"[DEBUG] 📅 기준일 추론됨 (LLM): {ref_date}")
            return {
                "window_days": res["window_days"],
                "db_path": db_path,
                "reference_date": ref_date
            }
        except Exception as e:
            print(f"[WARN] window_days 추론 실패, 기본값 사용: 1일, db: {db_path}, error: {e}")
            return {
                "window_days": 1,
                "db_path": db_path,
                "reference_date": ref_date
            }


    window_chain = RunnableLambda(lambda d: {
        **d,
        **get_window_info_with_fallback(d["question"])
    })
    #  쿼리 문 추출 
    system_prompt = SystemMessagePromptTemplate.from_template(config["sql_system_prompt"])
    user_prompt = HumanMessagePromptTemplate.from_template(config["user_prompt_template"])

    prompt_template = ChatPromptTemplate.from_messages([
        system_prompt,
        user_prompt
    ])

    def generate_sql_only(d):
        question = d["question"]
        try:
            # 올바른 메시지 포맷 생성
            messages = prompt_template.format_messages(
                question=question,
                sql_chunks=d.get("sqlguide_chunks", ""),
                chat_history="",
                context=d.get("context", ""),
                date=d.get("date", TODAY),  # 기본값 TODAY 사용
                query=question
            )

            # LLM 호출
            raw_output = llm.invoke(messages)
            sql_code = clean_sql_code(raw_output.content)

        except Exception as e:
            sql_code = f"-- ❌ SQL 생성 실패: {str(e)}"

        return {
            **d,
            "sql_code": sql_code
        }
    
    sql_generate_chain = RunnableLambda(generate_sql_only)

    faulty_machine_sql_chain = RunnableLambda(get_faulty_machines)
    # 🔹 3. 매뉴얼 검색
    def chunk_searcher(d):
        # 머신 리스트가 비어있는 경우
        if isinstance(d['data'],str) or not d["data"] or len(d["data"]) == 0:
            print("[WARN] ❌ 고장 기계 없음 → chunk 검색 스킵")
            return {**d, "chunks": []}

        # 가장 오류가 많은 기계 하나만 사용
        top_machine ,num= d["data"][0]["machine"], d["data"][0]["error_count"]
        print(f"[DEBUG] 🥇 chunk 검색 대상 기계: {top_machine}")

        # 검색 수행
        chunks = search_manual_chunks(
            [top_machine],
            device=d.get("device"),
            vector_dir="data/manual/vector_store",
            chunk_dir="data/manual/processed_chunks"
        )

        # chunks에 머신 정보 추가
        for chunk in chunks:
            chunk["machine"] = top_machine
            chunk["status"] = f" ({num}회) 오류 발생" 

        print(f"[DEBUG] 📚 매뉴얼 chunk 검색 완료: {len(chunks)}개")
        return {
            **d,
            "chunks": chunks
        }

    manual_chunk_chain = RunnableLambda(chunk_searcher)

    # system/user 프롬프트 구성
    system_summary_prompt = SystemMessagePromptTemplate.from_template(config["manual_system_prompt"])
    user_summary_prompt = HumanMessagePromptTemplate.from_template(config["user_prompt_template"])

    # ChatPromptTemplate 생성
    manual_prompt = ChatPromptTemplate.from_messages([
        system_summary_prompt,
        user_summary_prompt
    ])

    # 🔹 GPT 응답 생성 체인
    def generate_manual_summary(data):
        context_text = summarize_faulty_machines(data["data"])
        outputs = []

        if not data["chunks"]:
            print("[WARN] ⚠️ chunk 없음 → 빈 응답 반환")
            return {
                "question_type": "manual",
                "response": ""
            }

        for item in data["chunks"]:
            try:
                prompt = manual_prompt.format(
                    context=context_text,
                    machine=item["machine"],
                    status=item["status"],
                    manual_chunk=item["manual_chunk"],
                    window_days=data["window_days"] +1,  # +1일은 기준일 포함
                    chat_history=data.get("chat_history", ""),
                    query=data.get("question", "")
                )
                print(f"[DEBUG] 📤 Prompt 생성됨 \n{prompt}")
                res = llm.invoke(prompt)
                content = res.content.strip() if hasattr(res, "content") else str(res)
            except Exception as e:
                print(f"[ERROR] GPT 응답 실패 ({item['machine']}): {e}")
                content = f"❌ 응답 실패: {str(e)}"
            outputs.append(f"\U0001f6e0️ {item['machine']}\n{content}\n")

        return {
            "question_type": "manual",
            "response": "\n".join(outputs),
            "output": "\n".join(outputs)  # ✅ LangChain callback용 키 보완
        }


    manual_gpt_chain = RunnableLambda(generate_manual_summary)
    # 🔹 메모리 설정
    chat_histories = {}

    def get_session_history(session_id: str):
        if session_id not in chat_histories:
            chat_histories[session_id] = InMemoryChatMessageHistory()
        return chat_histories[session_id]

    # 체인 구성 (inject_history_chain 제거)
    manual_chain = (
        window_chain 
        | sql_generate_chain
        | faulty_machine_sql_chain 
        | manual_chunk_chain 
        | manual_gpt_chain
    )

    # RunnableWithMessageHistory로 감싸기
    manual_chain_with_memory = RunnableWithMessageHistory(
        manual_chain,
        get_session_history=get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history"
    )

    return manual_chain_with_memory


def summarize_faulty_machines(data: list[dict]) -> str:
    """
    오류 기계 데이터를 줄글 형태의 설명으로 변환합니다.

    Args:
        data (list[dict]): {"machine": str, "error_count": int} 형태의 리스트

    Returns:
        str: 줄글 형태의 요약 문장
    """
    if not data:
        return "최근 기간 동안 오류가 발생한 기계가 없습니다."

    lines = []
    for i, item in enumerate(data, 1):
        machine = item.get("machine", "이름 미상")
        count = item.get("error_count", 0)
        lines.append(f"{i}. {machine}에서 총 {count}회 오류 발생")
    
    return "\n".join(lines)

# 🔹 2. 고장 기계 탐지
def get_faulty_machines(d) -> list[str]:
    reference_date = d.get("reference_date", TODAY)
    window_days = d.get("window_days", 0)
    db_path = d['db_path']

    try:
        if isinstance(reference_date, str):
            reference_date = datetime.strptime(reference_date, "%Y-%m-%d")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 기준일을 문자열 YYYY-MM-DD 형식으로 변환
        ref_date = reference_date
        query = d.get("sql_code", "")
        print("[DEBUG] SQL 코드:", query)
        if query=="":
            query = '''
                    SELECT 
                        Machine,
                        COUNT(*) AS error_count
                    FROM logs
                    WHERE (
                        (
                            Year > :start_year OR
                            (Year = :start_year AND Month > :start_month) OR
                            (Year = :start_year AND Month = :start_month AND Day >= :start_day)
                        )
                        AND (
                            Year < :end_year OR
                            (Year = :end_year AND Month < :end_month) OR
                            (Year = :end_year AND Month = :end_month AND Day <= :end_day)
                        )
                    )
                    AND operation IN ('error')
                    GROUP BY Machine
                    HAVING COUNT(*) >= 2
                    ORDER BY error_count DESC
                    '''

            start_date = ref_date - timedelta(days=window_days)
            end_date = ref_date

            cursor.execute(query, {
                "start_year": start_date.year,
                "start_month": start_date.month,
                "start_day": start_date.day,
                "end_year": end_date.year,
                "end_month": end_date.month,
                "end_day": end_date.day
            })
            rows = cursor.fetchall()
            machines = [row[0] for row in rows if row[0] is not None]
            counts = [row[1] for row in rows if row[1] is not None]
            data = [{"machine": m, "error_count": c} for m, c in zip(machines, counts)]
        else:
            # SQL 코드가 주어진 경우 실행
            cursor.execute(query)
            rows = cursor.fetchall()
            error = cursor.fetchone()
            if isinstance(error, tuple):
                error = error[0]
            else:
                error = None
            if error:
                print(f"[ERROR] SQL 실행 오류: {error}")
                return {**d, "error": error}

            if not rows:
                print("[WARN] 고장 기계 없음")
                return {**d, "data": []}

            # 결과를 딕셔너리 형태로 변환
        data = [{"machine": row[0], "error_count": row[1]} for row in rows]
        print(f"[DEBUG] 🛠️ 고장 기계 탐지 (기준일: {ref_date}, {window_days}일): {rows}")
        conn.close()
        return {**d,'data':data}
    except Exception as e:
        print(f"[ERROR] DB 조회 실패: {e}")
        return []

