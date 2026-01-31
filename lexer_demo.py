# lexer_demo.py

from mapping import KW_DEF, HAN_KEYWORDS

# 키워드 판정은 중앙 맵핑 기반으로
KEYWORDS = HAN_KEYWORDS

# def 에 해당하는 한글 키워드
DEF_KEYWORD = KW_DEF

SYMBOLS = ["(", ")", "[", "]", ":", ",", "=", "+", "-", "*", "/", "<", ">", "!"]

def simple_lexer(text: str):
    """
    데모 Lexer:
    - 줄 단위로 읽으면서 선행 공백 개수로 들여쓰기 레벨을 판단
    - 들여쓰기 증가 : INDENT 토큰
    - 들여쓰기 감소 : DEDENT 토큰
    - 각 줄 끝에 NEWLINE 토큰
    - 괄호 / 콜론 / 쉼표 / 연산자 등은 SYMBOL 토큰
    - 키워드 / 숫자 / 이름 구분
    """
    tokens = []
    indent_stack =[0] # 들여쓰기 레벨 스택

    lines = text.splitlines()

    for raw_line in lines:
        # 줄 끝 개행 문자 제거
        line = raw_line.rstrip("\n\r")

        # 완전 빈 줄이면 스킵 (브록 구조에 영향 주지 않게)
        if line.strip() =="":
            continue
        # 1) 선행 공백 개수 세기 (스페이스/탭 지원)
        indent = 0
        i = 0
        while i < len(line) and line[i] in (" ", "\t"):
            if line[i] == " ":
                indent += 1
            else:  # '\t'
                indent +=4
            i += 1
        
        # 2) 이전 줄과 들여쓰기 비교해서 INDENT / DEDENT 토큰 생성
        if indent > indent_stack[-1]:
            indent_stack.append(indent)
            tokens.append(("INDENT", ""))
        elif indent < indent_stack[-1]:
            # 한 번에 여러 레벨 줄어들 수도 있으니 while
            while indent < indent_stack[-1]:
                indent_stack.pop()
                tokens.append(("DEDENT", ""))
            if indent != indent_stack[-1]:
                raise IndentationError("들여쓰기가 일관되지 않습니다.")
            
        # 3) 실제 코드 부분(선행 공백 제거된 부분)을 토큰화
        code = line[i:]

        hash_pos = code.find("#")
        if hash_pos != -1:
            code = code[:hash_pos]

        j = 0
        while j < len(code):
            ch = code[j]

            # 공백/탭 스킵
            if ch in(" ", "\t"):
                j += 1
                continue

            # 문자열 리터럴: "..."
            if ch in('"', "'"):
                quote = ch
                j += 1
                buf = ""
                while j <len(code) and code[j] != quote:
                    buf += code[j]
                    j += 1
                # 닫는 따옴표 건너뛰기 (있다면)
                if j < len(code) and code[j] == quote:
                    j += 1
                tokens.append(("STRING", buf))
                continue

            # 심볼 (연산자, 괄호 등)
            if ch in SYMBOLS:
                tokens.append(("SYMBOL", ch))
                j += 1
                continue

            # 그외: 키워드 / 숫자 / 이름
            start = j
            while (
                j < len(code)
                and code[j] not in (" ", "\t")
                and code[j] not in SYMBOLS
                and code[j] not in ('"', "'")
            ):
                j += 1
            w = code[start:j]

            if w in KEYWORDS:
                tokens.append(("KEYWORD", w))
            elif w.isdigit():
                tokens.append(("NUMBER", w))
            else:
                tokens.append(("IDENT", w))

        # 4) 줄 끝 표시
        tokens.append(("NEWLINE", ""))

    # 파일이 끝났는데 아직 들여쓰기가 남아 있다면 모두 DEDENT
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(("DEDENT", ""))
    
    return tokens


if __name__ == "__main__":
    # 테스트용 한글 코드 한줄
    code = """만약 값 < 10:
    값 = 값 + 1
    값 = 값 + 2
그외:
    값 = 0
"""

    tokens = simple_lexer(code)

    print("입력 코드:", code)
    print(code)
    print("토큰들:")
    for t in tokens:
        print(" ", t)