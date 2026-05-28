# edu_runner.py
#
# 변환된 Python 코드 문자열을 실행하고 결과를 반환하는 실행 헬퍼.
# edu_api.py는 변환 전용으로 유지하고, 실행 책임은 이 파일에서 맡는다.

import ast
import io
import multiprocessing
import queue
from contextlib import redirect_stdout


DEFAULT_TIMEOUT_SECONDS = 3.0


def run_python_code(
    python_code: str,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
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

        return run_python_code_in_subprocess(python_code, timeout_seconds)

    except Exception as e:
        return False, make_runtime_error_message(e)


def run_python_code_in_subprocess(
    python_code: str,
    timeout_seconds: float,
) -> tuple[bool, str]:
    """제한 시간을 두고 별도 프로세스에서 Python 코드를 실행한다."""
    result_queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=run_python_code_worker,
        args=(python_code, result_queue),
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
    result_queue: multiprocessing.Queue,
) -> None:
    """별도 프로세스에서 실행 결과를 queue로 전달한다."""
    result_queue.put(execute_python_code(python_code))


def execute_python_code(python_code: str) -> tuple[bool, str]:
    """변환된 Python 코드를 실제로 실행한다."""
    output = io.StringIO()

    try:
        env = {}

        with redirect_stdout(output):
            exec(python_code, env, env)

        result = output.getvalue()
        if result.strip():
            return True, result.rstrip()

        return True, "(출력 없음)"

    except Exception as e:
        return False, make_runtime_error_message(e)


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


def make_runtime_error_message(error: Exception) -> str:
    """실행 중 발생한 오류를 입문자가 읽기 쉬운 문장으로 바꾼다."""
    return (
        "문제: 실행 중 오류가 발생했어요.\n"
        "\n"
        f"이유: {type(error).__name__}: {error}\n"
        "\n"
        "해결: 변수 이름이 맞는지, 문자열과 숫자를 잘못 더하지 않았는지,"
        "함수 이름을 잘못 적지 않았는지 확인해보세요."
    )
