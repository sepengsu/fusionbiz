def classify_question_type(question: str) -> str:
    question = question.lower()
    count_keywords = ["몇 번", "얼마나", "몇 시", "횟수", "총", "개수", "비율", "시간"]
    if any(kw in question for kw in count_keywords):
        return "count"
    return "rag"
