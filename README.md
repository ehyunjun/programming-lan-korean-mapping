# programming-lan-korean-mapping / edu-v1

`edu-v1`은 코딩 입문자가 영어 키워드 장벽을 낮추고, 파이썬의 기본 구조를 먼저 이해할 수 있도록 만든 **학습용 한글 파이썬 변환 엔진**입니다.

이 프로젝트는 완전히 새로운 프로그래밍 언어를 만드는 것이 목적이 아닙니다.  
한글 문법으로 먼저 코딩 흐름을 익히고, 버튼 하나로 실제 Python 문법과 연결되는 **입문자용 학습형 IDE**를 만드는 것을 목표로 합니다.

예를 들어 사용자는 다음과 같이 한글로 코드를 작성할 수 있습니다.

```python
반복 i 안에 범위(1, 6):
    출력(i)
```

그리고 이를 실제 Python 코드로 변환할 수 있습니다.

```python
for i in range(1, 6):
    print(i)
```

---

## 프로젝트 목표

이 브랜치의 목표는 다음과 같습니다.

1. 한글 키워드로 파이썬 기초 문법을 학습할 수 있게 만들기
2. 한글 코드와 실제 Python 코드를 서로 연결해서 보여주기
3. 웹 IDE에서 사용할 수 있는 변환 API 만들기
4. 입문자에게 너무 어려운 문법은 숨기고, 단계적으로 학습할 수 있게 하기

최종적으로는 웹에서 다음과 같은 형태의 학습 환경을 만드는 것을 목표로 합니다.

```text
[미션 설명]     [한글 코드창]     [Python 변환 결과]
                                  [실행 결과]
```

---

## edu-v1 지원 범위

`edu-v1`은 입문자 학습용 범위만 지원합니다.

### 지원 문법

| 분류 | 한글 문법 예시 | Python 변환 |
|---|---|---|
| 출력 | `출력("안녕")` | `print("안녕")` |
| 입력 | `입력("이름: ")` | `input("이름: ")` |
| 변수 | `이름 = "현준"` | `이름 = "현준"` |
| 조건문 | `만약`, `아니면`, `그외` | `if`, `elif`, `else` |
| 반복문 | `동안` | `while` |
| 반복문 | `반복 i 안에 범위(...)` | `for i in range(...)` |
| 함수 | `정의`, `반환` | `def`, `return` |
| 기본 연산 | `+`, `-`, `*`, `/`, 비교 연산 | Python 기본 연산 |

---

## edu-v1에서 제한하는 문법

입문자 학습 흐름을 단순하게 유지하기 위해 아래 문법은 아직 지원하지 않습니다.

| 제한 문법 | 이유 |
|---|---|
| `클래스` / `class` | 객체지향은 기초 문법 이후 단계에서 다루는 것이 적절함 |
| `불러오기` / `import` | 웹 실행 환경에서 보안 문제와 복잡도가 생길 수 있음 |
| `꺼내기` / `from import` | import와 같은 이유로 제한 |
| `함께` / `with` | 파일 처리 등 고급 주제로 분리 |
| `시도`, `예외`, `마침` | 예외 처리는 기초 문법 이후 단계로 분리 |
| `던지기` / `raise` | 예외 처리와 함께 이후 단계에서 지원 예정 |
| 객체 속성 접근 | `객체.속성`, `객체.함수()`는 아직 제한 |
| 딕셔너리 / 집합 / 슬라이싱 | edu-v1 이후 단계에서 확장 예정 |

---

## 현재 파일 구조

```text
programming-lan-korean-mapping/
├── ast_demo.py
├── codegen_demo.py
├── lexer_demo.py
├── mapping.py
├── parser_demo.py
├── run_korean.py
├── tokens.py
├── edu_scope.py
├── edu_api.py
├── edu_runner.py
├── edu_cli.py
├── api_server.py
├── lessons/
│   └── lessons.json
├── examples/
│   └── *.han
├── web/
│   ├── index.html
│   ├── style.css
│   └── main.js
├── .github/
│   └── workflows/
│       └── test.yml
├── test_all.py
├── test_lesson.py
├── test_edu_error.py
├── test_edu_runner.py
├── test_edu_cli.py
├── test_examples.py
├── test_api_server.py
├── test_web_static.py
└── edu_scope_v1.md
```

현재는 기존 실험용 파일명을 유지하고 있습니다.

```text
ast_demo.py
lexer_demo.py
parser_demo.py
codegen_demo.py
```

나중에 구조가 안정화되면 아래처럼 이름을 정리할 예정입니다.

```text
ast_demo.py      → ast_nodes.py
lexer_demo.py    → lexer.py
parser_demo.py   → parser.py
codegen_demo.py  → codegen.py
run_korean.py    → runner.py 또는 cli.py
```

---

## 핵심 흐름

현재 edu-v1의 변환 흐름은 다음과 같습니다.

