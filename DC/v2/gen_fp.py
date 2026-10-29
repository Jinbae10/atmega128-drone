"""Project footprints for drone DC v2 -> drone_dc_v2.pretty/

AT128A-70B module: per side two 1x15 female sockets in line = 30 positions (module uses 29;
position 30, after PD7/PC0, is an unconnected mechanical pin).
ROW_SPACING is inferred from the module width (25.4 mm board, pins at both long edges -> 0.9").
!! Measure the real module with calipers before ordering the PCB and change ROW_SPACING if needed.
"""
import os

ROW_SPACING = 22.86          # mm, left row (/PEN..PD7) to right row (PF0..PC0)
N = 29                       # module pins per side
SOCK = 15                    # one female header = 1x15, two per side -> 30 positions
P = 2.54
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drone_dc_v2.pretty")
os.makedirs(DIR, exist_ok=True)

def fp(name, descr, body, attr="through_hole"):
    return (f'(footprint "{name}" (version 20241229) (generator "gen_fp") (layer "F.Cu")\n'
            f'  (descr "{descr}")\n  (attr {attr})\n{body})\n')

def text(kind, val, x, y, layer, hide=False):
    h = " (hide yes)" if hide else ""
    return (f'  (property "{kind}" "{val}" (at {x} {y} 0) (layer "{layer}"){h}'
            f' (effects (font (size 1 1) (thickness 0.15))))\n')

def line(x1, y1, x2, y2, layer, w=0.12):
    return f'  (fp_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width {w}) (type solid)) (layer "{layer}"))\n'

def rect(x1, y1, x2, y2, layer, w=0.05):
    return f'  (fp_rect (start {x1} {y1}) (end {x2} {y2}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}"))\n'

def pad(num, x, y, shape="oval"):
    return (f'  (pad "{num}" thru_hole {shape} (at {round(x, 3)} {round(y, 3)}) (size 1.7 1.7) (drill 1)'
            f' (layers "*.Cu" "*.Mask"))\n')

def silk_text(s, x, y, size=0.8, justify=""):  # 0.8 = KiCad min silk height
    j = f" (justify {justify})" if justify else ""
    return (f'  (fp_text user "{s}" (at {x} {y} 0) (layer "F.SilkS")'
            f' (effects (font (size {size} {size}) (thickness 0.12)){j}))\n')

# ---------- AT128A-70B module sockets ----------
L = (N - 1) * P                                   # 71.12
mx0, mx1 = -(25.4 - ROW_SPACING) / 2, ROW_SPACING + (25.4 - ROW_SPACING) / 2
my0, my1 = -(76.2 - L) / 2, L + (76.2 - L) / 2
b = text("Reference", "REF**", ROW_SPACING / 2, my0 - 1.5, "F.SilkS")
b += text("Value", "AT128A-70B", ROW_SPACING / 2, L / 2, "F.Fab")
b += rect(mx0, my0, mx1, my1, "F.Fab", 0.1)                     # module outline (sits above the sockets)
LS = (2 * SOCK - 1) * P                           # 30 positions -> last at 73.66
for x in (0, ROW_SPACING):                                       # 2x 1x15 socket outlines per side
    for k in range(2):
        y0 = k * SOCK * P - 1.27
        b += rect(x - 1.27, y0, x + 1.27, y0 + SOCK * P, "F.SilkS", 0.12)
    b += rect(x - 1.8, -1.8, x + 1.8, LS + 1.8, "F.CrtYd")
b += line(-1.8, -2.2, 1.0, -2.2, "F.SilkS")                      # pin-1 mark
b += silk_text("/PEN", 3.4, 0) + silk_text("PF0", ROW_SPACING - 2.6, 0)
b += silk_text("PD7", 2.6, L) + silk_text("PC0", ROW_SPACING - 2.6, L)
for i in range(N):
    b += pad(i + 1, 0, i * P, "rect" if i == 0 else "oval")
    b += pad(i + 30, ROW_SPACING, i * P)
b += pad("", 0, LS) + pad("", ROW_SPACING, LS)                   # socket position 30: no module pin
open(os.path.join(DIR, "AT128A-70B_Module.kicad_mod"), "w", encoding="utf-8", newline="\n").write(
    fp("AT128A-70B_Module", f"MAI AT128A-70B V2.0 on 4x 1x15 female sockets (2 per side), row spacing {ROW_SPACING} mm (verify)", b))

# ---------- MT3608 boost module, wired to 4 pads ----------
b = text("Reference", "REF**", 0, -2.8, "F.SilkS")
b += text("Value", "MT3608_MODULE", 0, 4 * P, "F.Fab")
b += rect(-1.27, -1.27, 1.27, 3 * P + 1.27, "F.SilkS", 0.12)
b += rect(-1.8, -1.8, 1.8, 3 * P + 1.8, "F.CrtYd")
for i, s in enumerate(["IN+", "IN-", "OUT+", "OUT-"]):
    b += pad(i + 1, 0, i * P, "rect" if i == 0 else "oval")
    b += silk_text(s, -1.6, i * P, justify="right")
open(os.path.join(DIR, "MT3608_Module_Wire.kicad_mod"), "w", encoding="utf-8", newline="\n").write(
    fp("MT3608_Module_Wire", "MT3608 boost module connected by wires / pin strip: IN+ IN- OUT+ OUT-", b))

# footprint library table
open(os.path.join(os.path.dirname(DIR), "fp-lib-table"), "w", encoding="utf-8", newline="\n").write(
    '(fp_lib_table (version 7)\n  (lib (name "drone_dc_v2")(type "KiCad")(uri "${KIPRJMOD}/drone_dc_v2.pretty")(options "")(descr "drone DC v2 modules")))\n')
print("footprints ->", DIR)
