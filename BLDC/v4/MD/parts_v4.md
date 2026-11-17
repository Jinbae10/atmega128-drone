# 부품 목록 (v4, 스루홀)

- 기준일: 2026-11-17. 값·수량은 [drone_v4.kicad_sch](../drone_v4.kicad_sch) 기준.
- 가격 표기: "VAT 별도 / VAT 포함". **†는 웹검색 스냅샷 가격**이라 주문할 때 다시 확인해야 합니다.
- 조사 중 디바이스마트가 자동 조회를 IP 차단해서, 일부 품목은 상품 페이지를 끝까지 확인하지 못했습니다(아래 「미확인」).
- 데이터시트는 [../datasheet/](../datasheet/)에 있습니다.

## 1. 납땜 소자 (디바이스마트)

| 회로도 번호 | 소자 | 상품 | 풋프린트 (치수 근거) | 필요 | 구매 단위 | 가격 |
|---|---|---|---|---|---|---|
| R1, R2, R4~R7, R14 | 10k 1/4W ±5% 탄소피막 | [103J no=856](https://www.devicemart.co.kr/goods/view?no=856) | `R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal` (몸체 6.5×Ø2.3, 리드 Ø0.6) | 7 | 30개 | 23 / 25.3원/개 |
| R3, R12 | 1k 1/4W ±5% | [102J no=876](https://www.devicemart.co.kr/goods/view?no=876) | 위와 같음 | 2 | 30개 | 23 / 25.3원/개 |
| R13 | 2k 1/4W ±5% | [202J no=872](https://www.devicemart.co.kr/goods/view?no=872) | 위와 같음 | 1 | 30개 | 23 / 25.3원/개 |
| R8~R11 | 100Ω 1/4W ±5% | [101J no=895](https://www.devicemart.co.kr/goods/view?no=895) | 위와 같음 | 4 | 20개 | 23 / 25.3원/개 |
| C3~C7 | 100nF 50V 적층 세라믹(Y5V) | [Mono Cap 0.1uF no=1399](https://www.devicemart.co.kr/goods/view?no=1399) | `C_Disc_D5.0mm_W2.5mm_P5.00mm` (리드 간격 **미확인**, 2.54mm면 리드를 벌려 꽂음) | 5 | 10개 | 30 / 33원/개 |
| F1 | 폴리퓨즈 0.5A 홀드 / 1.1A 트립, 33V | [FRT050-33F no=10918593](https://www.devicemart.co.kr/goods/view?no=10918593) | `C_Rect_L7.2mm_W3.5mm_P5.00mm` (몸체 7.4×3.0, 리드 간격 5.1, 리드 Ø0.51) | 1 | 10개 | 140 / 154원/개 |
| D1 | 쇼트키 1N5819 40V 1A | [1N5819 no=27](https://www.devicemart.co.kr/goods/view?no=27) | `D_DO-41_SOD81_P10.16mm_Horizontal` (몸체 최대 5.2×Ø2.7, 리드 Ø0.86) | 1 | 10개 | 40 / 44원/개 |
| C1, C2 | 전해 100µF 35V Ø6.3×11 | DIP E/C KM 35V 100uF 105℃ (상품번호 **미확인**) | `CP_Radial_D6.3mm_P2.50mm` (v1과 동일) | 2 | 미확인 | 미확인 |
| SW1 | 슬라이드 SS-12D02 1P2T 0.3A | [SS-12D02 노브 6mm no=14572](https://www.devicemart.co.kr/goods/view?no=14572) | `drone_v4:SW_SS-12D02_P2.54` (v1과 동일, **핀 간격 미확인 — 2.0mm일 수 있음**) | 1 | 1개 | 150 / 165원 |
| J1, J3·J6·J7·J8, U1 장착 | 핀헤더 1×40 수 2.54mm | [no=2825](https://www.devicemart.co.kr/goods/view?no=2825) | J3·J6·J7·J8은 `PinHeader_1x03_P2.54mm_Vertical` (ESC 서보형 커넥터를 그대로 꽂음) | 1줄 (2+12+U1핀) | 1줄 | 200원† |

데이터시트: 저항 `JEIL_RD-1-4W-J.pdf`, 폴리퓨즈 `FRT050-33F.pdf`(유통사 미러본), 다이오드 `1N5819.pdf`(onsemi). `BAT43.pdf`는 디바이스마트에서 팔지 않아 참고용입니다.

### v1 대비 바뀐 소자

| 항목 | v1 | v4 | 이유 |
|---|---|---|---|
| 저항 | 2012 칩 | 1/4W 축형, 리드 간격 10.16mm | 스루홀. 몸체 최대 7.0mm라 7.62mm 간격은 빠듯함 |
| 100nF | 3216 MLCC | 리드형 Y5V 50V | 디바이스마트에서 X7R 리드형을 찾지 못함. Y5V는 용량 편차(-80%~+30%)가 크지만 5V 바이패스·ADC RC 필터 용도로는 사용 가능 |
| F1 | 3216 SMD 0.5A 24V | FRT050-33F 리드형 0.5A 33V | MF-R050·RXEF050은 재고 없음 |
| D1 | BAT54 SOT-23 | 1N5819 DO-41 | BAT85·BAT43 등 소신호 쇼트키는 재고 없음. **1N5819는 누설 전류가 커서** (분압 출력 임피던스 약 7.7kΩ) 상온에서 ADC 오차가 수 % 생길 수 있음 → 펌웨어에서 멀티미터 실측값으로 배터리 전압 보정 계수를 둘 것 |
| 20k | 10k 2개 직렬 | 그대로 유지 | 품목 수를 줄이기 위함(10k를 이미 30개 삼) |

## 2. 모듈·기타 (디바이스마트)

| 부품 | 상품 | 수량 | 가격 |
|---|---|---|---|
| MPU-6050 GY-521 | [SZH-EK007 no=1247052](https://www.devicemart.co.kr/goods/view?no=1247052) | 1 | 4,500 / 4,950원† |
| HC-06 DIP 슬레이브 | [SZH-EK105 no=1376882](https://www.devicemart.co.kr/goods/view?no=1376882) (v1.8 슬레이브 전용) | 1 | 5,500원† |
| MP1584 강압 모듈 | [SZH-PWSD-002 no=1321132](https://www.devicemart.co.kr/goods/view?no=1321132) — v1 풋프린트는 VLT-VC042 기준이라 **패드 위치 실측 필요** | 1 | 미확인 |
| XT60 암수 세트 (Amass) | [no=1078005](https://www.devicemart.co.kr/goods/view?no=1078005) | 2 | 1,600원†/세트 |
| 14AWG 실리콘 전선 | DFRobot FIT0583 1m 적/흑 (상품번호 미확인) | 1 | 1,800원† |
| 벨크로 타이 | [Coms BB881 13×300mm no=1327827](https://www.devicemart.co.kr/goods/view?no=1327827) | 1 | 1,400원† |
| 열수축 튜브 5파이 검정 1m | [no=1065347](https://www.devicemart.co.kr/goods/view?no=1065347) | 1 | 미확인 |
| 프로펠러 SMG 5045 3엽 CW/CCW | [TYE-DR086 no=15138145](https://www.devicemart.co.kr/goods/view?no=15138145) — 상세는 [motor_esc_propeller.md](motor_esc_propeller.md) | 5쌍(최소 주문) | 3,000 / 3,300원/쌍 |

## 3. 예상 합계 (VAT 포함, 구매 단위로 올림)

| 구분 | 금액 |
|---|---|
| 저항 4종 (110개) | 2,783원 |
| 100nF·폴리퓨즈·1N5819·SS-12D02 | 2,475원 |
| 핀헤더·GY-521·HC-06(EK105)·XT60 2세트·14AWG·벨크로 | 약 17,050원† |
| 프로펠러 5쌍 | 16,500원 |
| **소계** | **약 38,800원** |
| 빠진 것 | 전해 100µF ×2, MP1584, 열수축 튜브, 배송비 2,700원(66,000원 이상 무료) |

## 4. 디바이스마트에 없는 것 → 다른 곳

| 부품 | 구입처 | 비고 |
|---|---|---|
| 3S LiPo 1300~1600mAh | RC 샵 | 디바이스마트에는 단셀만 있음 |
| 3S 밸런스 충전기, LiPo 가방, 전원 분배 보드(40A 이상, 4출력) | RC 샵 | v1 목록과 같음 |
| PCB 2층 0.8mm | JLCPCB | v4 PCB 배치 후 |

## 5. 미확인 (주문 전에 상품 페이지에서 확인)

1. 100nF 리드 간격·크기 (X7R 리드형이 있으면 그쪽이 더 좋음)
2. 전해 100µF 35V 6.3×11 상품번호·가격·리드 간격(2.5mm 예상)
3. **SS-12D02 핀 간격** — 2.0mm면 `SW_SS-12D02_P2.54` 풋프린트를 고쳐야 함
4. MP1584 모듈 패드 위치 (모듈 상품이 v1 기준 VLT-VC042와 다를 수 있음)
5 †가 붙은 가격과 모든 품목 재고 (디바이스마트는 재고 수량을 공개하지 않음)
