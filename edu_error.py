# edu_error.py
#
# edu-v1 에서 발생하는 오류를 입문자가 이해하기 쉬운 문장으로 바꿔주는 파일.
# Python/Parser 오류를 그대로 보여주면 처음 배우는 사람에게 어렵기 때문에,
# 문제 원인, 해결 방법, 예시를 함께 보여준다.

BLOCK_KEYWORDS = ("만약", "동안", "반복", "정의", "아니면", "그외")


def make_error_message(
    title: str,
    reason: str,
    solution: str,
    example: str = "",
    example_label: str = "예시:",
) -> str:
    """오류 메시지 형식을 한 곳에서 통일한다."""
    parts = [
        f"문제: {title}",
        "",
        f"이유: {reason}",
        "",
        f"해결: {solution}",
    ]

    if example:
        parts.extend(["", example_label, example])

    return "\n".join(parts)

def friendly_error_message(error: Exception, source: str = "") -> str:
    """
    예외 객체를 받아서 입문자용 오류 메시지로 변환한다.
    edu_api.py에서 except 블록마다 이 함수를 사용한다.
    """
    if isinstance(error, IndentationError):
        return friendly_indentation_error(error)
    
    if isinstance(error, SyntaxError):
        return friendly_syntax_error(error, source)
    
    return make_error_message(
        title="알 수 없는 오류가 발생했어요.",
        reason=str(error),
        solution="코드를 조금씩 나누어 실행하면서 어느 부분에서 문제가 생기는지 확인해보세요.",
    )

def friendly_indentation_error(error: IndentationError) -> str:
    """들여쓰기 오류를 입문자용 메시지로 바꾼다."""
    return make_error_message(
        title="들여쓰기가 맞지 않아요.",
        reason=(
            "파이썬은 중괄호({}) 대신 들여쓰기로 코드 블록을 구분해요."
            "같은 블록에 있는 코드는 같은 칸만큼 들여써야 합니다."
        ),
        solution="조건문, 반복문, 함수 안쪽 코드는 보통 스페이스 4칸으로 맞춰주세요.",
        example=(
            "만약 점수 >=60:\n"
            "    출력(\"합격\")"
        ),
    )

def friendly_syntax_error(error: SyntaxError, source: str = "") -> str:
    """SyntaxError 메시지를 보고 자주 나오는 실수를 친절하게 안내한다."""
    message = str(error)

    # parser_demo.py의 expect()는 기대한 값보다 타입을 먼저 검사한다.
    # 그래서 ':' 누락이나 ')' 누락이 모두 "SYMBOL 가 와야..."처럼 보일 수 있다.
    # 입문자용 메시지에서는 원본 코드를 함께 보고 흔한 실수를 먼저 안내한다.
    source_hint = detect_source_level_error(source)
    if source_hint is not None:
        return source_hint
    
    # parser_demo.py의 edu-v1 제한 메시지는 이미 의미가 분명하므로,
    # 문법 오류라는 말보다 학습 범위 안내로 보여준다.
    if "현재 교육용 1차 버전에서는" in message:
        return make_error_message(
            title="아직 edu-v1에서 배우지 않는 문법이에요.",
            reason=message,
            solution="지금 단계에서는 출력, 변수, 조건문, 반복문, 함수부터 연습해볼게요.",
        )
    
    if "INDENT 가 와야" in message:
        return make_indent_needed_message()
    
    if "':' 가 와야" in message:
        return make_colon_missing_message()
    
    if "')' 가 와야" in message:
        return make_right_paren_missing_message()
    
    if "']' 가 와야" in message:
        return make_right_bracket_missing_message()
    
    if "숫자/문자열/이름/괄호/리스트로 시작하는 표현식" in message:
        return make_error_message(
            title="값이나 식이 와야 하는 자리가 비어있어요.",
            reason="대입, 출력, 조건문 안에는 숫자, 문자열, 변수 이름 같은 값이 필요해요",
            solution="비어 있는 부분에서 사용할 값이나 변수 이름을 적어주세요.",
            example=(
                "이름 = \"홍길동\"\n"
                "출력(이름)"
            ),
        )

    if "지원하지 않는 문장 시작 토큰" in message:
        return make_error_message(
            title="문장의 시작을 이해하지 못했어요.",
            reason="edu-v1에서 아직 지원하지 않는 문법이거나, 문장 앞부분에 오타가 있을 수 있어요.",
            solution="출력, 입력, 만약, 반복, 동안, 정의 같은 edu-v1 문법으로 시작했는지 확인해주세요.",
            example=(
                "출력(\"안녕\")\n"
                "\n"
                "만약 점수 >= 60:\n"
                "    출력(\"합격\")"
            ),
        )
    
    return make_error_message(
        title="문법 오류가 있어요.",
        reason=message,
        solution="괄호, 따옴표, 콜론(:), 들여쓰기를 먼저 확인해보세요.",
    )

