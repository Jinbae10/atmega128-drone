// 30cm급 BLDC 쿼드콥터 스케치 (anatomy 스킬). 실행: node sketch/drone30/build.mjs [--light]
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "file:///C:/Users/skn29/.claude/skills/anatomy/kit/iso-kit.mjs";
import { kitScript } from "file:///C:/Users/skn29/.claude/skills/anatomy/scripts/inline-kit.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const theme = process.argv.includes("--light") ? "light" : "dark";
const WIDTH = 740;
const HEIGHT = 500;

// 세계 단위 = 1 mm. 모터 대각 간격 300 mm (300급 X 프레임)
const HALF = 40; // 중앙 판 ±40
const ARM_W = 9; // 암 반폭
const PAD_R = 17; // 모터 마운트 패드
const MD = 150; // 중심 → 모터 거리
const FRAME_H = 4;
const PROP_R = 76; // 6인치 프롭
const PROP_Z = 25;
const FLOOR = -33;
const LIFT_MAX = 45;

// 무게·추력 모델 (추정값, 실측으로 교체)
const MASS = { 프레임: 110, 모터: 4 * 28, ESC: 4 * 8, 프롭: 4 * 6, 배터리: 125, 보드: 35, 배선: 25 };
const AUW = Object.values(MASS).reduce((a, b) => a + b, 0); // 463 g
const THRUST_MAX = 600; // 2205 2300KV + 6045, 3S, 모터 1개 최대 추력 (g)
const RPM_MAX = 20000;

const P = k.fitProjection(
  [45, 135, 225, 315].flatMap((deg) => {
    const t = (deg * Math.PI) / 180;
    return Array.from({ length: 24 }, (_, n) => {
      const a = (n / 24) * Math.PI * 2;
      return [MD * Math.cos(t) + PROP_R * Math.cos(a), MD * Math.sin(t) + PROP_R * Math.sin(a), n % 2 ? FLOOR : PROP_Z + LIFT_MAX];
    });
  }),
  WIDTH,
  HEIGHT,
  { pad: 18, azimuth: 45 },
);

const at = (p) => k.iso(p, P);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (pts, style) => k.dotsSvg(pts, style);
const depth = ([x, y]) => k.depthOf([x, y, 0], P);
const box = (x, y, w, d, z, h, r = 0.6) => k.slabOf({ x, y, w, d, r }, z, h, P, 2);

// 대각 암 4개: u = 암 방향, v = u를 90° 돌린 방향. 대각끼리 같은 회전 방향
const ARMS = [45, 135, 225, 315].map((deg, i) => {
  const t = (deg * Math.PI) / 180;
  const u = [Math.cos(t), Math.sin(t)];
  const v = [-u[1], u[0]];
  return { i, u, v, M: [MD * u[0], MD * u[1]], dir: i % 2 ? -1 : 1 };
});
const along = (q, a, b) => [a * q.u[0] + b * q.v[0], a * q.u[1] + b * q.v[1]];
const at3 = (q, a, b, z) => [...along(q, a, b), z];
const armBox = (q, a0, a1, hw, z, h) => k.extrude([[a0, -hw], [a1, -hw], [a1, hw], [a0, hw]].map(([a, b]) => along(q, a, b)), z, h, P);
const armRing = (q, a0, a1, hw) => [[a0, -hw], [a1, -hw], [a1, hw], [a0, hw]].map(([a, b]) => along(q, a, b));

// X 프레임 외곽 하나 (중앙 사각 + 암 + 패드)
function frameRing() {
  const ring = [];
  const entry = HALF * Math.SQRT2 - ARM_W;
  const beta = Math.asin(ARM_W / PAD_R);
  for (const q of ARMS) {
    ring.push(along(q, entry, -ARM_W));
    for (let s = 0; s <= 24; s++) {
      const phi = -(Math.PI - beta) + (s / 24) * 2 * (Math.PI - beta);
      ring.push(along(q, MD + PAD_R * Math.cos(phi), PAD_R * Math.sin(phi)));
    }
    ring.push(along(q, entry, ARM_W));
  }
  return ring;
}

