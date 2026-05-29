# test_api_server.py
#
# api_server.py의 주요 로컬 API 동작을 검사한다.
# pytest 없이 그냥 py test_api_server.py 로 실행 가능하게 만든다.

import json
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from api_server import EduApiHandler


HOST = "127.0.0.1"
PORT = 8765
BASE_URL = f"http://{HOST}:{PORT}"


class ApiServerTestError(Exception):
    """API 서버 검사 중 문제가 있을 때 사용하는 에러."""
    pass


class TestHTTPServer(ThreadingHTTPServer):
    """테스트 재실행 시 포트가 바로 재사용되도록 한다."""

    allow_reuse_address = True


def start_server() -> TestHTTPServer:
    """테스트용 API 서버를 별도 스레드에서 시작한다."""
    try:
        server = TestHTTPServer((HOST, PORT), EduApiHandler)
    except OSError as e:
        raise ApiServerTestError(
            f"테스트용 포트 {PORT}를 사용할 수 없습니다.\n"
            "해결: 같은 포트를 쓰는 프로그램을 종료한 뒤 다시 실행해주세요.\n"
            f"이유: {e}"
        ) from e

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    wait_for_server()
    return server


def wait_for_server() -> None:
    """서버가 요청을 받을 준비가 될 때까지 잠깐 재시도한다."""
    last_error: Exception | None = None

    for _ in range(20):
        try:
            get_text("/web/")
            return
        except Exception as e:
            last_error = e
            time.sleep(0.1)

    raise ApiServerTestError(
        "테스트용 API 서버가 제때 시작되지 않았습니다.\n"
        f"마지막 오류: {last_error}"
    )


def get_response(path: str) -> tuple[int, str]:
    """GET 요청을 보내고 status code와 응답 본문을 반환한다."""
    url = BASE_URL + path

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            body = response.read().decode("utf-8")
            return response.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return e.code, body
    except urllib.error.URLError as e:
        raise ApiServerTestError(
            f"GET {path} 요청에 실패했습니다.\n"
            f"이유: {e}"
        ) from e


def get_text(path: str) -> str:
    """GET 요청이 200으로 성공하는지 확인하고 본문을 반환한다."""
    status, body = get_response(path)
    if status != 200:
        raise ApiServerTestError(
            f"GET {path} 응답 상태가 200이 아닙니다.\n"
            f"실제 상태: {status}\n"
            f"응답 본문:\n{body}"
        )

    return body


def post_json(path: str, payload: dict[str, object]) -> tuple[int, dict[str, object]]:
    """JSON POST 요청을 보내고 status code와 JSON 응답을 반환한다."""
    url = BASE_URL + path
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return post_raw(path, body)


def post_raw(path: str, body: bytes) -> tuple[int, dict[str, object]]:
    """원시 POST 본문을 보내고 status code와 JSON 응답을 반환한다."""
    url = BASE_URL + path
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            raw_response = response.read().decode("utf-8")
            status = response.status
    except urllib.error.HTTPError as e:
        raw_response = e.read().decode("utf-8")
        status = e.code
    except urllib.error.URLError as e:
        raise ApiServerTestError(
            f"POST {path} 요청에 실패했습니다.\n"
            f"이유: {e}"
        ) from e

    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError as e:
        raise ApiServerTestError(
            f"POST {path} 응답을 JSON으로 읽을 수 없습니다.\n"
            f"응답 본문:\n{raw_response}"
        ) from e

    if not isinstance(data, dict):
        raise ApiServerTestError(
            f"POST {path} 응답 JSON이 객체가 아닙니다.\n"
            f"응답 JSON:\n{data}"
        )

    return status, data


def check_web_index() -> None:
    body = get_text("/web/")
    if "한글 Python 학습 도구" not in body:
        raise ApiServerTestError(
            "GET /web/ 응답에서 제목 문구를 찾을 수 없습니다.\n"
            "기대 문구: 한글 Python 학습 도구"
        )

    print("[통과] GET /web/ 응답 확인")


def check_lessons_json() -> None:
    body = get_text("/lessons/lessons.json")

    try:
        lessons = json.loads(body)
    except json.JSONDecodeError as e:
        raise ApiServerTestError(
            "GET /lessons/lessons.json 응답을 JSON으로 읽을 수 없습니다."
        ) from e

    if not isinstance(lessons, list) or not lessons:
        raise ApiServerTestError(
            "lessons/lessons.json 응답이 비어 있지 않은 JSON 배열이어야 합니다."
        )

    print("[통과] GET /lessons/lessons.json 응답 확인")


def check_compile_success() -> None:
    status, data = post_json("/api/compile", {"source": '출력("안녕")'})
    if status != 200 or data.get("ok") is not True or not data.get("python_code"):
        raise ApiServerTestError(
            "POST /api/compile 성공 응답이 기대와 다릅니다.\n"
            f"status: {status}\n"
            f"응답 JSON:\n{data}"
        )

    print("[통과] POST /api/compile 성공 응답 확인")


