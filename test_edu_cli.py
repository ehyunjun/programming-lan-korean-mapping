# test_edu_cli.py
#
# edu_cli.py가 실제 CLI로 한글 코드 파일을 변환/실행하는지 검사한다.
# pytest 없이 그냥 py test_edu_cli.py 로 실행 가능하게 만든다.

import os
import subprocess
import sys


def run_edu_cli() -> subprocess.CompletedProcess[str]:
    """현재 Python 실행 파일로 edu_cli.py를 실행한다."""
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")

    return subprocess.run(
        [sys.executable, "edu_cli.py", "example.han"],
        text=True,
        capture_output=True,
        encoding="utf-8",
        env=env,
    )


def assert_contains(output: str, expected_text: str) -> None:
    """출력에 기대 문구가 있는지 확인한다."""
    if expected_text not in output:
        raise AssertionError(
            f"CLI 출력에서 {expected_text!r} 문구를 찾지 못했습니다.\n\n"
            f"실제 출력:\n{output}"
        )


def run_tests() -> None:
    print("[edu_cli 테스트] example.han 실행")

    result = run_edu_cli()
    output = result.stdout

    if result.returncode != 0:
        raise AssertionError(
            "edu_cli.py 실행이 실패했습니다.\n"
            f"exit code: {result.returncode}\n\n"
            f"stdout:\n{result.stdout}\n\n"
            f"stderr:\n{result.stderr}"
        )

    assert_contains(output, "[한글 코드]")
    assert_contains(output, "[변환된 Python 코드]")
    assert_contains(output, "[실행 결과]")
    assert_contains(output, "큼")

    print(output.rstrip())
    print()
    print("모든 edu_cli 테스트가 끝났습니다.")


if __name__ == "__main__":
    run_tests()
