<h1 align="center">제로음료 주유소</h1>

<p align="center">
  <strong>음료 가격도, 주유소 가격판처럼.</strong><br>
  배송비와 행사 수량을 반영해 원/L로 비교하는 토스 미니앱
</p>

<p align="center">
  <a href="#price-check">가격 검증 사례</a> ·
  <a href="#run">코드 실행</a> ·
  <a href="docs/IMPLEMENTATION.md">데이터 흐름</a>
</p>

<p align="center"><sub>데모 화면 · 합성 데이터</sub></p>

<table align="center">
  <tr>
    <td align="center">
      <img src="assets/demo-board.png" alt="합성 데이터로 실행한 개발 화면: 음료별 원/L 가격판" width="180"><br>
      <sub>가격판 · 데모</sub>
    </td>
    <td align="center">
      <img src="assets/demo-detail.png" alt="합성 데이터로 실행한 개발 화면: 구매 수량과 배송비 포함 결제가" width="180"><br>
      <sub>구매 조건 · 데모</sub>
    </td>
    <td align="center" valign="middle">
      <strong>토스에서 직접 써보기</strong><br><br>
      <a href="https://minion.toss.im/9KclBrXp"><img src="assets/open-in-toss.png" alt="토스 앱 공유 링크 QR 코드" width="128"></a><br><br>
      PC에서는 휴대폰으로 QR 스캔<br>
      모바일에서는 <a href="https://minion.toss.im/9KclBrXp">토스에서 열기 ↗</a>
    </td>
  </tr>
</table>


온라인 24캔 묶음과 편의점 2+1, 어느 쪽이 더 쌀까요? 표시 가격 대신 **실제로 내는 금액 ÷ 받는 음료의 총 용량**으로 비교합니다.

- **온라인 가격** — 배송비를 포함한 원/L와 구매 수량 확인
- **편의점 행사** — 증정 수량을 반영해 체인별 행사 비교
- **내 가격표** — 비교할 음료와 용량을 고르고, 상세에서 계산 근거 확인

## 맡은 일

기획·문제 정의·제품 판단·검토·운영을 맡았습니다. 코드 구현은 AI 코딩 도구와 협업했습니다.

개인용 **Hotdeal Agent**의 수집 기반을 활용해, 음료의 구매 조건을 검증하고 가격표로 보여주는 흐름을 만들었습니다. 두 프로젝트가 공유하는 기반 위에 음료 비교 기능을 확장한 작업입니다.

<a name="price-check"></a>

## 배송비를 모르면, 최저가라고 할 수 있을까?

상품가가 가장 낮아도 배송비를 더하면 순서가 바뀝니다. 그렇다고 배송비가 빠진 행을 버리면, 확인하지 못한 판매처를 빼고 최저가를 정하게 됩니다.

그래서 **불완전한 행도 남겨 두고, 확인된 가격보다 더 쌀 가능성이 있는지** 함께 검사합니다.

아래는 기존 검증 코드를 합성 가격으로 실행한 결과입니다. A의 상품가는 12,000원, 배송비는 3,000원입니다.

| B의 상품가 · 배송비 미확인 | A의 15,000원을 비교 후보로 쓸 수 있나? |
|---|---|
| 16,000원 | 예. B는 배송비를 더하기 전에도 비쌉니다. |
| 15,000원 | 보류. 같은 가격일 수 있습니다. |
| 14,000원 | 보류. B가 더 쌀 수 있습니다. |

같은 판매 옵션에 서로 다른 가격이 붙거나, 상품가와 배송비의 합계가 맞지 않는 경우도 걸러냅니다. 이 코드는 앱에 가격을 내보내기 전 거치는 검증 단계입니다.

[판정 코드 읽기](examples/price_evidence.py) · [경계 사례와 실행 결과](docs/VERIFICATION.md)

<a name="run"></a>

## 직접 실행

Python 3.10 이상에서 실행합니다. 패키지 설치나 API 키는 필요 없습니다.

```bash
python3 -I -B examples/demo.py
python3 -I -B tests/test_price_gate.py -v
```

첫 명령은 합성 판매처 표의 판정 결과를, 둘째 명령은 회귀 검사 결과를 출력합니다. `gate_eligible`은 가격 증거 검증을 통과한 판매처 목록입니다.

[입력 바꿔 보기](examples/scenarios.json) · [기대 출력](examples/expected.json) · [예제 연결 코드](examples/demo.py)

<details>
<summary>어떤 데이터를 거쳐 앱에 표시되나요?</summary>

수집 → 상품·수량·구매 조건 정리 → 검증 → 원/L 비교 → 앱 제공

원문 후보와 처리 결과를 보존하고, 상품 일치와 가격 조건을 검사합니다. 앱은 검증을 거쳐 만들어진 가격판·상세 데이터를 읽습니다.

[전체 흐름과 코드의 역할](docs/IMPLEMENTATION.md)

</details>

<details>
<summary>모바일 앱과 화면·코드의 출처</summary>

토스 앱 공유 주소는 프로젝트 소유자가 제공했습니다. 화면은 기존 앱 코드를 합성 데이터로 실행한 데모이며, 코드 예제도 합성 데이터로 실행합니다.

[앱 연결 정보와 구현 출처](docs/PROVENANCE.md)

</details>
