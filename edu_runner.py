# edu_runner.py
#
# 변환된 Python 코드 문자열을 실행하고 결과를 반환하는 실행 헬퍼.
# edu_api.py는 변환 전용으로 유지하고, 실행 책임은 이 파일에서 맡는다.

import io
from contextlib import redirect_stdout


def run_python_code(python_code: str) -> tuple[bool, str]:
    """
    변환된 Python 코드를 실행하고 출력 결과를 문자열로 반환한다.

    성공하면:
        (True, 실행 출력)

    실패하면:
        (False, 오류 메시지)
    """
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