function below() {
  const items = [];
  // 배터리 3S 1500mAh + 벨크로 스트랩 2줄
  const bat = { x: -52, y: -17.5, w: 104, d: 35, r: 3 };
  let b = S(k.slabOf(bat, -25, 24, P, 4, 0.8), { tone: "lo" });
  b += L(k.sideSeam(bat, -20, P, 4), { tone: "faint" });
  for (const cx of [-25, 25]) b += S(k.slabOf({ x: cx - 10, y: -18.7, w: 20, d: 37.4, r: 1.5 }, -26, 26, P, 3), { tone: "mid" });
  items.push({ key: 0, svg: b });
  // 착지 다리
  for (const q of ARMS) {
    const [x, y] = along(q, 118, 0);
    items.push({ key: depth([x, y]), svg: S(k.cylinder(x, y, 6, FLOOR, 3, P, 20), { tone: "lo" }) + S(k.cylinder(x, y, 4, FLOOR + 3, -FLOOR - 3, P, 20), { tone: "mid" }) });
  }
  return items.sort((a, b) => a.key - b.key).map((i) => i.svg).join("");
}

function frame() {
  const out = [S(k.extrude(frameRing(), 0, FRAME_H, P, { convex: false }), { tone: "mid" })];
  const z = FRAME_H;
  out.push(L(k.planOutline({ x: -34, y: -34, w: 68, d: 68, r: 4 }, z, P), { tone: "faint" }));
  for (const q of ARMS) {
    out.push(L(k.onTop(armRing(q, 104, 128, 3), z, P, true), { tone: "lo" })); // 경량 슬롯
    const bolts = [along(q, 58, -5), along(q, 58, 5)];
    out.push(L(bolts.map(([x, y]) => k.ring(x, y, 1.8, z, P, 14)).join(""), { tone: "lo" }));
    out.push(D(bolts.map(([x, y]) => at([x, y, z])), { size: 0.5 }));
    const pads = [along(q, 40, -3), along(q, 40, 3)]; // 전원 분배 패드
    out.push(S(k.extrude(armRing(q, 38, 42, 5), z, 0.3, P), { tone: "lo", flat: true }));
    out.push(D(pads.map(([x, y]) => at([x, y, z + 0.3])), { size: 0.6, tone: "hi" }));
  }
  return out.join("");
}

// 배터리 리드 → XT60 → 프레임 아래 전원 패드
function powerLead() {
  const out = [];
  out.push(wire([52, -4, -12], [60, -4, -12]), wire([52, 4, -12], [60, 4, -12]));
  out.push(S(k.slabOf({ x: 60, y: -8, w: 16, d: 16, r: 2 }, -18, 12, P, 3, 0.5), { tone: "mid" }));
  out.push(S(k.slabOf({ x: 76, y: -6, w: 3, d: 12, r: 1 }, -16, 8, P, 2), { tone: "lo" }));
  out.push(wire([60, -3, -6], [40, -3, 0], [[56, -3, -2]]), wire([60, 3, -6], [40, 3, 0], [[56, 3, -2]]));
  return out.join("");
}

function wire(a, b, via = [], tone = "lo") {
  return k.wireSvg(at(a), at(b), { via: via.map(at), tone, size: 0.9 });
}

function motor(q) {
  const [x, y] = q.M;
  const out = [];
  out.push(S(k.cylinder(x, y, 13.5, FRAME_H, 3, P, 40), { tone: "lo" }));
  out.push(S(k.cylinder(x, y, 14, 7, 12, P, 48, 0.6), { tone: "hi", crease: "lo" }));
  out.push(L(k.knurl(x, y, 14, 9.5, 16.5, 30, P, 0.6), { tone: "lo" })); // 냉각 슬롯
  out.push(L(k.ring(x, y, 9, 19, P, 40), { tone: "lo" }));
  const screws = [0, 1, 2, 3].map((n) => [x + 6 * Math.cos(n * Math.PI / 2 + 0.6), y + 6 * Math.sin(n * Math.PI / 2 + 0.6)]);
  out.push(D(screws.map(([sx, sy]) => at([sx, sy, 19])), { size: 0.55 }));
  out.push(S(k.cylinder(x, y, 2.5, 19, 4, P, 16), { tone: "mid" }));
  return out.join("");
}

