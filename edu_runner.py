# edu_runner.py
#
# 변환된 Python 코드 문자열을 실행하고 결과를 반환하는 실행 헬퍼.
# edu_api.py는 변환 전용으로 유지하고, 실행 책임은 이 파일에서 맡는다.

import ast
import multiprocessing
import queue
import re
from contextlib import redirect_stdout


DEFAULT_TIMEOUT_SECONDS = 3.0
MAX_OUTPUT_CHARS = 4000


def run_python_code(
    python_code: str,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    max_output_chars: int = MAX_OUTPUT_CHARS,
) -> tuple[bool, str]:
    """
    변환된 Python 코드를 실행하고 출력 결과를 문자열로 반환한다.

    성공하면:
        (True, 실행 출력)

    실패하면:
        (False, 오류 메시지)
    """
    try:
        if contains_input_call(python_code):
            return False, make_input_not_supported_message()

        return run_python_code_in_subprocess(
            python_code,
            timeout_seconds,
            max_output_chars,
        )

    except Exception as e:
        return False, make_runtime_error_message(e)


def run_python_code_in_subprocess(
    python_code: str,
    timeout_seconds: float,
    max_output_chars: int,
) -> tuple[bool, str]:
    """제한 시간을 두고 별도 프로세스에서 Python 코드를 실행한다."""
    result_queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=run_python_code_worker,
        args=(python_code, max_output_chars, result_queue),
    )

    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join()
        return False, make_timeout_error_message()

    try:
        return result_queue.get_nowait()
    except queue.Empty:
        return False, make_runtime_error_message(
            RuntimeError("실행 결과를 받을 수 없습니다.")
        )


def run_python_code_worker(
    python_code: str,
    max_output_chars: int,
    result_queue: multiprocessing.Queue,
) -> None:
    """별도 프로세스에서 실행 결과를 queue로 전달한다."""
    result_queue.put(execute_python_code(python_code, max_output_chars))


def execute_python_code(python_code: str, max_output_chars: int) -> tuple[bool, str]:
    """변환된 Python 코드를 실제로 실행한다."""
    output = LimitedOutput(max_output_chars)

    try:
        env = {}

        with redirect_stdout(output):
            exec(python_code, env, env)

        return make_success_output(output)

    except Exception as e:
        return False, make_runtime_error_message(e)


class LimitedOutput:
    """stdout 내용을 최대 글자 수까지만 저장하는 파일 비슷한 객체."""

    def __init__(self, max_chars: int) -> None:
        self.max_chars = max(0, max_chars)
        self.parts: list[str] = []
        self.char_count = 0
        self.truncated = False

    def write(self, text: str) -> int:
        if not isinstance(text, str):
            text = str(text)

        text_len = len(text)
        remaining = self.max_chars - self.char_count

        if remaining > 0:
            kept = text[:remaining]
            self.parts.append(kept)
            self.char_count += len(kept)

        if text_len > max(0, remaining):
            self.truncated = True

        return text_len

    def flush(self) -> None:
        return None

    def getvalue(self) -> str:
        return "".join(self.parts)


def make_success_output(output: LimitedOutput) -> tuple[bool, str]:
    """실행 성공 시 출력 제한 상태를 반영해 결과를 만든다."""
    result = output.getvalue()

    if output.truncated:
        shown_output = result.rstrip()
        if shown_output:
            return True, f"{shown_output}\n\n{make_output_truncated_message()}"

        return True, make_output_truncated_message()

    if result.strip():
        return True, result.rstrip()

    return True, "(출력 없음)"


def contains_input_call(python_code: str) -> bool:
    """Python AST에서 직접 input(...) 호출이 있는지 확인한다."""
    tree = ast.parse(python_code)

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "input"
        ):
            return True

    return False


def make_input_not_supported_message() -> str:
    """웹 실행에서 input() 사용을 막을 때 보여줄 안내 메시지."""
    return (
        "문제: 웹 실행에서는 입력()을 아직 사용할 수 없어요.\n"
        "\n"
        "이유: 브라우저 실행 결과 창에서는 터미널처럼 키보드 입력을 받을 수 없어요.\n"
        "Python의 input()은 실행 중에 사용자가 값을 입력할 때까지 기다리기 때문에, "
        "웹 실행이 멈춘 것처럼 보일 수 있어요.\n"
        "\n"
        "해결: 입력() 대신 변수에 값을 직접 넣어보세요.\n"
        "\n"
        "예시:\n"
        "이름 = \"현준\"\n"
        "출력(이름)"
    )


