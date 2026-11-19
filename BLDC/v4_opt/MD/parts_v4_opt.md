# 부품 목록 (v4_opt, 최종)

- 기준일: 2026-11-18. 값·수량은 [drone_v4_opt.kicad_sch](../drone_v4_opt.kicad_sch) BOM 기준(v4와 소자·수량 동일, 배치·MCU 핀만 다름).
- 가격은 **VAT 포함**, 디바이스마트 상품 페이지 값(2026-11-17~18 확인). 상세 근거는 [../../v4/MD/parts_v4.md](../../v4/MD/parts_v4.md).
- **v4_opt 주의**: 모듈(U2) 아래에 저항 14개·D1·C3·C4가 들어가므로 U2 암헤더는 반드시 **8.5mm 높이(VLT-PH054 Type 1)**. 저항·D1·C3·C4를 먼저 납땜한 뒤 암헤더를 납땜합니다.

## 1. 납땜 소자 (디바이스마트)

| 회로도 번호 | 소자 | 상품 | 필요 | 구매 단위 | 가격 |
|---|---|---|---|---|---|
| R1, R2, R4~R7, R14 | 10k 1/8W 1% (20k = R1+R14 직렬) | [no=1907](https://www.devicemart.co.kr/goods/view?no=1907) | 7 | 10개 | 330원 |
| R3, R12 | 1k 1/8W | [no=2150](https://www.devicemart.co.kr/goods/view?no=2150) | 2 | 10개 | 165원 |
| R13 | 2k 1/8W | [no=2146](https://www.devicemart.co.kr/goods/view?no=2146) | 1 | 10개 | 165원 |
| R8~R11 | 100Ω 1/8W | [no=2166](https://www.devicemart.co.kr/goods/view?no=2166) | 4 | 10개 | 165원 |
| C3~C7 | 100nF 50V 적층 세라믹 | [no=1399](https://www.devicemart.co.kr/goods/view?no=1399) | 5 | 10개 | 330원 |
| F1 | 폴리퓨즈 FRT050-33F 0.5A 33V | [no=10918593](https://www.devicemart.co.kr/goods/view?no=10918593) | 1 | 10개 | 1,540원 |
| D1 | 1N4148 DO-35 | [no=25](https://www.devicemart.co.kr/goods/view?no=25) | 1 | 10개 | 220원 |
| C1, C2 | 전해 100µF 35V Ø6.3×11 | [no=12211007](https://www.devicemart.co.kr/goods/view?no=12211007) | 2 | 10개 | 440원 |
| SW1 | 슬라이드 SS-12D02 | [no=14572](https://www.devicemart.co.kr/goods/view?no=14572) | 1 | 1개 | 165원 |
| J1, J3, U1 장착 | 수 핀헤더 1×40 2.54mm | [no=2825](https://www.devicemart.co.kr/goods/view?no=2825) | 1줄 | 1줄 | 220원 |
| | | | | **소계** | **약 3,740원** |

## 2. 모듈 (디바이스마트)

| 부품 | 상품 | 수량 | 가격 |
|---|---|---|---|
| MPU-6050 GY-521 | [no=1247052](https://www.devicemart.co.kr/goods/view?no=1247052) | 1 | 4,950원 |
| HC-06 DIP 슬레이브 | [no=1376882](https://www.devicemart.co.kr/goods/view?no=1376882) | 1 | 6,050원 |
| MP1584 강압 모듈 SZH-PWSD-002 | [no=1321132](https://www.devicemart.co.kr/goods/view?no=1321132) | 1 | 2,200원 |
| | | **소계** | **13,200원** |

## 3. PCB 밖 (디바이스마트)

| 부품 | 상품 | 수량 | 가격 |
|---|---|---|---|
| 암 핀헤더 1×40 **8.5mm** (VLT-PH054) — U2·센서 소켓 | [no=15959307](https://www.devicemart.co.kr/goods/view?no=15959307) | 3 (2개면 74핀 충분, 1개 예비) | 1,320원 |
| XT60 암수 세트 | [no=1078005](https://www.devicemart.co.kr/goods/view?no=1078005) | 2 | 3,520원 |
| 열수축 튜브 5파이 1m | [no=1065347](https://www.devicemart.co.kr/goods/view?no=1065347) | 1 | 253원 |
| 프로펠러 SMG 5030 2엽 CW/CCW | [no=1342513](https://www.devicemart.co.kr/goods/view?no=1342513) | 3쌍 | 8,580원 |

## 4. 합계 (VAT 포함)

| 구분 | 금액 |
|---|---|
| 납땜 소자 | 약 3,740원 |
| 모듈 | 13,200원 |
| PCB 밖 (암헤더·XT60·열수축·프로펠러) | 13,673원 |
| **디바이스마트 부품 합계** | **약 30,613원** |
| PCB 제작 (사용자 확인 가격, 64×80mm 조건 미확인) | 19,000원 |
| 배송비 | 2,700원 |
| **디바이스마트 총액** | **약 52,313원** |

- 2026-11-18 장바구니(PCB 제외): 33,313원(배송 포함).
- `parts_v4.md` 합계(29,293원)에는 암헤더 1,320원이 빠져 있어 여기서는 포함했습니다.
- 이미 구매: 모터 MT2204 2300KV ×4, ESC LittleBee-Spring 20A ×4, 3S LiPo 1300mAh 90C XT60, 충전기 Imax B3 Pro. 보유·대여: HC-SR04, ATmega128A 모듈, JTAG ICE, AR-UART2USB.

## 5. 주문 전 확인

1. 100nF 리드 간격, SS-12D02 고정 탭, MP1584 모듈 패드 위치 (실측)
2. SW1 ON 방향(실크 ON/OFF는 추정) — 멀티미터 확인
3. 암헤더 높이 8.5mm 제품인지 확인
