# edu_scope.py
#
# edu-v1에서 허용할 문법과 막을 문법을 검사하는 파일.
# 기존 parser/codegen은 넓은 문법을 처리할 수 있지만,
# 입문자 학습용 웹 IDE에서는 일부 문법만 통과시킨다.

from ast_demo import (
    Program, Stmt, Expr, Assign, ChainedAssign, AugAssign,
    ExprStmt, If, While, For, FunctionDef, Return, ClassDef,
    Import, FromImport, With, Try, Raise, Break, Continue,
    Pass, Name, Number, String, Bool, NoneLiteral, BinOp,
    Compare, UnaryOp, Call, ListLiteral, TupleLiteral,
    SetLiteral, DictLiteral, Index, Slice, Attribute,
    IfExpr, NamedExpr,
)

class EduScopeError(Exception):
    """edu-v1 학습 범위 밖의 문법을 만났을 때 발생하는 에러."""
    pass

def validate_edu_v1(program: Program) -> None:
    """
    Program 전체가 edu-v1 범위 안에 있는지 검사한다.
    
    문제가 없으면 아무것도 반환하지 않고,
    문제가 있으면 EduScopeError를 발생시킨다.
    """
    for stmt in program.body:
        validate_stmt(stmt, in_loop=False, in_function=False)


def validate_stmt(stmt: Stmt, *, in_loop:bool, in_function: bool) -> None:
    """"문장 하나가 edu-v1 범위 안에 있는지 검사한다."""

    # =======================
    # edu-v1에서 막을 문법들
    # =======================

    if isinstance(stmt, ClassDef):
        raise EduScopeError(
            "아직 edu-v1에서는 클래스 문법을 지원하지 않아요.\n"
            "먼저 변수, 조건문, 반복문, 함수부터 연습해볼게요."
        )
    
    if isinstance(stmt, Import):
        raise EduScopeError(
            "아직 edu-v1에서는 불러오기(import)를 지원하지 않아요.\n"
            "기본 함수부터 사용해볼게요."
        )
    
    if isinstance(stmt, FromImport):
        raise EduScopeError(
            "아직 edu-v1에서는 꺼내기(from import)를 지원하지 않아요."
        )
    
    if isinstance(stmt, With):
        raise EduScopeError(
            "아직 edu-v1에서는 함께(with) 문법을 지원하지 않아요."
        )
    
    if isinstance(stmt, Try):
        raise EduScopeError(
            "아직 edu-v1에서는 시도/예외/마침 문법을 지원하지 않아요."
        )
    
    if isinstance(stmt, Raise):
        raise EduScopeError(
            "아직 edu-v1에서는 던지기(raise) 문법을 지원하지 않아요."
        )
    
    # =======================
    # edu-v1에서 허용할 문법들
    # =======================

    if isinstance(stmt, Assign):
        validate_expr(stmt.target)
        validate_expr(stmt.value)
        return
    
    if isinstance(stmt, ChainedAssign):
        for target in stmt.targets:
            validate_expr(target)
        validate_expr(stmt.value)
        return
    
    if isinstance(stmt, AugAssign):
        validate_expr(stmt.target)
        validate_expr(stmt.value)
        return
    
    if isinstance(stmt, ExprStmt):
        validate_expr(stmt.value)
        return
    
    if isinstance(stmt, If):
        validate_expr(stmt.test)

        for body_stmt in stmt.body:
            validate_stmt(
                body_stmt, in_loop=in_loop, in_function=in_function,
            )

        if stmt.orelse:
            for else_stmt in stmt.orelse:
                validate_stmt(
                    else_stmt, in_loop=in_loop, in_function=in_function,
                )

        return
    
    if isinstance(stmt, While):
        validate_expr(stmt.test)

        for body_stmt in stmt.body:
            validate_stmt(
                body_stmt, in_loop=True, in_function=in_function,
            )

        return
    
    if isinstance(stmt, For):
        validate_for_stmt(stmt, in_function=in_function)
        return
    
    if isinstance(stmt, FunctionDef):
        for param in stmt.args:
            if param.default is not None:
                validate_expr(param.default)

        for body_stmt in stmt.body:
            validate_stmt(
                body_stmt, in_loop=False, in_function=True,
            )

        return
    
    if isinstance(stmt, Return):
        if not in_function:
            raise EduScopeError(
                "반환(return)은 함수 안에서만 사용할 수 있어요."
            )
        
        if stmt.value is not None:
            validate_expr(stmt.value)

        return
    
    if isinstance(stmt, Break):
        if not in_loop:
            raise EduScopeError(
                "중단(break)은 반복문 안에서만 사용할 수 있어요."
            )
        
        return
    
    if isinstance(stmt, Continue):
        if not in_loop:
            raise EduScopeError(
                "계속(continue)은 반복문 안에서만 사용할 수 있어요."
            )
        
        return
    
    if isinstance(stmt, Pass):
        return
    
    raise EduScopeError(
        f"아직 edu-v1에서 지원하지 않는 문장입니다: {type(stmt).__name__}"
    )

