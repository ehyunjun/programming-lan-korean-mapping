# test_lesson.py
#
# lessons/lessons.json 데이터가 웹 IDE에서 사용할 수 있는 형태인지 검사한다.
# pytest 없이 그냥 py test_lesson.py 로 실행 가능하게 만든다.

import json
from pathlib import Path
from typing import Any

from edu_api import compile_korean_to_python


LESSONS_PATH = Path("lessons") / "lessons.json"
REQUIRED_FIELDS = [
    "id",
    "title",
    "concept",
    "level",
    "description",
    "goal",
    "starter_code",
    "answer_code",
    "hint",
    "korean_keywords",
    "python_keywords",
    "related_example",
]
QUIZ_REQUIRED_FIELDS = [
    "id",
    "title",
    "question",
    "starter_code",
    "answer_code",
    "hint",
]


class LessonTestError(Exception):
    """lesson 데이터 검사 중 문제가 있을 때 사용하는 에러."""
    pass


def load_lessons() -> list[dict[str, Any]]:
    """lessons.json 파일을 읽어서 lesson 목록을 반환한다."""
    if not LESSONS_PATH.exists():
        raise LessonTestError(f"파일을 찾을 수 없습니다: {LESSONS_PATH}")
    
    try:
        with LESSONS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise LessonTestError(
            f"JSON 형식이 올바르지 않습니다: {e}"
        ) from e

    if not isinstance(data, list):
        raise LessonTestError("lessons.json의 최상위 구조는 list여야 합니다.")
    
    if not data:
        raise LessonTestError("lesson 데이터가 비어 있습니다.")

    return data


def lesson_label(index: int, lesson: Any) -> str:
    """오류 메시지에서 lesson 위치를 쉽게 알아볼 수 있게 표시한다."""
    if isinstance(lesson, dict):
        lesson_id = lesson.get("id", "(id 없음)")
    else:
        lesson_id = "(id 없음)"
    return f"{index + 1}번째 lesson(id: {lesson_id})"


def quiz_label(index: int, lesson: dict[str, Any], quiz_index: int, quiz: Any) -> str:
    """오류 메시지에서 quiz 위치를 읽기 쉽게 표시한다."""
    if isinstance(quiz, dict):
        quiz_id = quiz.get("id", "(id 없음)")
    else:
        quiz_id = "(id 없음)"

    return f"{lesson_label(index, lesson)}, {quiz_index + 1}번째 quiz(id: {quiz_id})"


def validate_required_fields(index: int, lesson: Any) -> None:
    """lesson 하나에 필수 필드가 모두 있는지 검사한다."""
    label = lesson_label(index, lesson)

    if not isinstance(lesson, dict):
        raise LessonTestError(
            f"{label} 데이터가 올바르지 않습니다.\n"
            "해결: 각 lesson은 { ... } 형태의 JSON 객체여야 합니다."
        )

    missing_fields = [
        field for field in REQUIRED_FIELDS
        if field not in lesson
    ]

    if missing_fields:
        raise LessonTestError(
            f"{label}에 필수 필드가 빠져 있습니다.\n"
            f"빠진 필드: {', '.join(missing_fields)}\n"
            "해결: lessons.json에서 해당 lesson에 빠진 항목을 추가해주세요."
        )


def validate_related_example(index: int, lesson: dict[str, Any]) -> None:
    """related_example 경로가 examples 폴더의 실제 .han 파일인지 검사한다."""
    related_example = lesson.get("related_example")
    if not related_example:
        return

    label = lesson_label(index, lesson)

    if not isinstance(related_example, str):
        raise LessonTestError(
            f"{label}의 related_example 값이 문자열이 아닙니다.\n"
            "해결: 예를 들어 \"examples/01_print.han\"처럼 문자열로 적어주세요."
        )

    example_path = Path(related_example)

    if example_path.parts[:1] != ("examples",):
        raise LessonTestError(
            f"{label}의 related_example 경로가 examples 폴더를 가리키지 않습니다.\n"
            f"현재 값: {related_example}\n"
            "해결: examples/파일이름.han 형태로 적어주세요."
        )

    if example_path.suffix != ".han":
        raise LessonTestError(
            f"{label}의 related_example 파일 확장자가 .han이 아닙니다.\n"
            f"현재 값: {related_example}\n"
            "해결: 한글 코드 예제 파일은 .han 확장자를 사용해주세요."
        )

    if not example_path.exists():
        raise LessonTestError(
            f"{label}의 related_example 파일을 찾을 수 없습니다.\n"
            f"찾으려던 파일: {related_example}\n"
            "해결: examples 폴더에 해당 .han 파일을 만들거나 경로를 고쳐주세요."
        )