function arm(q) {
  const parts = [];
  // ESC 20A (수축튜브) + 케이블 타이 2개
  let esc = S(armBox(q, 66, 100, 7, FRAME_H, 6), { tone: "mid" });
  for (const a of [72, 94]) esc += S(armBox(q, a - 1.2, a + 1.2, 7.6, FRAME_H, 6.6), { tone: "lo", crease: "none" });
  parts.push({ key: depth(along(q, 83, 0)), svg: esc });
  // 모터 3선 (ESC → 모터), 전원 2선 (패드 → ESC)
  let w = "";
  for (const b of [-3.5, 0, 3.5]) w += wire(at3(q, 100, b, 7), at3(q, MD - 13.6, b, 5.5), [at3(q, 118, b, 5)]);
  for (const b of [-3, 3]) w += wire(at3(q, 40, b, FRAME_H + 0.3), at3(q, 66, b, 6.5), [at3(q, 54, b, 5.2)], b < 0 ? "mid" : "lo");
  parts.push({ key: depth(along(q, 118, 0)) + (q.u[0] + q.u[1] > 0 ? -1 : 1), svg: w });
  parts.push({ key: depth(q.M), svg: motor(q) });
  const sorted = parts.sort((a, b) => a.key - b.key).map((p) => p.svg).join("");
  // 신호선 (서보 PWM): ESC 안쪽 끝 → 보드 모서리 3핀 헤더
  const hx = Math.sign(q.u[0]) * 41, hy = Math.sign(q.u[1]) * 20;
  const sig = wire(at3(q, 66, 0, 10), [hx, hy, 30], [at3(q, 60, 0, 22), [hx + Math.sign(q.u[0]) * 3, hy + Math.sign(q.u[1]) * 8, 32]], "hi");
  const disc = `<g data-disc="${q.i}" opacity="0">${L(k.ring(q.M[0], q.M[1], PROP_R, PROP_Z + 0.7, P, 72), { tone: "faint", dotted: true })}</g>`;
  return sorted + sig + disc + `<g data-prop="${q.i}">${propSvg(k, P, q.M, 0)}</g>`;
}

// 2엽 6045 프롭: 매 프레임 다시 그린다 (z축 회전은 화면 변환으로 안 됨)
function propSvg(K, P, M, theta) {
  const R = 76, Z = 25, HUB = 6;
  const blade = (t) => {
    const c = Math.cos(t), s = Math.sin(t);
    const pt = (r, w) => [M[0] + r * c - w * s, M[1] + r * s + w * c];
    const hw = (r) => 2.5 + 3.5 * Math.sin((Math.PI * (r - HUB)) / 80);
    const side = [];
    for (let r = HUB; r <= R - 6; r += 4) side.push(r);
    const tipW = hw(R - 6);
    const ring = side.map((r) => pt(r, hw(r)));
    for (let n = 1; n < 8; n++) { const a = Math.PI / 2 - (n / 8) * Math.PI; ring.push(pt(R - 6 + tipW * Math.cos(a), tipW * Math.sin(a))); }
    for (const r of [...side].reverse()) ring.push(pt(r, -hw(r)));
    return { key: K.depthOf([M[0] + 40 * c, M[1] + 40 * s, 0], P), svg: K.solidSvg(K.extrude(ring, Z, 1.5, P), { tone: "mid", crease: "lo" }) };
  };
  const blades = [blade(theta), blade(theta + Math.PI)].sort((a, b) => a.key - b.key);
  const mid = K.depthOf([M[0], M[1], 0], P);
  const hub = K.solidSvg(K.cylinder(M[0], M[1], HUB, 23, 5, P, 24), { tone: "mid" });
  const nut = K.solidSvg(K.cylinder(M[0], M[1], 4.5, 28, 3, P, 6), { tone: "hi" }) + K.solidSvg(K.cylinder(M[0], M[1], 2.5, 31, 1.5, P, 14), { tone: "mid" });
  return blades.filter((b) => b.key < mid).map((b) => b.svg).join("") + hub + blades.filter((b) => b.key >= mid).map((b) => b.svg).join("") + nut;
}