def validate_for_stmt(stmt: For, *, in_function: bool) -> None:
    """
    edu-v1의 for문은 일단 '반복 i 안에 범위(...)' 형태만 허용한다.
    """

    validate_expr(stmt.target)
    validate_expr(stmt.iter)

    if not isinstance(stmt.iter, Call):
        raise EduScopeError(
            "edu-v1의 반복문은 일단 범위(...)만 사용할 수 있어요.\n\n"
            "예:\n"
            "반복 i 안에 범위(1, 6):\n"
            "   출력(i)"
        )
    
    if not isinstance(stmt.iter.func, Name):
        raise EduScopeError(
            "반복문에는 범위(...)형태를 사용해주세요."
        )
    
    if stmt.iter.func.id not in ("범위", "range"):
        raise EduScopeError(
            "edu-v1의 반복문은 일단 범위(...)만 사용할 수 있어요.\n\n"
            "예:\n"
            "반복 i 안에 범위(1, 6):\n"
            "   출력(i)"
        )
    
    for body_stmt in stmt.body:
        validate_stmt(
            body_stmt, in_loop=True, in_function=in_function,
        )

def validate_expr(expr: Expr) -> None:
    """표현식 하나가 edu-v1 범위 안에 있는지 검사한다."""

    if isinstance(expr, Name):
        return

    if isinstance(expr, Number):
        return
    
    if isinstance(expr, String):
        return
    
    if isinstance(expr, Bool):
        return
    
    if isinstance(expr, NoneLiteral):
        return
    
    if isinstance(expr, BinOp):
        validate_expr(expr.left)
        validate_expr(expr.right)
        return
    
    if isinstance(expr, Compare):
        validate_expr(expr.left)
        for item in expr.comparators:
            validate_expr(item)
        return
    
    if isinstance(expr, UnaryOp):
        validate_expr(expr.operand)
        return
    
    if isinstance(expr, Call):
        validate_call_expr(expr)
        return
    
    if isinstance(expr, ListLiteral):
        for item in expr.elements:
            validate_expr(item)
        return
    
    if isinstance(expr, TupleLiteral):
        for item in expr.elements:
            validate_expr(item)
        return
    
    if isinstance(expr, Index):
        validate_expr(expr.value)
        validate_expr(expr.index)
        return
    
    # 아래 표현식들은 edu-v1에서는 숨긴다.

    if isinstance(expr, Attribute):
        raise EduScopeError(
            "아직 edu-v1에서는 점(.)을 이용한 속성 접근을 지원하지 않아요."
        )
    
    if isinstance(expr, Slice):
        raise EduScopeError(
            "아직 edu-v1에서는 슬라이싱 문법을 지원하지 않아요."
        )
    
    if isinstance(expr, DictLiteral):
        raise EduScopeError(
            "아직 edu-v1에서는 딕셔너리 문법을 지원하지 않아요."
        )
    
    if isinstance(expr, SetLiteral):
        raise EduScopeError(
            "아직 edu-v1에서는 집합 문법을 지원하지 않아요."
        )
    
    if isinstance(expr, IfExpr):
        raise EduScopeError(
            "아직 edu-v1에서는 한 줄 조건식을 지원하지 않아요."
        )
    
    if isinstance(expr, NamedExpr):
        raise EduScopeError(
            "아직 edu-v1에서는 := 문법을 지원하지 않아요."
        )
    
    raise EduScopeError(
        f"아직 edu-v1에서 지원하지 않는 표현식입니다: {type(expr).__name__}"
    )

def validate_call_expr(expr: Call) -> None:
    """
    함수 호출 검사.
    
    출력(...)
    입력(...)
    범위(...)
    사용자가 정의한 함수(...)
    정도는 허용한다.
    
    단, 객체.함수() 같은 속성 호출은 edu-v1에서 막는다.
    """

    if not isinstance(expr.func, Name):
        raise EduScopeError(
            "edu-v1에서는 아직 객체.함수() 형태의 호출을 지원하지 않아요."
        )
    
    for arg in expr.args:
        validate_expr(arg)

    if expr.keywords:
        for _, value in expr.keywords:
            validate_expr(value)