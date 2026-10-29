"""Build drone_dc_v2.kicad_pcb from the schematic netlist: outline, placement, nets, routing, GND pours.

Run with KiCad's python:  D:/app/kicad/bin/python.exe DC/v2/gen_pcb.py   (v2 = through-hole parts)
Stages: place -> Freerouting (DSN/SES) -> GND pour -> save.  Coordinates below are mm from the
board's top-left corner (x right, y down).
"""
import os, re, subprocess, sys
import pcbnew

DIR = os.path.dirname(os.path.abspath(__file__))
PROJ = "drone_dc_v2"
PCB = os.path.join(DIR, PROJ + ".kicad_pcb")
SCH = os.path.join(DIR, PROJ + ".kicad_sch")
KICAD = r"D:/app/kicad"
FPLIB = KICAD + "/share/kicad/footprints"
FREEROUTING = os.path.expanduser("~/.kicad-mcp/freerouting-2.5.0.jar")
TMP = os.environ.get("TEMP", DIR)

W, H = 60.0, 100.0                       # board size (mm): standing resistors/diodes keep it at v1 width
OX, OY = 100.0, 50.0                     # sheet offset of the board's top-left corner
MOD_X, MOD_Y = 18.57, 19.05              # AT128A-70B pad 1 (left row top); right row = +22.86

# ref: (x, y, rotation_deg).  Pad 1 of every THT 2-pin part sits at (x, y); rot 0 -> pad 2 at +x,
# 90 -> -y, 180 -> -x, 270 -> +y.  The module covers x 17.3..42.7, y 16.5..92.7 -> no parts there.
# Side strips, outside -> in:  VBAT lane (x 1.5 / 58.5) | motor J + standing diode | MOSFET | standing resistors | corridor | sockets
# Resistors: pad 1 (body) on the module side, pad 2 outward, reference text beyond pad 2.
PLACE = {
    # top zone in power-flow order: battery -> bulk C1 -> MT3608 -> C2/C3 at its output
    "J1": (5.0, 9.0, 0), "C1": (24.0, 6.5, 0), "U2": (50.0, 3.5, 0),
    "C2": (34.0, 9.0, 0), "C3": (40.5, 12.5, 0),
    "U1": (MOD_X, MOD_Y, 0),
    # left strip: motor 1 (top) / motor 4 (bottom), GY-521 + module decoupling in the middle
    "J2": (4.5, 19.5, 0), "D1": (4.5, 31.16, 90), "Q1": (9.5, 26.08, 180),
    "R3": (15.0, 31.0, 180), "R7": (15.0, 34.3, 180),
    "J8": (4.5, 38.0, 0), "C5": (12.5, 45.0, 90), "C6": (12.5, 51.0, 90),
    "Q4": (9.5, 75.42, 180), "D4": (4.5, 70.34, 270), "J5": (4.5, 82.0, 180),
    "R6": (15.0, 85.3, 180), "R10": (15.0, 88.6, 180),
    # right strip (mirror): motor 2 (top) / motor 3 (bottom), VBAT divider, HC-06 + level divider
    "J3": (55.5, 19.5, 0), "D2": (55.5, 31.16, 90), "Q2": (50.5, 26.08, 0),
    "R1": (45.0, 18.0, 0), "R2": (45.0, 21.3, 0), "C4": (45.0, 24.6, 270),
    "R4": (45.0, 31.0, 0), "R8": (45.0, 34.3, 0),
    "J6": (55.5, 38.0, 0), "R11": (45.0, 40.0, 0), "R12": (45.0, 43.3, 0),
    "Q3": (50.5, 75.42, 0), "D3": (55.5, 70.34, 270), "J4": (55.5, 82.0, 180),
    "R9": (45.0, 68.0, 0), "R5": (45.0, 71.3, 0),
    # bottom zone: HC-SR04 cable socket
    "J7": (34.0, 96.5, 270),
}
# reference text (dx, dy, angle) relative to the part; resistors default to just beyond pad 2
REFTXT = {
    "Q1": (0, -2.3, 0), "Q4": (0, -2.3, 0), "Q2": (0, -2.3, 0), "Q3": (0, -2.3, 0),
    "D1": (2.6, 0, 90), "D4": (2.6, 0, 90), "D2": (-2.6, 0, 90), "D3": (-2.6, 0, 90),
    "C1": (1.75, 5.4, 0), "C2": (1.25, 4.5, 0), "C4": (-1.6, 1.25, 90), "C5": (3.3, -1.0, 90),
    "C6": (2.0, -1.25, 90), "U1": (11.43, 11.0, 0),
}
HOLES = {"H1": (2.5, 2.5), "H2": (57.5, 2.5), "H3": (2.5, 97.5), "H4": (57.5, 97.5)}

