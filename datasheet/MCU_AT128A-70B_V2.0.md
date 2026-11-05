# AT128A-70B V2.0 매뉴얼 (ATmega128A-AU MCU, Manual Ver 2.0)

> 출처: `MCU_AT128A-70B_V2.0.pdf` — 엠에이아이 (www.maicom.co.kr)

## 1. 모델 이름
AT128A-70B V2.0 (ATmega128A-AU **브레드보드 타입**)

## 2. 용도
ATmega128A-AU MCU의 학습 및 개발용 브레드보드 타입 MCU 보드. USART 커넥터가 장착되어 있다.

## 3. 제품 사양
1. ATmega128A-AU MCU
2. 6핀 ISP 커넥터, 10핀 JTAG 커넥터로 디버깅 포트 확장
3. Flash 128KB / EEPROM 4KB / SRAM 4KB
4. 16MHz 크리스털, 녹색 전원 확인 LED, 외부 POWER 커넥터 (케이블 별도)
5. USART 커넥터 장착 → AR-UART2USB와 바로 연결 가능

## 4. 외형
- 크기: **25.4mm × 76.2mm**
- 상단: USART 커넥터(`5V, RX, TX, GND`), 외부전원 커넥터(`5V, GND`)

### 핀 배치 (위에서 본 기준, 좌/우 헤더)
| 좌측 | 우측 |
|---|---|
| /PEN | PF0 |
| PE0 | PF1 |
| PE1 | PF2 |
| PE2 | PF3 |
| PE3 | PF4 |
| PE4 | PF5 |
| PE5 | PF6 |
| PE6 | PF7 |
| PE7 | /RST |
| **VCC** | **GND** |
| PB0 | PA0 |
| PB1 | PA1 |
| PB2 | PA2 |
| PB3 | PA3 |
| PB4 | PA4 |
| PB5 | PA5 |
| PB6 | PA6 |
| PB7 | PA7 |
| PG3 | PG2 |
| PG4 | PG1 |
| **GND** | PG0 |
| PD0 | PC7 |
| PD1 | PC6 |
| PD2 | PC5 |
| PD3 | PC4 |
| PD4 | PC3 |
| PD5 | PC2 |
| PD6 | PC1 |
| PD7 | PC0 |

## 5. 각 부분 설명
| 부분 | 설명 |
|---|---|
| USART 커넥터 | 5V, RX, TX, GND (4핀 하네스) |
| 외부전원 커넥터 | 외부 5V 입력 |
| JTAG 커넥터 | 10핀 디버깅 포트 |
| ATmega128A-AU | 메인 MCU (64핀 TQFP) |
| 16MHz | 크리스털 발진자 |
| 6핀 ISP 커넥터 | 프로그램 다운로드 |
| RESET 스위치 | 수동 리셋 |
| 녹색 전원 LED | 전원 확인 |

## 6. AR-UART2USB 연결
보드 상단 USART 커넥터에 AR-UART2USB의 4핀 하네스 케이블을 꽂고, USB로 PC에 연결한다. (상세: [USB-UART_AR-UART2USB.md](USB-UART_AR-UART2USB.md))

## 7. 회로도 요약

### 전원 / 리셋 / 클럭
- **VCC_BB**: 보드 전원 레일 (VCC 21, 52핀)
- **AVCC / AREF (64, 62핀)**: L1 10µH 인덕터를 거쳐 VCC에 연결, C6 1µF 디커플링
- 디커플링: C4 10µF, C5 1µF
- **전원 LED**: LED1 + R3 820Ω
- **외부전원**: CON2
- **리셋**: R1 10kΩ 풀업 + C1 1µF + D1(1N4148) + SW1 → /RST(20핀)
- **/PEN (1핀)**: R2 10kΩ 풀업
- **크리스털**: X1 16.0MHz, C2·C3 20pF (XTAL1 24핀, XTAL2 23핀)

### USART (J3, 4핀 하네스)
| MCU 핀 | 기능 | 경유 | J3 |
|---|---|---|---|
| PD2 (27핀) | RXD1 | 1kΩ (R12) | RX |
| PD3 (28핀) | TXD1 | 1kΩ (R6) | TX |
| — | — | — | VCC (VCC_BB) |
| — | — | — | GND |

> 이 커넥터는 ATmega128의 **USART1** 에 연결되어 있다 (USART0 아님).

### ISP (J2, 6핀 Box)
| 핀 | 신호 | MCU 핀 |
|---|---|---|
| 1 | MISO | **PE1** (TXD0/PDO) |
| 2 | VCC | VCC_BB |
| 3 | SCK | PB1 |
| 4 | MOSI | **PE0** (RXD0/PDI) |
| 5 | /RST | /RST |
| 6 | GND | GND |

> ATmega128의 ISP는 PB2/PB3가 아니라 **PE0(PDI)/PE1(PDO)** 를 사용한다.

### JTAG (J1, 10핀)
| 핀 | 신호 | 핀 | 신호 |
|---|---|---|---|
| 1 | TCK (PF4) | 2 | GND |
| 3 | TDO (PF6) | 4 | VREF (VCC_BB) |
| 5 | TMS (PF5) | 6 | /RST |
| 7 | VDD (VCC_BB) | 8 | NC |
| 9 | TDI (PF7) | 10 | GND |

- PF4~PF7에 4.7kΩ 풀업 저항(R8~R11)
- JTAG 퓨즈(JTAGEN)가 켜져 있으면 PF4~PF7을 일반 I/O로 쓸 수 없다.
