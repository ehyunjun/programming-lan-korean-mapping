# lexer_demo.py
# 한글 키워드 목록
KEYWORDS = {"함수", "만약", "아니면", "그외", "반환", "동안"}

def simple_lexer(text: str):
	"""
	데모 Lexer:
	- 괄호 / 콜론 / 쉼표를 따로 떼어내고
	- 공백 기준으로 쪼개서
	- 키워드 / 기호 / 숫자 / 이름 을 구분만 해본다.
	"""

	# 기호들 주변에 공백을 넣어서 분리하기 쉽게 만든다.
	for ch in ["(", ")", ":", ",", "=", "+", "-", "*", "/", "<", ">"]:
		text = text.replace(ch, f" {ch} ")

	words = text.split()
	tokens = []

	for w in words:
		if w in KEYWORDS:
			tokens.append(("KEYWORD", w))
		elif w in ["(", ")", ":", ",", "=", "+", "-", "*", "/", "<", ">"]:
			tokens.append(("SYMBOL", w))
		elif w.isdigit():
			tokens.append(("NUMBER", w))
		else:
			# 나머지는 일단 "이름" 취급
			tokens.append(("IDENT", w))
	return tokens

if __name__ == "__main__":
	# 테스트용 한글 코드 한줄
	code = "만약 값 < 10: 값 = 값 + 1"

	tokens = simple_lexer(code)

	print("입력 코드:", code)
	print("토큰들:")
	for t in tokens:
		print(" ", t)