# edu_api.py
#
# 웹 IDE에서 사용할 교육용 변환 API.
# 한글 코드를 받아서 edu-v1 범위인지 검사한 뒤,
# Python 코드 문자열로 변환한다.
#
# 중요한 점:
# 여기서는 exec로 실행하지 않는다.
# 실행은 나중에 웹 브라우저 쪽에서 따로 처리한다.

from dataclasses import dataclass
from typing import Any

from lexer_demo import simple_lexer
from parser_demo import Parser
from codegen_demo import gen_program
from edu_scope import EduScopeError, validate_edu_v1

@dataclass
class CompileResult:
    ok: bool
    python_code: str =""
    error: str = ""
    error_type: str = ""
    tokens: list[tuple[str, str]] | None = None
    ast: Any | None = None


def compile_korean_to_python(source: str) -> CompileResult:
    """
    한글 코드를 Python 코드로 변환한다.
    
    성공하면:
        CompileResult(ok=True, python_code="...")
        
    실패하면:
        CompileResult(ok=False, error="...")
    """

    try:
        # 1. 한글 코드 -> 토큰
        tokens = simple_lexer(source)

        # 2. 토큰 -> AST
        parser = Parser(tokens)
        program_ast = parser.parse_program()

        # 3. edu-v1 학습 범위 검사
        validate_edu_v1(program_ast)

        # 4. AST -> Python 코드
        python_code = gen_program(program_ast)

        return CompileResult(
            ok=True, python_code=python_code, tokens=tokens, ast=program_ast,
        )
    
    except EduScopeError as e:
        return CompileResult(
            ok=False, error=str(e), error_type="EduScopeError",
        )
    
    except SyntaxError as e:
        return CompileResult(
            ok=False, error=f"문법 오류가 있어요: {e}", error_type="SyntaxError",
        )
    
    except IndentationError as e:
        return CompileResult(
            ok=False, error=f"들여쓰기 오류가 있어요: {e}", error_type="IndentationError",
        )
    
    except Exception as e:
        return CompileResult(
            ok=False, error=f"알 수 없는 오류가 발생했어요: {e}", error_type=type(e).__name__,
        )
    

if __name__ == "__main__":
    sample = """
반복 i 안에 범위 (1, 6):
    출력(i)
"""
    result = compile_korean_to_python(sample)

    if result.ok:
        print("변환 성공!")
        print()
        print(result.python_code)
    else:
        print("변환 실패!")
        print()
        print(result.error)
