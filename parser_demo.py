# parser_demo.py
#
# "값 = 1 + 2" 같은 코드를
# 1) simple_lexer 로 토큰 리스트로 만들고
# 2) Parser 로 AST(Program/Assign/BinOp/Number/Name) 트리로 바꿔보는 데모

from lexer_demo import simple_lexer
from ast_demo import Program, Assign, Name, Number, BinOp, print_program

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0  # 현재 읽고 있는 토큰 위치 인덱스

	
	@property
	def current(self):
		if self.pos < len(self.tokens):
			return self.tokens[self.pos]
		return ("EOF", "")
	
	# 토큰 하나 소비하면서 앞으로 한 칸 이동
	def advance(self):
		self.pos += 1
	
	# 기대하는 타입/값과 맞는지 검사하면서 토큰 소비
	def expect(self, expected_type=None, expected_value=None):
		tok = self.current
		ttype, tvalue = tok

		if expected_type is not None and ttype != expected_type:
			raise SyntaxError(f"{expected_type} 가 와야 하는데 {ttype} 를 만났습니다: {tok}")
		if expected_value is not None and tvalue != expected_value:
			raise SyntaxError(f"{expected_value!r} 가 와야 하는데 {tvalue!r} 를 만났습니다: {tok}")
		
		self.advance()
		return tok
	
	# 파싱 시작점

	def parse_program(self) -> Program:
		"""
		지금은 한 줄짜리 대입문만 있다고 가정하고
		Program(body=[Assign(...)] ) 하나만 만든다.
		"""
		stmt = self.parse_assign()
		return Program(body=[stmt])
	
	def parse_assign(self) -> Assign:
		"""
		대입문: IDENT '=' expr
		예:     값     = 1 + 2
		"""
		# 1) 왼쪽 변수 이름
		ident_type, ident_value = self.expect("IDENT")
		target = Name(ident_value)

		# 2) '=' 기호
		self.expect("SYMBOL", "=")

		# 3) 오른쪽 표현식
		value_expr = self.parse_expr()

		return Assign(target=target, value=value_expr)
	
	# 표현식 파싱

	def parse_expr(self):
		"""
		expr ::= term ( '+' term )*
		term ::= NUMBER | IDENT
		지금은 + 만 지원 (우선순위 같은 건 신경 안 쓰는 간단 버전)
		"""
		left = self.parse_term()

		# 뒤에 "+ term" 이 계속 붙을 수 있음: 1 + 2 + 3 ...
		while self.current[0] == "SYMBOL" and self.current[1] == "+":
			self.expect("SYMBOL", "+")
			right = self.parse_term()
			left = BinOp(left=left, op="+", right=right)

		return left
	
	def parse_term(self):
		tok_type, tok_value = self.current

		if tok_type == "NUMBER":
			self.advance()
			return Number(int(tok_value))
		elif tok_type == "IDENT":
			self.advance()
			return Name(tok_value)
		else:
			raise SyntaxError(f"숫자나 이름이 와야 하는 위치에서 {self.current}를 만났습니다.")
		
if __name__ == "__main__":
	# 1) 한글 코드 한 줄
	code = "값 = a + 3"

	# 2) 렉서로 토큰 뽑기
	tokens = simple_lexer(code)
	print("토큰들:")
	for t in tokens:
		print(" ", t)

	# 3) 파서로 AST 만들기
	parser = Parser(tokens)
	program_ast = parser.parse_program()

	print("\nAst 구조:")
	print_program(program_ast)