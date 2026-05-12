# test_edu_error.py
#
# 입문자 친화 오류 메시지가 잘 나오는지 확인하는 테스트.
# pytest 없이 그냥 py test_edu_error.py 로 실행 가능하게 만든다.

from edu_api import compile_korean_to_python

def check_error_contatins(title: str, source: str, expectest_test: str) -> None:
    print(f"[오류 메시지 테스트] {title}")

    result = compile_korean_to_python(source)

    if result.ok:
        print("원래는 실패해야 하는데 성공했습니다.")
        print(result.python_code)
        raise AssertionError(f"{title} 테스트 실패")
    
    print(result.error)
    print()

    if expectest_test not in result.error:
        raise AssertionError(
            f"{title} 테스트 실패: {expectest_test!r} 문구를 찾지 못했습니다."
        )
    
    def run_tests() -> None:
        check_error_contatins(
            "조건문 콜론 누락",
            """
    점수 = 80
    만약 점수 >= 60
        출력("합격")
    """,
            "콜론(:)이 빠졌어요.",
        )

        check_error_contatins(
            "본문 들여쓰기 누락",
            """
    만약 점수 >= 60:
    출력("합격")
    """,
            "본문 들여쓰기가 필요해요.",
        )

        check_error_contatins(
            "닫는 괄호 누락",
            """
    출력("안녕"
    """,
            "닫는 괄호')'가 빠졌어요.",
        )

        check_error_contatins(
            "교육용 범위 밖 문법",
            """
    불러오기 os
    """,
            "아직 edu-v1에서 배우지 않는 문법이에요.",
        )

    if __name__ == "__main__":
        run_tests()
        print("모든 입문자 친화 오류 메시지 테스트가 끝났습니다.")
