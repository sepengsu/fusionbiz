import re

# 한글 표현 매핑
DAY_ALIAS = {
    "하루": 0,
    "이틀": 1,
    "사흘": 2,
    "나흘": 3,
    "닷새": 4,
    "엿새": 5,
    "이레": 7-1,
    "일주일": 7-1,
    "한 주": 7-1,
    "한 달": 30-1,
    "한달": 30-1,
    "두 달": 60-1,
    "두달": 60-1,
    "세 달": 90-1,
    "세달": 90-1,
}

def extract_window_days(question: str) -> int:
    # 1. "최근" 앞에 있는 문장 제거
    if "최근" in question:
        question = question.split("최근", 1)[1]

        # 2. 숫자 기반 추출 (ex. 5일, 10일간)
        if match := re.search(r"(\d+)\s*(일|일간|동안)", question):
            return int(match.group(1))

        # 3. 개월 수 추출 (ex. 2개월, 3 개월 동안)
        if match := re.search(r"(\d+)\s*개월", question):
            return int(match.group(1)) * 30

        # 4. 한글 표현 매핑 (하루, 한 달 등)
        for word, value in DAY_ALIAS.items():
            if word in question:
                return value

        # 5. "최근" 있었지만 구체적인 숫자나 단어 없으면 기본값
        return 0 # 기본값은 0일로 설정, 필요시 변경 가능

    else:
        # 6. "최근"이라는 단어 자체가 없을 경우 기본값
        return 0 # 기본값은 1일로 설정, 필요시 변경 가능
