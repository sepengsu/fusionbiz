# rag_engine/chain/full_chain.py

from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory

from rag_engine.chain.utils.history import InMemoryChatHistory
from rag_engine.chain.classifier.classifier import classify_question_type
from rag_engine.chain.manual_chain import get_manual_chain
from rag_engine.chain.sql_chain import get_sql_chain
from rag_engine.chain.summary_chain import summary_chain
from rag_engine.chain.utils.history import format_chat_history


def build_full_chain(llm, config):
    print("[INFO] ✅ full_chain 구성 시작")

    # ✅ 1. session_id 기반 메모리 함수
    def get_memory(session_id: str) -> InMemoryChatHistory:
        print(f"[INFO] ✅ get_memory 진입 (session_id: {session_id})")
        return InMemoryChatHistory(session_id=session_id)

    # ✅ 2. 체인 구성
    sql_chain = get_sql_chain(llm, config)
    manual_chain = get_manual_chain(llm, config)
    print("[INFO] ✅ 체인 로딩 완료")

    # ✅ 3. 라우팅 함수 (출력 형식 보장)
    def route_and_run_chain(data: dict):
        raw_input = data["question"]
        session_id = data.get("session_id", "default")
        memory = get_memory(session_id)
        
        # 최근 메시지 가져오기
        chat_history = memory.messages
        formatted_history = format_chat_history(chat_history)  # 아까 만든 함수

        # 실제 사용자 질문 추출
        if isinstance(raw_input, list):  # LangChain Message일 경우
            question = raw_input[-1].content
        else:
            question = raw_input

        qtype = classify_question_type(question, mode=config.get("classification_mode", "embedding"))

        data.update({
            "question": question,               # 추출한 질문 (str)
            "chat_history": formatted_history   # 문자열로 변환된 기록
        })

        if qtype == "sql":
            output = sql_chain.invoke(data)
        elif qtype == "manual":
            output = manual_chain.invoke(data)
        else:
            output = summary_chain.invoke(data)

        # 정리된 후처리
        if isinstance(output, str):
            output = {"response": output}
        elif isinstance(output, dict):
            if "output" in output and "response" not in output:
                output = {"response": output["output"]}
        else:
            output = {"response": str(output)}

        return output
        

    # ✅ 4. 메모리 연동 체인 구성
    base_chain = RunnableLambda(route_and_run_chain)

    full_chain = RunnableWithMessageHistory(
        runnable=base_chain,
        get_session_history=get_memory,
        input_messages_key="question"
    )

    return full_chain
