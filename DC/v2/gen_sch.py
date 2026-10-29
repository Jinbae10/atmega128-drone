"""Generate DC v2 schematic (drone_dc_v2.kicad_sch) + project symbol lib from KiCad stock libraries.

Blocks are wired with real wires; power rails use power symbols, signals that go to the
AT128A-70B module use net labels.  Run: python DC/v2/gen_sch.py
"""
import math, os, re, uuid

LIB = r"D:/app/kicad/share/kicad/symbols"
DIR = os.path.dirname(os.path.abspath(__file__))
PROJ = "drone_dc_v2"
OUT = os.path.join(DIR, PROJ + ".kicad_sch")
ROOT = "abd99193-d4d0-4816-869a-8cd61332cc99"   # fixed: keeps annotation/PCB links stable across runs
U = lambda: str(uuid.uuid4())
G = 2.54

# ---------- tiny s-expression parser ----------
def parse(text, i=0):
    out = []
    while i < len(text):
        c = text[i]
        if c == '(':
            sub, i = parse(text, i + 1); out.append(sub)
        elif c == ')':
            return out, i + 1
        elif c.isspace():
            i += 1
        elif c == '"':
            j = i + 1
            while text[j] != '"':
                j += 2 if text[j] == '\\' else 1
            out.append(('s', text[i + 1:j])); i = j + 1
        else:
            j = i
            while not text[j].isspace() and text[j] not in '()':
                j += 1
            out.append(text[i:j]); i = j
    return out, i

def find_symbol_text(path, name):
    txt = open(path, encoding="utf-8").read()
    start = re.search(r'\(symbol "' + re.escape(name) + r'"\s', txt).start()
    depth, i = 0, start
    while True:
        if txt[i] == '(': depth += 1
        elif txt[i] == ')':
            depth -= 1
            if depth == 0: break
        elif txt[i] == '"':
            i += 1
            while txt[i] != '"': i += 2 if txt[i] == '\\' else 1
        i += 1
    return txt[start:i + 1]

def pins_of(tree):
    pins = {}
    def walk(n):
        if isinstance(n, list):
            if n and n[0] == 'pin':
                at = next(x for x in n if isinstance(x, list) and x[0] == 'at')
                num = next(x for x in n if isinstance(x, list) and x[0] == 'number')[1][1]
                pins[num] = (float(at[1]), float(at[2]), float(at[3]))
            for c in n: walk(c)
    walk(tree)
    return pins

# ---------- project symbols (modules drawn as boxes, pins in physical order) ----------
def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
F = '(effects (font (size 1.27 1.27))'

def box_symbol(name, ref, desc, left, right, half_w, plen):
    """left/right: list of (number, name, type) or None (gap), top row at y=0."""
    rows = max(len(left), len(right))
    top, bot = G, -(rows - 1) * G - G
    s = [f'(symbol {q(name)} (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
         f'(property "Reference" {q(ref)} (at 0 {top + 1.27} 0) {F}))',
         f'(property "Value" {q(name)} (at 0 {bot - 1.27} 0) {F}))',
         f'(property "Footprint" "" (at 0 0 0) {F} (hide yes)))',
         f'(property "Datasheet" "" (at 0 0 0) {F} (hide yes)))',
         f'(property "Description" {q(desc)} (at 0 0 0) {F} (hide yes)))',
         f'(symbol "{name}_0_1" (rectangle (start {-half_w} {top}) (end {half_w} {bot}) (stroke (width 0.254) (type default)) (fill (type background))))',
         f'(symbol "{name}_1_1"']
    for side, lst in ((-1, left), (1, right)):
        for k, p in enumerate(lst):
            if p is None: continue
            num, nm, typ = p
            x = side * (half_w + plen)
            s.append(f'(pin {typ} line (at {x} {-k * G} {0 if side < 0 else 180}) (length {plen}) (name {q(nm)} {F})) (number {q(num)} {F})))')
    s.append(')) ')
    return '\n'.join(s)

