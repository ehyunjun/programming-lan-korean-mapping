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

# lexer에서키워드 판정에 쓸 한글 키워드 집합
HAN_KEYWORDS = set(PY_TO_HAN.values())

# 자주 쓰는 편의 상수 (기존 코드 호완용)
KW_DEF = PY_TO_HAN["def"]

BUILTIN_HAN_TO_PY: dict[str, str] = build_reverse_map(BUILTIN_PY_TO_HAN)