def validate_code_compiles(index: int, lesson: dict[str, Any], field_name: str) -> None:
    """starter_code 또는 answer_code가 한글 Python 코드로 컴파일되는지 검사한다."""
    code = lesson.get(field_name)
    label = lesson_label(index, lesson)

    if not isinstance(code, str):
        raise LessonTestError(
            f"{label}의 {field_name} 값이 문자열이 아닙니다.\n"
            "해결: 실행할 한글 코드를 따옴표로 감싼 문자열로 적어주세요."
        )

    if not code.strip():
        raise LessonTestError(
            f"{label}의 {field_name} 코드가 비어 있습니다.\n"
            "해결: 학습자가 실행해볼 수 있는 한글 코드를 넣어주세요."
        )

    result = compile_korean_to_python(code)
    if not result.ok:
        raise LessonTestError(
            f"{label}의 {field_name} 코드를 컴파일할 수 없습니다.\n"
            "해결: lessons.json의 코드를 확인하고, 한글 문법 오류를 고쳐주세요.\n\n"
            f"컴파일 오류:\n{result.error}"
        )


def validate_quiz_code_compiles(
    index: int,
    lesson: dict[str, Any],
    quiz_index: int,
    quiz: dict[str, Any],
    field_name: str,
    *,
    allow_empty: bool = False,
) -> None:
    """quiz의 starter_code 또는 answer_code가 한글 Python 코드로 컴파일되는지 검사한다."""
    code = quiz.get(field_name)
    label = quiz_label(index, lesson, quiz_index, quiz)

    if not isinstance(code, str):
        raise LessonTestError(
            f"{label}의 {field_name} 값이 문자열이 아닙니다.\n"
            "해결: 퀴즈 코드는 따옴표로 감싼 문자열로 적어주세요."
        )

    if not code.strip():
        if allow_empty:
            return

        raise LessonTestError(
            f"{label}의 {field_name} 코드가 비어 있습니다.\n"
            "해결: answer_code에는 실행해볼 수 있는 한글 코드를 넣어주세요."
        )

    result = compile_korean_to_python(code)
    if not result.ok:
        raise LessonTestError(
            f"{label}의 {field_name} 코드를 컴파일할 수 없습니다.\n"
            "해결: quizzes 안의 코드를 확인하고, edu-v1 문법 오류를 고쳐주세요.\n\n"
            f"컴파일 오류:\n{result.error}"
        )


def validate_quizzes(index: int, lesson: dict[str, Any]) -> None:
    """lesson에 연결된 quiz 목록이 웹 IDE에서 사용할 수 있는 형태인지 검사한다."""
    label = lesson_label(index, lesson)
    quizzes = lesson.get("quizzes")

    if not isinstance(quizzes, list):
        raise LessonTestError(
            f"{label}의 quizzes 값이 배열이 아닙니다.\n"
            "해결: quizzes는 [ ... ] 형태의 JSON 배열로 적어주세요."
        )

    if not quizzes:
        raise LessonTestError(
            f"{label}의 quizzes가 비어 있습니다.\n"
            "해결: 각 lesson마다 최소 1개 이상의 quiz를 추가해주세요."
        )

    for quiz_index, quiz in enumerate(quizzes):
        current_label = quiz_label(index, lesson, quiz_index, quiz)

        if not isinstance(quiz, dict):
            raise LessonTestError(
                f"{current_label} 데이터가 올바르지 않습니다.\n"
                "해결: 각 quiz는 { ... } 형태의 JSON 객체여야 합니다."
            )

        missing_fields = [
            field for field in QUIZ_REQUIRED_FIELDS
            if field not in quiz
        ]
        if missing_fields:
            raise LessonTestError(
                f"{current_label}의 필수 필드가 빠져 있습니다.\n"
                f"빠진 필드: {', '.join(missing_fields)}\n"
                "해결: id, title, question, starter_code, answer_code, hint를 모두 넣어주세요."
            )

        for field_name in ("id", "title", "question", "answer_code", "hint"):
            value = quiz.get(field_name)
            if not isinstance(value, str) or not value.strip():
                raise LessonTestError(
                    f"{current_label}의 {field_name} 값이 비어 있습니다.\n"
                    "해결: 입문자가 읽을 수 있는 내용을 문자열로 적어주세요."
                )

        validate_quiz_code_compiles(
            index,
            lesson,
            quiz_index,
            quiz,
            "starter_code",
            allow_empty=True,
        )
        validate_quiz_code_compiles(
            index,
            lesson,
            quiz_index,
            quiz,
            "answer_code",
        )


def validate_lesson(index: int, lesson: Any) -> None:
    """lesson 하나에 필요한 검사를 모두 수행한다."""
    validate_required_fields(index, lesson)
    validate_related_example(index, lesson)
    validate_code_compiles(index, lesson, "starter_code")
    validate_code_compiles(index, lesson, "answer_code")
    validate_quizzes(index, lesson)


def run_tests() -> None:
    """lessons.json 전체를 검사한다."""
    lessons = load_lessons()

    for index, lesson in enumerate(lessons):
        validate_lesson(index, lesson)
        print(f"[통과] {lesson_label(index, lesson)}")

    print()
    print(f"모든 lesson 검사가 끝났습니다. 총 {len(lessons)}개 lesson이 통과했습니다.")


if __name__ == "__main__":
    try:
        run_tests()
    except LessonTestError as e:
        print("[lesson 검사 실패]")
        print(e)
        raise SystemExit(1)