# AT128A-70B V2.0 header, viewed from top (AT128A-70B_V20_data.md 4장). Left row = pins 1..29, right row = 30..58
L_ROW = ["/PEN", "PE0", "PE1", "PE2", "PE3", "PE4", "PE5", "PE6", "PE7", "VCC",
         "PB0", "PB1", "PB2", "PB3", "PB4", "PB5", "PB6", "PB7", "PG3", "PG4", "GND",
         "PD0", "PD1", "PD2", "PD3", "PD4", "PD5", "PD6", "PD7"]
R_ROW = ["PF0", "PF1", "PF2", "PF3", "PF4", "PF5", "PF6", "PF7", "/RST", "GND",
         "PA0", "PA1", "PA2", "PA3", "PA4", "PA5", "PA6", "PA7", "PG2", "PG1", "PG0",
         "PC7", "PC6", "PC5", "PC4", "PC3", "PC2", "PC1", "PC0"]
ptype = lambda n: 'power_in' if n in ('VCC', 'GND') else 'bidirectional'
PROJ_SYMS = {
    "AT128A-70B": box_symbol("AT128A-70B", "U", "MAI AT128A-70B V2.0 ATmega128A module (breadboard type, 2x29 header)",
                             [(str(i + 1), n, ptype(n)) for i, n in enumerate(L_ROW)],
                             [(str(i + 30), n, ptype(n)) for i, n in enumerate(R_ROW)], 12.7, 5.08),
    "MT3608_MODULE": box_symbol("MT3608_MODULE", "U", "MT3608 boost module (adjustable, set 5.0V)",
                                [("1", "VIN+", "passive"), None, ("2", "VIN-", "passive")],
                                [("3", "VOUT+", "passive"), None, ("4", "VOUT-", "passive")], 7.62, 2.54),
}
SYMLIB = os.path.join(DIR, PROJ + ".kicad_sym")
open(SYMLIB, 'w', encoding='utf-8', newline='\n').write(
    '(kicad_symbol_lib (version 20241209) (generator "gen_sch") (generator_version "9.0")\n'
    + '\n'.join(PROJ_SYMS.values()) + ')\n')
open(os.path.join(DIR, 'sym-lib-table'), 'w', encoding='utf-8', newline='\n').write(
    f'(sym_lib_table (version 7)\n  (lib (name "{PROJ}")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJ}.kicad_sym")(options "")(descr "drone DC v2 modules")))\n')

SYMS = {}
def load(lib_id):
    if lib_id not in SYMS:
        lib, name = lib_id.split(':')
        path = SYMLIB if lib == PROJ else f"{LIB}/{lib}.kicad_sym"
        t = find_symbol_text(path, name)
        assert '(extends' not in t, lib_id
        SYMS[lib_id] = (t.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1), pins_of(parse(t)[0][0]))
    return SYMS[lib_id]

# ---------- geometry ----------
def xf(x, y, rot, mirror, px, py):
    if mirror: px = -px
    a = math.radians(rot)
    rx = px * math.cos(a) - py * math.sin(a)
    ry = px * math.sin(a) + py * math.cos(a)
    return round(x + rx, 2), round(y - ry, 2)

def outward(pa, rot, mirror):
    if mirror: pa = 180 - pa
    return int((pa + rot + 180) % 360)

parts, wires, labels, ncs, texts = [], [], [], [], []
PIN = {}            # (ref, pin) -> (x, y, outward)
pwr_n = [0]