mm = pcbnew.FromMM
def pt(x, y): return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))

# ---------- netlist ----------
def netlist():
    path = os.path.join(TMP, PROJ + ".net")
    subprocess.run([KICAD + "/bin/kicad-cli.exe", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", path, SCH],
                   check=True, capture_output=True)
    t = open(path, encoding="utf-8").read()
    comps = {}
    for blk in re.split(r'\(comp\s', t.split("(libparts")[0])[1:]:
        g = lambda k: re.search(r'\(' + k + r' "([^"]*)"', blk).group(1)
        comps[g("ref")] = dict(value=g("value"), footprint=g("footprint"), uuid=re.findall(r'\(tstamps "([^"]*)"', blk)[-1])
    nets = {}
    for blk in re.split(r'\(net\s*\n', t.split("(nets")[1])[1:]:
        name = re.search(r'\(name "([^"]+)"', blk).group(1)
        nets[name] = re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"', blk)
    return comps, nets

IO = pcbnew.PCB_IO_KICAD_SEXPR()        # pcbnew.FootprintLoad() breaks on repeated runs

def load_fp(fpid):
    lib, name = fpid.split(":")
    libdir = os.path.join(DIR, lib + ".pretty") if lib == PROJ else f"{FPLIB}/{lib}.pretty"
    fp = IO.FootprintLoad(libdir, name)
    assert fp, fpid
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp

# ---------- net classes (project file) ----------
CLASSES = {  # name: (track, clearance, via_dia, via_drill, patterns)
    "Power":  (0.8, 0.4, 1.0, 0.5, ["VBAT"]),   # battery / motor supply
    "Motor":  (1.0, 0.5, 1.0, 0.5, ["Net-(D*-A)"]),               # PWM switching nodes: keep signals away
    "Gnd":    (0.8, 0.25, 0.8, 0.4, ["GND"]),
    "Supply": (0.5, 0.3, 0.8, 0.4, ["+5V"]),
}
def set_netclasses():
    import json
    pro = os.path.join(DIR, PROJ + ".kicad_pro")
    pj = json.load(open(pro, encoding="utf-8"))
    ns = pj["net_settings"]
    default = next(c for c in ns["classes"] if c["name"] == "Default")
    default.update(track_width=0.25, clearance=0.25)
    ns["classes"] = [default]
    for i, (name, (tw, cl, vd, vdr, pats)) in enumerate(CLASSES.items()):
        c = dict(default, name=name, track_width=tw, clearance=cl, via_diameter=vd, via_drill=vdr, priority=i)
        ns["classes"].append(c)
    ns["netclass_patterns"] = [{"netclass": n, "pattern": p} for n, v in CLASSES.items() for p in v[4]]
    json.dump(pj, open(pro, "w", encoding="utf-8", newline="\n"), indent=2)

# ---------- hand-routed power (autorouter only does signals) ----------
# Widths by IPC-2221, 1 oz outer layer, ~10 C rise: 1.5 mm ~ 4 A (battery, all motors),
# 1.2 mm ~ 3 A (one side = 2 motors), 1.0 mm ~ 2.5 A (one motor), 0.8 mm boost input (< 0.5 A).
class Copper:
    """Small helper to drop tracks/vias in board-local mm."""
    def __init__(self, board):
        self.b = board
        self.pads = {(f.GetReference(), p.GetNumber()): p for f in board.GetFootprints() for p in f.Pads()}
    def P(self, ref, n):
        v = self.pads[(ref, n)].GetPosition()
        return (round(pcbnew.ToMM(v.x) - OX, 3), round(pcbnew.ToMM(v.y) - OY, 3))
    def trk(self, net, w, *pts):
        for a, b in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(self.b)
            t.SetStart(pt(*a)); t.SetEnd(pt(*b)); t.SetWidth(mm(w)); t.SetLayer(pcbnew.F_Cu)
            t.SetNet(self.b.FindNet(net)); t.SetLocked(True)
            self.b.Add(t)
    def via(self, net, x, y, d=1.0, drill=0.5, locked=True):
        v = pcbnew.PCB_VIA(self.b)
        v.SetPosition(pt(x, y)); v.SetWidth(mm(d)); v.SetDrill(mm(drill))
        v.SetNet(self.b.FindNet(net)); v.SetLocked(locked)
        self.b.Add(v)

def power_routes(board):
    c = Copper(board); P, trk = c.P, c.trk
    VB = "VBAT"
    # battery -> trunk -> C1 (bulk); no power switch (unplug J1 = off). Runs below J1 to avoid its GND pin
    j1, c1 = P("J1", "1"), P("C1", "1")
    trk(VB, 1.5, j1, (j1[0], 12.8), (20.0, 12.8))
    trk(VB, 1.5, (20.0, c1[1]), c1)
    # C1 -> MT3608 input along the top edge
    u2 = P("U2", "1")
    trk(VB, 0.8, c1, (c1[0], 1.6), (u2[0] - 3.0, 1.6), (u2[0] - 3.0, u2[1]), u2)
    # motor supply: C1 -> bus above the module -> lanes on the outer board edges
    trk(VB, 1.5, (20.0, c1[1]), (20.0, 15.0))
    trk(VB, 1.5, (1.5, 15.0), (W - 1.5, 15.0))
    trk(VB, 1.2, (1.5, 15.0), (1.5, 82.0))
    trk(VB, 1.2, (W - 1.5, 15.0), (W - 1.5, 82.0))
    r1 = P("R1", "1")
    trk(VB, 0.5, r1, (r1[0], 15.0))                     # divider top straight up to the bus
    for lane, chans in ((1.5, (("J2", "D1", "Q1"), ("J5", "D4", "Q4"))),
                        (W - 1.5, (("J3", "D2", "Q2"), ("J4", "D3", "Q3")))):
        for j, d, q in chans:
            dn = f"Net-({d}-A)"
            jp1, jp2, k, a, qd = P(j, "1"), P(j, "2"), P(d, "1"), P(d, "2"), P(q, "3")
            trk(VB, 1.0, (lane, jp1[1]), jp1)               # lane -> motor +
            trk(VB, 1.0, (lane, k[1]), k)                   # lane -> flyback diode K
            trk(dn, 1.0, jp2, a)                            # motor - -> diode A (same column)
            trk(dn, 1.0, a, qd)                             # diode A -> MOSFET drain (same column)

def gnd_stubs(board):
    """MOSFET source -> two vias to the bottom GND plane (motor return current). GND is never autorouted."""
    c = Copper(board); P, trk, via, G = c.P, c.trk, c.via, "GND"
    for q, side in (("Q1", 1), ("Q4", 1), ("Q2", -1), ("Q3", -1)):
        sx, sy = P(q, "2"); gy = P(q, "1")[1]
        v1 = (round(sx + side * 1.8, 2), sy)
        v2 = (v1[0], round(sy + (-1.3 if sy < gy else 1.3), 2))   # away from the gate pin
        trk(G, 0.8, (sx, sy), v1, v2); via(G, *v1); via(G, *v2)

def _obstacles(board, c):
    segs = [(pcbnew.ToMM(t.GetStart().x) - OX, pcbnew.ToMM(t.GetStart().y) - OY,
             pcbnew.ToMM(t.GetEnd().x) - OX, pcbnew.ToMM(t.GetEnd().y) - OY,
             pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu) if t.GetClass() == "PCB_VIA" else t.GetWidth()) / 2,
             t.GetNetname(), t.GetLayer() if t.GetClass() != "PCB_VIA" else -1)
            for t in board.GetTracks()]   # via width needs a layer (else KiCad asserts and blocks)
    boxes = []
    for f in board.GetFootprints():          # every pad, incl. unnumbered mounting pads
      for p in f.Pads():
        ref, num = f.GetReference(), p.GetNumber()
        bb = p.GetBoundingBox()
        boxes.append((pcbnew.ToMM(bb.GetLeft()) - OX, pcbnew.ToMM(bb.GetTop()) - OY,
                      pcbnew.ToMM(bb.GetRight()) - OX, pcbnew.ToMM(bb.GetBottom()) - OY, (ref, num or None)))
    return segs, boxes

