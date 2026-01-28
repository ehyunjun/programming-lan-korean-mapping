# parser_demo.py
#
# "값 = 1 + 2" 같은 코드를
# 1) simple_lexer 로 토큰 리스트로 만들고
# 2) Parser 로 AST 트리로 바꿔보는 데모
# + if/while/for/def 에서 파이썬 처럼 블록(들여쓰기) 지원

from codegen_demo import gen_program
from lexer_demo import simple_lexer, DEF_KEYWORD
from ast_demo import (
    Expr, Stmt, 
    Program, Assign, Name, Number, BinOp, 
    If, While, For, FunctionDef, Return, Call, ExprStmt,
    print_program
)

# 연산자 집합
BINARY_OPS = {"+", "-", "*", "/", "<", ">"}
ADD_OPS = {"+", "-"}
MUL_OPS = {"*", "/"}
COMP_OPS = {"<", ">"}

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
    
    # ======================
    #  프로그램 시작점
    # ======================

    def parse_program(self) -> Program:
        body = []
        while self.current[0] != "EOF":
            # 빈 줄(NEWLINE)은 건너뜀
            if self.current[0] == "NEWLINE":
                self.advance()
                continue
            body.append(self.parse_stmt())
        return Program(body=body)
    
    # =======================
    #  표현식 파싱 (우선순위)
    # =======================
    
    def parse_expr(self) -> Expr:
        """
        이제 expr는 '비교식'의 진입점 역할만 한다.
        """
        return self.parse_comparison()
    
    def parse_comparison(self) -> Expr:
        """
        comparison ::= sum (('<' | '>') sum)*
        비교 연산(<, >)은 덧셈/곱셈보다 우선순위가 낮다.
        """
        left = self.parse_sum()

        while self.current[0] == "SYMBOL" and self.current[1] in COMP_OPS:
            op = self.current[1]
            self.advance()
            right = self.parse_sum()
            left = BinOp(left=left, op=op, right=right)
        
        return left
    
    def parse_sum(self) -> Expr:
        """
        sum ::= term (('+' | '-') term)*
        """
        left = self.parse_term()

        while self.current[0] == "SYMBOL" and self.current[1] in ADD_OPS:
            op = self.current[1]
            self.advance()
            right = self.parse_term()
            left = BinOp(left=left, op=op, right=right)
        
        return left
    
    def parse_term(self) -> Expr:
        """
        term ::= factor (('*' | '/') factor)*
        """
        left = self.parse_factor()

        while self.current[0] == "SYMBOL" and self.current[1] in MUL_OPS:
            op = self.current[1]
            self.advance()
            right = self.parse_factor()
            left = BinOp(left=left, op=op, right=right)
        
        return left
    
    def parse_factor(self) -> Expr:
        """
        factor ::= NUMBER
                | IDENT / 함수 호출
                | '(' expr ')'
        """
        tok_type, tok_value = self.current

        # 숫자
        if tok_type == "NUMBER":
            self.advance()
            return Number(int(tok_value))
        
        # 괄호식: (expr)
        if tok_type == "SYMBOL" and tok_value == "(":
            self.advance() # '(' 소비
            inner = self.parse_expr()
            self.expect("SYMBOL", ")")
            return inner
        
        # 이름(변수 또는 함수호출)
        if tok_type == "IDENT":
            ident_name = tok_value
            self.advance()

            # 함수 호출인지 확인: 이름 뒤에 '(' 이 오면 호출
            if self.current[0] == "SYMBOL" and self.current[1] == "(":
                self.advance() # '(' 소비
                args: list[Expr] = []
                if not (self.current[0] == "SYMBOL" and self.current[1] == ")"):
                    while True:
                        arg_expr = self.parse_expr()
                        args.append(arg_expr)

                        if self.current[0] == "SYMBOL" and self.current[1] == ",":
                            self.advance() # ',' 소비
                            continue
                        break
            
                # ')'
                self.expect("SYMBOL", ")")
                return Call(func=Name(ident_name), args=args)
            
            # 그냥 변수 이름
            return Name(ident_name)
        
        # 그 외는 에러
        raise SyntaxError(f" 숫자, 이름, 혹은 괄호로 시작하는 표현식이 와야 하는데 {self.current}를 만났습니다.")
    
    # =====================
    #  블록(suite) 파싱
    # =====================
    
    def parse_suite(self) -> list[Stmt]:
        """
        ':' 뒤에 오는 본문을 파싱한다.

        두 형태 지원:
        1) 한 줄짜리:
            만약 값 < 10: 값 = 값 + 1

        2) 여러 줄 블록:
            만약 값 < 10:
                값 = 값 + 1
                값 = 값 + 2
        """
        # case 2: NEWLINE + INDENT -> 블록
        if self.current[0] == "NEWLINE":
            # 줄 끝
            self.advance()
            # 다음은 반드시 INDENT 여야 함
            self.expect("INDENT")
            body: list[Stmt] = []
            while self.current[0] not in ("DEDENT", "EOF"):
                if self.current[0] == "NEWLINE":
                    self.advance()
                    continue
                body.append(self.parse_stmt())
            # 블록 끝
            self.expect("DEDENT")
            return body
        
        # case 1: 같은 줄에 한 문장
        stmt = self.parse_stmt()
        return [stmt]
    
    # ========================
    #  문장들 (if/while/for/def/return)
    # ========================
    
    def parse_assign(self) -> Assign:
        """
        대입문: IDENT '=' expr
        예:     값     = 1 + 2
        """
        # 1) 왼쪽 변수 이름
        _, ident_value = self.expect("IDENT")
        target = Name(ident_value)

        # 2) '=' 기호
        self.expect("SYMBOL", "=")

        # 3) 오른쪽 표현식
        value_expr = self.parse_expr()

        return Assign(target=target, value=value_expr)

    def parse_if(self) -> If:
        """
        if문 : 
            만약 expr ':' suite
            [아니면 expr ':' suite]
            [그외 ':' suite]
        
        파이썬 if/elif/else 처럼
        - '아니면' 여러 번 가능
        - 마지막에 '그외' 한 번 가능
        """
        # 1) '만약' 키워드 소비
        self.expect("KEYWORD", "만약")

        # 2) 첫 번째 조건식 (값 < 10 부분)
        cond = self.parse_expr()

        # 3) ':' 기호
        self.expect("SYMBOL", ":")

        # 4) then 블록
        then_body = self.parse_suite()

        # 루트 if 노드
        root_if = If(test=cond, body=then_body, orelse=None)
        current_if = root_if
        
        # 5) '아니면' (elif) 여러 번 처리
        while self.current[0] == "KEYWORD" and self.current[1] == "아니면":
            
            # '아니면' 키워드 소비
            self.expect("KEYWORD", "아니면")
            
            # elif 조건식
            elif_cond = self.parse_expr()
            
            # ':' 기호
            self.expect("SYMBOL", ":")
            
            # elif 본문
            elif_body = self.parse_suite()
            
            # 새 if 노드를 만들어서 현재 if의 orelse에 달아줌
            new_if = If(test=elif_cond, body=elif_body, orelse=None)
            current_if.orelse = [new_if]
            current_if = new_if # 체인의 끝을 업데이트

        # elif 다음에 '그외'가 올 수도 있음
        if self.current[0] == "KEYWORD" and self.current[1] == "그외":
            self.expect("KEYWORD", "그외")
            self.expect("SYMBOL", ":")
            else_body = self.parse_suite()
            current_if.orelse = else_body

        return root_if

    def parse_while(self) -> While:
        """
        While문:
            동안 expr ':' suite
        예: 
            동안 값 < 10: 
                값 = 값 + 1
        """
        # 1) '동안' 키워드 소비
        self.expect("KEYWORD", "동안")
        
        # 2) 조건식
        cond = self.parse_expr()
        
        # 3) ':' 기호
        self.expect("SYMBOL", ":")
        
        # 4) 본문 suite
        body = self.parse_suite()

        return While(test=cond, body=body)
    
    def parse_for(self) -> For:
        """
        For문:
            반복 i = 0, 10: suite
        를
            for i in range(0, 10):
        로 변환하는 AST 생성
        """
        # 1) '반복' 키워드 소비
        self.expect("KEYWORD", "반복")

        # 2) 반복 변수 이름
        _, ident_value = self.expect("IDENT")
        target = Name(ident_value)

        # 3) '=' 기호
        self.expect("SYMBOL", "=")

        # 4) 시작값
        start_expr = self.parse_expr()

        # 5) ',' 기호
        self.expect("SYMBOL", ",")

        # 6) 끝값
        end_expr = self.parse_expr()

        # 7) ':' 기호
        self.expect("SYMBOL", ":")

        # 8) 본문: 지금은 대입문 하나라고 가정
        body = self.parse_suite()

        return For(target=target, start=start_expr, end=end_expr, body=body)
    
    def parse_function(self) -> FunctionDef:
        """
        함수 정의:
            정의 이름(파라미터들): suite
        """
        # '정의' or '함수' 키워드 (브랜치에 따라 달라짐)
        self.expect("KEYWORD", DEF_KEYWORD)

        # 함수 이름
        _, func_name = self.expect("IDENT")

        # '(' 
        self.expect("SYMBOL", "(")

        # 파라미터 리스트
        params: list[str] = []
        if not (self.current[0] == "SYMBOL" and self.current[1] == ")"):
            while True:
                _, param_name = self.expect("IDENT")
                params.append(param_name)

                if self.current[0] == "SYMBOL" and self.current[1] == ",":
                    self.advance()
                    continue
                break
        # ')'
        self.expect("SYMBOL", ")")

        # ':'
        self.expect("SYMBOL", ":")

        # 함수 본문 suite (여러 문장 가능)
        body = self.parse_suite()
        
        return FunctionDef(name=func_name, args=params, body=body)
    
    def parse_return(self) -> Return:
        """
        반환문:
            반환 expr
        지금은 항상 값이 있는 형태만 지원(반환 alone은 나중에 확장)
        """
        self.expect("KEYWORD", "반환")
        value_expr = self.parse_expr()
        return Return(value=value_expr)

    def parse_stmt(self) -> Stmt:
        ttype, tvalue = self.current

        if ttype == "KEYWORD" and tvalue == "만약":
            return self.parse_if()
        elif ttype == "KEYWORD" and tvalue == "동안":
            return self.parse_while()
        elif ttype == "KEYWORD" and tvalue == "반복":
            return self.parse_for()
        elif ttype == "KEYWORD" and tvalue == DEF_KEYWORD:
            return self.parse_function()
        elif ttype == "KEYWORD" and tvalue == "반환":
            return self.parse_return()
        elif ttype == "IDENT":
            next_type, next_value = ("EOF", "")
            if self.pos + 1 < len(self.tokens):
                next_type, next_value = self.tokens[self.pos + 1]
            if next_type == "SYMBOL" and next_value == "=":
                return self.parse_assign()
            else:
                expr = self.parse_expr()
                return ExprStmt(value=expr)
        else:
            raise SyntaxError(f"문장이 시작될 수 없는 토큰: {self.current}")
        
if __name__ == "__main__":
    # 1) 한글 코드
    code = f"""{DEF_KEYWORD} 더하기(x, y):
    합 = x + y
    반환 합
값 = 0

만약 값 < 10:
    값 = 더하기(1, 2)
    값 = 값 + 1
그외:
    값 = 0

동안 값 < 20:
    값 = 값 + 2

반복 i = 0, 3:
    값 = 값 + i
"""

    # 2) 렉서로 토큰 뽑기
    tokens = simple_lexer(code)
    print("==== 입력 코드 ====")
    print(code)
    print("==== 토큰들 ====")
    for t in tokens:
        print(" ", t)

    # 3) 파서로 AST 만들기
    parser = Parser(tokens)
    program_ast = parser.parse_program()

    print("\n===== Ast 구조 ====")
    print_program(program_ast)

    # 4) AST -> 파이썬 코드 생성
    py_code = gen_program(program_ast)
    print("\n==== 생성된 파이썬 코드 ====")
    print(py_code)

    # 5) 실제로 실행해보기
    env = {"값": 3}
    exec(py_code, env, env)
    print("\n==== 실행 결과 ====")
    print("값 =", env["값"])