def part(lib_id, ref, val, fp, x, y, nets=None, rot=0, mirror=False, power=False):
    pins = load(lib_id)[1]
    nets = nets or {}
    assert set(nets) <= set(pins), (ref, set(nets) - set(pins))
    parts.append((lib_id, ref, val, fp, x, y, rot, mirror, power))
    for num, (px, py, pa) in pins.items():
        PIN[(ref, num)] = (*xf(x, y, rot, mirror, px, py), outward(pa, rot, mirror))
    for num, net in nets.items():
        ex, ey, o = PIN[(ref, num)]
        if net is None: ncs.append((ex, ey))
        elif net in ('+5V', 'VBAT') and o in (0, 180) and 'Conn_' in lib_id:   # connector rail pin: stub, symbol upright
            end = at(ex + (G if o == 0 else -G), ey)
            W((ex, ey), end); psym(net, end)
        elif net in ('GND', '+5V', 'VBAT'): psym(net, (ex, ey), o)
        elif net == '-': pass                       # wired by hand below
        else: labels.append((net, ex, ey, o))

def psym(net, pt, o=None):
    """Power symbol at pt, graphic pointing in direction o (default: GND down, rails up)."""
    pwr_n[0] += 1
    lib = {'GND': 'power:GND', '+5V': 'power:+5V', 'VBAT': 'power:+BATT'}[net]
    base = 270 if net == 'GND' else 90
    if o is None: o = base
    part(lib, f"#PWR{pwr_n[0]:02d}", net, "", pt[0], pt[1], rot=(o - base) % 360, power=True)

def flag(pt, d=(G * 2, 0)):
    """PWR_FLAG on a short stub from pt."""
    end = (round(pt[0] + d[0], 2), round(pt[1] + d[1], 2))
    W(pt, end)
    pwr_n[0] += 1
    part("power:PWR_FLAG", f"#FLG{pwr_n[0]:02d}", "PWR_FLAG", "", end[0], end[1], power=True)

def P(ref, pin): return PIN[(ref, pin)][:2]

def W(*pts):
    for a, b in zip(pts, pts[1:]):
        assert a[0] == b[0] or a[1] == b[1], ("diagonal wire", a, b)
        wires.append((tuple(a), tuple(b)))

def at(x, y): return (round(x, 2), round(y, 2))

FP_R = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical"   # 1/4 W axial, standing (saves board area)
FP_C = "Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm"                   # ceramic disc 100nF
SOCK = "Connector_PinSocket_2.54mm:PinSocket_1x{:02d}_P2.54mm_Vertical"
CONN = "Connector_Generic:Conn_01x{:02d}"

# ================= POWER =================
texts.append((20.32, 38.1, "POWER: 1S LiPo -> VBAT (motors direct) / MT3608 module -> +5V. Power off = unplug J1\n"
                           "!! Adjust MT3608 to 5.0V with a multimeter BEFORE plugging the MCU module"))
