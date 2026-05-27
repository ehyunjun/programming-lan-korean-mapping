# edu_cli.py
#
# edu-v1 학습용 CLI 실행기.
# 한글 코드 파일을 읽어서
# 1) 원본 한글 코드 출력
# 2) edu_api.py를 통해 Python 코드로 변환
# 3) 변환된 Python 코드 출력
# 4) 실행 결과 출력
#
# 사용 예:
# py edu_cli.py example.han
# py edu_cli.py example.han --no-exec

import argparse
import sys

from edu_api import compile_korean_to_python
from edu_runner import run_python_code


SECTION_LINE = "=" * 50

def print_section(title: str, content: str) -> None:
    """CLI 화면에서 구역을 보기 좋게 출력한다."""
    print(SECTION_LINE)
    print(title)
    print(SECTION_LINE)

    if content.strip():
        print(content.rstrip())
    else:
        print("(내용 없음)")
    
    print()


def read_source_file(filename: str) -> str:
    """UTF-8 기준으로 한글 코드 파일을 읽는다."""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()
    

def run_cli(filename: str, *, execute: bool = True) -> int:
    """파일 하나를 읽어서 변환 결과와 실행 결과를 출력한다."""
    try:
        source = read_source_file(filename)
    except OSError as e:
        print(f"파일을 열 수 없습니다: {e}", file=sys.stderr)
        return 1
    
    print_section("[한글 코드]", source)

    result = compile_korean_to_python(source)
    if not result.ok:
        print_section("[오류 메시지]", result.error)
        return 1
    
    print_section("[변환된 Python 코드]", result.python_code)

    if not execute:
        print("실행은 건너뛰었습니다. (--no-exec 옵션 사용)")
        return 0
    
    ok, output = run_python_code(result.python_code)
    if not ok:
        print_section("[실행 오류]", output)
        return 1
    
    print_section("[실행 결과]", output)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="edu-v1 한글 파이썬 학습용 CLI"
    )
    parser.add_argument(
        "filename",
        help="실행할 한글 코드 파일 경로",
    )
    parser.add_argument(
        "--no-exec",
        action="store_true",
        help="Python 코드로 변환만 하고 실행은 하지 않습니다."
    )

    args = parser.parse_args(argv)

    return run_cli(
        args.filename,
        execute=not args.no_exec,
    )


if __name__ == "__main__":
    raise SystemExit(main())
