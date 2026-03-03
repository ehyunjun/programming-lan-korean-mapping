# parser_demo.py
#
# "값 = 1 + 2" 같은 코드를
# 1) simple_lexer 로 토큰 리스트로 만들고
# 2) Parser 로 AST 트리로 바꿔보는 데모
# + if/while/for/def 꺼내기 파이썬 처럼 블록(들여쓰기) 지원

from codegen_demo import gen_program
from lexer_demo import simple_lexer, DEF_KEYWORD
from tokens import ADD_OPS, MUL_OPS, COMP_OPS, SHIFT_OPS, POW_OP, BITAND_OP, BITOR_OP, BITXOR_OP
from ast_demo import (
    Expr, Stmt, 
    Program, Assign, ChainedAssign, AugAssign, Name, Number, BinOp, 
    If, While, For, FunctionDef, ClassDef, Return, Call, ExprStmt,
    Break, Continue, Pass,
    Bool, NoneLiteral, UnaryOp,
    print_program,
    String, ListLiteral, Index, Slice, Attribute,
    TupleLiteral, SetLiteral, DictLiteral,
    Compare, IfExpr, NamedExpr, 
    Param, Import, FromImport,
    Try, ExceptHandler, Raise,
)

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

    # 현재 위치꺼내기 offset 만큼 앞의 토큰을 미리보기
    def peek(self, offset: int = 1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return ("EOF", "")
    
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
            before = self.pos
            stmt = self.parse_stmt()
            if self.pos == before:
                near = self.tokens[self.pos:self.pos+10]
                raise RuntimeError(f"[parser stuck] pos={self.pos}, current={self.current}, next10={near}")
            body.append(stmt)
        return Program(body=body)
    
    # =======================
    #  표현식 파싱 (우선순위)
    # =======================
    
    def parse_expr(self) -> Expr:
        """
        expr ::= or_expr
        """
        return self.parse_namedexpr()
    
    def parse_namedexpr(self) -> Expr:
        """
        namedexpr ::= IDENT ':=' conditional_expr | conditional_expr
        """
        if self.current[0] == "IDENT" and self.peek(1) == ("SYMBOL", ":="):
            _, name = self.expect("IDENT")
            self.expect("SYMBOL", ":=")
            value = self.parse_conditional()
            return NamedExpr(target=Name(name), value=value)
        return self.parse_conditional()
    
    def parse_conditional(self) -> Expr:
        """
        conditional_expr ::= or_expr ('만약' or_expr '그외' conditional_expr)?
        (Python의 a if cond else b 를 'a 만약 cond 그외 b'로 지원)
        """
        body = self.parse_or()
        if self.current[0] == "KEYWORD" and self.current[1] == "만약":
            self.expect("KEYWORD", "만약")
            test = self.parse_or()
            self.expect("KEYWORD", "그외")
            orelse = self.parse_conditional()
            return IfExpr(body=body, test=test, orelse=orelse)
        return body
    
    def parse_or(self) -> Expr:
        """ or_expr ::= and_expr ("또는" and_expr)* """
        left = self.parse_and()
        while self.current[0] == "KEYWORD" and self.current[1] == "또는":
            self.expect("KEYWORD", "또는")
            right = self.parse_and()
            left = BinOp(left=left, op="or", right=right)
        return left
    
    def parse_and(self) -> Expr:
        """
        and_expr ::= not_expr ("그리고" not_expr)*
        """
        left = self.parse_not()
        while self.current[0] == "KEYWORD" and self.current[1] == "그리고":
            self.expect("KEYWORD", "그리고")
            right = self.parse_not()
            left = BinOp(left=left, op="and", right=right)
        return left
    
    def parse_not(self) -> Expr:
        """
        not_expr ::= "아니다" not_expr | comparison
        """
        if self.current[0] == "KEYWORD" and self.current[1] == "아니다":
            self.expect("KEYWORD", "아니다")
            operand = self.parse_not()
            return UnaryOp(op="not", operand=operand)
        return self.parse_comparison()

    def parse_comparison(self) -> Expr:
        """
        comparison ::= bitor ((comp_op | "안에" | "아니다 안에") bitor)*
        비교 연산(<, >, <=, >=, ==, !=, in)은 비트연산(|,^)보다 우선순위가 낮다.
        """
        left = self.parse_bitor()

        ops: list[str] = []
        comparators: list[Expr] = []

        while True:
            ttype, tvalue = self.current

            # 0) "아니다 안에" (not in) - 비교 연산자로 취급
            if ttype == "KEYWORD" and tvalue == "아니다":
                nt, nv = self.peek(1)
                if nt == "KEYWORD" and nv == "안에":
                    # "아니다", "안에" 소비
                    self.advance()
                    self.advance()
                    op = "not in"
                else:
                    break

            # 1) "안에" (in)
            elif ttype == "KEYWORD" and tvalue == "안에":
                self.advance()
                op = "in"

            # 2) 기존 비교 연산자들
            elif ttype == "SYMBOL" and tvalue in COMP_OPS:
                op = tvalue
                self.advance()
            else:
                break

            right = self.parse_bitor()
            ops.append(op)
            comparators.append(right)

        if not ops:
            return left
        
        return Compare(left=left, ops=ops, comparators=comparators)
    
    def parse_bitor(self) -> Expr:
        """
        bitor ::= bitxor ('|' bitxor)*
        """
        left = self.parse_bitxor()
        while self.current == ("SYMBOL", BITOR_OP):
            self.advance()
            right = self.parse_bitxor()
            left = BinOp(left=left, op="|", right=right)
        return left
    
    def parse_bitxor(self) -> Expr:
        """
        bitxor ::= bitand ('^' bitand)*
        """
        left = self.parse_bitand()
        while self.current == ("SYMBOL", BITXOR_OP):
            self.advance()
            right = self.parse_bitand()
            left = BinOp(left=left, op="^", right=right)
        return left
    
    def parse_bitand(self) -> Expr:
        """
        bitand ::= shift ('&' shift)*
        """
        left = self.parse_shift()
        while self.current == ("SYMBOL", BITAND_OP):
            self.advance()
            right = self.parse_shift()
            left = BinOp(left=left, op="&", right=right)
        return left

    def parse_shift(self) -> Expr:
        """
        shift ::= sum (('<<' | '>>') sum)*
        """
        left = self.parse_sum()
        while self.current[0] == "SYMBOL" and self.current[1] in SHIFT_OPS:
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
        term ::= factor (('*' | '/' | '//' | '%') factor)*
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
        factor ::= ('+' | '-' | '~') factor | power
        """
        tok_type, tok_value = self.current 
        if tok_type == "SYMBOL" and tok_value in ("+", "-", "~"):
            self.advance()
            operand = self.parse_factor()
            return UnaryOp(op=tok_value, operand=operand)
        return self.parse_power()
    
    def parse_power(self) -> Expr:
        """
        power ::= atom_expr ('**' factor)? (오른쪽 결합)
        """
        left = self.parse_atom_expr()
        if self.current == ("SYMBOL", POW_OP):
            self.advance()
            right = self.parse_factor()
            return BinOp(left=left, op="**", right=right)
        return left
    
    def parse_atom_expr(self) -> Expr:
        """
        atom_expr ::= NUMBER | STRING | bool/none | IDENT | '(' expr ')' | list/tuple/set/dict
                    (postfix: call/index/slice/attr)*
        """
        tok_type, tok_value = self.current
        node: Expr
        
        # 숫자
        if tok_type == "NUMBER":
            self.advance()
            if ("." in tok_value) or ("e" in tok_value) or ("E" in tok_value):
                node = Number(float(tok_value), raw=tok_value)
            else:
                node = Number(int(tok_value), raw=tok_value)
        
        # 문자열
        elif tok_type == "STRING":
            self.advance()
            node = String(tok_value)
        
        # 불리언 / None 리터럴
        elif tok_type == "KEYWORD" and tok_value in ("참", "거짓", "없음"):
            self.advance()
            if tok_value == "참":
                node = Bool(True)
            elif tok_value == "거짓":
                node = Bool(False)
            else:
                node = NoneLiteral()
        
        # 괄호식/튜플: (expr) / (a, b) / (a,) / ()
        elif tok_type == "SYMBOL" and tok_value == "(":
            self.advance() # '(' 소비

            # 빈 튜플: ()
            if self.current[0] == "SYMBOL" and self.current[1] == ")":
                self.advance()
                node = TupleLiteral(elements=[])
            else:
                first = self.parse_expr()

                # 콤마가 있으면 튜플
                if self.current[0] == "SYMBOL" and self.current[1] == ",":
                    elements: list[Expr] = [first]
                    while self.current[0] == "SYMBOL" and self.current[1] == ",":
                        self.advance() # ',' 소비
                        # trailing comma 허용: (a,)
                        if self.current[0] == "SYMBOL" and self.current[1] == ")":
                            break
                        elements.append(self.parse_expr())
                    self.expect("SYMBOL", ")")
                    node = TupleLiteral(elements=elements)
                else:
                    # 콤마가 없으면 그냥 괄호 그룹
                    self.expect("SYMBOL", ")")
                    node = first
        
        # 리스트 리터럴: [a, b, c]
        elif tok_type == "SYMBOL" and tok_value == "[":
            self.advance()
            elements: list[Expr] = []

            if not (self.current[0] == "SYMBOL" and self.current[1] == "]"):
                while True:
                    elements.append(self.parse_expr())
                    if self.current[0] == "SYMBOL" and self.current[1] == ",":
                        self.advance()
                        continue
                    break

            self.expect("SYMBOL", "]")
            node = ListLiteral(elements=elements)

        # dict/set 리터럴: {k: v} / {a, b, c}
        elif tok_type == "SYMBOL" and tok_value == "{":
            self.advance()

            # 빈 dict: {}
            if self.current[0] == "SYMBOL" and self.current[1] == "}":
                self.advance()
                node = DictLiteral(items=[])
            else:
                first = self.parse_expr()

                # dict: {key: value, ...}
                if self.current[0] == "SYMBOL" and self.current[1] == ":":
                    items: list[tuple[Expr, Expr]] = []
                    while True:
                        self.expect("SYMBOL", ":")
                        value = self.parse_expr()
                        items.append((first, value))

                        if self.current[0] == "SYMBOL" and self.current[1] == ",":
                            self.advance()
                            # trailing comma 허용
                            if self.current[0] == "SYMBOL" and self.current[1] == "}":
                                break
                            first = self.parse_expr()
                            continue
                        break

                    self.expect("SYMBOL", "}")
                    node = DictLiteral(items=items)
                else:
                    # set: {a, b, c}
                    elements: list[Expr] = [first]
                    while self.current[0] == "SYMBOL" and self.current[1] == ",":
                        self.advance()
                        # trailing comma 허용
                        if self.current[0] == "SYMBOL" and self.current[1] == "}":
                            break
                        elements.append(self.parse_expr())
                    self.expect("SYMBOL", "}")
                    node = SetLiteral(elements=elements)
        
        # 이름(변수 또는 함수호출)
        elif tok_type == "IDENT":
            ident_name = tok_value
            self.advance()
            node = Name(ident_name)
        else:
            raise SyntaxError(f"숫자/문자열/이름/괄호/리스트로 시작하는 표현식이 와야하는데 {self.current}를 만났습니다.")
        
        # postfix: 호출/인덱싱/속성접근을 연쇄로 지원
        while True:
            # 인덱싱/슬라이싱: x[0], x[1:3], x[:], x[::2]
            if self.current[0] == "SYMBOL" and self.current[1] == "[":
                self.advance()

                if self.current == ("SYMBOL", "]"):
                    raise SyntaxError("빈 인덱스는 허용되지 않습니다: x[]")
                
                # start / first
                start = None
                first = None
                if self.current != ("SYMBOL", ":"):
                    first = self.parse_expr()
                
                # ':'가 있으면 슬라이스, 아니면 인덱싱
                if self.current == ("SYMBOL", ":"):
                    start = first
                    self.advance()

                    # stop
                    if self.current not in (("SYMBOL", ":"), ("SYMBOL", "]")):
                        stop = self.parse_expr()
                    else:
                        stop = None
                    
                    # step(optional)
                    step = None
                    if self.current == ("SYMBOL", ":"):
                        self.advance()
                        if self.current != ("SYMBOL", "]"):
                            step = self.parse_expr()
                    
                    self.expect("SYMBOL", "]")
                    node = Slice(value=node, start=start, stop=stop, step=step)
                else:
                    if first is None:
                        raise SyntaxError("인덱싱 표현식이 필요합니다.")
                    self.expect("SYMBOL", "]")
                    node = Index(value=node, index=first)
                
                continue

            # 속성 접근: x.y
            if self.current[0] == "SYMBOL" and self.current[1] == ".":
                self.advance()
                if self.current[0] != "IDENT":
                    raise SyntaxError(f"'.' 다음에는 IDENT(속성 이름)이 와야 합니다: {self.current}")
                
                _, attr = self.expect("IDENT")
                node = Attribute(value=node, attr=attr)
                continue

            # 함수/메서드 호출: f(...), obj.m(...)
            if self.current[0] == "SYMBOL" and self.current[1] == "(":
                self.advance()
                args: list[Expr] = []
                keywords: list[tuple[str, Expr]] = []
                seen_kw = False
                if not (self.current[0] == "SYMBOL" and self.current[1] == ")"):
                    while True:
                        if self.current[0] == "IDENT" and self.peek(1) == ("SYMBOL", "="):
                            seen_kw = True
                            _, key = self.expect("IDENT")
                            self.expect("SYMBOL", "=")
                            val = self.parse_expr()
                            keywords.append((key, val))
                        else:
                            if seen_kw:
                                raise SyntaxError("키워드 인자 뒤에는 위치 인자를 둘 수 없습니다.")
                            args.append(self.parse_expr())
                        
                        if self.current[0] == "SYMBOL" and self.current[1] == ",":
                            self.advance()
                            if self.current[0] == "SYMBOL" and self.current[1] == ")":
                                break
                            continue
                        break
                self.expect("SYMBOL", ")")
                node = Call(func=node, args=args, keywords=keywords)
                continue
            break
        return node
    
    def parse_target(self) -> Expr:
        """대입 타겟: Name ('.' IDENT | '[' expr ']')* (호출()은 금지)"""
        _, ident_value = self.expect("IDENT")
        node: Expr
        node = Name(ident_value)

        while True:
            if self.current[0] == "SYMBOL" and self.current[1] == "[":
                self.advance()
                if self.current == ("SYMBOL", "]"):
                    raise SyntaxError("빈 인덱스는 허용되지 않습니다: x[]")
                
                first = None
                if self.current != ("SYMBOL", ":"):
                    first = self.parse_expr()

                # ":" 면 슬라이스, 아니면 인덱싱
                if self.current == ("SYMBOL", ":"):
                    start = first
                    self.advance()

                    # stop
                    if self.current not in (("SYMBOL", ":"), ("SYMBOL", "]")):
                        stop = self.parse_expr()
                    else:
                        stop = None

                    # step(optional)
                    step = None
                    if self.current == ("SYMBOL", ":"):
                        self.advance()
                        if self.current != ("SYMBOL", "]"):
                            step = self.parse_expr()
                    
                    self.expect("SYMBOL", "]")
                    node = Slice(value=node, start=start, stop=stop, step=step)
                else:
                    if first is None:
                        raise SyntaxError("인덱싱 표현식이 필요합니다.")
                    self.expect("SYMBOL", "]")
                    node = Index(value=node, index=first)
                continue

            if self.current[0] == "SYMBOL" and self.current[1] == ".":
                self.advance()
                if self.current[0] != "IDENT":
                    raise SyntaxError(f"'.' 다음에는 IDENT(속성 이름)이 와야 합니다: {self.current}")
                _, attr = self.expect("IDENT")
                node = Attribute(value=node, attr=attr)
                continue
            
            break
        
        return node
    
    def parse_augassign(self) -> AugAssign:
        """
        복합대입: IDENT ('+'|'-'|'*'|'/') '=' expr
        예: 값 += 1 (토큰은 '+', '='로 분리되어 들어옴)
        """
        target = self.parse_target()
        _, op_value = self.expect("SYMBOL")
        if op_value not in ("+", "-", "*", "/", "//", "%", "**", "<<", ">>", "&", "^", "|"):
            raise SyntaxError(f"복합대입 연산자가 올바르지 않습니다: {op_value!r}")
        self.expect("SYMBOL", "=")
        value_expr = self.parse_expr()
        return AugAssign(target=target, op=op_value, value=value_expr)

    # =====================
    #  블록(suite) 파싱
    # =====================
    
    def parse_target_list(self) -> Expr:
        """
        target_list ::= target (',' target)* [',']
        - a, b 같은 언패킹 타겟 지원
        - 1개면 그대로 반환, 2개 이상이면 TupleLiteral
        """
        first = self.parse_target()
        if self.current != ("SYMBOL", ','):
            return first
        
        elements: list[Expr] = [first]
        while self.current == ("SYMBOL", ","):
            self.advance()

            if self.current[0] in ("NEWLINE", "DEDENT", "EOF"):
                break
            if self.current == ("KEYWORD", "안에"):
                break

            elements.append(self.parse_target())

        return TupleLiteral(elements=elements)

    def parse_expr_list(self, stop_symbols: set[str] | None = None) -> Expr:
        """
        expr_list ::= expr(',' expr)* [',']
        - RHS 튜플(1,2) / 반환 a,b 등을 TupleLiteral로
        """
        if stop_symbols is None:
            stop_symbols = set()

        first = self.parse_expr()
        if self.current != ("SYMBOL", ","):
            return first
        
        elements: list[Expr] = [first]
        while self.current == ("SYMBOL", ","):
            self.advance()

            if self.current[0] in ("NEWLINE", "DEDENT", "EOF"):
                break
            if self.current[0] == "SYMBOL" and self.current[1] in stop_symbols:
                break

            elements.append(self.parse_expr())

        return TupleLiteral(elements=elements)

    def parse_dotted_name(self) -> str:
        """
        dotted_name ::= IDENT ('.' IDENT)*
        예: math / os.path / a.b.c
        """
        if self.current[0] != "IDENT":
            raise SyntaxError(f"모듈/이름은 IDENT로 시작해야 합니다: {self.current}")
        _, first = self.expect("IDENT")
        parts = [first]
        while self.current == ("SYMBOL", "."):
            self.advance()
            _, name = self.expect("IDENT")
            parts.append(name)
        return ".".join(parts)
    
    def parse_import(self) -> Import:
        """
        불러오기 module [별칭 alias] (',' module [별칭 alias])*
        예: 불러오기 math
            불러오기 os.path 별칭 경로
        """
        self.expect("KEYWORD", "불러오기")
        names: list[tuple[str, str | None]] =[]

        while True:
            module = self.parse_dotted_name()
            asname: str | None = None

            if self.current == ("KEYWORD", "별칭"):
                self.advance()
                _, asname = self.expect("IDENT")

            names.append((module, asname))

            if self.current == ("SYMBOL", ","):
                self.advance()
                continue
            break

        return Import(names=names)
    
    def parse_from_import(self) -> FromImport:
        """
        꺼내기 module 불러오기 name [별칭 alias] (',' name [별칭 alias])*
        예: 꺼내기 math 불러오기 sqrt
            꺼내기 math 불러오기 sqrt 별칭 루트
            꺼내기 math 불러오기 *
        """
        self.expect("KEYWORD", "꺼내기")
        module = self.parse_dotted_name()
        self.expect("KEYWORD", "불러오기")

        names: list[tuple[str, str | None]] = []

        if self.current == ("SYMBOL", "*"):
            self.advance()
            names.append(("*", None))
            return FromImport(module=module, names=names)
        
        while True:
            if self.current[0] != "IDENT":
                raise SyntaxError(f"불러오기 뒤에는 IDENT 또는 * 가 와야 합니다: {self.current}")
            _, name = self.expect("IDENT")

            asname: str | None = None
            if self.current == ("KEYWORD", "별칭"):
                self.advance()
                _, asname = self.expect("IDENT")

            names.append((name, asname))

            if self.current == ("SYMBOL", ","):
                self.advance()
                continue
            break

        return FromImport(module=module, names=names)
    
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
        대입문:
        - 단일: a = expr
        - 언패킹 : a, b = expr, expr
        - 연쇄: a = b = expr
        """
        left = self.parse_target_list()
        self.expect("SYMBOL", "=")

        # 언패킹 대입: 왼쪽이 튜플이면 연쇄 대입 금지
        if isinstance(left, TupleLiteral):
            value_expr = self.parse_expr_list()
            if self.current == ("SYMBOL", "="):
                raise SyntaxError("언패킹 대입에서는 연쇄 대입(a=b=...)을 지원하지 않습니다.")
            return Assign(target=left, value=value_expr)
        
        # 연쇄 대입: a = b = c
        targets: list[Expr] = [left]
        while True:
            save = self.pos
            try:
                nxt = self.parse_target()
                if self.current == ("SYMBOL", "="):
                    targets.append(nxt)
                    self.advance()
                    continue
                self.pos = save
                break
            except SyntaxError:
                self.pos = save
                break

        value_expr = self.parse_expr_list()
        if len(targets) == 1:
            return Assign(target=targets[0], value=value_expr)
        return ChainedAssign(targets=targets, value=value_expr)

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
            반복 i 안에 expr: suite
        예:
            반복 i 안에 범위(0, 10, 2):
                출력(i)
        """
        # '반복' 키워드 소비
        self.expect("KEYWORD", "반복")

        # 반복 변수 / 타겟 (언패킹 지원)
        target = self.parse_target_list()

        # in -> 안에
        self.expect("KEYWORD", "안에")

        # iterable 표현식 (범위(...) / 변수 / 함수호출 등)
        iter_expr = self.parse_expr()

        # :
        self.expect("SYMBOL", ":")

        # 본문
        body = self.parse_suite()
        
        return For(target=target, iter=iter_expr, body=body)
    
    def parse_class(self) -> ClassDef:
        """
        클래스 정의:
            클래스 이름:
                suite

            클래스 이름(베이스1, 베이스2):
                suite
        """
        self.expect("KEYWORD", "클래스")

        _, class_name = self.expect("IDENT")

        bases: list[Expr] = []
        if self.current == ("SYMBOL", "("):
            self.advance()
            if self.current != ("SYMBOL", ")"):
                while True:
                    bases.append(self.parse_expr())
                    if self.current ==("SYMBOL", ","):
                        self.advance()
                        # trailing comma 허용
                        if self.current == ("SYMBOL", ")"):
                            break
                        continue
                    break
            self.expect("SYMBOL", ")")

        self.expect("SYMBOL", ":")
        body = self.parse_suite()
        return ClassDef(name=class_name, bases=bases, body=body)

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
        params: list[Param] = []
        if not (self.current[0] == "SYMBOL" and self.current[1] == ")"):
            while True:
                _, param_name = self.expect("IDENT")
                default_val: Expr | None = None
                if self.current == ("SYMBOL", "="):
                    self.advance()
                    default_val = self.parse_expr()
                params.append(Param(name=param_name, default=default_val))

                if self.current[0] == "SYMBOL" and self.current[1] == ",":
                    self.advance()
                    if self.current[0] == "SYMBOL" and self.current[1] == ")":
                        break
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
            반환
            반환 expr
            반환 a, b   (튜플 반환)
        """
        self.expect("KEYWORD", "반환")
        if self.current[0] in ("NEWLINE", "DEDENT", "EOF"):
            return Return(value=None)
        value_expr = self.parse_expr_list()
        return Return(value=value_expr)
    
    def parse_raise(self) -> Raise:
        """
        던지기 문:
            던지기
            던지기 expr
        """
        self.expect("KEYWORD", "던지기")
        if self.current[0] in ("NEWLINE", "DEDENT", "EOF"):
            return Raise(exc=None)
        exc = self.parse_expr()
        return Raise(exc=exc)
    
    def parse_try(self) -> Try:
        """
        예외 처리:
            시도: suite
            예외 [TypeExpr] [별칭 name]: suite
            성공: suite
            마침: suite
        """
        self.expect("KEYWORD", "시도")
        self.expect("SYMBOL", ":")
        body = self.parse_suite()

        handlers: list[ExceptHandler] = []
        orelse: list[Stmt] | None = None
        finalbody: list[Stmt] | None = None

        # except handlers (0개 이상)
        while self.current == ("KEYWORD", "예외"):
            self.advance()

            exc_type: Expr | None = None
            exc_name: str | None = None

            # 예외 뒤에 ':'가 바로 오면 catch-all
            if self.current != ("SYMBOL", ":"):
                exc_type = self.parse_expr()

            if self.current == ("KEYWORD", "별칭"):
                self.advance()
                if exc_type is None:
                    raise SyntaxError("'예외 별칭 e' 형태는 지원하지 않습니다. (타입 없이 별칭 불가)")
                _, exc_name = self.expect("IDENT")

            self.expect("SYMBOL", ":")
            h_body = self.parse_suite()
            handlers.append(ExceptHandler(type=exc_type, name=exc_name, body=h_body))

        # try-else
        if self.current == ("KEYWORD", "성공"):
            self.advance()
            self.expect("SYMBOL", ":")
            orelse = self.parse_suite()

        # finally
        if self.current == ("KEYWORD", "마침"):
            self.advance()
            self.expect("SYMBOL", ":")
            finalbody = self.parse_suite()

        if not handlers and finalbody is None:
            raise SyntaxError("시도 문에는 최소 1개의 예외 블록 또는 마침 블록이 필요합니다.")
        
        return Try(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody)

    def parse_stmt(self) -> Stmt:
        ttype, tvalue = self.current

        if ttype == "KEYWORD" and tvalue == "만약":
            return self.parse_if()
        elif ttype == "KEYWORD" and tvalue == "동안":
            return self.parse_while()
        elif ttype == "KEYWORD" and tvalue == "반복":
            return self.parse_for()
        elif ttype == "KEYWORD" and tvalue == "클래스":
            return self.parse_class()
        elif ttype == "KEYWORD" and tvalue == DEF_KEYWORD:
            return self.parse_function()
        elif ttype == "KEYWORD" and tvalue == "반환":
            return self.parse_return()
        elif ttype == "KEYWORD" and tvalue == "중단":
            self.expect("KEYWORD", "중단")
            return Break()
        elif ttype == "KEYWORD" and tvalue == "계속":
            self.expect("KEYWORD", "계속")
            return Continue()
        elif ttype == "KEYWORD" and tvalue == "통과":
            self.expect("KEYWORD", "통과")
            return Pass()
        elif ttype == "KEYWORD" and tvalue == "불러오기":
            return self.parse_import()
        elif ttype == "KEYWORD" and tvalue == "꺼내기":
            return self.parse_from_import()
        elif ttype == "KEYWORD" and tvalue == "시도":
            return self.parse_try()
        elif ttype == "KEYWORD" and tvalue == "던지기":
            return self.parse_raise()
        elif ttype == "IDENT":
            pos0 = self.pos

            try:
                _ = self.parse_target_list()
                if self.current == ("SYMBOL", "="):
                    self.pos = pos0
                    return self.parse_assign()
                
                t1 = self.current
                t2 = self.peek(1)
                if t1[0] == "SYMBOL" and t1[1] in ("+", "-", "*", "/", "//", "%", "**", "<<", ">>", "&", "^", "|") and t2 == ("SYMBOL", "="):
                    self.pos = pos0
                    return self.parse_augassign()
            except SyntaxError:
                pass

            self.pos = pos0
            expr = self.parse_expr()
            return ExprStmt(value=expr)

        raise SyntaxError(f"지원하지 않는 문장 시작 토큰: {self.current}")

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

반복 i 안에 범위(0, 3):
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