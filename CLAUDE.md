# 프로젝트 맥락
작업 전 노션 페이지를 먼저 읽을 것: https://app.notion.com/p/4085b14adfeb8144a6ffe57df8584b89
노션과 이 파일이 충돌하면 노션이 기준.

# 코드 전용 정보
- 빌드/실행: 아래 "환경"의 재생성 순서 참고 (펌웨어는 미착수)
- 디렉터리 구조: 아래 "파일 구성" 참고

# CLAUDE.md

ATmega128A 마이크로프로세서 텀 프로젝트 — 노트북(Tera Term)에서 블루투스로 조종하는 쿼드콥터 드론 (2인).
전체 계획·부품·결정 사항은 [drone_term_project.md](drone_term_project.md)가 기준 문서다. 결정이 바뀌면 그 문서를 함께 고친다.

## 파일 구성
| 경로 | 내용 |
|---|---|
| `drone_term_project.md` | 프로젝트 정리본 (확정 사항, 부품, 설계 제약, 확인 필요 항목) |
| `hw_block_diagram.svg` | 시스템 블록도 |
| `AT128A-70B_V20_data.md/.pdf` | 대여 MCU 모듈(AT128A-70B V2.0) 매뉴얼 — 핀맵, 회로도 요약 |
| `AR_UART2USB.md/.pdf` | USB-UART 변환 모듈(CP2102) 매뉴얼 — 유선 백업 통신 |
| `DC/` | 브러시드 DC 버전 KiCad 프로젝트 (채택안) |
| `DC/v0/` | 초기 DC 설계 (ATmega128 직접 실장안, 보관용) |
| `DC/v1/` | 현재 DC 설계 — AT128A-70B 모듈 암헤더 장착 |
| `DC/v1/gen_sch.py` | DC v1 회로도(`drone_dc_v1.kicad_sch`)를 KiCad 기본 라이브러리로 생성하는 스크립트 |
| `DC/v1/gen_fp.py` | 모듈 풋프린트(`drone_dc_v1.pretty`) 생성 — 모듈 핀 줄 간격 `ROW_SPACING` |
| `DC/v1/gen_pcb.py` | PCB 생성: 배치 → Freerouting 자동 배선 → GND 폴리곤 (KiCad python으로 실행) |
| `DC/v1/gerber/` | 제작용 거버·드릴 (PCB 재생성 후 다시 출력해야 함) |
| `DC/v2/` | v1과 같은 회로, **스루홀(THT) 부품** PCB (세워 꽂는 1/4W 저항·1N5819, 디스크/전해 커패시터) 60×100mm. 스크립트 구조는 v1과 동일 |
| `DC/v3/v3_plan.md` | v3 계획 — 1020 7.4V 모터 + 2S 배터리 (추력 부족 대응, 미착수) |
| `BLDC/` | BLDC 버전 KiCad 프로젝트 (비교용, 미채택) |

`.history/`, `.mcp-backups/`, `*.bak`는 KiCad·MCP 자동 백업이다. 편집하지 말 것.

## 환경
- 펌웨어: AVR Studio 4.19 + WinAVR-20100110 (avr-gcc, 구버전 — 최신 C 문법 주의), JTAG ICE
- PCB: KiCad (`D:/app/kicad`), kicad MCP 사용 가능
- `gen_sch.py`는 경로가 하드코딩되어 있다(`LIB`, `OUT`). 실행: `python DC/v1/gen_sch.py`
- 전체 재생성 순서 (v2도 같음, 경로만 `DC/v2`): `python DC/v1/gen_fp.py` → `python DC/v1/gen_sch.py` → `D:/app/kicad/bin/python.exe DC/v1/gen_pcb.py`
  → `kicad-cli pcb drc` → `kicad-cli pcb export gerbers` / `export drill` (출력 폴더 `DC/v1/gerber/`)
- PCB 배선 방식 (`gen_pcb.py`): 전원(VBAT·모터 루프·MOSFET 소스)은 `power_routes()`에서 좌표로 직접 배선(고정),
  GND는 자동 배선하지 않고 양면 폴리곤 + 패드별 GND 비아(배선 전 fan-out) + 스티칭/섬 비아로 연결,
  Freerouting은 신호·+5V만 배선하며 뒷면 비용을 높여(`RULES`) 뒷면을 GND 플레인으로 유지한다
- Freerouting 결과는 입력에 따라 민감하다. 미배선이 남으면 `_unrouted_debug.kicad_pcb`로 저장되니 DRC로 원인 확인
- `drone_dc_v1.kicad_dru`: THT GND 핀의 서멀 스포크 최소 1개 허용 (손납땜용 서멀 릴리프 유지)
- pcbnew python 주의: `BOARD.Remove()` 후 SWIG 객체가 깨진다 → 매번 `NewBoard`로 새로 만들고, 풋프린트는 보드 작업 전에 미리 로드

## 하드웨어 제약 (꼭 지킬 것)
- MCU 16MHz, 5V 전원 (1S LiPo → MT3608 승압). 모터는 배터리 직결 + SI2302 저측 스위칭
- **PF4–PF7은 JTAG** → ADC는 PF0–PF3만. 퓨즈 변경 금지 (JTAGEN/SPIEN)
- **USART1 = PD2(RXD1)/PD3(TXD1)** — 모듈 USART 커넥터, HC-06, AR-UART2USB 공용. INT2/INT3 사용 불가
- I²C(TWI) = PD0/PD1 (MPU-6050)
- ISP는 PB2/PB3가 아니라 **PE0(PDI)/PE1(PDO)** + PB1(SCK)
- 보율 9600/19200만 (16MHz에서 115200은 오차 -3.5%)
- 대여 모듈은 납땜·개조 금지, 암헤더로 탈착
- HC-06 RX는 3.3V → TXD1 출력은 1kΩ/2kΩ 분압
- 총무게 약 75g 이하 (8520 ×4 추력 기준)

## 작업 규칙
- 답변·문서는 한국어
- 부품값·핀 할당을 바꾸면 회로도와 `drone_term_project.md`를 같이 맞춘다