def _dseg(x, y, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy or 1e-9)))
    return ((x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2) ** 0.5

def _free(x, y, r, segs, boxes, gap=0.55, skip_pad=None, layer=None):  # >= largest class clearance (Motor 0.5 incl. margin rules)
    """True if a circle of radius r at (x, y) clears tracks (on `layer`, or all for a via), pads, holes, edge."""
    if not (1.0 < x < W - 1.0 and 1.0 < y < H - 1.0): return False
    if any(((x - hx) ** 2 + (y - hy) ** 2) ** 0.5 < 3.5 for hx, hy in HOLES.values()): return False
    for sg in segs:
        if layer is not None and sg[6] not in (-1, layer): continue
        if _dseg(x, y, *sg[:4]) < sg[4] + r + gap: return False
    for b in boxes:
        if b[4] == skip_pad: continue
        if b[0] - r - gap < x < b[2] + r + gap and b[1] - r - gap < y < b[3] + r + gap: return False
    return True

# x ranges just outside the socket rows: signals from the module pins fan out here
CORRIDORS = ((MOD_X - 2.6, MOD_X - 0.8), (MOD_X + 22.86 + 0.8, MOD_X + 22.86 + 2.6))

def gnd_pad_vias(board):
    """Every SMD GND pad gets its own via to the bottom GND plane (top pour islands can't strand it)."""
    import math
    c = Copper(board)
    segs, boxes = _obstacles(board, c)
    n = 0
    for (ref, num), p in c.pads.items():
        if p.GetNetname() != "GND" or p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or ref.startswith("Q"):
            continue
        px, py = c.P(ref, num)
        done = False
        for d in (1.3, 1.6, 2.0, 2.4, 2.8):
            for k in range(16):
                a = 2 * math.pi * k / 16
                vx, vy = round(px + d * math.cos(a), 2), round(py + d * math.sin(a), 2)
                if not _free(vx, vy, 0.4, segs, boxes, skip_pad=(ref, num)): continue
                # via outside its own pad too (an open via in a pad wicks solder away from the joint)
                if not _free(vx, vy, 0.4, [], [b for b in boxes if b[4] == (ref, num)], gap=0.1): continue
                if any(lo < vx < hi for lo, hi in CORRIDORS) and 17 < vy < 94: continue
                # the 0.4 mm stub from pad to via must clear other copper on the top layer too
                steps = max(2, int(d / 0.2))
                if not all(_free(px + (vx - px) * i / steps, py + (vy - py) * i / steps, 0.2, segs,
                                 [b for b in boxes if b[4] != (ref, num)], gap=0.2, layer=pcbnew.F_Cu)
                           or ((px + (vx - px) * i / steps - px) ** 2 + (py + (vy - py) * i / steps - py) ** 2) ** 0.5 < 0.6
                           for i in range(steps + 1)):
                    continue
                c.trk("GND", 0.4, (px, py), (vx, vy)); c.via("GND", vx, vy, 0.8, 0.4)
                segs.append((px, py, vx, vy, 0.2, "GND", pcbnew.F_Cu)); segs.append((vx, vy, vx, vy, 0.4, "GND", -1))
                n += 1; done = True
                break
            if done: break
        if not done: print(f"  !! no via spot for {ref}.{num}")
    return n

def island_vias(board):
    """Drop a GND via inside every top-layer GND pour island so none is left floating (ties it to the
    bottom plane). Searches a 0.5 mm grid inside each island for a spot that clears all copper."""
    c = Copper(board)
    segs, boxes = _obstacles(board, c)
    n = 0
    for z in board.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != "GND" or not z.IsOnLayer(pcbnew.F_Cu): continue
        polys = z.GetFilledPolysList(pcbnew.F_Cu)
        for i in range(polys.OutlineCount()):
            ol = polys.Outline(i)
            bb = ol.BBox()
            x0, y0 = pcbnew.ToMM(bb.GetLeft()) - OX, pcbnew.ToMM(bb.GetTop()) - OY
            x1, y1 = pcbnew.ToMM(bb.GetRight()) - OX, pcbnew.ToMM(bb.GetBottom()) - OY
            # skip islands that already hold a GND via
            if any(sg[6] == -1 and sg[5] == "GND" and ol.PointInside(pt(sg[0], sg[1])) for sg in segs): continue
            done, y = False, y0 + 0.5
            while y < y1 and not done:
                x = x0 + 0.5
                while x < x1:
                    if ol.PointInside(pt(x, y)) and _free(x, y, 0.4, segs, boxes):
                        c.via("GND", x, y, 0.8, 0.4, locked=False); n += 1
                        segs.append((x, y, x, y, 0.4, "GND", -1)); done = True
                        break
                    x += 0.5
                y += 0.5
    return n

def stitch(board, step=4.0):
    """GND stitching vias on a grid wherever they clear every track, pad and hole (ties both pours together)."""
    c = Copper(board)
    segs, boxes = _obstacles(board, c)
    n = 0
    y = 2.0
    while y < H - 1.5:
        x = 2.0
        while x < W - 1.5:
            if _free(x, y, 0.4, segs, boxes):
                c.via("GND", x, y, 0.8, 0.4, locked=False); n += 1
                segs.append((x, y, x, y, 0.4, "GND", -1))
            x += step
        y += step
    return n

# ---------- build ----------
def build():
    set_netclasses()
    comps, nets = netlist()
    assert set(comps) == set(PLACE), ("placement mismatch", set(comps) ^ set(PLACE))
    # load every footprint BEFORE touching the board: removing board items breaks later SWIG loads
    fps = {ref: load_fp(c["footprint"]) for ref, c in comps.items()}
    fps.update({ref: load_fp("MountingHole:MountingHole_2.2mm_M2") for ref in HOLES})
    board = pcbnew.NewBoard(PCB)          # fresh board each run (BOARD.Remove() corrupts SWIG state)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(0.8))         # weight: 0.8 mm FR4 ~ half of 1.6 mm
    ds.m_CopperEdgeClearance = mm(0.3)    # common fab capability (e.g. JLCPCB 0.3 mm)
    ds.m_TrackMinWidth = mm(0.1)          # Freerouting necks down near pads (~0.125); JLCPCB 2-layer min 0.1

    netinfo = {}
    for name in nets:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netinfo[name] = ni
    padnet = {(r, p): n for n, nodes in nets.items() for r, p in nodes}

    for ref, c in comps.items():
        fp = fps[ref]
        x, y, rot = PLACE[ref]
        fp.SetReference(ref); fp.SetValue(c["value"])
        fp.SetPosition(pt(x, y)); fp.SetOrientationDegrees(rot)
        fp.SetPath(pcbnew.KIID_PATH("/" + c["uuid"]))
        if ref in REFTXT:
            dx, dy, ang = REFTXT[ref]
            fp.Reference().SetPosition(pt(x + dx, y + dy)); fp.Reference().SetTextAngleDegrees(ang)
            if ref == "C4":                # squeezed between the socket outline and its own body
                fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); fp.Reference().SetTextThickness(mm(0.12))
        elif ref[0] == "R":                 # standing resistor: text beyond pad 2, away from the body
            a, b = [p.GetPosition() for p in fp.Pads()]
            fp.Reference().SetPosition(pcbnew.VECTOR2I(b.x + (b.x - a.x) * 2350 // 2540, b.y))
            fp.Reference().SetTextAngleDegrees(0)
        board.Add(fp)
        for pad in fp.Pads():
            n = padnet.get((ref, pad.GetNumber()))
            if n: pad.SetNet(netinfo[n])
    power_routes(board)
    gnd_stubs(board)
    print(f"  GND pad vias: {gnd_pad_vias(board)}")   # fan-out before autorouting, kept as fixed obstacles
    for ref, (x, y) in HOLES.items():
        fp = fps[ref]
        fp.SetReference(ref); fp.SetValue("M2"); fp.SetPosition(pt(x, y))
        fp.SetBoardOnly(True); fp.SetExcludedFromBOM(True)
        board.Add(fp)

    # 0.5 mm no-track/no-via band along the edge (Freerouting ignores the edge clearance rule)
    k = 0.5
    for x0, y0, x1, y1 in ((0, 0, W, k), (0, H - k, W, H), (0, 0, k, H), (W - k, 0, W, H)):
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetDoNotAllowZoneFills(False)
        z.SetLayerSet(pcbnew.LSET.AllCuMask())
        o = z.Outline(); o.NewOutline()
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): o.Append(mm(OX + x), mm(OY + y))
        board.Add(z)
    edge = pcbnew.PCB_SHAPE(board)
    edge.SetShape(pcbnew.SHAPE_T_RECT); edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(mm(0.1))
    edge.SetStart(pt(0, 0)); edge.SetEnd(pt(W, H))
    board.Add(edge)
    # connector pin names on silk (polarity / pin order at a glance while plugging and debugging)
    c = Copper(board)
    L, R, C = pcbnew.GR_TEXT_H_ALIGN_LEFT, pcbnew.GR_TEXT_H_ALIGN_RIGHT, pcbnew.GR_TEXT_H_ALIGN_CENTER
    labels = [("+", *c.P("J1", "1"), 0, 3.6, C), ("-", *c.P("J1", "2"), 0, 3.6, C)]
    for J, m, top in (("J2", "M1", True), ("J3", "M2", True), ("J4", "M3", False), ("J5", "M4", False)):
        left = J in ("J2", "J5")
        dx, al = (1.8, L) if left else (-1.8, R)
        labels += [(m + "+", *c.P(J, "1"), dx, 0, al), (m + "-", *c.P(J, "2"), dx, 0, al)]
    for i, n in enumerate(["5V", "G", "TX", "RX"]):                                   # HC-06
        labels.append((n, *c.P("J6", str(i + 1)), -1.8, 0, R))
    for i, n in enumerate(["5V", "G", "SCL", "SDA", "XDA", "XCL", "AD0", "INT"]):      # GY-521
        labels.append((n, *c.P("J8", str(i + 1)), 1.8, 0, L))
    for i, n in enumerate(["5V", "TRG", "ECH", "G"]):                                 # HC-SR04
        labels.append((n, *c.P("J7", str(i + 1)), 0, 2.2, C))
    for txt, x, y, dx, dy, al in labels:
        t = pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(pt(x + dx, y + dy)); t.SetLayer(pcbnew.F_SilkS)
        t.SetHorizJustify(al)
        t.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); t.SetTextThickness(mm(0.12))
        board.Add(t)
    for txt, (x, y), layer in [("DRONE DC v2  THT", (46.0, 97.5), pcbnew.F_SilkS),
                               ("SET MT3608 TO 5.0V BEFORE PLUGGING MCU", (30.0, 54.0), pcbnew.F_SilkS)]:
        t = pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(pt(x, y)); t.SetLayer(layer)
        if "MT3608" in txt: t.SetTextAngleDegrees(90)   # under the module: visible while adjusting, before plugging
        t.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); t.SetTextThickness(mm(0.12))
        board.Add(t)
    board.Save(PCB)
    return board

