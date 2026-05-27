# test_web_static.py
#
# web 폴더의 정적 파일 구조를 검사한다.
# pytest 없이 그냥 py test_web_static.py 로 실행 가능하게 만든다.

from pathlib import Path


WEB_DIR = Path("web")
INDEX_PATH = WEB_DIR / "index.html"
STYLE_PATH = WEB_DIR / "style.css"
MAIN_JS_PATH = WEB_DIR / "main.js"

REQUIRED_INDEX_TEXTS = [
    "한글 Python 학습 도구",
    "lesson 목록",
    "lessonDescription",
    "한글 코드",
    "변환된 Python 코드",
    "실행 결과",
    "변환하기",
    "실행하기",
]

REQUIRED_MAIN_JS_TEXTS = [
    "id:",
    "title:",
    "description:",
    "starter_code:",
    "answer_code:",
    "koreanCode.value = lesson.starter_code",
    "lessonDescription.textContent = lesson.description",
    "아직 변환 API가 연결되지 않았습니다.",
    "아직 실행 API가 연결되지 않았습니다.",
]


class WebStaticTestError(Exception):
    """web 정적 파일 검사 중 문제가 있을 때 사용하는 에러."""
    pass


def read_text(path: Path) -> str:
    """파일을 UTF-8로 읽는다."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        raise WebStaticTestError(
            f"{path} 파일을 읽을 수 없습니다.\n"
            f"이유: {e}"
        ) from e


def check_file_exists(path: Path) -> None:
    """필수 파일이 존재하는지 검사한다."""
    if not path.exists():
        raise WebStaticTestError(
            f"필수 파일이 없습니다: {path}\n"
            "해결: web 폴더 안에 필요한 정적 파일을 만들어주세요."
        )

    if not path.is_file():
        raise WebStaticTestError(
            f"필수 경로가 파일이 아닙니다: {path}\n"
            "해결: 해당 경로가 일반 파일인지 확인해주세요."
        )

    print(f"[통과] 파일 존재: {path}")


def check_contains(content: str, text: str, *, file_label: str) -> None:
    """문구가 파일 내용에 포함되어 있는지 검사한다."""
    if text not in content:
        raise WebStaticTestError(
            f"{file_label}에서 필요한 문구를 찾을 수 없습니다.\n"
            f"빠진 문구: {text}"
        )

    print(f"[통과] {file_label} 문구 확인: {text}")


def check_index_links(index_html: str) -> None:
    """index.html이 CSS와 JS 파일을 연결하는지 검사한다."""
    check_contains(index_html, 'href="style.css"', file_label="web/index.html")
    check_contains(index_html, 'src="main.js"', file_label="web/index.html")


def run_tests() -> None:
    for path in (INDEX_PATH, STYLE_PATH, MAIN_JS_PATH):
        check_file_exists(path)

    index_html = read_text(INDEX_PATH)
    main_js = read_text(MAIN_JS_PATH)

    check_index_links(index_html)

    for text in REQUIRED_INDEX_TEXTS:
        check_contains(index_html, text, file_label="web/index.html")

    for text in REQUIRED_MAIN_JS_TEXTS:
        check_contains(main_js, text, file_label="web/main.js")

    print()
    print("모든 web 정적 파일 검사가 끝났습니다.")


if __name__ == "__main__":
    try:
        run_tests()
    except WebStaticTestError as e:
        print("[web 정적 파일 검사 실패]")
        print(e)
        raise SystemExit(1)