// 중앙 스택: 스탠드오프 → 캐리어 PCB → AT128A-70B 모듈(암헤더) → 센서·BT·분압저항·헤더
const CZ = 20; // 캐리어 PCB 바닥
const CT = CZ + 1.6;
function centre() {
  const out = [];
  const stand = [[-36, -10], [36, -10], [-36, 10], [36, 10]].sort((a, b) => depth(a) - depth(b));
  for (const [x, y] of stand) out.push(S(k.cylinder(x, y, 2.5, FRAME_H, CZ - FRAME_H, P, 6), { tone: "lo" }));
  const carrier = { x: -45, y: -25, w: 90, d: 50, r: 2 };
  out.push(`<path class="iso-halo" d="${k.haloOf(k.insetPlan(carrier, 4), FRAME_H, 0.1, P)}" style="filter:blur(3px)"/>`);
  out.push(S(k.slabOf(carrier, CZ, 1.6, P, 4, 0.5), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(carrier, 1.5), CT, P, 4), { tone: "faint" }));
  out.push(D(stand.map(([x, y]) => at([x, y, CT])), { size: 0.7, tone: "hi" }));
  out.push(L(stand.map(([x, y]) => k.ring(x, y, 2.6, CT, P, 14)).join(""), { tone: "lo" }));

  const items = [];
  const header3 = (cx, cy) => {
    let s = box(cx - 1.27, cy - 3.8, 2.54, 7.6, CT, 2.5, 0.3);
    s = S(s, { tone: "lo" });
    for (const dy of [-2.54, 0, 2.54]) s += S(box(cx - 0.32, cy + dy - 0.32, 0.64, 0.64, CT + 2.5, 5.9, 0.1), { tone: "hi", crease: "none" });
    return s;
  };
  for (const [cx, cy] of [[-41, -20], [41, -20], [-41, 20], [41, 20]]) items.push({ key: depth([cx, cy]), svg: header3(cx, cy) });

  // 모듈 스택 (한 덩어리로 정렬)
  let m = "";
  for (const ry of [-21.7, 1.1]) m += S(box(-37.5, ry - 1.27, 75, 2.54, CT, 8.5, 0.3), { tone: "lo" });
  const MZ = CT + 8.5;
  const MT = MZ + 1.6;
  const mod = { x: -38.1, y: -23, w: 76.2, d: 25.4, r: 1 };
  m += S(k.slabOf(mod, MZ, 1.6, P, 3, 0.5), { tone: "hi" });
  for (const ry of [-21.7, 1.1]) m += D(Array.from({ length: 30 }, (_, n) => at([-36.8 + n * 2.54, ry, MT])), { size: 0.45, tone: "lo" });
  const mparts = [];
  // HC-49 크리스탈 16MHz
  const xtal = { x: -26, y: -12.6, w: 11, d: 4.6, r: 2.2 };
  mparts.push({ key: depth([-20.5, -10.3]), svg: S(k.slabOf(xtal, MT, 3.5, P, 6, 0.4), { tone: "mid", inner: L(k.sideSeam(xtal, MT + 0.8, P, 6), { tone: "lo" }) }) });
  // ATmega128A TQFP-64 (리드 프레임 + 몸체) — 강조 부품
  mparts.push({ key: depth([0, -10.3]), svg: S(box(-8, -18.3, 16, 16, MT, 0.25, 0.2), { tone: "lo", flat: true }) + S(box(-7, -17.3, 14, 14, MT, 1.2, 0.4), { tone: "hi", lit: true }) + D([at([-5, -15.3, MT + 1.2])], { size: 0.6, tone: "lo" }) });
  // JTAG 2×5 박스 헤더
  const jt = { x: 22, y: -20.5, w: 8.9, d: 20.3, r: 0.6 };
  mparts.push({ key: depth([26.4, -10.3]), svg: S(k.slabOf(jt, MT, 9, P, 2, 0.3), { tone: "lo" }) + L(k.planOutline(k.insetPlan(jt, 1.3), MT + 9, P, 2), { tone: "mid" }) + D(Array.from({ length: 10 }, (_, n) => at([24.6 + (n % 2) * 2.54 + 1.2, -15.4 + Math.floor(n / 2) * 2.54, MT + 9])), { size: 0.4, tone: "hi" }) });
  // 리셋 스위치 + LED 2개 + 0805 캡
  mparts.push({ key: depth([-31.5, -4]), svg: S(box(-34.5, -7, 6, 6, MT, 3.5, 0.6), { tone: "lo" }) + S(k.cylinder(-31.5, -4, 1.75, MT + 3.5, 1, P, 16), { tone: "hi" }) });
  for (const [cx, cy, tone] of [[-33, -14, "hi"], [-33, -18, "mid"], [10, -3.5, "lo"], [10, -17, "lo"], [-10, -3.5, "lo"]]) mparts.push({ key: depth([cx, cy]), svg: S(box(cx - 1, cy - 0.62, 2, 1.25, MT, 0.8, 0.2), { tone }) });
  m += mparts.sort((a, b) => a.key - b.key).map((p) => p.svg).join("");

  // 왼쪽 뒤 헤더 → 모듈 → 나머지 앞쪽 부품
  out.push(items.shift().svg);
  out.push(m);

  // GY-521 (MPU-6050)
  let gy = S(box(-32, 6, 19, 2.5, CT, 2.5, 0.3), { tone: "lo" });
  const gyp = { x: -33, y: 5.5, w: 21, d: 16, r: 1 };
  gy += S(k.slabOf(gyp, CT + 2.5, 1.6, P, 3, 0.4), { tone: "mid" });
  gy += L([[-31.3, 19.8], [-13.7, 19.8]].map(([x, y]) => k.ring(x, y, 1.3, CT + 4.1, P, 12)).join(""), { tone: "lo" });
  gy += D(Array.from({ length: 8 }, (_, n) => at([-31.4 + n * 2.54, 7.25, CT + 4.1])), { size: 0.4, tone: "lo" });
  gy += S(box(-24.5, 12, 4, 4, CT + 4.1, 0.9, 0.2), { tone: "hi" }) + S(box(-29, 15, 3, 1.6, CT + 4.1, 1, 0.2), { tone: "lo" });
  items.push({ key: depth([-22.5, 13.5]), svg: gy });
  // HC-06 (베어 보드, 하프홀 납땜)
  const hc = { x: -9.5, y: 7, w: 27, d: 13, r: 0.8 };
  let h = S(k.slabOf(hc, CT, 0.8, P, 2, 0.3), { tone: "mid" });
  h += D(Array.from({ length: 13 }, (_, n) => [at([-8 + n * 1.5, 7.6, CT + 0.8]), at([-8 + n * 1.5, 19.4, CT + 0.8])]).flat(), { size: 0.35, tone: "hi" });
  h += S(box(-6.5, 10.3, 6.4, 6.4, CT + 0.8, 0.8, 0.2), { tone: "lo" }) + S(box(1.5, 11, 4, 5, CT + 0.8, 0.8, 0.2), { tone: "lo" });
  const zig = [[11, 9], [11, 18], [12.5, 18], [12.5, 10], [14, 10], [14, 18], [15.5, 18], [15.5, 10]];
  h += L(k.onTop(zig, CT + 0.8, P), { tone: "hi" }) + D([at([11, 9, CT + 0.8]), at([15.5, 10, CT + 0.8])], { size: 0.4, tone: "hi" });
  items.push({ key: depth([4, 13.5]), svg: h });
  // TXD1 분압 저항 1k/2k (THT 1/4W 눕힘)
  for (const ry of [12, 16]) {
    let r = S(box(22.8, ry, 6.3, 2.4, CT, 2.4, 1.1), { tone: "hi", crease: "lo" });
    for (const bx of [24.2, 25.4, 26.6]) r += L(k.lineOnTop([bx, ry], [bx, ry + 2.4], CT + 2.4, P), { tone: "lo" });
    r += D([at([21, ry + 1.2, CT]), at([30.9, ry + 1.2, CT])], { size: 0.5, tone: "mid" });
    items.push({ key: depth([26, ry + 1.2]), svg: r });
  }
  // 전해 캡 (ESC BEC 5V 평활)
  let cap = S(k.cylinder(30, 5.5, 3, CT, 7, P, 24), { tone: "mid" }) + L(k.sideArc(30, 5.5, 3, CT + 5.8, P, 16), { tone: "lo" });
  cap += L(k.ring(30, 5.5, 2.2, CT + 7, P, 20) + k.lineOnTop([27.8, 5.5], [32.2, 5.5], CT + 7, P) + k.lineOnTop([30, 3.3], [30, 7.7], CT + 7, P), { tone: "lo" });
  items.push({ key: depth([30, 5.5]), svg: cap });

  out.push(items.sort((a, b) => a.key - b.key).map((i) => i.svg).join(""));
  return out.join("");
}

