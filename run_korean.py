# run_korean.py
#
# 한글 코드 파일을 읽어서:
# 1) 토큰화 (simple_lexer)
# 2) 파싱 (Parse)
# 3) 파이썬 코드 생성 (gen_program)
# 4) exec 로 실행
#
# 사용 예:
# python run_korean.py example.han

import argparse
import sys

from lexer_demo import simple_lexer
from parser_demo import Parser
from codegen_demo import gen_program
from ast_demo import print_program

def run_korean_source(
        source: str,
        *,
        show_tokens: bool = False,
        show_ast: bool = False,
        show_python: bool = False,
        execute: bool = True,
):
    """한글 소스 코드 한 덩어리를 실행하는 헬퍼 함수"""

    # 1) 렉싱
    tokens = simple_lexer(source)
    if show_tokens:
        print("=== 토큰들 ===")
        for t in tokens:
            print(" ", t)
        print()

    # 2) 파싱
    parser = Parser(tokens)
    program_ast = parser.parse_program()

    if show_ast:
        print("=== AST 구조 ===")
        print_program(program_ast)
        print()

    # 3) 파이썬 코드 생성
    py_code = gen_program(program_ast)
    if show_python:
        print("=== 생성된 파이썬 코드 ===")
        print(py_code)
        print()

    # 4) 실행
    env = {}
    if execute:
        exec(py_code, env, env)

    return py_code, env

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="한글 미니 언어 실행기 (lexer -> parser -> codegen -> exec)"
    )
    parser.add_argument(
        "filename",
        help="실행할 한글 소스 코드 파일 경로"
    )
    parser.add_argument(
        "--show-tokens",
        action="store_true",
        help="토큰 리스트를 출력합니다.",
    )
    parser.add_argument(
        "--show-ast",
        action="store_true",
        help="AST 구조를 출력합니다.",
    )
    parser.add_argument(
        "--show-python",
        action="store_true",
        help="생성된 파이썬 코드를 출력합니다.",
    )
    parser.add_argument(
        "--no-exec",
        action="store_true",
        help="코드를 생성만 하고 실행은 하지 않습니다.",
    )

    args = parser.parse_args(argv)

    # 파일 읽기 (UTF-8 가정)
    try:
        with open(args.filename, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"파일을 열 수 없습니다: {e}", file=sys.stderr)
        return 1
    
    # 실제 실행
    try:
        run_korean_source(
            source,
            show_tokens=args.show_tokens,
            show_ast=args.show_ast,
            show_python=args.show_python,
            execute=not args.no_exec,
        )
    except Exception as e:
        print("실행 중 에러 발생:", repr(e), file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())