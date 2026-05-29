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


def check_truncated_output(
    title: str,
    python_code: str,
    max_output_chars: int,
    expected_kept_text: str,
) -> None:
    """출력이 너무 길 때 앞부분만 보여주고 안내 문구를 붙이는지 확인한다."""
    print(f"[runner 출력 제한 테스트] {title}")

    ok, output = run_python_code(python_code, max_output_chars=max_output_chars)

    if not ok:
        print("실패 이유:")
        print(output)
        raise AssertionError(f"{title} 테스트 실패")

    print(output)
    print()

    if not output.startswith(expected_kept_text):
        raise AssertionError(
            f"{title} 테스트 실패: 출력 앞부분이 기대와 다릅니다.\n"
            f"기대 시작: {expected_kept_text!r}\n"
            f"실제 출력: {output!r}"
        )

    if output.count("가") != len(expected_kept_text):
        raise AssertionError(
            f"{title} 테스트 실패: 제한보다 많은 출력 본문이 남아 있습니다.\n"
            f"실제 출력: {output!r}"
        )

    if "출력이 너무 길어서 일부만 보여줬어요" not in output:
        raise AssertionError(
            f"{title} 테스트 실패: 출력 제한 안내 문구를 찾지 못했습니다."
        )


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


def check_runtime_error_contains(
    title: str,
    python_code: str,
    expected_texts: list[str],
    timeout_seconds: float | None = None,
) -> None:
    """실행 실패 메시지에 필요한 문구들이 모두 들어 있는지 확인한다."""
    print(f"[runner 오류 테스트] {title}")

    if timeout_seconds is None:
        ok, output = run_python_code(python_code)
    else:
        ok, output = run_python_code(python_code, timeout_seconds=timeout_seconds)

    if ok:
        print("원래는 실패해야 하는데 성공했습니다.")
        print(output)
        raise AssertionError(f"{title} 테스트 실패")

    print(output)
    print()

    for expected_text in expected_texts:
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

    check_success(
        "문자열 안의 input 단어는 실행 허용",
        'print("input은 입력 함수입니다")',
        "input은 입력 함수입니다",
    )

    check_truncated_output(
        "긴 출력 일부만 반환",
        'print("가" * 100)',
        max_output_chars=20,
        expected_kept_text="가" * 20,
    )

    check_runtime_error(
        "실행 중 오류 메시지",
        "print(없는변수)",
        "문제: 실행 중 오류가 발생했어요.",
    )

    check_runtime_error_contains(
        "웹 input 실행 차단",
        'name = input("이름: ")\nprint(name)',
        [
            "입력()",
            "웹 실행",
            "변수에 값을 직접 넣어보세요",
        ],
    )

    check_runtime_error_contains(
        "무한 반복 timeout",
        "while True:\n    pass",
        [
            "실행 시간이 너무 오래",
            "반복문",
            "조건",
            "거짓",
        ],
        timeout_seconds=0.5,
    )


if __name__ == "__main__":
    run_tests()
    print("모든 edu_runner 테스트가 끝났습니다.")
