# edu-v1 examples

이 폴더는 edu-v1 학습용 예제 코드를 모아둔 곳입니다.
각 `.han` 파일은 한글 파이썬 문법으로 작성되어 있으며, `edu_cli.py`로 실행해볼 수 있습니다.

## 실행 방법

```bash
py edu_cli.py examples/01_print.han
```

Python 코드로 변환만 확인하려면 다음 옵션을 사용합니다.

```bash
py edu_cli.py examples/01_print.han --no-exec
```

## 예제 목록

| 파일 | 내용 |
|---|---|
| `01_print.han` | 출력 연습 |
| `02_variable.han` | 변수 연습 |
| `03_if.han` | 조건문 연습 |
| `04_for_range.han` | `반복 i 안에 범위(...)` 연습 |
| `05_while.han` | `동안` 반복문 연습 |
| `06_function.han` | 함수 정의와 호출 연습 |
| `07_function_return.han` | 함수 반환값 연습 |
| `08_list_index.han` | 리스트와 인덱스 연습 |
| `99_error_missing_colon.han` | 콜론 누락 오류 예제 |
| `99_error_for_not_range.han` | edu-v1 범위 밖 반복문 오류 예제 |
