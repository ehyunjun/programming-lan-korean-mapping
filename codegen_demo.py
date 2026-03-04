# codegen_demo.py
#
# AST(Program / Assign / BinOp / Number / Name)를
# 실제 파이썬 코드 문자열로 바꿔보는 데모

from mapping import BUILTIN_HAN_TO_PY, SPECIAL_IDENT_HAN_TO_PY

from ast_demo import (
    Program, Assign, ChainedAssign, AugAssign, If, While, Name, Number, BinOp, IfExpr, NamedExpr,
    Expr, Stmt, For, FunctionDef, ClassDef, Return, Call, ExprStmt,
    Break, Continue, Pass,
    Bool, NoneLiteral, UnaryOp, String,
    ListLiteral, TupleLiteral, SetLiteral, DictLiteral, Index, Slice, Attribute,
    Compare, Param, Import, FromImport,
    With, WithItem,
    Try, ExceptHandler, Raise,
)
def gen_expr(node: Expr) -> str:
    """ 표현식(Expr) -> 파이썬 코드 문자열 """
    if isinstance(node, Number):
        return node.raw if node.raw is not None else str(node.value)
    elif isinstance(node, Name):
        return SPECIAL_IDENT_HAN_TO_PY.get(node.id, node.id)
    elif isinstance(node, BinOp):
        left = gen_expr(node.left)
        right = gen_expr(node.right)
        return f"({left} {node.op} {right})"
    elif isinstance(node, Compare):
        parts = [gen_expr(node.left)]
        for op, cmp_ in zip(node.ops, node.comparators):
            parts.append(op)
            parts.append(gen_expr(cmp_))
        return f"({' '.join(parts)})"
    elif isinstance(node, IfExpr):
        return f"({gen_expr(node.body)} if {gen_expr(node.test)} else {gen_expr(node.orelse)})"
    elif isinstance(node, NamedExpr):
        return f"({gen_expr(node.target)} := {gen_expr(node.value)})"
    elif isinstance(node, Call):
        if isinstance(node.func, Name):
            func_code = BUILTIN_HAN_TO_PY.get(node.func.id, node.func.id)
        else:
            func_code = gen_expr(node.func)
        parts: list[str] = []
        parts.extend(gen_expr(a) for a in node.args)
        if node.keywords:
            parts.extend(f"{k}={gen_expr(v)}" for k, v in node.keywords)
        args_code = ", ".join(parts)
        return f"{func_code}({args_code})"
    elif isinstance(node, ListLiteral):
        elems = ", ".join(gen_expr(e) for e in node.elements)
        return f"[{elems}]"
    elif isinstance(node, TupleLiteral):
        elems = ", ".join(gen_expr(e) for e in node.elements)
        if len(node.elements) == 0:
            return "()"
        if len(node.elements) == 1:
            return f"({elems},)"
        return f"({elems})"
    elif isinstance(node, SetLiteral):
        if len(node.elements) == 0:
            return "set()"
        elems = ", ".join(gen_expr(e) for e in node.elements)
        return f"{{{elems}}}"
    elif isinstance(node, DictLiteral):
        if not node.items:
            return "{}"
        items = ", ".join(f"{gen_expr(k)}: {gen_expr(v)}" for k, v in node.items)
        return f"{{{items}}}"
    elif isinstance(node, Attribute):
        return f"{gen_expr(node.value)}.{node.attr}"
    elif isinstance(node, Index):
        return f"{gen_expr(node.value)}[{gen_expr(node.index)}]"
    elif isinstance(node, Slice):
        start = "" if node.start is None else gen_expr(node.start)
        stop = "" if node.stop is None else gen_expr(node.stop)
        if node.step is None:
            inside = f"{start}:{stop}"
        else:
            step = "" if node.step is None else gen_expr(node.step)
            inside = f"{start}:{stop}:{step}"
        return f"{gen_expr(node.value)}[{inside}]"
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
        target_code = gen_expr(node.target)
        value_code = gen_expr(node.value)
        return f"{target_code} = {value_code}"
    
    if isinstance(node, ChainedAssign):
        parts = [gen_expr(t) for t in node.targets]
        return f"{' = '.join(parts)} = {gen_expr(node.value)}"
    
    # 1.5) AugAssign (+=, -=, *=, /=)
    elif isinstance(node, AugAssign):
        target_code = gen_expr(node.target)
        value_code = gen_expr(node.value)
        return f"{target_code} {node.op}= {value_code}"
    
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
        target = gen_expr(node.target)
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
    
    # 6) functiondef
    elif isinstance(node, FunctionDef):
        parts: list[str] = []
        for p in node.args:
            if not isinstance(p, Param):
                raise TypeError(f"FunctionDef.args에는 Param만 들어갈 수 있습니다: {p!r}")
            if p.default is None:
                parts.append(SPECIAL_IDENT_HAN_TO_PY.get(p.name, p.name))
            else:
                n = SPECIAL_IDENT_HAN_TO_PY.get(p.name, p.name)
                parts.append(f"{n}={gen_expr(p.default)}")
        params = ", ".join(parts)
        lines = [f"def {node.name}({params}):"]
        if not node.body:
            lines.append("    pass")
        else:
            for stmt in node.body:
                body_code = gen_stmt(stmt)
                for line in body_code.splitlines():
                    lines.append("    " + line)

        return "\n".join(lines)
    elif isinstance(node, ClassDef):
        if node.bases:
            bases_code = ', '.join(gen_expr(b) for b in node.bases)
            head = f"class {node.name}({bases_code}):"
        else:
            head = f"class {node.name}:"

        lines = [head]
        if not node.body:
            lines.append('    pass')
        else:
            for stmt in node.body:
                body_code = gen_stmt(stmt)
                for line in body_code.splitlines():
                    lines.append('    ' + line)
        return '\n'.join(lines)
    elif isinstance(node, With):
        items: list[str] = []
        for it in node.items:
            if not isinstance(it, WithItem):
                raise TypeError(f"With.items에는 WithItem만 들어갈 수 있습니다: {it!r}")
            part = gen_expr(it.context_expr)
            if it.optional_vars is not None:
                part += f" as {gen_expr(it.optional_vars)}"
            items.append(part)

        head = f"with {', '.join(items)}:"
        lines = [head]
        if not node.body:
            lines.append(" pass")
        else:
            for stmt in node.body:
                body_code = gen_stmt(stmt)
                for line in body_code.splitlines():
                    lines.append(" " + line)
        return "\n".join(lines)
    elif isinstance(node, Import):
        items: list[str] = []
        for module, asname in node.names:
            if asname:
                items.append(f"{module} as {asname}")
            else:
                items.append(module)
        return f"import {', '.join(items)}"
    elif isinstance(node, FromImport):
        items: list[str] = []
        for name, asname in node.names:
            if name == "*":
                if asname:
                    raise SyntaxError("from ... import * 는 별칭(as)을 붙일 수 없습니다.")
                items.append("*")
            else:
                if asname:
                    items.append(f"{name} as {asname}")
                else:
                    items.append(name)
        return f"from {node.module} import {', '.join(items)}"
    elif isinstance(node, Raise):
        if node.exc is None:
            return "raise"
        return f"raise {gen_expr(node.exc)}"
    elif isinstance(node, Try):
        lines: list[str] = ["try:"]
        if not node.body:
            lines.append("    pass")
        else:
            for stmt in node.body:
                body_code = gen_stmt(stmt)
                for line in body_code.splitlines():
                    lines.append("    " + line)

        for h in node.handlers:
            if not isinstance(h, ExceptHandler):
                raise TypeError(f"Try.handlers에는 ExceptHandler만 들어갈 수 있습니다: {h!r}")
            head = "except"
            if h.type is not None:
                head += f" {gen_expr(h.type)}"
            if h.name is not None:
                if h.type is None:
                    raise SyntaxError("'예외 별칭 e' 형태는 지원하지 않습니다. (타입 없이 별칭 불가)")
                head += f" as {h.name}"
            head += ":"
            lines.append(head)
            if not h.body:
                lines.append("    pass")
            else:
                for stmt in h.body:
                    body_code = gen_stmt(stmt)
                    for line in body_code.splitlines():
                        lines.append("    " + line)

        if node.orelse is not None:
            lines.append("else:")
            if not node.orelse:
                lines.append("    pass")
            else:
                for stmt in node.orelse:
                    body_code = gen_stmt(stmt)
                    for line in body_code.splitlines():
                        lines.append("    " + line)

        if node.finalbody is not None:
            lines.append("finally:")
            if not node.finalbody:
                lines.append("    pass")
            else:
                for stmt in node.finalbody:
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