def check_run_success() -> None:
    status, data = post_json("/api/run", {"source": '출력("안녕")'})
    output = data.get("output")
    if (
        status != 200
        or data.get("ok") is not True
        or not data.get("python_code")
        or not isinstance(output, str)
        or "안녕" not in output
    ):
        raise ApiServerTestError(
            "POST /api/run 성공 응답이 기대와 다릅니다.\n"
            f"status: {status}\n"
            f"응답 JSON:\n{data}"
        )

    print("[통과] POST /api/run 성공 응답 확인")


def check_compile_error() -> None:
    source = '만약 1 > 0\n    출력("안녕")'
    status, data = post_json("/api/compile", {"source": source})
    error = data.get("error")
    if status != 200 or data.get("ok") is not False or not isinstance(error, str):
        raise ApiServerTestError(
            "POST /api/compile 오류 응답이 기대와 다릅니다.\n"
            f"status: {status}\n"
            f"응답 JSON:\n{data}"
        )

    print("[통과] POST /api/compile 오류 응답 확인")


def check_translate_korean_to_python() -> None:
    status, data = post_json("/api/translate", {"source": '출력("안녕")'})
    translated_code = data.get("translated_code")
    if (
        status != 200
        or data.get("ok") is not True
        or data.get("direction") != "ko_to_py"
        or not isinstance(translated_code, str)
        or "print(" not in translated_code
        or "안녕" not in translated_code
        or data.get("error") is not None
    ):
        raise ApiServerTestError(
            "POST /api/translate 한글 → Python 응답이 기대와 다릅니다.\n"
            f"status: {status}\n"
            f"응답 JSON:\n{data}"
        )

    print("[통과] POST /api/translate 한글 → Python 응답 확인")


def check_translate_python_to_korean() -> None:
    status, data = post_json("/api/translate", {"source": 'print("안녕")'})
    translated_code = data.get("translated_code")
    if (
        status != 200
        or data.get("ok") is not True
        or data.get("direction") != "py_to_ko"
        or not isinstance(translated_code, str)
        or '출력("안녕")' not in translated_code
        or data.get("error") is not None
    ):
        raise ApiServerTestError(
            "POST /api/translate Python → 한글 응답이 기대와 다릅니다.\n"
            f"status: {status}\n"
            f"응답 JSON:\n{data}"
        )

    print("[통과] POST /api/translate Python → 한글 응답 확인")


def check_translate_python_with_korean_variable() -> None:
    source = '이름 = "현준"\nprint(이름)'
    status, data = post_json("/api/translate", {"source": source})
    translated_code = data.get("translated_code")
    if (
        status != 200
        or data.get("ok") is not True
        or data.get("direction") != "py_to_ko"
        or not isinstance(translated_code, str)
        or '이름 = "현준"' not in translated_code
        or "출력(이름)" not in translated_code
    ):
        raise ApiServerTestError(
            "POST /api/translate 한글 변수명 Python 응답이 기대와 다릅니다.\n"
            f"status: {status}\n"
            f"응답 JSON:\n{data}"
        )

    print("[통과] POST /api/translate 한글 변수명 Python 응답 확인")


def check_translate_missing_source_error() -> None:
    status, data = post_json("/api/translate", {})
    if (
        status != 400
        or data.get("ok") is not False
        or data.get("direction") is not None
        or data.get("translated_code") != ""
        or data.get("error_type") != "BadRequest"
    ):
        raise ApiServerTestError(
            "POST /api/translate source 누락 응답이 기대와 다릅니다.\n"
            f"status: {status}\n"
            f"응답 JSON:\n{data}"
        )

    print("[통과] POST /api/translate source 누락 응답 확인")


def check_translate_invalid_json_error() -> None:
    status, data = post_raw("/api/translate", b"{")
    if (
        status != 400
        or data.get("ok") is not False
        or data.get("error_type") != "BadRequest"
    ):
        raise ApiServerTestError(
            "POST /api/translate 잘못된 JSON 응답이 기대와 다릅니다.\n"
            f"status: {status}\n"
            f"응답 JSON:\n{data}"
        )

    print("[통과] POST /api/translate 잘못된 JSON 응답 확인")


def run_tests() -> None:
    server = start_server()
    try:
        check_web_index()
        check_lessons_json()
        check_compile_success()
        check_run_success()
        check_compile_error()
        check_translate_korean_to_python()
        check_translate_python_to_korean()
        check_translate_python_with_korean_variable()
        check_translate_missing_source_error()
        check_translate_invalid_json_error()
    finally:
        server.shutdown()
        server.server_close()

    print()
    print("모든 API 서버 검사가 끝났습니다.")


if __name__ == "__main__":
    try:
        run_tests()
    except ApiServerTestError as e:
        print("[API 서버 검사 실패]")
        print(e)
        raise SystemExit(1)
