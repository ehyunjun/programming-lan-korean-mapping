# Programming Language Korean Mapping

Python의 핵심 문법을 한국어 키워드로 표현하고,  
한글 코드와 영어 코드 간 변환을 지원하는 교육용 프로그래밍 프런트엔드 프로젝트입니다.

이 프로젝트는 단순 문자열 치환기가 아니라,  
lexer / parser / AST / code generator 구조를 직접 구현하여  
한글 프로그래밍 문법의 가능성을 탐구하는 것을 목표로 합니다.

---

## Why this project?

코딩 입문자는 `print`, `if`, `while`, `return` 같은 영어 키워드부터 낯설게 느끼는 경우가 많습니다.  
이 프로젝트는 초·중·고 및 코딩 입문자가 Python의 핵심 문법을 한국어 키워드로 먼저 익히고,  
이후 영어 코드와 자연스럽게 연결될 수 있도록 돕기 위해 시작되었습니다.

또한 포트폴리오 목적으로,  
단순 치환이 아닌 lexer / parser / AST / code generation 기반의 언어 처리 구조를 직접 구현하는 데 의미를 두고 있습니다.

---

## Features

- Python 핵심 문법의 한국어 키워드 매핑
- 한글 코드 → 영어 Python 코드 변환
- 영어 Python 코드 → 한글 코드 변환
- lexer / parser / AST / code generator 분리 구조
- 교육용 문법 범위 내 코드 실행 파이프라인
- 일부 에러 메시지 한국어화 (진행 중)

---

## Example

### Korean-style code
```python
x = 10

만약 x > 5:
    출력("5보다 큽니다")
아니면:
    출력("5 이하입니다")
