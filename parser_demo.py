# parser_demo.py
#
# "값 = 1 + 2" 같은 코드를
# 1) simple_lexer 로 토큰 리스트로 만들고
# 2) Parser 로 AST(Program/Assign/BinOp/Number/Name) 트리로 바꿔보는 데모

from codegen_demo import gen_program
from lexer_demo import simple_lexer
from ast_demo import Program, Assign, Name, Number, BinOp, If, print_program
BINARY_OPS = {"+", "-", "*", "/", "<", ">"}

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

		stmt = self.parse_stmt()
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
		while self.current[0] == "SYMBOL" and self.current[1] in BINARY_OPS:
			op = self.current[1]
			self.advance()
			right = self.parse_term()
			left = BinOp(left=left, op=op, right=right)

		return left
	
	def parse_if(self) -> If:
		"""
		if문 : 
			만약 expr ':' assign
			[아니면 expr ':' assign]
			[그외 ':' assign]
			(elif는 현재 한 번만 허용)
		"""
		# 1) '만약' 키워드 소비
		self.expect("KEYWORD", "만약")

		# 2) 첫 번째 조건식 (값 < 10 부분)
		cond = self.parse_expr()

		# 3) ':' 기호
		self.expect("SYMBOL", ":")

		# 4) if 본문은 지금은 '대입문 하나'라고 가정
		then_stmt = self.parse_assign()

		# 기본 if 노드
		if_node = If(test=cond, body=[then_stmt], orelse=None)
		
		# 선택적인 '아니면' 처리 (elif 한 번만)
		if self.current[0] == "KEYWORD" and self.current[1] == "아니면":
			# '아니면' 키워드 소비
			self.expect("KEYWORD", "아니면")
			# elif 조건식
			elif_cond = self.parse_expr()
			# ':' 기호
			self.expect("SYMBOL", ":")
			# elif 본문 (대입문 하나)
			elif_stmt = self.parse_assign()
			# elif는 "else 안의 if"로 표현
			inner_if = If(test=elif_cond, body=[elif_stmt], orelse=None)
			if_node.orelse = [inner_if]

			# elif 다음에 '그외'가 올 수도 있음
			if self.current[0] == "KEYWORD" and self.current[1] == "그외":
				self.expect("KEYWORD", "그외")
				self.expect("SYMBOL", ":")
				else_stmt = self.parse_assign()
				inner_if.orelse = [else_stmt]

			return if_node
		
		# '아니면' 없이 바로 '그외'만 있는 경우
		if self.current[0] == "KEYWORD" and self.current[1] == "그외":
			self.expect("KEYWROD", "그외")
			self.expect("SYMBOL", ":")
			else_stmt = self.parse_assign()
			if_node.orelse = [else_stmt]

		return if_node
	
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
		
	def parse_stmt(self):
		ttype, tvalue = self.current

		if ttype == "KEYWORD" and tvalue == "만약":
			return self.parse_if()
		elif ttype == "IDENT":
			return self.parse_assign()
		else:
			raise SyntaxError(f"문장이 시작될 수 없는 토큰: {self.current}")
		
if __name__ == "__main__":
	# 1) 한글 코드 한 줄
	code = "만약 값 < 10: 값 = 값 + 1 아니면 값 < 20: 값 = 값 + 2 그외: 값 = 0"

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

	# 4) AST -> 파이썬 코드 생성
	py_code = gen_program(program_ast)
	print("\n생성된 파이썬 코드:")
	print(py_code)

	# 5) 실제로 실행해보기
	env = {"값": 3}
	exec(py_code, env, env)
	print("실행 결과, 값 =", env["값"])