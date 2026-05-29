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
    "한글 코드는 Python 코드로, Python 코드는 한글 코드로 바꿔볼 수 있습니다.",
    "코드 입력",
    "변환 결과",
    "실행 결과",
    "자동 변환하기",
    "실행하기",
    "예제 코드 다시 불러오기",
    "코드 미리보기",
    "codePreview",
    "1단계: 왼쪽에서 학습할 예제를 고릅니다.",
    "2단계: 한글 코드나 Python 코드를 읽거나 직접 고쳐봅니다.",
    "3단계: 자동 변환하기 또는 실행하기 버튼을 눌러 결과를 확인합니다.",
    "실행하기는 현재 한글 코드 기준으로 동작합니다.",
]

REQUIRED_MAIN_JS_TEXTS = [
    'fetch("../lessons/lessons.json")',
    "async function loadLessons()",
    "lesson 데이터를 불러오지 못했습니다. 로컬 서버로 실행했는지 확인해주세요.",
    "renderLessons();",
    "selectLesson(lessons[0].id);",
    "id:",
    "title:",
    "description:",
    "starter_code:",
    "answer_code:",
    "koreanCode.value = lesson.starter_code",
    "lessonDescription.textContent = lesson.description",
    'postSourceToApi("/api/translate", source)',
    'postSourceToApi("/api/run", source)',
    'method: "POST"',
    "JSON.stringify({ source })",
    "API 서버에 연결할 수 없습니다. py api_server.py로 서버를 실행했는지 확인해주세요.",
    "한글 코드를 먼저 입력해주세요.",
    "translated_code",
    "direction",
    "한글 코드 → Python 코드",
    "Python 코드 → 한글 코드",
    "keydown",
    "Tab",
    "shiftKey",
    "updateCodePreview",
    "escapeHtml",
    "highlightCode",
    "codePreview",
    "resetLessonButton",
    "먼저 lesson을 선택해주세요.",
    "새 lesson을 불러왔어요. 자동 변환하기를 누르면 변환 결과가 여기에 보여요.",
    "실행하기를 누르면 결과가 여기에 보여요.",
    "예제 코드를 다시 불러왔어요. 자동 변환하기 또는 실행하기로 다시 확인해보세요.",
    "아직 변환 API가 연결되지 않았습니다.",
    "아직 실행 API가 연결되지 않았습니다.",
]

REQUIRED_STYLE_TEXTS = [
    "code-preview-panel",
    "code-preview-box",
    "token-keyword",
    "token-function",
    "token-string",
    "token-number",
    "token-comment",
    "--code-bg: #111827",
    "--code-panel",
    "--code-border",
    "caret-color",
    "::placeholder",
    "output-box.notice",
    "white-space: pre-wrap",
    "line-height",
    "monospace",
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
    style_css = read_text(STYLE_PATH)
    main_js = read_text(MAIN_JS_PATH)

    check_index_links(index_html)

    for text in REQUIRED_INDEX_TEXTS:
        check_contains(index_html, text, file_label="web/index.html")

    for text in REQUIRED_MAIN_JS_TEXTS:
        check_contains(main_js, text, file_label="web/main.js")

    for text in REQUIRED_STYLE_TEXTS:
        check_contains(style_css, text, file_label="web/style.css")

    print()
    print("모든 web 정적 파일 검사가 끝났습니다.")


if __name__ == "__main__":
    try:
        run_tests()
    except WebStaticTestError as e:
        print("[web 정적 파일 검사 실패]")
        print(e)
        raise SystemExit(1)
