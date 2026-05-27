# test_edu_runner.py
#
# edu_runner.py의 Python 코드 실행 헬퍼를 검사한다.
# pytest 없이 그냥 py test_edu_runner.py 로 실행 가능하게 만든다.

from edu_runner import run_python_code


def check_success(title: str, python_code: str, expected_output: str) -> None:
    """정상 실행 결과가 기대한 출력과 같은지 확인한다."""
    print(f"[runner 성공 테스트] {title}")

    ok, output = run_python_code(python_code)

    if not ok:
        print("실패 이유:")
        print(output)
        raise AssertionError(f"{title} 테스트 실패")

    if output != expected_output:
        raise AssertionError(
            f"{title} 테스트 실패: 출력이 다릅니다.\n"
            f"기대: {expected_output!r}\n"
            f"실제: {output!r}"
        )

    print(output)
    print()


def check_runtime_error(title: str, python_code: str, expected_text: str) -> None:
    """실행 중 오류가 사용자용 오류 메시지로 반환되는지 확인한다."""
    print(f"[runner 오류 테스트] {title}")

    ok, output = run_python_code(python_code)

    if ok:
        print("원래는 실패해야 하는데 성공했습니다.")
        print(output)
        raise AssertionError(f"{title} 테스트 실패")

    print(output)
    print()

    if expected_text not in output:
        raise AssertionError(
            f"{title} 테스트 실패: {expected_text!r} 문구를 찾지 못했습니다."
        )


def run_tests() -> None:
    check_success(
        "출력 결과 반환",
        "print('안녕')",
        "안녕",
    )

    check_success(
        "출력 없는 코드",
        "x = 1 + 2",
        "(출력 없음)",
    )

    check_runtime_error(
        "실행 중 오류 메시지",
        "print(없는변수)",
        "문제: 실행 중 오류가 발생했어요.",
    )


if __name__ == "__main__":
    run_tests()
    print("모든 edu_runner 테스트가 끝났습니다.")