part(CONN.format(2), "J1", "BATT_1S", "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", 30.48, 50.8, {"1": "-", "2": "GND"}, mirror=True)
part("Device:C_Polarized", "C1", "470uF", "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm", 58.42, 52.07, {"1": "-", "2": "GND"})
part(f"{PROJ}:MT3608_MODULE", "U2", "MT3608_MODULE", f"{PROJ}:MT3608_Module_Wire", 81.28, 48.26, {"1": "-", "2": "GND", "3": "-", "4": "GND"})
part("Device:C_Polarized", "C2", "220uF", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", 99.06, 52.07, {"1": "-", "2": "GND"})
part("Device:C", "C3", "100nF", FP_C, 114.3, 52.07, {"1": "-", "2": "GND"})
vb = at(48.26, P("C1", "1")[1])                                  # no power switch: unplugging J1 is the off switch
W(P("J1", "1"), at(vb[0], P("J1", "1")[1]), vb, P("C1", "1"), P("U2", "1"))   # VBAT
psym('VBAT', P("C1", "1"))
flag(vb, (0, -G))
W(P("U2", "3"), P("C2", "1"), P("C3", "1"))                      # +5V
psym('+5V', P("C3", "1"))
flag(P("C3", "1"), (G * 2, 0))
flag(P("C3", "2"), (G * 2, 0))                                   # GND flag

# VBAT sense divider -> PF0 (ADC0)
texts.append((20.32, 66.04, "VBAT sense: 10k/10k -> PF0 (ADC0), 4.2V -> 2.1V"))
part("Device:R", "R1", "10k", FP_R, 35.56, 74.93, {"1": "VBAT", "2": "-"})
part("Device:R", "R2", "10k", FP_R, 35.56, 87.63, {"1": "-", "2": "GND"})
part("Device:C", "C4", "100nF", FP_C, 45.72, 85.09, {"1": "-", "2": "GND"})
node = at(35.56, 81.28)
W(P("R1", "2"), node, P("R2", "1"))
W(node, P("C4", "1"), at(55.88, 81.28))
labels.append(("VBAT_SENSE", 55.88, 81.28, 0))

# ================= MOTOR DRIVERS x4 =================
texts.append((20.32, 116.84, "MOTOR DRIVER x4: SI2302 low-side, 1N5819 flyback across motor, gate 100R series + 10k pulldown"))
for n in range(1, 5):
    x0 = 20.32 + (n - 1) * 50.8
    J, D, Q, RS, RP = f"J{n+1}", f"D{n}", f"Q{n}", f"R{n+2}", f"R{n+6}"
    part(CONN.format(2), J, f"MOTOR{n}", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", x0 + 20.32, 134.62, {"1": "-", "2": "-"}, mirror=True)
    part("Device:D_Schottky", D, "1N5819", "Diode_THT:D_DO-41_SOD81_P5.08mm_Vertical_AnodeUp", x0 + 33.02, 133.35, {"1": "-", "2": "-"}, rot=270)
    part("Transistor_FET:Q_NMOS_GSD", Q, "SI2302", "Package_TO_SOT_SMD:SOT-23_Handsoldering", x0 + 30.48, 152.4, {"1": "-", "2": "GND", "3": "-"})
    part("Device:R", RS, "100", FP_R, x0 + 19.05, 152.4, {"1": f"M{n}_PWM", "2": "-"}, rot=90)
    part("Device:R", RP, "10k", FP_R, x0 + 22.86, 158.75, {"1": "-", "2": "GND"})
    top = at(x0 + 33.02, 127.0)
    W(P(J, "1"), at(x0 + 27.94, 134.62), at(x0 + 27.94, 127.0), top, P(D, "1"))      # VBAT -> motor+, K
    psym('VBAT', top)
    W(P(J, "2"), P(D, "2"), P(Q, "3"))                                                  # motor- / A / drain
    g = P(RS, "2")
    W(g, P(Q, "1")); W(g, P(RP, "1"))                                                   # gate node

# ================= PERIPHERALS =================
texts.append((20.32, 195.58, "PERIPHERALS (plug-in modules)\n"
                             "HC-06: TX -> RXD1 direct, RXD1 <- TXD1 via 1k/2k (5V -> 3.3V). Check module pin order (VCC/GND/TXD/RXD) before PCB\n"
                             "GY-521: 5V in (onboard LDO + I2C pullups), AD0 onboard pulldown -> addr 0x68"))
part(CONN.format(4), "J6", "HC-06", SOCK.format(4), 30.48, 213.36, {"1": "+5V", "2": "GND", "3": "RXD1", "4": "-"}, mirror=True)
part("Device:R", "R11", "1k", FP_R, 57.15, 218.44, {"1": "-", "2": "TXD1"}, rot=90)
part("Device:R", "R12", "2k", FP_R, 45.72, 222.25, {"1": "-", "2": "GND"})
W(P("J6", "4"), P("R12", "1"), P("R11", "1"))                    # BT_RXD node
part(CONN.format(4), "J7", "HC-SR04", SOCK.format(4), 81.28, 213.36, {"1": "+5V", "2": "TRIG", "3": "ECHO", "4": "GND"}, mirror=True)
part(CONN.format(8), "J8", "GY-521", SOCK.format(8), 119.38, 213.36,
     {"1": "+5V", "2": "GND", "3": "SCL", "4": "SDA", "5": None, "6": None, "7": None, "8": "IMU_INT"}, mirror=True)

# ================= MCU MODULE =================
texts.append((248.92, 38.1, "MCU: AT128A-70B V2.0 on 2x 1x29 female headers (do not solder the module)\n"
                            "PF4-PF7 = JTAG (onboard 4.7k pullups), PE0/PE1/PB1 = ISP -> left unused"))
SIG = {"PE3": "M4_PWM", "PE4": "ECHO", "PE5": "TRIG", "PE6": "IMU_INT", "VCC": "+5V",
       "PB5": "M1_PWM", "PB6": "M2_PWM", "PB7": "M3_PWM",
       "PD0": "SCL", "PD1": "SDA", "PD2": "RXD1", "PD3": "TXD1", "PF0": "VBAT_SENSE", "GND": "GND"}
mods = {}
for i, n in enumerate(L_ROW): mods[str(i + 1)] = SIG.get(n)
for i, n in enumerate(R_ROW): mods[str(i + 30)] = SIG.get(n)
part(f"{PROJ}:AT128A-70B", "U1", "AT128A-70B", f"{PROJ}:AT128A-70B_Module", 304.8, 58.42, mods)
part("Device:C", "C5", "10uF", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", 248.92, 95.25, {"1": "+5V", "2": "GND"})
part("Device:C", "C6", "100nF", FP_C, 261.62, 95.25, {"1": "+5V", "2": "GND"})
texts.append((243.84, 111.76, "C5/C6: bulk + decoupling\nat module VCC header"))
texts.append((332.74, 132.08,
              "PIN MAP\n"
              "PB5/PB6/PB7 = OC1A/B/C -> M1/M2/M3 PWM\n"
              "PE3 = OC3A -> M4 PWM\n"
              "PE4 = INT4 <- ECHO,  PE5 -> TRIG\n"
              "PE6 = INT6 <- MPU-6050 INT\n"
              "PD0/PD1 = SCL/SDA (TWI)\n"
              "PD2/PD3 = RXD1/TXD1 (USART1, also module USART conn)\n"
              "PF0 = ADC0 <- VBAT/2\n\n"
              "WIRED BACKUP (AR-UART2USB): plug into the module's own\n"
              "USART connector (same USART1). Remove HC-06 first and\n"
              "leave the red 5V wire unconnected (board has its own 5V)."))

# ---------- junctions ----------
from collections import Counter
cnt = Counter()
for a, b in wires: cnt[a] += 1; cnt[b] += 1
pinpts = Counter((x, y) for (x, y, _) in PIN.values())
labpts = {(x, y) for _, x, y, _ in labels}
def on_seg(p, a, b):
    return (a[0] == b[0] == p[0] and min(a[1], b[1]) < p[1] < max(a[1], b[1])) or \
           (a[1] == b[1] == p[1] and min(a[0], b[0]) < p[0] < max(a[0], b[0]))
junctions = set()
for p in cnt:
    if cnt[p] + pinpts[p] >= 3 or any(on_seg(p, a, b) for a, b in wires): junctions.add(p)
    if cnt[p] == 1 and pinpts[p] == 0 and p not in labpts and not any(on_seg(p, a, b) for a, b in wires):
        raise SystemExit(f"dangling wire end at {p}")

# ---------- emit ----------
out = [f'(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid "{ROOT}") (paper "A3")',
       '(title_block (title "Drone DC v2 - ATmega128A quadcopter (brushed 8520)") (date "2026-10-17") (rev "v2")'
       ' (comment 1 "MCU module: AT128A-70B V2.0 on female headers"))',
       '(lib_symbols']
for lib_id in sorted({p[0] for p in parts}):
    out.append(load(lib_id)[0])
out.append(')')

for lib_id, ref, val, fp, x, y, rot, mirror, power in parts:
    m = ' (mirror y)' if mirror else ''
    hide = ' (hide yes)'
    if power:
        out.append(f'(symbol (lib_id {q(lib_id)}) (at {x} {y} {rot}){m} (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no) (uuid "{uuid.uuid5(uuid.NAMESPACE_URL, PROJ + "/" + ref)}")')
        o = ((270 if lib_id == 'power:GND' else 90) + rot) % 360
        dx, dy = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[o]
        vx, vy = round(x + dx * 3.81, 2), round(y + dy * 3.81, 2)
        j = {0: ' (justify right)', 180: ' (justify left)'}.get(o, '')   # flipped: rot is 90/270 here
        if lib_id == 'power:GND' and o in (0, 180): j += ' (hide yes)'      # sideways GND: shape says it
        out.append(f'(property "Reference" {q(ref)} (at {x} {y} {rot}) {F}{hide}))')
        out.append(f'(property "Value" {q(val)} (at {vx} {vy} {rot}) {F}{j}){" (hide yes)" if "FLAG" in lib_id else ""})')
    else:
        ends = [PIN[k][:2] for k in PIN if k[0] == ref]
        xs = {e[0] for e in ends}; ys = [e[1] for e in ends] + [y]
        if lib_id.endswith('AT128A-70B') or lib_id.endswith('MT3608_MODULE'):
            rp, vp, j = (x, y - 3.81), (x, max(ys) + 3.81), ''
        elif mirror:
            rp, vp, j = (x, min(ys) - 2.54), (x, max(ys) + 2.54), ''
        elif len(xs) == 1 or 'NMOS' in lib_id:
            dx = 5.08 if 'NMOS' in lib_id else 3.81
            rp, vp = (x + dx, y - 1.27), (x + dx, y + 1.27)
            j = ' (justify right)' if rot in (90, 270) else ' (justify left)'
        else:
            rp, vp, j = (x, min(ys) - 2.54), (x, max(ys) + 2.54), ''
        out.append(f'(symbol (lib_id {q(lib_id)}) (at {x} {y} {rot}){m} (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{uuid.uuid5(uuid.NAMESPACE_URL, PROJ + "/" + ref)}")')
        out.append(f'(property "Reference" {q(ref)} (at {rp[0]} {rp[1]} {rot}) {F}{j}))')
        out.append(f'(property "Value" {q(val)} (at {vp[0]} {vp[1]} {rot}) {F}{j}))')
    out.append(f'(property "Footprint" {q(fp)} (at {x} {y} 0) {F}{hide}))')
    out.append(f'(property "Datasheet" "" (at {x} {y} 0) {F}{hide}))')
    for num in load(lib_id)[1]: out.append(f'(pin {q(num)} (uuid "{U()}"))')
    out.append(f'(instances (project {q(PROJ)} (path "/{ROOT}" (reference {q(ref)}) (unit 1)))))')

for a, b in wires:
    out.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{U()}"))')
for p in sorted(junctions):
    out.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid "{U()}"))')
for x, y in ncs:
    out.append(f'(no_connect (at {x} {y}) (uuid "{U()}"))')
for net, x, y, o in labels:
    just = 'left' if o in (0, 90) else 'right'
    out.append(f'(label {q(net)} (at {x} {y} {o}) {F} (justify {just} bottom)) (uuid "{U()}"))')
for x, y, t in texts:
    out.append(f'(text {q(t)} (exclude_from_sim no) (at {x} {y} 0) {F} (justify left bottom)) (uuid "{U()}"))')

out.append('(sheet_instances (path "/" (page "1"))))')
open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
# register the schematic in the project file (KiCad 10 needs schematic.top_level_sheets)
import json
pro = os.path.join(DIR, PROJ + ".kicad_pro")
pj = json.load(open(pro, encoding="utf-8"))
pj["schematic"]["top_level_sheets"] = [{"filename": PROJ + ".kicad_sch", "name": PROJ, "uuid": "00000000-0000-0000-0000-000000000000"}]
pj["sheets"] = [[ROOT, "Root"]]
json.dump(pj, open(pro, "w", encoding="utf-8", newline="\n"), indent=2)

print("written", OUT, sum(1 for p in parts if not p[8]), "parts,", len(wires), "wires,", len(junctions), "junctions")
