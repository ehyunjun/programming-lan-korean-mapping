# tokens.py
# 렉서/파서 공통으로 쓰는 "토큰 규격" (심볼/연산자 집합)

from __future__ import annotations

# 렉서가 SYMBOL로 인식할 단일 문자들
SYMBOLS: list[str] = [
    "(", ")", "[", "]",
    ":", ",", ".",
    "=", "+", "-", "*", "/",
    "<", ">", "!",
]

ADD_OPS: set[str] = {"+", "-"}
MUL_OPS: set[str] = {"*", "/"}