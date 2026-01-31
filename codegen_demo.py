# codegen_demo.py
#
# AST(Program / Assign / BinOp / Number / Name)를
# 실제 파이썬 코드 문자열로 바꿔보는 데모

from mapping import BUILTIN_HAN_TO_PY

from ast_demo import (
    Program, Assign, If, While, Name, Number, BinOp,
    Expr, Stmt, For, FunctionDef, Return, Call, ExprStmt,
    Break, Continue, Pass,
    Bool, NoneLiteral, UnaryOp, String,
)
def gen_expr(node: Expr) -> str:
    """ 표현식(Expr) -> 파이썬 코드 문자열 """
    if isinstance(node, Number):
        return str(node.value)
    elif isinstance(node, Name):
        return BUILTIN_HAN_TO_PY.get(node.id, node.id)
        return node.id
    elif isinstance(node, BinOp):
        left = gen_expr(node.left)
        right = gen_expr(node.right)
        return f"({left} {node.op} {right})"
    elif isinstance(node, Call):
        func_code = gen_expr(node.func)
        args_code = ", ".join(gen_expr(a) for a in node.args)
        return f"{func_code}({args_code})"
    elif isinstance(node, String):
        return repr(node.value)
    elif isinstance(node, Bool):
        return "True" if node.value else "False"
    elif isinstance(node, NoneLiteral):
        return "None"
    elif isinstance(node, UnaryOp):
        if node.op == "not":
            return f"(not {gen_expr(node.operand)})"
        else:
            return f"({node.op}{gen_expr(node.operand)})"
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
        lines = []

        def emit_if_chain(n: If, first: bool):
            cond_code = gen_expr(n.test)
            head = "if" if first else "elif"
            lines.append(f"{head} {cond_code}:")
            for stmt in n.body:
                body_code = gen_stmt(stmt)
                for line in body_code.splitlines():
                    lines.append("    " + line)

            if n.orelse and len(n.orelse) == 1 and isinstance(n.orelse[0], If):
                emit_if_chain(n.orelse[0], first=False)
            # 그 외의 orelse(일반 else 블록)
            elif n.orelse:
                lines.append("else:")
                for stmt in n.orelse:
                    body_code = gen_stmt(stmt)
                    for line in body_code.splitlines():
                        lines.append("    " + line)
        
        emit_if_chain(node, first=True)
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
        iter_code = gen_expr(node.iter)
        lines = [f"for {target} in {iter_code}:"]
        for stmt in node.body:
            body_code = gen_stmt(stmt)
            for line in body_code.splitlines():
                lines.append("    " + line)
        return "\n".join(lines)
    
    # 4.5) break / continue / pass
    elif isinstance(node, Break):
        return "break"
    elif isinstance(node, Continue):
        return "continue"
    elif isinstance(node, Pass):
        return "pass"
    
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