const order = ARMS.map((q) => ({ key: depth(q.M), svg: arm(q) }));
order.push({ key: -1, svg: centre() });
const svg = k.figureSvg({
  width: WIDTH,
  height: HEIGHT,
  label:
    "300급 X 프레임 쿼드콥터 스케치. 중앙 판 위 스탠드오프에 캐리어 PCB가 있고, 그 위에 AT128A-70B 모듈이 암헤더로 꽂혀 있다. 캐리어에는 MPU-6050(GY-521), HC-06, TXD1 분압 저항이 있다. 각 암에는 ESC가 묶여 있고 2205 BLDC 모터와 6인치 2엽 프롭이 달려 있다. 배터리는 3S로 프레임 아래에 스트랩으로 고정한다.",
  body: [
    `<path data-part="halo" class="iso-halo" d="${k.haloOf({ x: -110, y: -110, w: 220, d: 220, r: 80 }, FLOOR, 0.1, P)}" style="filter:blur(6px)"/>`,
    `<g data-part="drone">`,
    below(),
    frame(),
    powerLead(),
    order.sort((a, b) => a.key - b.key).map((i) => i.svg).join(""),
    `</g>`,
  ],
});

const live = `
const P = ${JSON.stringify(P)};
const ARMS = ${JSON.stringify(ARMS.map((q) => ({ M: q.M, dir: q.dir })))};
const AUW = ${AUW}, THRUST_MAX = ${THRUST_MAX}, RPM_MAX = ${RPM_MAX}, LIFT_MAX = ${LIFT_MAX};
const propSvg = ${propSvg.toString()};
const K = { depthOf, solidSvg, extrude, cylinder };
const stage = document.querySelector(".iso-stage");
const svg = stage.querySelector("svg");
const drone = svg.querySelector('[data-part="drone"]');
const halo = svg.querySelector('[data-part="halo"]');
const props = ARMS.map((_, i) => svg.querySelector('[data-prop="' + i + '"]'));
const discs = ARMS.map((_, i) => svg.querySelector('[data-disc="' + i + '"]'));
const readout = document.querySelector("[data-readout]");
const still = matchMedia("(prefers-reduced-motion: reduce)");
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const HOVER = Math.sqrt(AUW / (4 * THRUST_MAX));
const tour = [[0, 0], [2, 0], [4, HOVER + 0.01], [7, HOVER + 0.01], [8.5, 0.62], [10, HOVER + 0.01], [12, 0], [13, 0]];
const tourAt = (t) => { t %= 13; for (let i = 1; i < tour.length; i++) if (t <= tour[i][0]) { const [t0, a] = tour[i - 1], [t1, b] = tour[i]; return a + (b - a) * (t - t0) / (t1 - t0); } return 0; };
const ratio = (thr) => 4 * THRUST_MAX * thr * thr / AUW;
const liftOf = (thr) => clamp((ratio(thr) - 0.95) * 90, 0, LIFT_MAX);
let thr = 0, target = 0, lift = 0, clock = 0, touring = true, visible = false, frame = 0, last = 0, idleTimer = 0;
const angles = ARMS.map((_, i) => i * 0.7);
function draw() {
  drone.setAttribute("transform", translateAlong(P, [0, 0, lift]));
  halo.style.opacity = String(1 - 0.6 * lift / LIFT_MAX);
  ARMS.forEach((q, i) => { props[i].innerHTML = propSvg(K, P, q.M, angles[i]); discs[i].setAttribute("opacity", String(clamp((thr - 0.15) * 1.6, 0, 0.8))); });
  const tw = ratio(thr);
  const state = tw < 0.97 ? "지상" : tw < 1.08 ? "호버" : "상승";
  const text = "스로틀 " + Math.round(thr * 100) + "% · 추력 " + Math.round(4 * THRUST_MAX * thr * thr) + " g / " + AUW + " g · " + Math.round(RPM_MAX * thr).toLocaleString() + " rpm · " + state;
  if (readout.textContent !== text) readout.textContent = text;
  stage.setAttribute("aria-valuenow", String(Math.round(thr * 100)));
  stage.setAttribute("aria-valuetext", text);
}
function tick(now) {
  const dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
  last = now;
  const calm = still.matches;
  if (touring) { clock += dt; target = tourAt(clock); }
  thr = calm ? target : thr + (target - thr) * (1 - Math.exp(-dt / 0.35));
  const want = liftOf(thr);
  lift = calm ? want : lift + (want - lift) * (1 - Math.exp(-dt / 0.7));
  if (!calm) ARMS.forEach((q, i) => { angles[i] += q.dir * thr * Math.PI * 2 * 2.2 * dt; });
  draw();
  const settled = !touring && Math.abs(target - thr) < 1e-4 && Math.abs(want - lift) < 0.01 && thr < 0.01;
  frame = visible && !settled ? requestAnimationFrame(tick) : 0;
}
const run = () => { if (!frame && visible) { last = 0; frame = requestAnimationFrame(tick); } };
const steer = (next) => { touring = false; target = clamp(next, 0, 1); clearTimeout(idleTimer); idleTimer = setTimeout(() => { touring = !still.matches; clock = 0; run(); }, 4000); run(); };
new IntersectionObserver((e) => { visible = e[e.length - 1].isIntersecting; if (visible) run(); }, { rootMargin: "120px 0px" }).observe(stage);
if (still.matches) { touring = false; target = HOVER; thr = HOVER; lift = liftOf(HOVER); }
stage.addEventListener("pointermove", (event) => { const b = svg.getBoundingClientRect(); steer(clamp(((event.clientX - b.left) / b.width - 0.15) / 0.7, 0, 1)); });
stage.addEventListener("keydown", (event) => {
  const step = { ArrowRight: 0.05, ArrowUp: 0.05, ArrowLeft: -0.05, ArrowDown: -0.05 }[event.key];
  if (event.key === "Home") { event.preventDefault(); return steer(0); }
  if (event.key === "End") { event.preventDefault(); return steer(HOVER + 0.01); }
  if (step === undefined) return;
  event.preventDefault();
  steer(target + step);
});
draw();
`;

