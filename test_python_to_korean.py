# test_python_to_korean.py
#
# Python → edu-v1 한글 코드 변환을 검사한다.
# pytest 없이 그냥 py test_python_to_korean.py 로 실행 가능하게 만든다.

from textwrap import dedent

from python_to_korean import translate_python_to_korean


class PythonToKoreanTestError(Exception):
    """Python → 한글 변환 검사 중 문제가 있을 때 사용하는 에러."""
    pass


def normalize_code(code: str) -> str:
    """테스트 코드 들여쓰기와 앞뒤 개행을 정리한다."""
    return dedent(code).strip("\n")


def check_translation(title: str, source: str, expected: str) -> None:
    """Python 코드가 기대한 한글 코드로 변환되는지 검사한다."""
    print(f"[Python → 한글 변환 테스트] {title}")

    source = normalize_code(source)
    expected = normalize_code(expected)
    result = translate_python_to_korean(source)

    if not result.ok:
        raise PythonToKoreanTestError(
            f"{title} 테스트 실패: 변환에 실패했습니다.\n"
            f"입력:\n{source}\n\n"
            f"오류:\n{result.error}"
        )

    if result.korean_code != expected:
        raise PythonToKoreanTestError(
            f"{title} 테스트 실패: 변환 결과가 다릅니다.\n"
            f"입력:\n{source}\n\n"
            f"기대 결과:\n{expected}\n\n"
            f"실제 결과:\n{result.korean_code}"
        )

    print(result.korean_code)
    print()


def run_tests() -> None:
    check_translation(
        "print 호출 변환",
        """
        print("안녕")
        """,
        """
        출력("안녕")
        """,
    )

    check_translation(
        "input과 print 호출 변환",
        """
        name = input("이름: ")
        print(name)
        """,
        """
        name = 입력("이름: ")
        출력(name)
        """,
    )

    check_translation(
        "if else 변환",
        """
        score = 80
        if score >= 60:
            print("합격")
        else:
            print("불합격")
        """,
        """
        score = 80
        만약 score >= 60:
            출력("합격")
        그외:
            출력("불합격")
        """,
    )

    check_translation(
        "for range 변환",
        """
        for i in range(1, 6):
            print(i)
        """,
        """
        반복 i 안에 범위(1, 6):
            출력(i)
        """,
    )

    check_translation(
        "def return 변환",
        """
        def add(a, b):
            return a + b
        """,
        """
        정의 add(a, b):
            반환 a + b
        """,
    )

    check_translation(
        "문자열 안 단어 유지",
        """
        print("if와 print는 문자열 안에서는 바뀌면 안 됩니다")
        """,
        """
        출력("if와 print는 문자열 안에서는 바뀌면 안 됩니다")
        """,
    )

    check_translation(
        "True False None 변환",
        """
        done = True
        empty = None
        print(done)
        print(empty)
        """,
        """
        done = 참
        empty = 없음
        출력(done)
        출력(empty)
        """,
    )


if __name__ == "__main__":
    try:
        run_tests()
    except PythonToKoreanTestError as e:
        print("[Python → 한글 변환 검사 실패]")
        print(e)
        raise SystemExit(1)

    print("모든 Python → 한글 변환 테스트가 끝났습니다.")
