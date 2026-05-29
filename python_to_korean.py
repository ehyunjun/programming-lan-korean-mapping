# python_to_korean.py
#
# Python 코드를 edu-v1 한글 코드로 바꾸는 1차 변환기.
# 전체 Python 문법 변환기가 아니라, 입문자용 기본 문법만 안전하게 치환한다.

from __future__ import annotations

from dataclasses import dataclass
import io
import tokenize

from mapping import BUILTIN_PY_TO_HAN, PY_TO_HAN


KEYWORD_TRANSLATIONS = {
    key: PY_TO_HAN[key]
    for key in (
        "if",
        "elif",
        "else",
        "while",
        "for",
        "in",
        "def",
        "return",
        "True",
        "False",
        "None",
    )
}

CALL_TRANSLATIONS = {
    key: BUILTIN_PY_TO_HAN[key]
    for key in (
        "print",
        "input",
        "range",
    )
}

IGNORED_LOOKAHEAD_TOKEN_TYPES = {
    tokenize.ENCODING,
    tokenize.NL,
    tokenize.NEWLINE,
    tokenize.INDENT,
    tokenize.DEDENT,
    tokenize.ENDMARKER,
}


@dataclass
class PythonToKoreanResult:
    ok: bool
    korean_code: str = ""
    error: str = ""
    error_type: str = ""


def translate_python_to_korean(source: str) -> PythonToKoreanResult:
    """
    Python 코드를 edu-v1 한글 코드로 변환한다.

    성공하면:
        PythonToKoreanResult(ok=True, korean_code="...")

    실패하면:
        PythonToKoreanResult(ok=False, error="...")
    """
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
        replacements = collect_replacements(tokens)
        korean_code = apply_replacements(source, replacements)
        return PythonToKoreanResult(ok=True, korean_code=korean_code)
    except (IndentationError, tokenize.TokenError) as e:
        return PythonToKoreanResult(
            ok=False,
            error=f"Python 코드를 읽는 중 문제가 생겼습니다: {e}",
            error_type=type(e).__name__,
        )
    except Exception as e:
        return PythonToKoreanResult(
            ok=False,
            error=f"Python → 한글 변환 중 문제가 생겼습니다: {e}",
            error_type=type(e).__name__,
        )


def collect_replacements(
    tokens: list[tokenize.TokenInfo],
) -> dict[int, list[tuple[int, int, str]]]:
    """토큰 목록에서 줄별 치환 위치를 모은다."""
    replacements: dict[int, list[tuple[int, int, str]]] = {}

    for index, token in enumerate(tokens):
        if token.type != tokenize.NAME:
            continue

        replacement = get_token_replacement(tokens, index)
        if replacement is None:
            continue

        line_no, start_col = token.start
        _, end_col = token.end
        replacements.setdefault(line_no, []).append((start_col, end_col, replacement))

    return replacements


def get_token_replacement(
    tokens: list[tokenize.TokenInfo],
    index: int,
) -> str | None:
    """토큰 하나가 한글로 바뀌어야 하는지 판단한다."""
    token_text = tokens[index].string

    if token_text in KEYWORD_TRANSLATIONS:
        return KEYWORD_TRANSLATIONS[token_text]

    if token_text in CALL_TRANSLATIONS and next_meaningful_token_text(tokens, index) == "(":
        return CALL_TRANSLATIONS[token_text]

    return None


def next_meaningful_token_text(
    tokens: list[tokenize.TokenInfo],
    index: int,
) -> str:
    """현재 토큰 뒤의 의미 있는 토큰 문자열을 찾는다."""
    for token in tokens[index + 1:]:
        if token.type in IGNORED_LOOKAHEAD_TOKEN_TYPES:
            continue
        return token.string

    return ""


def apply_replacements(
    source: str,
    replacements: dict[int, list[tuple[int, int, str]]],
) -> str:
    """원본 줄의 토큰 위치에 치환 문자열을 적용한다."""
    lines = source.splitlines(keepends=True)

    if not lines:
        return source

    for line_no, line_replacements in replacements.items():
        if line_no < 1 or line_no > len(lines):
            continue

        line = lines[line_no - 1]
        for start_col, end_col, replacement in sorted(line_replacements, reverse=True):
            line = line[:start_col] + replacement + line[end_col:]
        lines[line_no - 1] = line

    return "".join(lines)