def detect_source_level_error(source: str) -> str | None:
    """원본 코드만 봐도 알 수 있는 흔한 실수를 먼저 찾아낸다."""
    if has_unclosed_paren(source):
        return make_right_paren_missing_message()
    
    if has_unclosed_bracket(source):
        return make_right_bracket_missing_message()
    
    if has_block_line_without_colon(source):
        return make_colon_missing_message()
    
    return None

def has_block_line_without_colon(source: str) -> bool:
    """만약/동안/반복/정의 같은 블록 문장 끝에 ':'가 빠졌는지 확인한다."""
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith(BLOCK_KEYWORDS) and not has_trailing_colon_outside_strings(line):
            return True

    return False

def has_trailing_colon_outside_strings(line: str) -> bool:
    """문자열 밖의 마지막 의미 있는 문자가 ':'인지 확인한다."""
    last_char = ""
    quote: str | None = None
    escaped = False

    for ch in line:
        if quote is not None:
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == quote:
                quote = None
            continue

        if ch in ('"', "'"):
            quote = ch
            continue

        if ch == "#":
            break

        if not ch.isspace():
            last_char = ch

    return last_char == ":"
    
def has_unclosed_paren(source: str) -> bool:
    """문자열 밖의 괄호 개수를 간단히 확인한다."""
    return count_outside_strings(source, "(") > count_outside_strings(source, ")")

def has_unclosed_bracket(source: str) -> bool:
    """문자열 밖의 괄호 개수를 간단히 확인한다."""
    return count_outside_strings(source, "[") > count_outside_strings(source, "]")

def count_outside_strings(source: str, target: str) -> int:
    """문자열 내부를 제외하고 특정 문자의 개수를 센다."""
    count = 0
    quote: str | None = None
    escaped = False

    for ch in source:
        if quote is not None:
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == quote:
                quote = None
            continue

        if ch in ('"', "'"):
            quote = ch
            continue

        if ch == target:
            count += 1

    return count
    
def make_colon_missing_message() -> str:
    return make_error_message(
        title="콜론(:)이 빠졌어요.",
        reason="조건문, 반복문, 함수처럼 아래에 코드 블록이 이어지는 문장은 끝에 ':'를 붙여야 해요.",
        solution="만약, 동안, 반복, 정의 문장 끝에 ':'가 있는지 확인해주세요.",
        example=(
            "만약 점수 >= 60:\n"
            "    출력(\"합격\")"
        ),
    )

def make_indent_needed_message() -> str:
    return make_error_message(
        title="본문 들여쓰기가 필요해요.",
        reason="':' 다음 줄에는 실제로 실행할 코드를 한 단계 들여써야 해요.",
        solution="아래처럼 안쪽 코드를 4칸 들여써주세요.",
        example=(
            "반복 i 안에 범위(1, 6):\n"
            "    출력(i)"
        ),
        example_label="올바른 예:",
    )

def make_right_paren_missing_message() -> str:
    return make_error_message(
        title="닫는 괄호')'가 빠졌어요.",
        reason="여는 괄호 '('를 사용했다면 마지막에 닫는 괄호 ')'도 필요해요.",
        solution="출력(...) 입력(...) 범위(...) 처럼 괄호가 제대로 닫혔는지 확인해주세요.",
        example="출력(\"안녕\")",
    )

def make_right_bracket_missing_message() -> str:
    return make_error_message(
        title="닫는 대괄호 ']'가 빠졌어요.",
        reason="리스트를 만들 때 '['로 시작했다면 ']'로 닫아야 해요.",
        example="숫자들 = [1, 2, 3]",
    )
