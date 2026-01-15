# codegen_demo.py
#
# AST(Program / Assign / BinOp / Number / Name)를
# 실제 파이썬 코드 문자열로 바꿔보는 데모

from ast_demo import Program, Assign, If, Name, Number, BinOp, Expr, Stmt

def gen_expr(node: Expr) -> str:
	""" 표현식(Expr) -> 파이썬 코드 문자열 """
	if isinstance(node, Number):
		return str(node.value)
	elif isinstance(node, Name):
		return node.id
	elif isinstance(node, BinOp):
		left = gen_expr(node.left)
		right = gen_expr(node.right)
		return f"({left} {node.op} {right})"
	else:
		raise TypeError(f"지원하지 않는 Expr 타입: {node!r}")
	
def gen_stmt(node: Stmt) -> str:
	""" 문장(Stmt) -> 한 줄짜리 파이썬 코드 문자열 """
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
			)
		]
	)
	
	py_code = gen_program(ast)
	print("생성된 파이썬 코드:")
	print(py_code)

	# 실제로 실행해보기
	env = {}
	exec(py_code, env, env)
	print("실행 결과, 값 =", env["값"])