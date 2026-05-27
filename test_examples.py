# test_examples.py
#
# examples 폴더의 모든 .han 예제가 의도대로 컴파일되는지 검사한다.
# pytest 없이 그냥 py test_examples.py 로 실행 가능하게 만든다.

from pathlib import Path

from edu_api import compile_korean_to_python


EXAMPLES_DIR = Path("examples")
ERROR_EXAMPLE_PREFIX = "99_error_"


class ExampleTestError(Exception):
    """example 데이터 검사 중 문제가 있을 때 사용하는 에러."""
    pass


def load_example_files() -> list[Path]:
    """examples 폴더 안의 .han 파일 목록을 반환한다."""
    if not EXAMPLES_DIR.exists():
        raise ExampleTestError(
            f"examples 폴더를 찾을 수 없습니다: {EXAMPLES_DIR}\n"
            "해결: 프로젝트 루트에 examples 폴더가 있는지 확인해주세요."
        )

    if not EXAMPLES_DIR.is_dir():
        raise ExampleTestError(
            f"examples 경로가 폴더가 아닙니다: {EXAMPLES_DIR}\n"
            "해결: examples는 .han 파일을 담는 폴더여야 합니다."
        )

    files = sorted(EXAMPLES_DIR.glob("*.han"))
    if not files:
        raise ExampleTestError(
            "examples 폴더 안에 .han 예제 파일이 없습니다.\n"
            "해결: 실행해볼 한글 코드 예제를 examples 폴더에 추가해주세요."
        )

    return files


def read_example_file(path: Path) -> str:
    """예제 파일을 UTF-8로 읽는다."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise ExampleTestError(
            f"{path} 파일을 UTF-8로 읽을 수 없습니다.\n"
            "해결: 예제 파일의 인코딩을 UTF-8로 저장해주세요."
        ) from e
    except OSError as e:
        raise ExampleTestError(
            f"{path} 파일을 읽는 중 문제가 생겼습니다.\n"
            f"이유: {e}"
        ) from e


def is_error_example(path: Path) -> bool:
    """파일명이 99_error_로 시작하는 예제인지 확인한다."""
    return path.name.startswith(ERROR_EXAMPLE_PREFIX)


def validate_normal_example(path: Path) -> None:
    """일반 예제 파일 하나가 컴파일되는지 검사한다."""
    source = read_example_file(path)
    result = compile_korean_to_python(source)

    if not result.ok:
        raise ExampleTestError(
            f"{path} 예제를 컴파일할 수 없습니다.\n"
            "해결: 예제 코드의 한글 문법을 확인해주세요.\n\n"
            f"컴파일 오류:\n{result.error}"
        )


def validate_error_example(path: Path) -> None:
    """오류 예제 파일 하나가 예상대로 컴파일 실패하는지 검사한다."""
    source = read_example_file(path)
    result = compile_korean_to_python(source)

    if result.ok:
        raise ExampleTestError(
            f"{path} 오류 예제가 예상과 다르게 컴파일에 성공했습니다.\n"
            "해결: 99_error_로 시작하는 예제는 학습용 오류 예제이므로, "
            "컴파일에 실패하는 코드인지 확인해주세요.\n\n"
            f"생성된 Python 코드:\n{result.python_code}"
        )


def run_tests() -> None:
    """examples 폴더의 모든 .han 파일을 검사한다."""
    files = load_example_files()
    failures: list[str] = []
    normal_pass_count = 0
    error_pass_count = 0

    for path in files:
        try:
            if is_error_example(path):
                validate_error_example(path)
            else:
                validate_normal_example(path)
        except ExampleTestError as e:
            failures.append(str(e))
            print(f"[실패] {path.name}")
            print(e)
            print()
            continue

        if is_error_example(path):
            error_pass_count += 1
            print(f"[예상된 오류 통과] {path.name}")
        else:
            normal_pass_count += 1
            print(f"[통과] {path.name}")

    if failures:
        raise ExampleTestError(
            f"총 {len(files)}개 예제 중 {len(failures)}개 예제가 실패했습니다."
        )

    print()
    print(
        "모든 example 검사가 끝났습니다. "
        f"정상 예제 {normal_pass_count}개, "
        f"오류 예제 {error_pass_count}개가 통과했습니다."
    )


if __name__ == "__main__":
    try:
        run_tests()
    except ExampleTestError as e:
        print("[example 검사 실패]")
        print(e)
        raise SystemExit(1)