const body = k.plateHtml({
  fig: "Fig 1",
  title: "300급 BLDC 쿼드 — 최소 구성 스케치",
  hint: "가로로 움직여 스로틀 · ←/→ 키 5%",
  readout: `스로틀 0% · 추력 0 g / ${AUW} g · 0 rpm · 지상`,
  keys: [
    { mark: "lit", label: "ATmega128A (AT128A-70B 모듈) — Timer1/3 서보형 PWM 4채널로 ESC 구동" },
    { mark: "raised", label: "2205 2300KV 모터 ×4 + 6045 프롭, 각 암에 20A ESC (BEC 5V로 보드 전원)" },
    { mark: "edge", label: "밝은 선: ESC 신호선 (PWM 1–2 ms) — 보드 모서리 3핀 헤더" },
  ],
  caption: `모터 대각 300 mm X 프레임. 보드는 대여 모듈을 암헤더로 꽂는 캐리어 하나에 MPU-6050(GY-521)·HC-06·TXD1 분압 저항(1k/2k)만 올렸다. 승압 회로·MOSFET 없이 ESC 4개와 BEC 5V로 대체. 이륙중량 약 ${AUW} g(추정), 모터당 최대 추력 약 ${THRUST_MAX} g(3S, 추정) → 추력비 약 ${((4 * THRUST_MAX) / AUW).toFixed(1)}, 호버 스로틀 약 ${Math.round(Math.sqrt(AUW / (4 * THRUST_MAX)) * 100)}%. 추력은 스로틀²에 비례로 가정했고 상승 높이는 표현용이다.`,
  body: `<div class="iso-stage" tabindex="0" role="slider" aria-label="쿼드콥터 스로틀: 화살표 키로 5%씩 조절" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">${svg}</div>`,
});

const name = theme === "light" ? "drone30-light.html" : "drone30.html";
writeFileSync(join(HERE, name), k.pageHtml({ title: "300급 BLDC 쿼드", theme, body, script: kitScript() + live, width: 780 }));
console.log("wrote", name, "AUW", AUW);
