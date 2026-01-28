# codegen_demo.py
#
# AST(Program / Assign / BinOp / Number / Name)를
# 실제 파이썬 코드 문자열로 바꿔보는 데모

from ast_demo import (
    Program, Assign, If, While, Name, Number, BinOp,
    Expr, Stmt, For, FunctionDef, Return, Call, ExprStmt
)
def gen_expr(node: Expr) -> str:
    """ 표현식(Expr) -> 파이썬 코드 문자열 """
    if isinstance(node, Number):
        return str(node.value)
    elif isinstance(node, Name):
        if node.id == "출력":
            return "print"
        return node.id
    elif isinstance(node, BinOp):
        left = gen_expr(node.left)
        right = gen_expr(node.right)
        return f"({left} {node.op} {right})"
    elif isinstance(node, Call):
        func_code = gen_expr(node.func)
        args_code = ", ".join(gen_expr(a) for a in node.args)
        return f"{func_code}({args_code})"
    else:
        raise TypeError(f"지원하지 않는 Expr 타입: {node!r}")
    
def gen_stmt(node: Stmt) -> str:
    """ 문장(Stmt) -> 한 줄짜리 파이썬 코드 문자열 """
    # 0) 표현식 문 (예: 출력(값))
    if isinstance(node, ExprStmt):
        return gen_expr(node.value)
    
    # 1) 대입문
    if isinstance(node, Assign):
        target = node.target.id
        value_code = gen_expr(node.value)
        return f"{target} = {value_code}"
    
    # 2) if 문
    elif isinstance(node, If):
        cond_code = gen_expr(node.test)
        lines = [f"if {cond_code}:"]
        for stmt in node.body:
            body_code = gen_stmt(stmt)
            for line in body_code.splitlines():
                lines.append("    " + line)

        if node.orelse:
            lines.append("else:")
            for stmt in node.orelse:
                body_code = gen_stmt(stmt)
                for line in body_code.splitlines():
                    lines.append("    " + line)
        return "\n".join(lines)

    # 3) while 문
    elif isinstance(node, While):
        cond_code = gen_expr(node.test)
        lines = [f"while {cond_code}:"]
        for stmt in node.body:
            body_code = gen_stmt(stmt)
            for line in body_code.splitlines():
                lines.append("    " + line)
        return "\n".join(lines)

    # 4) for 문
    elif isinstance(node, For):
        target = node.target.id
        start_code = gen_expr(node.start)
        end_code = gen_expr(node.end)
        lines = [f"for {target} in range({start_code}, {end_code}):"]
        for stmt in node.body:
            body_code = gen_stmt(stmt)
            for line in body_code.splitlines():
                lines.append("    " + line)
        return "\n".join(lines)
    
    # 5) return
    elif isinstance(node, Return):
        if node.value is None:
            return "return"
        else:
            return f"return {gen_expr(node.value)}"
    
    # 6) functionderf
    elif isinstance(node, FunctionDef):
        params = ", ".join(node.args)
        lines = [f"def {node.name}({params}):"]
        if not node.body:
            lines.append("    pass")
        else:
            for stmt in node.body:
                body_code = gen_stmt(stmt)
                for line in body_code.splitlines():
                    lines.append("    " + line)

        return "\n".join(lines)
    else:
        raise TypeError(f"지원하지 않는 Stmt 타입: {node!r}")
    
def gen_program(prog: Program) -> str:
    """ Program 전체를 파이썬 소스코드 문자열로 변환 """
    lines: list[str] = []
    for stmt in prog.body:
        code = gen_stmt(stmt)
        lines.extend(code.splitlines())
    return "\n".join(lines)

if __name__ == "__main__":
    # 간단 테스트: 손으로 AST 하나 만들어서 코드 생성
    ast = Program(
        body=[
            Assign(
                target=Name("값"),
                value=BinOp(
                    left=Number(1),
                    op="+",
                    right=Number(2),
                ),
            ),
            ExprStmt(
                value=Call(
                    func=Name("출력"),
                    args=[Name("값")],
                )
            ),
        ]
    )
    
    py_code = gen_program(ast)
    print("생성된 파이썬 코드:")
    print(py_code)

    # 실제로 실행해보기
    env = {}
    exec(py_code, env, env)
    print("실행 결과:")