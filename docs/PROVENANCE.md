# 코드·화면의 출처와 역할

[제품 소개](../README.md) · [구현 설명](IMPLEMENTATION.md)

## 기존 구현과 공개 예제의 관계

가격 파싱·판정 코드는 비공개 Zero Soda Agent의 구현에서 발췌했습니다. 외부 접속 없이 실행할 수 있도록 연결 코드와 합성 데이터를 별도로 구성했습니다.

원본 기준 커밋: `ac2fd3fbd6234a3f61f828bd05b3622113b1b1ff`. 코드 추출의 기준 버전이며 현재 운영 버전을 나타내지는 않습니다.

| 공개 파일 | 출처와 변경 범위 |
|---|---|
| [seller_table.py](../examples/seller_table.py) | 원본 `src/zero_soda_agent/danawa.py`의 가격 파싱·표 판정 함수 6개. 함수 본문·상수는 유지하고 표준 라이브러리 import와 출처 설명을 추가했습니다. HTTP 수집·HTML 파싱·목적지 조회는 제외했습니다. |
| [price_evidence.py](../examples/price_evidence.py) | 원본의 같은 이름 모듈을 그대로 가져왔습니다. |
| [demo.py](../examples/demo.py) | 원본 수집기의 행별 근거 연결 구조를 참고해 공개 예제용으로 작성했습니다. 목적지 조회 대신 합성 URL을 사용하고 저장·게시를 제외했습니다. |
| [scenarios.json](../examples/scenarios.json) · [expected.json](../examples/expected.json) | 원본의 경계 조건을 참고해 만든 합성 입력과 기대 결과입니다. 실제 판매처 응답이 아닙니다. |
| [test_price_gate.py](../tests/test_price_gate.py) | 공개 예제의 동작을 확인하는 테스트입니다. 원본 시스템의 전체 통합 테스트와는 별개입니다. |

## 화면과 앱 링크

| 자료 | 설명 |
|---|---|
| [가격판 데모](../assets/demo-board.png) · [상세 데모](../assets/demo-detail.png) | 기존 앱의 개발 브랜치 `experiment/value-first-repackage`를 합성 데이터로 실행한 캡처입니다. 가격·판매처·행사·갱신 시각은 예시이며 현재 토스 출시 화면과 다를 수 있습니다. |
| [초기 가격판](../assets/historical-online.png) | 초기 등록 자료에 포함된 과거 화면입니다. 현재 UI나 가격을 보여주는 자료는 아닙니다. |
| [토스 공유 QR](../assets/open-in-toss.png) | README의 [토스 앱 링크](https://minion.toss.im/9KclBrXp)와 같은 주소를 담고 있습니다. |

데모 원본은 `01-online-first-390x844.png`와 `03-online-detail-390x844.png`, 초기 가격판 원본은 `01-online-main-636x1048.png`입니다. 이미지 파일은 그대로 사용했습니다. 화면의 제품 식별 그림은 프로젝트의 SVG/CSS 도형이며, 별도 폰트 파일이나 제3자 로고 원본은 배포하지 않습니다.

## 역할과 AI 협업

제품의 비교 기준과 화면 구성을 정하고, 검토·운영을 맡았습니다. 코드 구현은 AI 코딩 도구와 협업했습니다. 구체적인 제품 선택은 [README의 ‘맡은 일’](../README.md#맡은-일)에 설명했습니다.

공개 예제의 함수 추출, 합성 데이터, 연결 코드, 테스트와 문서 초안은 Codex가 작성했으며, 문서 정리에도 AI 도구를 사용했습니다.

## 이용 범위

발췌한 원본 함수의 주석과 docstring을 유지했습니다. 이 저장소에는 별도의 오픈소스 라이선스를 부여하지 않았습니다. 제품명과 상표의 권리는 해당 권리자에게 있습니다.
