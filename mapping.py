# mapping.py
# 파이썬 <-> 한글 키워드/리터럴 중앙 맵핑

from __future__ import annotations

PY_TO_HAN = {
    # fliw / decl
    "def": "정의",
    "return": "반환",
    "if": "만약",
    "elif": "아니면",
    "else": "그외",
    "while": "동안",
    "for": "반복",
    "with": "함께",

    # opp
    "class": "클래스",

    # logical
    "and": "그리고",
    "or": "또는",
    "not": "아니다",
    "in": "안에",

    # literals
    "True": "참",
    "False": "거짓",
    "None": "없음",

    # loop control
    "break": "중단",
    "continue": "계속",
    "pass": "통과",

    # modules
    "import": "불러오기",
    "from": "꺼내기",
    "as": "별칭",

    # exceptions
    "try": "시도",
    "except": "예외",
    "finally": "마침",
    "raise": "던지기",
}

# "출력"은 키워드가 아니라 내장함수(print) 맵핑이지만,
# 버튼 변환(파이썬 <-> 한글)에서는 치환 대상이 될 수 있으니 중앙 맵핑에서 관리
BUILTIN_PY_TO_HAN = {
    "print": "출력",
    "range": "범위",
}

def build_reverse_map(d: dict[str, str]) -> dict[str, str]:
    # 역매핑 만들 때 충돌(동일 한글에 여러 파이썬)이 있으면 조기 발견
    rev: dict[str, str] = {}
    for k, v in d.items():
        if v in rev and rev[v] != k:
            raise ValueError(f"중복 한글 맵핑 충돌: {v!r} <- {rev[v]!r} 와 {k!r}")
        rev[v] = k
    return rev

HAN_TO_PY = build_reverse_map(PY_TO_HAN)
BUILTIN_HAN_TO_PY = build_reverse_map(BUILTIN_PY_TO_HAN)
# '본인'은 키워드가 아니라 식별자 별칭으로만 취급한다.
SPECIAL_IDENT_PY_TO_HAN = {
    'self' : '본인',
}
SPECIAL_IDENT_HAN_TO_PY = {
    '본인' : 'self',
}

# lexer에서키워드 판정에 쓸 한글 키워드 집합
HAN_KEYWORDS = set(PY_TO_HAN.values())

# try/except의 else는 파이썬 키워드(else)와 1:1 매핑이 아니라 문맥 의존이라,
# 한글 소스에서는 별도 키워드(성공)를 허용한다.
HAN_KEYWORDS.add("성공")

# 자주 쓰는 편의 상수 (기존 코드 호완용)
KW_DEF = PY_TO_HAN["def"]
KW_CLASS = PY_TO_HAN["class"]