```text
한글 코드
  ↓
lexer_demo.py
  ↓
parser_demo.py
  ↓
AST
  ↓
edu_scope.py
  ↓
codegen_demo.py
  ↓
Python 코드
```

각 파일의 역할은 다음과 같습니다.

| 파일 | 역할 |
|---|---|
| `lexer_demo.py` | 한글 코드를 토큰으로 분리 |
| `parser_demo.py` | 토큰을 AST 구조로 변환 |
| `ast_demo.py` | AST 노드 클래스 정의 |
| `codegen_demo.py` | AST를 Python 코드 문자열로 변환 |
| `mapping.py` | 한글 키워드와 Python 키워드 매핑 |
| `tokens.py` | 토큰 타입 정의 |
| `edu_scope.py` | edu-v1에서 허용할 문법과 막을 문법 검사 |
| `edu_api.py` | 한글 코드를 Python 코드로 변환하는 변환 전용 API |
| `edu_runner.py` | 변환된 Python 코드를 실행하고 출력/오류 메시지 반환 |
| `edu_cli.py` | CLI 입력/출력 담당, `edu_api.py`와 `edu_runner.py`를 조합 |
| `api_server.py` | 로컬 웹 IDE와 API를 제공하는 `http.server` 기반 서버 |
| `lessons/lessons.json` | 웹 IDE에서 불러올 lesson 목록과 starter code |
| `examples/` | edu-v1 문법 예제와 오류 예제 |
| `web/index.html` | 로컬 서버에서 열어보는 웹 IDE 첫 화면 |
| `web/style.css` | 웹 IDE 첫 화면 스타일 |
| `web/main.js` | lesson 목록 표시, starter code 입력, `/api/compile`, `/api/run` 호출 |
| `test_lesson.py` | lessons/lessons.json 데이터 검증 |
| `test_edu_error.py` | 입문자 친화 오류 메시지 검증 |
| `test_edu_runner.py` | Python 실행 헬퍼 검증 |
| `test_edu_cli.py` | edu_cli.py example.han 실행 흐름 검증 |
| `test_examples.py` | examples/*.han 예제 검증 |
| `test_api_server.py` | `/web/`, `/lessons/lessons.json`, `/api/compile`, `/api/run` 검증 |
| `test_web_static.py` | web/ 정적 파일 구조 검증 |
| `.github/workflows/test.yml` | push/pull_request 때 `py test_all.py` 자동 실행 |
| `test_all.py` | 전체 테스트 실행 |

---

## 사용 예시

### 한글 코드

```python
점수 = 80

만약 점수 >= 60:
    출력("합격")
그외:
    출력("불합격")
```

### 변환된 Python 코드

```python
점수 = 80

if 점수 >= 60:
    print("합격")
else:
    print("불합격")
```

현재 변수명은 사용자가 작성한 이름을 그대로 유지합니다.  
즉, `점수`라는 변수명은 Python 코드에서도 그대로 유지될 수 있습니다.

---

## 실행 방법

### 기본 실행

```bash
py edu_cli.py example.han
```

`edu_cli.py`는 한글 코드 파일을 읽고, 변환된 Python 코드와 실행 결과를 함께 보여줍니다.

### 로컬 웹 IDE 실행

프로젝트 루트에서 로컬 API 서버를 실행합니다.

```bash
py api_server.py
```

브라우저에서 아래 주소로 접속합니다.

```text
http://localhost:8000/web/
```

확인이 끝나면 서버를 실행한 터미널에서 `Ctrl + C`로 종료합니다.

`web/index.html`을 더블클릭해서 `file://`로 직접 열면 브라우저 보안 정책 때문에 `lessons/lessons.json` 또는 API 호출이 정상 동작하지 않을 수 있습니다.  
반드시 `py api_server.py`로 서버를 실행한 뒤 `http://localhost:8000/web/`로 접속합니다.

### 전체 테스트 실행

```bash
py test_all.py
```

### 개별 테스트

```bash
py test_lesson.py
```

`lessons/lessons.json`이 웹 IDE에서 사용할 수 있는 형태인지 검사합니다.

```bash
py test_edu_error.py
```

콜론 누락, 들여쓰기 누락, 괄호 누락 같은 오류가 입문자에게 읽기 쉬운 한국어 메시지로 바뀌는지 검사합니다.

```bash
py test_edu_runner.py
```

변환된 Python 코드를 실행하는 `edu_runner.py`가 출력, 출력 없음, 실행 중 오류를 올바르게 처리하는지 검사합니다.

```bash
py test_edu_cli.py
```

`edu_cli.py example.han` 실행 흐름을 검증합니다.

```bash
py test_examples.py
```

`examples/*.han` 예제 파일을 검사합니다. 일반 예제는 컴파일에 성공해야 통과하고, `99_error_`로 시작하는 예제는 의도적으로 오류를 담은 예제라서 컴파일 실패해야 정상입니다.

```bash
py test_web_static.py
```

`web/` 정적 파일 구조를 검증합니다.

```bash
py test_api_server.py
```

`api_server.py`가 `/web/`, `/lessons/lessons.json`, `/api/compile`, `/api/run` 요청을 올바르게 처리하는지 검사합니다.

모든 검사를 한 번에 확인할 때는 `py test_all.py`를 사용하면 됩니다.

---

## 로컬 웹 API

`api_server.py`를 실행하면 웹 IDE와 아래 API를 함께 사용할 수 있습니다.

| 메서드 | 경로 | 역할 |
|---|---|---|
| GET | `/web/` | 웹 IDE 화면 제공 |
| GET | `/lessons/lessons.json` | 학습 lesson 목록 제공 |
| POST | `/api/compile` | 한글 코드를 Python 코드로 변환 |
| POST | `/api/run` | 한글 코드를 변환한 뒤 실행 결과 반환 |

`POST /api/compile`, `POST /api/run` 요청 본문은 아래처럼 보냅니다.

```json
{
  "source": "출력(\"안녕\")"
}
```

---

## edu_api.py 사용 예시

`edu_api.py`는 웹 IDE에서 사용할 변환 API입니다.

```python
from edu_api import compile_korean_to_python

source = """
반복 i 안에 범위(1, 6):
    출력(i)
"""

result = compile_korean_to_python(source)

if result.ok:
    print(result.python_code)
else:
    print(result.error)
```

출력 예시:

```python
for i in range(1, 6):
    print(i)
```

---

## run_korean.py, edu_api.py, edu_runner.py, edu_cli.py, api_server.py의 차이

기존 `run_korean.py`는 변환된 Python 코드를 바로 실행하는 실험용 파일입니다.

현재 `edu-v1`에서는 변환, 실행, CLI, 웹 API 책임을 나누어 둡니다.

```text
run_korean.py
→ 기존 실험용 실행 파일

edu_api.py
→ 한글 코드 → Python 코드 변환 전용

edu_runner.py
→ 변환된 Python 코드 실행 및 결과 반환

edu_cli.py
→ 터미널에서 파일 단위로 변환/실행 흐름 확인

api_server.py
→ 브라우저 웹 IDE와 연결되는 로컬 API 서버
```

웹 IDE에서는 다음과 같은 흐름으로 동작합니다.

```text
한글 코드 입력
→ Python 코드로 변환
→ 로컬 API 서버에서 실행
→ 결과 출력
```

---

## 앞으로 만들 기능

### 1단계: edu-v1 변환 엔진 안정화

- edu-v1 지원 범위 고정
- 범위 밖 문법 차단
- 한글 오류 메시지 개선
- 테스트 코드 추가

### 2단계: 학습형 CLI 만들기

```bash
py edu_cli.py example.han
```

출력 예시:

```text
[한글 코드]
...

[변환된 Python 코드]
...

[실행 결과]
...
```

### 3단계: 웹 IDE 프로토타입

- 한글 코드 입력창
- Python 변환 결과창
- 실행 결과창
- 실행하기 버튼
- 영어로 보기 버튼
- 힌트 보기 버튼

### 4단계: 학습 콘텐츠 추가

- 출력하기
- 변수 만들기
- 조건문
- 반복문
- 함수
- 리스트
- 작은 프로젝트 미션

### 5단계: 한글 ↔ 영어 스위칭

사용자가 한글 코드로 먼저 이해한 뒤, 버튼 하나로 Python 코드와 비교할 수 있게 만듭니다.

```python
만약 점수 >= 60:
    출력("합격")
```

```python
if 점수 >= 60:
    print("합격")
```

---

## 프로젝트 방향성

이 프로젝트는 단순히 Python 키워드를 한글로 바꾸는 것을 목표로 하지 않습니다.

핵심 목표는 다음과 같습니다.

```text
영어 키워드 때문에 코딩을 어렵게 느끼는 입문자가
한글 문법으로 먼저 프로그래밍의 구조를 이해하고,
점진적으로 실제 Python 문법으로 넘어갈 수 있도록 돕는 것
```

즉, 이 프로젝트는 한글 프로그래밍 언어 그 자체보다  
**입문자를 위한 학습 경험**에 초점을 둡니다.

---

## 현재 상태

현재 `edu-v1`은 로컬 웹 IDE에서 lesson을 불러오고, 한글 코드를 변환/실행 API로 확인할 수 있는 단계입니다.

```text
현재 완료 목표:
- 한글 코드 파싱
- Python 코드 생성
- edu-v1 학습 범위 검사
- CLI 실행 흐름
- 로컬 API 서버
- 웹 IDE에서 lesson 목록 표시
- 웹 IDE에서 변환/실행 API 호출
- GitHub Actions 자동 테스트

다음 목표:
- 웹 UI 개선
- lesson 학습 화면 개선
- 입문자용 힌트/설명 강화
- 더 많은 예제 lesson 추가
```

---