def make_timeout_error_message() -> str:
    """실행 시간이 너무 오래 걸릴 때 보여줄 안내 메시지."""
    return (
        "문제: 코드 실행 시간이 너무 오래 걸려서 멈췄어요.\n"
        "\n"
        "이유: 반복문이 끝나지 않거나, 너무 많은 일을 하고 있을 수 있어요.\n"
        "\n"
        "해결: 반복문 조건이 언젠가 거짓이 되는지 확인해보세요.\n"
        "\n"
        "예시:\n"
        "i = 1\n"
        "동안 i <= 5:\n"
        "    출력(i)\n"
        "    i = i + 1"
    )


def make_output_truncated_message() -> str:
    """출력이 너무 길 때 보여줄 안내 메시지."""
    return (
        "출력이 너무 길어서 일부만 보여줬어요.\n"
        "반복 횟수를 줄이거나 출력하는 내용을 줄여보세요."
    )


def make_runtime_error_message(error: Exception) -> str:
    """실행 중 발생한 오류를 입문자가 읽기 쉬운 문장으로 바꾼다."""
    if isinstance(error, NameError):
        return make_name_error_message(error)

    if isinstance(error, ZeroDivisionError):
        return make_zero_division_error_message(error)

    if isinstance(error, TypeError):
        return make_type_error_message(error)

    return (
        "문제: 실행 중 오류가 발생했어요.\n"
        "\n"
        f"이유: {type(error).__name__}: {error}\n"
        "\n"
        "해결: 변수 이름이 맞는지, 문자열과 숫자를 잘못 더하지 않았는지,"
        "함수 이름을 잘못 적지 않았는지 확인해보세요.\n"
        "\n"
        f"원래 오류: {type(error).__name__}: {error}"
    )


def make_name_error_message(error: NameError) -> str:
    """정의되지 않은 이름을 사용할 때 보여줄 안내 메시지."""
    missing_name = extract_name_from_name_error(error)
    if missing_name:
        reason = (
            f"컴퓨터가 '{missing_name}'이라는 이름을 찾지 못했어요. "
            "변수를 사용하기 전에 먼저 값을 넣어야 해요."
        )
    else:
        reason = (
            "컴퓨터가 사용한 이름을 찾지 못했어요. "
            "변수를 사용하기 전에 먼저 값을 넣어야 해요."
        )

    return (
        "문제: 이름을 찾지 못했어요.\n"
        "\n"
        f"이유: {reason}\n"
        "\n"
        "해결: 변수 이름에 오타가 없는지 확인하고, 사용하기 전에 값을 넣어보세요.\n"
        "\n"
        "예시:\n"
        "이름 = \"현준\"\n"
        "출력(이름)\n"
        "\n"
        f"원래 오류: NameError: {error}"
    )


def extract_name_from_name_error(error: NameError) -> str:
    """NameError 메시지에서 찾지 못한 이름을 추출한다."""
    match = re.search(r"name '(.+?)' is not defined", str(error))
    if match:
        return match.group(1)

    return ""


def make_zero_division_error_message(error: ZeroDivisionError) -> str:
    """0으로 나누었을 때 보여줄 안내 메시지."""
    return (
        "문제: 숫자를 0으로 나눌 수 없어요.\n"
        "\n"
        "이유: 나누기에서 오른쪽 값이 0이면 계산할 수 없어요.\n"
        "\n"
        "해결: 나누는 값이 0이 아닌지 확인해보세요.\n"
        "\n"
        "예시:\n"
        "점수 = 10 / 2\n"
        "출력(점수)\n"
        "\n"
        f"원래 오류: ZeroDivisionError: {error}"
    )


def make_type_error_message(error: TypeError) -> str:
    """서로 맞지 않는 값의 종류를 함께 쓸 때 보여줄 안내 메시지."""
    return (
        "문제: 서로 맞지 않는 종류의 값을 함께 사용했어요.\n"
        "\n"
        "이유: 문자열과 숫자를 바로 더하려고 했을 수 있어요.\n"
        "\n"
        "해결: 숫자는 따로 출력하거나, 필요할 때 문자열로 바꿔서 사용해보세요.\n"
        "\n"
        "예시:\n"
        "나이 = 26\n"
        "출력(\"나이:\")\n"
        "출력(나이)\n"
        "\n"
        f"원래 오류: TypeError: {error}"
    )
