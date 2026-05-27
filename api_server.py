# api_server.py
#
# 로컬 개발용 웹/API 서버.
# 외부 패키지 없이 표준 라이브러리 http.server만 사용한다.
#
# 주의: /api/run은 학습용 로컬 실행을 위해 사용자 코드를 exec로 실행한다.
# 배포 서버에서 사용자 코드를 실행할 때는 별도의 보안 샌드박스가 필요하다.

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from edu_api import compile_korean_to_python
from edu_runner import run_python_code


HOST = "localhost"
PORT = 8000
ROOT_DIR = Path(__file__).resolve().parent

STATIC_ROUTES = {
    "/web/": ROOT_DIR / "web" / "index.html",
    "/web/index.html": ROOT_DIR / "web" / "index.html",
    "/web/style.css": ROOT_DIR / "web" / "style.css",
    "/web/main.js": ROOT_DIR / "web" / "main.js",
    "/lessons/lessons.json": ROOT_DIR / "lessons" / "lessons.json",
}

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
}


class EduApiHandler(BaseHTTPRequestHandler):
    server_version = "EduApiServer/0.1"

    def do_GET(self) -> None:
        path = unquote(urlparse(self.path).path)
        file_path = STATIC_ROUTES.get(path)

        if file_path is None:
            self.send_json(
                {"ok": False, "error": "요청한 파일을 찾을 수 없습니다."},
                status=404,
            )
            return

        self.send_static_file(file_path)

    def do_POST(self) -> None:
        path = unquote(urlparse(self.path).path)

        if path == "/api/compile":
            self.handle_compile()
            return

        if path == "/api/run":
            self.handle_run()
            return

        self.send_json(
            {"ok": False, "error": "지원하지 않는 API 경로입니다."},
            status=404,
        )

    def handle_compile(self) -> None:
        body = self.read_json_body()
        if body is None:
            return

        source = body.get("source")
        if not isinstance(source, str):
            self.send_json(
                {"ok": False, "error": "source 값은 문자열이어야 합니다.", "error_type": "BadRequest"},
                status=400,
            )
            return

        result = compile_korean_to_python(source)
        if result.ok:
            self.send_json({"ok": True, "python_code": result.python_code})
            return

        self.send_json(
            {
                "ok": False,
                "error": result.error,
                "error_type": result.error_type,
            }
        )

    def handle_run(self) -> None:
        body = self.read_json_body()
        if body is None:
            return

        source = body.get("source")
        if not isinstance(source, str):
            self.send_json(
                {"ok": False, "error": "source 값은 문자열이어야 합니다.", "error_type": "BadRequest"},
                status=400,
            )
            return

        compile_result = compile_korean_to_python(source)
        if not compile_result.ok:
            self.send_json(
                {
                    "ok": False,
                    "error": compile_result.error,
                    "error_type": compile_result.error_type,
                }
            )
            return

        ok, output = run_python_code(compile_result.python_code)
        if ok:
            self.send_json(
                {
                    "ok": True,
                    "python_code": compile_result.python_code,
                    "output": output,
                }
            )
            return

        self.send_json(
            {
                "ok": False,
                "python_code": compile_result.python_code,
                "output": output,
                "error": output,
                "error_type": "RuntimeError",
            }
        )

    def read_json_body(self) -> dict[str, object] | None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(
                {"ok": False, "error": "Content-Length 값이 올바르지 않습니다.", "error_type": "BadRequest"},
                status=400,
            )
            return None

        raw_body = self.rfile.read(content_length)

        try:
            data = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(
                {"ok": False, "error": "요청 본문은 UTF-8 JSON이어야 합니다.", "error_type": "BadRequest"},
                status=400,
            )
            return None

        if not isinstance(data, dict):
            self.send_json(
                {"ok": False, "error": "JSON 본문은 객체여야 합니다.", "error_type": "BadRequest"},
                status=400,
            )
            return None

        return data

    def send_static_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self.send_json(
                {"ok": False, "error": "정적 파일을 찾을 수 없습니다."},
                status=404,
            )
            return

        content = file_path.read_bytes()
        content_type = MIME_TYPES.get(file_path.suffix, "application/octet-stream")

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data: dict[str, object], *, status: int = 200) -> None:
        content = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[api_server] {self.address_string()} - {format % args}")


def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), EduApiHandler)
    print(f"로컬 개발 서버를 시작합니다: http://{HOST}:{PORT}/web/")
    print("종료하려면 Ctrl + C를 누르세요.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        print("서버를 종료합니다.")
    finally:
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
