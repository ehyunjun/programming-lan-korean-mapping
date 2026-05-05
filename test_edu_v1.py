# test_edu_v1.py
#
# edu-v1 범위가 제대로 작동하는지 확인하는 간단 테스트.
# pytest 없이 그냥 python test_edu_v1.py 로 실행 가능하게 만든다.

from edu_api import compile_korean_to_python


def check_success(title: str, source: str) -> None:
    print(f"[성공 테스트] {title}")

    result = compile_korean_to_python(source)

    if not result.ok:
        print("실패 이유:")
        print(result.error)
        raise AssertionError(f"{title} 테스트 실패")

    print(result.python_code)
    print()


def check_fail(title: str, source: str) -> None:
    print(f"[실패 테스트] {title}")

    result = compile_korean_to_python(source)

    if result.ok:
        print("원래는 실패해야 하는데 성공했습니다.")
        print(result.python_code)
        raise AssertionError(f"{title} 테스트 실패")

    print(result.error)
    print()


def run_tests() -> None:
    check_success(
        "출력",
        """
출력("안녕")
"""
    )

    check_success(
        "변수 대입",
        """
이름 = "현준"
출력(이름)
"""
    )

    check_success(
        "조건문",
        """
점수 = 80

만약 점수 >= 60:
    출력("합격")
그외:
    출력("불합격")
"""
    )

    check_success(
        "반복문 범위",
        """
반복 i 안에 범위(1, 6):
    출력(i)
"""
    )

    check_success(
        "함수 정의",
        """
정의 인사하기(이름):
    출력(이름)

인사하기("현준")
"""
    )

    check_success(
        "함수 반환",
        """
정의 더하기(a, b):
    반환 a + b

결과 = 더하기(2, 3)
출력(결과)
"""
    )

    check_fail(
        "불러오기 막기",
        """
불러오기 os
"""
    )

    check_fail(
        "클래스 막기",
        """
클래스 사람:
    통과
"""
    )

    check_fail(
        "범위 아닌 반복 막기",
        """
숫자들 = [1, 2, 3]

반복 n 안에 숫자들:
    출력(n)
"""
    )

    check_fail(
        "함수 밖 반환 막기",
        """
반환 1
"""
    )

    check_fail(
        "반복문 밖 중단 막기",
        """
중단
"""
    )


if __name__ == "__main__":
    run_tests()
    print("모든 edu-v1 테스트가 끝났습니다.")