def route(tries=6):
    # Freerouting is not deterministic: rerun until every connection is routed
    for i in range(tries):
        left = route_once()
        print(f"  route try {i + 1}: {left} unrouted")
        if left == 0: return
    sys.exit("routing incomplete")

# bottom layer is the GND plane: signals may only hop there when the top is blocked
RULES = """(rules PCB drone_dc_v2
  (snap_angle fortyfive_degree)
  (autoroute_settings
    (fanout off) (autoroute on) (postroute on) (vias on)
    (via_costs 30) (plane_via_costs 5) (start_ripup_costs 100) (start_pass_no 1)
    (layer_rule F.Cu (active on) (preferred_direction vertical)
      (preferred_direction_trace_costs 1.0) (against_preferred_direction_trace_costs 1.3))
    (layer_rule B.Cu (active on) (preferred_direction horizontal)
      (preferred_direction_trace_costs 4.0) (against_preferred_direction_trace_costs 5.0))))
"""

def strip_net(dsn_text, net):
    """Empty a net's pin list in the DSN: Freerouting won't route it (the pours do), but its fixed
    stubs/vias stay in the wiring as obstacles and come back in the session file."""
    i = dsn_text.index(f"(net {net}\n")
    j = dsn_text.index("(pins", i)
    depth, k = 0, j
    while True:
        if dsn_text[k] == "(": depth += 1
        elif dsn_text[k] == ")":
            depth -= 1
            if depth == 0: break
        k += 1
    return dsn_text[:j] + "(pins)" + dsn_text[k + 1:]

