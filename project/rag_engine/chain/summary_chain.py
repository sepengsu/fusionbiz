from langchain_core.runnables import RunnableLambda

# 🔹 요약 기능 placeholder 체인
summary_chain = RunnableLambda(lambda d: {
    "question_type": "summary",
    "response": "요약 기능은 준비 중입니다."
})
