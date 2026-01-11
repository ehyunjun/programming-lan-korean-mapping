# ast_demo.py
#
# "x = 1 + 2" 라는 코드를 AST로 표현해 보고,
# 그 트리를 예쁘게 출력해 보는 데모.

from dataclasses import dataclass
from typing import List, Union

# AST 노드 타입들

class Expr:
	""" 표현식(Expression)의 부모 클래스 """
	pass

@dataclass
class Number(Expr):
	value: int

@dataclass
class Name(Expr):
	id: str  # 변수 이름, 함수 이름 등

@dataclass
class BinOp(Expr):
	left: Expr
	op: str  # "+", "-", "*", "/" 같은 연산자 문자열
	right: Expr

class Stmt:
	"""" 문장(Statement)의 부모 클래스"""
	pass

@dataclass
class Assign(Stmt):
	target: Name  # 왼쪽: 대입 대상 변수
	value: Expr   # 오른쪽: 값(표현식)

@dataclass
class Program:
	body: List[Stmt]  # 프로그램은 문장들의 리스트

@dataclass
class If(Stmt):
	test: Expr
	body: List[Stmt]


# AST를 예쁘게 출력하는 함수들

def print_expr(node: Expr, indent: int = 0):
	space = " " * indent
	if isinstance(node, Number):
		print(f"{space}Number(value={node.value})")
	elif isinstance(node, Name):
		print(f"{space}Name(id={node.id!r})")
	elif isinstance(node, BinOp):
		print(f"{space}BinOp(op={node.op!r})")
		print(f"{space} left:")
		print_expr(node.left, indent + 2)
		print(f"{space} right:")
		print_expr(node.right, indent + 2)
	else:
		print(f"{space}<Unknown Expr {node}>")

def print_stmt(node: Stmt, indent: int = 0):
	space = " " * indent
	if isinstance(node, Assign):
		print(f"{space}Assign")
		print(f"{space} target:")
		print_expr(node.target, indent + 2)
		print(f"{space} value:")
		print_expr(node.value, indent + 2)
	elif isinstance(node, If):
		print(f"{space}If")
		print(f"{space} test:")
		print_expr(node.test, indent + 2)
		print(f"{space} body:")
		for s in node.body:
			print_stmt(s, indent + 2)
	else:
		print(f"{space}<Unknown Stmt {node!r}>")

def print_program(prog: Program):
	print("Program")
	for stmt in prog.body:
		print_stmt(stmt, indent=1)


# 여기서 실제로 AST 만들어 보기

if __name__ == "__main__":
	# x = 1 + 2 라는 코드를 AST로 직접 구성해 봄
	ast = Program(
		body=[
			Assign(
				target=Name("x"),
				value=BinOp(
					left=Number(1),
					op="+",
					right=Number(2),
				),
			)
		]
	)

	print_program(ast)