def route_once():
    board = pcbnew.LoadBoard(PCB)
    dsn, ses = os.path.join(TMP, PROJ + ".dsn"), os.path.join(TMP, PROJ + ".ses")
    rules = os.path.join(TMP, PROJ + ".rules")
    if os.path.exists(ses): os.remove(ses)
    assert pcbnew.ExportSpecctraDSN(board, dsn), "DSN export failed"
    t = strip_net(open(dsn, encoding="utf-8").read(), "GND")
    open(dsn, "w", encoding="utf-8").write(t)
    open(rules, "w", encoding="utf-8").write(RULES)
    java = next(iter(__import__("glob").glob(os.path.expanduser("~/.kicad-mcp/jre25/*/bin/java.exe"))), "java")
    if not os.path.exists(java): java = "java"
    r = subprocess.run([java, "-jar", FREEROUTING, "-de", dsn, "-dr", rules, "-do", ses, "-mp", "100", "--gui.enabled=false"],
                       capture_output=True, text=True, timeout=900)
    if not os.path.exists(ses):
        sys.exit("freerouting failed:\n" + r.stdout[-2000:] + r.stderr[-2000:])
    assert pcbnew.ImportSpecctraSES(board, ses), "SES import failed"   # replaces all tracks/vias
    nst = stitch(board)
    pour(board)
    for _ in range(3):                      # islands found after the first fill get their own via, refill
        if not island_vias(board): break
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    left = board.GetConnectivity().GetUnconnectedCount(False)
    print(f"  stitching vias: {nst}")
    board.Save(PCB if left == 0 else os.path.join(DIR, "_unrouted_debug.kicad_pcb"))
    return left

def pour(board):
    gnd = board.FindNet("GND")
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer); z.SetNet(gnd)
        z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(0.3)); z.SetThermalReliefSpokeWidth(mm(0.4))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        o = z.Outline(); o.NewOutline()
        for x, y in ((0.5, 0.5), (W - 0.5, 0.5), (W - 0.5, H - 0.5), (0.5, H - 0.5)):
            o.Append(mm(OX + x), mm(OY + y))
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

if __name__ == "__main__":
    stages = sys.argv[1:] or ["build", "route"]
    if "build" in stages: build(); print("placed")
    if "route" in stages: route(); print("routed + poured")
