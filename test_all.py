# test_all.py
#
# 프로젝트의 주요 테스트 파일을 순서대로 실행한다.
# pytest 없이 그냥 py test_all.py 로 실행 가능하게 만든다.

import os
import subprocess
import sys


TEST_COMMANDS = [
    ("lesson 데이터 검사", ["py", "test_lesson.py"]),
    ("입문자 친화 오류 메시지 검사", ["py", "test_edu_error.py"]),
    ("examples 예제 검사", ["py", "test_examples.py"]),
]


def configure_output() -> None:
    """통합 테스트 출력의 한글 인코딩을 안정적으로 맞춘다."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def run_test(title: str, command: list[str]) -> None:
    """테스트 하나를 실행하고 실패하면 즉시 종료한다."""
    print("=" * 50, flush=True)
    print(f"[테스트 실행] {title}", flush=True)
    print(f"명령: {' '.join(command)}", flush=True)
    print("=" * 50, flush=True)

    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")

    result = subprocess.run(command, env=env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    print(flush=True)


def main() -> int:
    configure_output()

    for title, command in TEST_COMMANDS:
        run_test(title, command)

    print("모든 테스트가 통과했습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
