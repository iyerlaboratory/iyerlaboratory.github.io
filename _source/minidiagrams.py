"""Flat, BioRender-like mini illustrations for the four research directions.
One blue (Rice Blue) in tints, plus neutral grays. Each returns an inline <svg>."""
import math, random

N100 = "#00205b"   # Rice Blue
N70 = "#4d6390"
N45 = "#8f9fbc"
N20 = "#c9d1df"
N10 = "#e6e9ef"
G60 = "#8a8e96"
G30 = "#c3c7ce"
G10 = "#eef0f3"
WHITE = "#ffffff"
FONT = "'Patrick Hand', 'Comic Neue', 'Segoe Print', cursive"

# Figure color code (tints/shades of Rice's secondary and accent palette)
MG_FILL, MG_STROKE, MG_NUC = "#C9F0F6", "#0A8597", "#7DD3E1"      # microglia / macrophages (cyan, as in our imaging)
NEU_FILL, NEU_STROKE, NEU_NUC = "#E4DDF1", "#5C4F86", "#B7AAD6"   # neurons (shadow purple)
LYS_FILL, LYS_STROKE, LYS_CORE = "#F7CFE2", "#A3286A", "#CF5C97"  # lysosomes (magenta)
PLQ_FILL, PLQ_STROKE, PLQ_HALO = "#E2B3A6", "#9A3D2B", "#F7E3DD"  # amyloid plaques (brick red)
INFL = "#C04829"                                                   # inflammation (brick red)
BRAIN_FILL, BRAIN_STROKE, BRAIN_GYRI = "#F7E0DA", "#B5584A", "#DFA597"
BOX_FILL, BOX_STROKE, BOX_TEXT = "#F8EDDA", "#9A7448", "#3B2A17"
ARROW = "#a2a8b2"
LABEL = "#3a4c6e"      # softer navy for figure labels
LABEL2 = "#5b6b86"
SURF_FILL, SURF_STROKE = "#D3E6F5", "#2F6FA8"                     # surface fish (medium blue)
CAVE_FILL, CAVE_STROKE = "#F7E1DA", "#B5584A"                     # cavefish (pale pink)
STRESS = "#E9A139"


def smooth_closed(pts):
    """Catmull-Rom spline through pts, as a closed cubic Bezier path."""
    n = len(pts)
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + " Z"


def smooth_open(pts):
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else pts[i + 1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def blob(cx, cy, rx, ry, seed, k=10, amp=0.08):
    r = random.Random(seed)
    pts = []
    for i in range(k):
        a = i / k * math.tau
        f = 1 + r.uniform(-amp, amp)
        pts.append((cx + math.cos(a) * rx * f, cy + math.sin(a) * ry * f))
    return smooth_closed(pts)


def tube(paths, w, fill, stroke):
    """Outlined tubes: thick stroke in outline color, slightly thinner in fill color."""
    s = "".join(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{ww + 2.4:.1f}" stroke-linecap="round" stroke-linejoin="round"/>' for d, ww in paths)
    s += "".join(f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{ww:.1f}" stroke-linecap="round" stroke-linejoin="round"/>' for d, ww in paths)
    return s


def processes(cx, cy, n, length, seed, depth=2, width=5.0, spread=0.7):
    r = random.Random(seed)
    out = []

    def grow(x, y, a, L, w, d):
        pts = [(x, y)]
        steps = 4
        for _ in range(steps):
            a += r.uniform(-0.25, 0.25)
            x += math.cos(a) * L / steps
            y += math.sin(a) * L / steps
            pts.append((x, y))
        out.append((smooth_open(pts), w))
        if d > 0:
            for side in (-1, 1):
                if r.random() < 0.85:
                    mx, my = pts[2]
                    grow(mx, my, a + side * r.uniform(0.5, spread + 0.3), L * r.uniform(0.5, 0.65), max(1.6, w * 0.6), d - 1)

    for i in range(n):
        a = i / n * math.tau + r.uniform(-0.35, 0.35)
        grow(cx, cy, a, length * r.uniform(0.8, 1.15), width, depth)
    return out


def microglia(cx, cy, scale=1.0, seed=1, n=6, length=34, depth=2, soma_r=13, fill=MG_FILL, stroke=MG_STROKE, nucleus=True, pw=4.6):
    p = processes(cx, cy, n, length * scale, seed, depth, pw * scale)
    s = tube(p, 0, fill, stroke)
    s = tube(p, 0, fill, stroke)  # placeholder overwritten below
    s = "".join(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w + 2.4:.1f}" stroke-linecap="round" stroke-linejoin="round"/>' for d, w in p)
    s += f'<path d="{blob(cx, cy, soma_r * scale + 1.2, soma_r * 0.9 * scale + 1.2, seed + 9)}" fill="{stroke}"/>'
    s += "".join(f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{w:.1f}" stroke-linecap="round" stroke-linejoin="round"/>' for d, w in p)
    s += f'<path d="{blob(cx, cy, soma_r * scale, soma_r * 0.9 * scale, seed + 9)}" fill="{fill}"/>'
    if nucleus:
        s += f'<path d="{blob(cx - 1.5 * scale, cy - 1 * scale, soma_r * 0.52 * scale, soma_r * 0.42 * scale, seed + 3, 8, 0.1)}" fill="{MG_NUC}" stroke="{MG_STROKE}" stroke-width="1"/>'
    return s


def neuron(x, y, scale=1.0, seed=4, fill=NEU_FILL, stroke=NEU_STROKE, boutons=True, n_dend=4, angle=-math.pi / 2):
    r = random.Random(seed)
    dend = []
    tips = []

    def grow(px, py, a, L, w, d):
        pts = [(px, py)]
        for _ in range(3):
            a += r.uniform(-0.18, 0.18)
            px += math.cos(a) * L / 3
            py += math.sin(a) * L / 3
            pts.append((px, py))
        dend.append((smooth_open(pts), w))
        if d > 0:
            for side in (-1, 1):
                mx, my = pts[2]
                grow(mx, my, a + side * r.uniform(0.4, 0.75), L * 0.55, max(1.5, w * 0.6), d - 1)
        else:
            tips.append((px, py))

    for i in range(n_dend):
        a = angle + (i - (n_dend - 1) / 2) * 0.78 + r.uniform(-0.1, 0.1)
        grow(x, y, a, 34 * scale, 4.2 * scale, 1)
    # axon
    ax = [(x, y), (x + 6 * scale, y + 22 * scale), (x - 2 * scale, y + 46 * scale)]
    dend.append((smooth_open(ax), 2.8 * scale))
    s = "".join(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w + 2.2:.1f}" stroke-linecap="round" stroke-linejoin="round"/>' for d, w in dend)
    s += "".join(f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{w:.1f}" stroke-linecap="round" stroke-linejoin="round"/>' for d, w in dend)
    s += f'<path d="{blob(x, y - 1 * scale, 10 * scale, 9 * scale, seed + 5, 8, 0.05)}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'
    s += f'<circle cx="{x}" cy="{y - 1 * scale}" r="{4 * scale:.1f}" fill="{NEU_NUC}"/>'
    if boutons:
        for tx, ty in tips[: boutons if isinstance(boutons, int) and boutons is not True else len(tips)]:
            s += f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="{3.6 * scale:.1f}" fill="{NEU_NUC}" stroke="{NEU_STROKE}" stroke-width="1.1"/>'
    return s, tips


def svg(content, title, desc, vb="0 0 320 200"):
    return (f'<svg class="mini-diagram" viewBox="{vb}" role="img" xmlns="http://www.w3.org/2000/svg">'
            f'<title>{title}</title><desc>{desc}</desc>{content}</svg>')


def label(x, y, text, anchor="middle", size=12, color=None, weight=700):
    color = color or LABEL
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size * 1.16:.1f}" '
            f'fill="{color}" text-anchor="{anchor}">{text}</text>')


# ------------------------------------------------------------------ 1. Disease
def disease():
    c = []
    n_svg, tips = neuron(96, 132, 1.25, seed=11, boutons=True, n_dend=4)
    c.append(n_svg)
    # reactive microglia reaching for a synapse
    mx, my = 206, 112
    c.append(microglia(mx, my, 1.25, seed=21, n=6, length=20, depth=1, soma_r=19))
    for dx, dy, r in [(-9, 5, 6.2), (8, 10, 5.2), (10, -9, 4.6)]:
        c.append(f'<circle cx="{mx + dx}" cy="{my + dy}" r="{r}" fill="{WHITE}" stroke="{N100}" stroke-width="1.4"/>')
        c.append(f'<circle cx="{mx + dx + 0.6}" cy="{my + dy + 0.6}" r="{r * 0.42:.1f}" fill="{G60}"/>')
    # engulfed synapse being carried in
    c.append(f'<circle cx="{mx - 34}" cy="{my - 22}" r="4.6" fill="{N45}" stroke="{N70}" stroke-width="1.2"/>')
    c.append(f'<path d="M{mx - 40},{my - 14} q6,-16 14,-14" fill="none" stroke="{N70}" stroke-width="2.4" stroke-linecap="round"/>')
    # DNA badge
    hx, hy = 282, 50
    strands1, strands2, rungs = [], [], []
    for i in range(13):
        t = i / 12
        y = hy - 17 + t * 34
        x1 = hx + math.sin(t * math.tau * 1.2) * 7
        x2 = hx - math.sin(t * math.tau * 1.2) * 7
        strands1.append((x1, y)); strands2.append((x2, y))
        if i % 2 == 0:
            col = N100 if i == 6 else G30
            rungs.append(f'<path d="M{x1:.1f},{y:.1f} L{x2:.1f},{y:.1f}" stroke="{col}" stroke-width="{2.6 if i == 6 else 1.3}" stroke-linecap="round"/>')
    c.append(f'<circle cx="{hx}" cy="{hy}" r="23" fill="{WHITE}" stroke="{G30}" stroke-width="1.2"/>')
    c.extend(rungs)
    c.append(f'<path d="{smooth_open(strands1)}" fill="none" stroke="{N70}" stroke-width="2" stroke-linecap="round"/>')
    c.append(f'<path d="{smooth_open(strands2)}" fill="none" stroke="{N45}" stroke-width="2" stroke-linecap="round"/>')
    c.append(label(hx, 90, "Risk genes", size=9.5))
    return svg("".join(c), "Microglia as contributors to neurological disease",
               "A neuron with synapses beside a reactive microglial cell that engulfs a synapse and holds lysosomes full of debris, with a DNA helix marking disease-risk genes.", vb="34 12 280 175")


# ------------------------------------------------------------------ 2. Evolution
def fish(x, y, s, body, stroke, eye=True, flip=False):
    sx = -1 if flip else 1
    def P(px, py):
        return f"{x + sx * px * s:.1f},{y + py * s:.1f}"
    body_d = (f"M{P(-34,0)} C{P(-24,-15)} {P(10,-18)} {P(30,-4)} C{P(36,0)} {P(36,2)} {P(30,5)} "
              f"C{P(10,17)} {P(-24,14)} {P(-34,0)} Z")
    tail_d = f"M{P(-30,0)} L{P(-48,-13)} Q{P(-43,0)} {P(-48,13)} Z"
    fin_d = f"M{P(-4,-14)} Q{P(4,-26)} {P(14,-12)} Z"
    fin2 = f"M{P(-2,12)} Q{P(4,22)} {P(12,10)} Z"
    s_ = (f'<path d="{tail_d}" fill="{body}" stroke="{stroke}" stroke-width="1.4" stroke-linejoin="round"/>'
          f'<path d="{fin_d}" fill="{body}" stroke="{stroke}" stroke-width="1.4" stroke-linejoin="round"/>'
          f'<path d="{fin2}" fill="{body}" stroke="{stroke}" stroke-width="1.4" stroke-linejoin="round"/>'
          f'<path d="{body_d}" fill="{body}" stroke="{stroke}" stroke-width="1.5" stroke-linejoin="round"/>')
    if eye:
        ex, ey = x + sx * 19 * s, y - 3 * s
        s_ += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{4.4 * s:.1f}" fill="{WHITE}" stroke="{stroke}" stroke-width="1.1"/>'
        s_ += f'<circle cx="{ex + sx * 0.8:.1f}" cy="{ey:.1f}" r="{2.2 * s:.1f}" fill="{N100}"/>'
    else:
        s_ += f'<path d="M{x + sx * 16 * s:.1f},{y - 3 * s:.1f} q{sx * 3 * s:.1f},{-2 * s:.1f} {sx * 6 * s:.1f},0" fill="none" stroke="{stroke}" stroke-width="1.1" stroke-linecap="round"/>'
    # gill line
    s_ += f'<path d="M{x + sx * 10 * s:.1f},{y - 7 * s:.1f} q{-sx * 4 * s:.1f},{7 * s:.1f} 0,{14 * s:.1f}" fill="none" stroke="{stroke}" stroke-width="1" stroke-linecap="round" opacity="0.7"/>'
    return s_


def evolution():
    c = []
    # phylogeny
    c.append(f'<path d="M22,100 L58,100 M58,52 L58,148 M58,52 L100,52 M58,148 L100,148" fill="none" stroke="{G60}" stroke-width="2" stroke-linecap="round"/>')
    c.append(f'<circle cx="58" cy="100" r="4" fill="{N100}"/>')
    c.append(fish(150, 52, 1.0, SURF_FILL, SURF_STROKE, eye=True))
    c.append(fish(150, 148, 1.0, CAVE_FILL, CAVE_STROKE, eye=False))
    c.append(label(150, 26, "Surface fish", size=9.5))
    c.append(label(150, 186, "Cavefish", size=9.5))
    # microglia compared
    c.append(f'<path d="M206,52 L222,52 M206,148 L222,148" stroke="{G30}" stroke-width="1.4" stroke-dasharray="2 3"/>')
    c.append(microglia(262, 52, 0.8, seed=31, n=6, length=30, depth=2, soma_r=11))
    c.append(microglia(262, 148, 0.8, seed=37, n=4, length=16, depth=1, soma_r=14, fill=MG_FILL))
    return svg("".join(c), "Evolution of microglia and macrophages",
               "A branching tree leading to a surface fish with eyes and an eyeless cavefish, each paired with a microglial cell of a different shape.")


# ------------------------------------------------------------------ 3. Cell biology
def cellbio():
    c = []
    cx, cy = 168, 104
    # cell body with a phagocytic cup on the left
    r = random.Random(5)
    pts = []
    k = 16
    for i in range(k):
        a = i / k * math.tau
        rr = 1 + r.uniform(-0.05, 0.05)
        rx, ry = 92 * rr, 72 * rr
        x, y = cx + math.cos(a) * rx, cy + math.sin(a) * ry
        if abs(a - math.pi) < 0.32:          # indent for the phagocytic cup
            x += 26
        pts.append((x, y))
    c.append(f'<path d="{smooth_closed(pts)}" fill="{MG_FILL}" stroke="{MG_STROKE}" stroke-width="2"/>')
    # cargo being engulfed
    c.append(f'<rect x="64" y="92" width="30" height="22" rx="11" fill="{G30}" stroke="{G60}" stroke-width="1.4"/>')
    c.append(f'<circle cx="74" cy="101" r="2" fill="{G60}"/><circle cx="84" cy="105" r="2" fill="{G60}"/>')
    # nucleus
    c.append(f'<path d="{blob(198, 110, 34, 26, 8, 10, 0.06)}" fill="{MG_NUC}" stroke="{MG_STROKE}" stroke-width="1.6"/>')
    c.append(f'<path d="M184,104 q8,-6 16,0 t16,2" fill="none" stroke="{MG_STROKE}" stroke-width="1.6" stroke-linecap="round"/>')
    c.append(f'<path d="M186,118 q8,5 18,-1" fill="none" stroke="{MG_STROKE}" stroke-width="1.6" stroke-linecap="round"/>')
    # lysosomes with cargo
    for lx, ly, lr in [(132, 70, 9), (150, 142, 10), (118, 128, 7.5), (232, 66, 8), (240, 148, 7)]:
        c.append(f'<circle cx="{lx}" cy="{ly}" r="{lr}" fill="{LYS_FILL}" stroke="{LYS_STROKE}" stroke-width="1.4"/>')
        c.append(f'<circle cx="{lx - lr * 0.25:.1f}" cy="{ly - lr * 0.2:.1f}" r="{lr * 0.22:.1f}" fill="{LYS_CORE}"/>')
        c.append(f'<circle cx="{lx + lr * 0.3:.1f}" cy="{ly + lr * 0.25:.1f}" r="{lr * 0.16:.1f}" fill="{LYS_CORE}"/>')
    # signal from nucleus to lysosomes
    c.append(f'<path d="M206,82 Q214,64 224,64" fill="none" stroke="{ARROW}" stroke-width="1.6" marker-end="url(#mini-arrow)"/>')
    # stress bolt outside the cell
    c.append(f'<path d="M290,20 L276,44 L286,44 L274,66 L298,36 L287,36 Z" fill="{STRESS}" stroke="{MG_STROKE}" stroke-width="1.2"/>')
    c.append(label(286, 84, "Stress", size=9.5))
    c.append(f'<defs><marker id="mini-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{ARROW}"/></marker></defs>')
    return svg("".join(c), "Cell biology of microglia and macrophages",
               "A phagocyte engulfing cargo at its surface, with a nucleus signaling to lysosomes and a stress signal outside the cell.")


# ------------------------------------------------------------------ 4. Physiology and behavior
def physiology():
    c = []
    # larval zebrafish, side view
    fold = "M118,84 C180,74 246,84 290,97 C246,110 180,120 118,112"
    body = ("M30,97 C30,82 46,74 70,76 C118,80 200,90 272,97 "
            "C200,104 118,114 70,118 C46,120 30,112 30,97 Z")
    c.append(f'<path d="{fold}" fill="{G10}" stroke="{G30}" stroke-width="1.2"/>')
    c.append(f'<path d="{body}" fill="{WHITE}" stroke="{G60}" stroke-width="1.6"/>')
    c.append(f'<path d="{blob(92, 108, 26, 9, 3, 10, 0.04)}" fill="{G10}" stroke="{G30}" stroke-width="1.1"/>')
    c.append(f'<path d="{blob(70, 88, 18, 9, 6, 10, 0.06)}" fill="{NEU_FILL}" stroke="{NEU_STROKE}" stroke-width="1.3"/>')
    c.append(f'<circle cx="48" cy="96" r="7.5" fill="#2b2d33"/><circle cx="46" cy="94" r="2" fill="{WHITE}"/>')
    # zoom callout to a microglia
    c.append(f'<path d="M66,80 L112,50 M84,86 L150,56" stroke="{G30}" stroke-width="1.1" stroke-dasharray="3 3"/>')
    c.append(f'<circle cx="130" cy="38" r="28" fill="{WHITE}" stroke="{MG_STROKE}" stroke-width="1.6"/>')
    c.append(microglia(130, 38, 0.62, seed=41, n=6, length=30, depth=1, soma_r=12))
    # swim trajectory = behavior
    traj = [(178, 160), (196, 146), (214, 166), (234, 142), (254, 160), (272, 138)]
    c.append(f'<path d="{smooth_open(traj)}" fill="none" stroke="{SURF_STROKE}" stroke-width="2" stroke-dasharray="1 5" stroke-linecap="round"/>')
    c.append(f'<path d="M266,132 L280,134 L272,146" fill="none" stroke="{SURF_STROKE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    c.append(label(226, 190, "Behavior", size=9.5))
    c.append(label(130, 186, "", size=9.5))
    return svg("".join(c), "Impact of microglia on animal physiology and behavior",
               "A larval zebrafish with its brain highlighted and magnified to show a microglial cell, next to a swimming trajectory representing behavior.")


ALL = {"disease": disease, "evolution": evolution, "cell-biology": cellbio, "physiology": physiology}

if __name__ == "__main__":
    import sys
    html = ['<!doctype html><html><head><style>body{margin:0;background:#fbfbfc;padding:24px;font-family:Lato,sans-serif}'
            '.g{display:grid;grid-template-columns:repeat(2,380px);gap:20px}.c{background:#fff;border:1px solid #e0e2e6;border-radius:14px;padding:16px}'
            'svg{width:100%;height:auto;display:block}</style></head><body><div class="g">']
    for k, f in ALL.items():
        html.append(f'<div class="c">{f()}</div>')
    html.append('</div></body></html>')
    open(sys.argv[1], "w").write("".join(html))


# ================================================================== Disease, detailed version
def _highlight(cx, cy, rx, ry):
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{WHITE}" fill-opacity="0.55"/>'


def _arrow(x1, y1, x2, y2, dashed=False, color=ARROW, curve=0):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    nx, ny = -(y2 - y1), (x2 - x1)
    L = math.hypot(nx, ny) or 1
    cx, cy = mx + nx / L * curve, my + ny / L * curve
    dash = ' stroke-dasharray="5 5"' if dashed else ""
    return (f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round"{dash} marker-end="url(#dz-arrow)"/>')


def _text(x, y, t, size=12, weight=400, color=None, anchor="middle", italic=False, spacing=0):
    color = color or "#44474f"
    size = size * 1.16
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size:.1f}" '
            f'fill="{color}" text-anchor="{anchor}">{t}</text>')


def _plaque(cx, cy, seed, size=1.0):
    r = random.Random(seed)
    s = f'<path d="{blob(cx, cy, 17 * size, 14 * size, seed + 50, 10, 0.12)}" fill="{PLQ_HALO}" stroke="{PLQ_FILL}" stroke-width="1" stroke-dasharray="2 3"/>'
    for _ in range(14):
        a = r.uniform(0, math.tau); d = r.uniform(0, 11 * size)
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        s += f'<path d="{blob(x, y, r.uniform(3.5, 6) * size, r.uniform(3, 5) * size, r.randint(0, 999), 7, 0.25)}" fill="{PLQ_FILL}" stroke="{PLQ_STROKE}" stroke-width="0.9"/>'
    return s


def _tapered(pts, w0, w1):
    """Closed outline of a branch whose width tapers from w0 to w1 along pts."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        x0, y0 = pts[max(0, i - 1)]
        x2, y2 = pts[min(n - 1, i + 1)]
        tx, ty = x2 - x0, y2 - y0
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        w = (w0 + (w1 - w0) * (i / (n - 1))) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    ex, ey = pts[-1]
    px, py = pts[-2]
    L = math.hypot(ex - px, ey - py) or 1
    tip = (ex + (ex - px) / L * w1 * 0.6, ey + (ey - py) / L * w1 * 0.6)
    return smooth_closed(left + [tip] + right[::-1])


def microglia_t(cx, cy, scale=1.0, seed=1, n=7, length=40, depth=2, soma_r=14, w0=7.0,
                fill=MG_FILL, stroke=MG_STROKE, nucleus=True, curl=0.18):
    """BioRender-style microglia: smooth soma with processes that taper to fine tips."""
    r = random.Random(seed)
    shapes = []

    def grow(x, y, a, L, wa, wb, d, bend):
        pts = [(x, y)]
        steps = 6
        for _ in range(steps):
            a += bend / steps + r.uniform(-0.06, 0.06)
            x += math.cos(a) * L / steps
            y += math.sin(a) * L / steps
            pts.append((x, y))
        shapes.append(_tapered(pts, wa, wb))
        if d > 0:
            for side in (-1, 1):
                if r.random() < 0.9:
                    t = r.uniform(0.35, 0.7)
                    k = int(t * steps)
                    bx, by = pts[k]
                    wt = wa + (wb - wa) * t
                    grow(bx, by, a - bend * (1 - t) + side * r.uniform(0.5, 0.85), L * r.uniform(0.42, 0.6),
                         wt * 0.72, max(0.7, wb * 0.8), d - 1, side * curl * 0.6)

    for i in range(n):
        a = i / n * math.tau + r.uniform(-0.3, 0.3)
        sx = cx + math.cos(a) * soma_r * scale * 0.7
        sy = cy + math.sin(a) * soma_r * scale * 0.7
        grow(sx, sy, a, length * scale * r.uniform(0.8, 1.15), w0 * scale, 1.0 * scale, depth,
             r.choice((-1, 1)) * curl)
    soma = blob(cx, cy, soma_r * scale, soma_r * 0.88 * scale, seed + 9, 10, 0.07)
    out = "".join(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="2.3" stroke-linejoin="round"/>' for d in shapes)
    out += f'<path d="{soma}" fill="none" stroke="{stroke}" stroke-width="2.3"/>'
    out += "".join(f'<path d="{d}" fill="{fill}"/>' for d in shapes)
    out += f'<path d="{soma}" fill="{fill}"/>'
    if nucleus:
        out += f'<path d="{blob(cx - 1.5 * scale, cy - 1 * scale, soma_r * 0.5 * scale, soma_r * 0.4 * scale, seed + 3, 8, 0.1)}" fill="{MG_NUC}" stroke="{MG_STROKE}" stroke-width="1"/>'
    return out


def neuron_t(x, y, scale=1.0, seed=12, fill="#f4f5f7", stroke="#6f737b", axon_len=58, synapses=1):
    """BioRender-style neuron: rounded soma, tapered dendrites, myelinated axon."""
    r = random.Random(seed)
    shapes = []

    def grow(px, py, a, L, wa, wb, d):
        pts = [(px, py)]
        bend = r.uniform(-0.25, 0.25)
        for _ in range(5):
            a += bend / 5 + r.uniform(-0.05, 0.05)
            px += math.cos(a) * L / 5
            py += math.sin(a) * L / 5
            pts.append((px, py))
        shapes.append(_tapered(pts, wa, wb))
        tips = [pts[-1]]
        if d > 0:
            for side in (-1, 1):
                k = r.choice((2, 3))
                bx, by = pts[k]
                tips += grow(bx, by, a + side * r.uniform(0.45, 0.75), L * r.uniform(0.45, 0.6),
                             wa * 0.55, max(0.8, wb), d - 1)
        return tips

    tips = []
    for ang in (-2.35, -1.85, -1.3, -0.8):
        sx, sy = x + math.cos(ang) * 8 * scale, y + math.sin(ang) * 8 * scale
        tips += grow(sx, sy, ang, r.uniform(30, 38) * scale, 6 * scale, 1.0 * scale, 1)
    # axon
    ax = [(x, y + 8 * scale)]
    for i in range(1, 6):
        ax.append((x + math.sin(i * 0.9) * 3 * scale, y + 8 * scale + i * axon_len / 5 * scale))
    shapes.append(_tapered(ax, 4.2 * scale, 2.4 * scale))
    soma = smooth_closed([(x, y - 13 * scale), (x + 11 * scale, y - 2 * scale), (x + 8 * scale, y + 10 * scale),
                          (x - 8 * scale, y + 10 * scale), (x - 11 * scale, y - 2 * scale)])
    out = "".join(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="2.2" stroke-linejoin="round"/>' for d in shapes)
    out += f'<path d="{soma}" fill="none" stroke="{stroke}" stroke-width="2.2"/>'
    out += "".join(f'<path d="{d}" fill="{fill}"/>' for d in shapes)
    out += f'<path d="{soma}" fill="{fill}"/>'
    out += f'<circle cx="{x}" cy="{y}" r="{4.6 * scale:.1f}" fill="{G30}" stroke="{stroke}" stroke-width="1"/>'
    # myelin segments along the axon
    for t in (0.35, 0.72):
        mx = x + math.sin(t * 5 * 0.9) * 3 * scale
        my = y + 8 * scale + t * axon_len * scale
        out += (f'<rect x="{mx - 4.2 * scale:.1f}" y="{my - 8 * scale:.1f}" width="{8.4 * scale:.1f}" height="{14 * scale:.1f}" '
                f'rx="{4 * scale:.1f}" fill="{WHITE}" stroke="{stroke}" stroke-width="1.2"/>')
    # a few remaining synapses on dendrite tips
    for tx, ty in tips[:synapses]:
        out += f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="{3.4 * scale:.1f}" fill="{N45}" stroke="{N70}" stroke-width="1.1"/>'
    return out


def _double_arrow(x1, y1, x2, y2, gap=3.5, color=ARROW):
    """Two parallel arrows pointing opposite ways (reciprocal relationship)."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * gap, dx / L * gap
    return (f'<path d="M{x1 + nx:.1f},{y1 + ny:.1f} L{x2 + nx:.1f},{y2 + ny:.1f}" stroke="{color}" stroke-width="2" marker-end="url(#dz-arrow-g)"/>'
            f'<path d="M{x2 - nx:.1f},{y2 - ny:.1f} L{x1 - nx:.1f},{y1 - ny:.1f}" stroke="{color}" stroke-width="2" marker-end="url(#dz-arrow-g)"/>')


def _box(x, y, w, h, lines, size=13):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.4"/>'
    n = len(lines)
    for i, t in enumerate(lines):
        s += _text(x + w / 2, y + h / 2 + (i - (n - 1) / 2) * (size + 3) + size * 0.36, t, size, 400, BOX_TEXT)
    return s


def _brain(cx, cy, s=1.0, uid="b"):
    """Simplified side-view brain with an inflamed region."""
    def P(x, y):
        return (cx + x * s, cy + y * s)
    outline = smooth_closed([P(-38, 4), P(-36, -12), P(-24, -24), P(-6, -29), P(12, -27), P(28, -19),
                             P(38, -6), P(38, 6), P(28, 13), P(12, 15), P(-4, 18), P(-20, 18), P(-33, 13)])
    cereb = smooth_closed([P(14, 12), P(28, 10), P(34, 18), P(26, 25), P(14, 22)])
    stem = f'M{cx + 8 * s:.1f},{cy + 16 * s:.1f} q{3 * s:.1f},{8 * s:.1f} {1 * s:.1f},{16 * s:.1f}'
    out = (f'<defs><radialGradient id="infl-{uid}" cx="50%" cy="50%" r="50%">'
           f'<stop offset="0" stop-color="{INFL}" stop-opacity="0.8"/><stop offset="1" stop-color="{INFL}" stop-opacity="0"/>'
           f'</radialGradient></defs>')
    out += f'<path d="{stem}" fill="none" stroke="{BRAIN_STROKE}" stroke-width="5" stroke-linecap="round"/>'
    out += f'<path d="{stem}" fill="none" stroke="{BRAIN_FILL}" stroke-width="2.6" stroke-linecap="round"/>'
    out += f'<path d="{cereb}" fill="{BRAIN_GYRI}" stroke="{BRAIN_STROKE}" stroke-width="1.4"/>'
    out += f'<path d="{outline}" fill="{BRAIN_FILL}" stroke="{BRAIN_STROKE}" stroke-width="1.6"/>'
    for g in ([P(-28, -6), P(-18, -14), P(-8, -10), P(2, -18)], [P(-30, 6), P(-16, 0), P(-4, 4), P(8, -4), P(20, -10)],
              [P(6, -24), P(10, -12), P(22, -6), P(30, 2)], [P(-14, 12), P(-2, 8), P(12, 8)]):
        out += f'<path d="{smooth_open(g)}" fill="none" stroke="{BRAIN_GYRI}" stroke-width="1.3" stroke-linecap="round"/>'
    out += f'<ellipse cx="{cx + 12 * s:.1f}" cy="{cy - 10 * s:.1f}" rx="{17 * s:.1f}" ry="{13 * s:.1f}" fill="url(#infl-{uid})"/>'
    return out


def _neuron_damaged(x, y, s=1.0, seed=31, fill=NEU_FILL, stroke=NEU_STROKE, axon=120):
    """Multipolar neuron with short, quickly tapering dendrites and a fragmenting axon."""
    r = random.Random(seed)
    shapes = []
    for i in range(8):
        a = math.pi * 0.3 + i / 7 * math.pi * 1.4 + r.uniform(-0.12, 0.12)
        L = r.uniform(16, 24) * s
        pts = [(x + math.cos(a) * 6 * s, y + math.sin(a) * 6 * s)]
        aa = a
        for _ in range(4):
            aa += r.uniform(-0.15, 0.15)
            px, py = pts[-1]
            pts.append((px + math.cos(aa) * L / 4, py + math.sin(aa) * L / 4))
        shapes.append(_tapered(pts, 6.5 * s, 1.0 * s))
        if r.random() < 0.7:  # one short fork
            bx, by = pts[2]
            fa = aa + r.choice((-1, 1)) * 0.7
            fp = [(bx, by)] + [(bx + math.cos(fa) * L * 0.45 * k / 3, by + math.sin(fa) * L * 0.45 * k / 3) for k in (1, 2, 3)]
            shapes.append(_tapered(fp, 3.2 * s, 0.8 * s))
    # proximal axon (intact)
    ax_pts = [(x + 6 * s, y)] + [(x + 6 * s + k * axon * 0.35 * s / 4, y + math.sin(k) * 1.5 * s) for k in (1, 2, 3, 4)]
    shapes.append(_tapered(ax_pts, 4.6 * s, 3.0 * s))
    soma = blob(x, y, 11 * s, 10 * s, seed + 2, 9, 0.08)
    out = "".join(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="2.2" stroke-linejoin="round"/>' for d in shapes)
    out += f'<path d="{soma}" fill="none" stroke="{stroke}" stroke-width="2.2"/>'
    out += "".join(f'<path d="{d}" fill="{fill}"/>' for d in shapes)
    out += f'<path d="{soma}" fill="{fill}"/>'
    out += f'<circle cx="{x}" cy="{y}" r="{4.2 * s:.1f}" fill="{NEU_NUC}" stroke="{stroke}" stroke-width="1"/>'
    out += f'<circle cx="{x}" cy="{y}" r="{1.6 * s:.1f}" fill="{stroke}"/>'
    # distal axon breaking into fragments
    fx = x + 6 * s + axon * 0.35 * s
    k = 0
    while fx < x + axon * s:
        seg = r.uniform(5, 10) * s * (1 - k * 0.05)
        fy = y + r.uniform(-2, 2) * s + k * 0.4 * s
        out += (f'<rect x="{fx:.1f}" y="{fy - 1.6 * s:.1f}" width="{max(2.5, seg):.1f}" height="{3.2 * s:.1f}" rx="{1.6 * s:.1f}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
        fx += seg + r.uniform(3, 6) * s
        k += 1
    for _ in range(6):
        out += f'<circle cx="{fx + r.uniform(-14, 6) * s:.1f}" cy="{y + r.uniform(-9, 9) * s:.1f}" r="{r.uniform(1.4, 2.4) * s:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="0.9"/>'
    return out


def _italic(x, y, t, size=12.5, color=None, anchor="middle"):
    color = color or "#6b7280"
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size * 1.16:.1f}" font-style="italic" '
            f'fill="{color}" text-anchor="{anchor}">{t}</text>')


def _hand_arrow(x1, y1, x2, y2, bend=0.12, seed=1, dashed=False, color=None, w=1.9, head=10):
    """Loose, hand-drawn arrow: a slightly wobbly curve with an open, sketched arrowhead."""
    color = color or ARROW
    r = random.Random(seed)
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    b1 = bend * L * r.uniform(0.8, 1.2)
    b2 = bend * L * r.uniform(0.6, 1.1)
    c1 = (x1 + dx / 3 + nx * b1 + r.uniform(-1.5, 1.5), y1 + dy / 3 + ny * b1 + r.uniform(-1.5, 1.5))
    c2 = (x1 + dx * 2 / 3 + nx * b2 + r.uniform(-1.5, 1.5), y1 + dy * 2 / 3 + ny * b2 + r.uniform(-1.5, 1.5))
    dash = ' stroke-dasharray="6 6"' if dashed else ""
    out = (f'<path d="M{x1:.1f},{y1:.1f} C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {x2:.1f},{y2:.1f}" fill="none" '
           f'stroke="{color}" stroke-width="{w}" stroke-linecap="round"{dash}/>')
    a = math.atan2(y2 - c2[1], x2 - c2[0])
    for side, k in ((-1, r.uniform(0.9, 1.1)), (1, r.uniform(0.8, 1.0))):
        aa = a + math.pi - side * r.uniform(0.42, 0.55)
        hx, hy = x2 + math.cos(aa) * head * k, y2 + math.sin(aa) * head * k
        mx, my = (x2 + hx) / 2 + r.uniform(-0.8, 0.8), (y2 + hy) / 2 + r.uniform(-0.8, 0.8)
        out += (f'<path d="M{x2:.1f},{y2:.1f} Q{mx:.1f},{my:.1f} {hx:.1f},{hy:.1f}" fill="none" stroke="{color}" '
                f'stroke-width="{w}" stroke-linecap="round"/>')
    return out


def _hand_double(x1, y1, x2, y2, gap=4.5, seed=5, color=None):
    """Two loose arrows running in opposite directions."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * gap, dx / L * gap
    return (_hand_arrow(x1 + nx, y1 + ny, x2 + nx, y2 + ny, bend=0.06, seed=seed, color=color) +
            _hand_arrow(x2 - nx, y2 - ny, x1 - nx, y1 - ny, bend=0.06, seed=seed + 11, color=color))


def _hand_double_len(x1, y1, x2, y2, length=56, seed=5):
    """Two-way hand-drawn arrows of a fixed length, centered between two points."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L * length / 2, dy / L * length / 2
    return _hand_double(mx - ux, my - uy, mx + ux, my + uy, seed=seed)


def disease_detailed():
    c = []
    W, H = 720, 424
    c.append(f'<defs><marker id="dz-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{ARROW}"/></marker>'
             f'<marker id="dz-arrow-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{ARROW}"/></marker></defs>')
    STATE = LABEL           # cell states: navy, largest
    PROC = "#6b7280"        # processes: gray italic, on arrows
    TOP, BOT = 112, 416
    LX, LW = 8, 252
    RX, RW = W - 8 - 216, 216
    # ---- disease contexts as tinted containers with headings
    for x0, w0, tint, edge, head, eg in [(LX, LW, "#FCF2EE", "#F0D5CC", "Neurodegenerative diseases", "e.g., Alzheimer’s disease"),
                                          (RX, RW, "#F4F1FA", "#DCD4EE", "Neurodevelopmental disorders", "e.g., lysosomal storage disorders")]:
        c.append(f'<rect x="{x0}" y="{TOP}" width="{w0}" height="{BOT - TOP}" rx="18" fill="{tint}" fill-opacity="0.45" stroke="{edge}" stroke-opacity="0.55" stroke-width="1.3"/>')
        c.append(_text(x0 + w0 / 2, TOP + 28, head, 15, 400, N100))
        c.append(_italic(x0 + w0 / 2, TOP + 48, eg, 12, LABEL2))
        c.append(f'<path d="M{x0 + 18},{TOP + 60} L{x0 + w0 - 18},{TOP + 60}" stroke="{edge}" stroke-opacity="0.6" stroke-width="1.1"/>')
    # what is known versus unknown, above each context
    for x0, w0, word, col in [(LX, LW, "Known roles", "#B5584A"), (RX, RW, "Unknown roles", "#5C4F86")]:
        mx_ = x0 + w0 / 2
        c.append(_text(mx_, TOP - 22, word, 17, 400, col))
        c.append(f'<path d="M{mx_ - 46},{TOP - 13} q46,-5 92,0" fill="none" stroke="{col}" stroke-opacity="0.55" stroke-width="2" stroke-linecap="round"/>')

    # ---- neurodegeneration: inflammation <-> neuronal damage, plaques alongside
    col = LX + 178
    c.append(_brain(LX + 62, TOP + 106, 1.0, uid="ad"))
    c.append(_italic(col, TOP + 100, "prolonged", 13, PROC))
    c.append(_italic(col, TOP + 117, "inflammation", 13, PROC))
    c.append(_hand_double_len(col, TOP + 124, col, TOP + 184, 58, seed=21))
    c.append(_italic(col, TOP + 198, "neuronal death", 13, PROC))
    c.append(_italic(col, TOP + 215, "and damage", 13, PROC))
    c.append(_text(LX + 70, TOP + 152, "amyloid plaques", 11.5, 400, LABEL2))
    c.append(_plaque(LX + 50, TOP + 176, 3, 0.8))
    c.append(_plaque(LX + 94, TOP + 184, 8, 0.6))
    c.append(_neuron_damaged(LX + 46, TOP + 248, 1.15, axon=140))

    # ---- neurodevelopmental: cell packed with swollen lysosomes
    lx, ly = RX + RW / 2, TOP + 168
    c.append(f'<path d="{blob(lx, ly, 56, 48, 14, 12, 0.05)}" fill="{MG_FILL}" stroke="{MG_STROKE}" stroke-width="1.6"/>')
    c.append(f'<path d="{blob(lx + 18, ly + 14, 16, 13, 2, 8, 0.06)}" fill="{MG_NUC}" stroke="{MG_STROKE}" stroke-width="1.2"/>')
    for dx, dy, rr in [(-26, -18, 10.5), (-4, -28, 9), (20, -17, 9.5), (-31, 10, 9), (-9, 5, 11), (4, 32, 8), (-22, 31, 7.5)]:
        c.append(f'<circle cx="{lx + dx}" cy="{ly + dy}" r="{rr}" fill="{LYS_FILL}" stroke="{LYS_STROKE}" stroke-width="1.3"/>')
        c.append(f'<circle cx="{lx + dx - rr * 0.25:.1f}" cy="{ly + dy - rr * 0.2:.1f}" r="{rr * 0.28:.1f}" fill="{LYS_CORE}"/>')
        c.append(f'<circle cx="{lx + dx + rr * 0.3:.1f}" cy="{ly + dy + rr * 0.25:.1f}" r="{rr * 0.2:.1f}" fill="{LYS_CORE}"/>')
    c.append(f'<circle cx="{lx + 52}" cy="{ly - 48}" r="13" fill="{N100}"/>')
    c.append(_text(lx + 52, ly - 43, "?", 15, 400, WHITE))
    c.append(_text(lx, ly + 78, "metabolite accumulation", 11.5, 400, LABEL2))
    c.append(_text(lx, ly + 95, "and distended lysosomes", 11.5, 400, LABEL2))

    # ---- cell states (center)
    cx = (LX + LW + RX) / 2
    c.append(_text(cx, 17, "Homeostatic microglia", 15.5, 400, STATE))
    c.append(microglia_t(cx, 82, 0.88, seed=53, n=7, length=46, depth=2, soma_r=13, w0=6.5, curl=0.25))
    c.append(_highlight(cx - 4, 77, 4.5, 2.6))
    c.append(_hand_arrow(cx - 2, 132, cx + 1, 180, bend=0.1, seed=3))
    c.append(_italic(cx, 202, "aberrant activation", 13, PROC))

    ay = 282
    r = random.Random(77)
    for _ in range(16):
        a = r.uniform(0, math.tau); d = r.uniform(44, 54)
        if abs(math.atan2(math.sin(a), math.cos(a))) < 0.55:
            a += 1.2
        c.append(f'<circle cx="{cx + math.cos(a) * d:.1f}" cy="{ay + math.sin(a) * d:.1f}" r="{r.uniform(1.6, 2.6):.1f}" fill="{INFL}" fill-opacity="0.8"/>')
    c.append(microglia_t(cx, ay, 1.0, seed=24, n=6, length=24, depth=1, soma_r=27, w0=11, curl=0.1))
    c.append(_highlight(cx - 11, ay - 13, 7, 4))
    for dx, dy, rr in [(-10, 7, 7.5), (10, 11, 6.5), (13, -9, 5.6), (-4, -13, 4.6)]:
        c.append(f'<circle cx="{cx + dx}" cy="{ay + dy}" r="{rr}" fill="{LYS_FILL}" stroke="{LYS_STROKE}" stroke-width="1.4"/>')
        c.append(f'<circle cx="{cx + dx + 0.6}" cy="{ay + dy + 0.6}" r="{rr * 0.45:.1f}" fill="{LYS_CORE}"/>')
    c.append(_text(cx, 368, "Aberrantly activated", 15.5, 400, STATE))
    c.append(_text(cx, 386, "microglia", 15.5, 400, STATE))

    # ---- processes linking the activated state to each context
    c.append(_hand_double_len(cx - 52, ay - 36, LX + LW - 22, TOP + 108, 58, seed=31))
    c.append(_hand_double_len(cx - 56, ay - 6, LX + LW - 22, TOP + 206, 58, seed=41))
    c.append(_hand_arrow(cx + 58, ay - 4, RX - 8, ay - 8, bend=0.18, seed=9, dashed=True))
    qx = (cx + 58 + RX - 8) / 2
    c.append(f'<circle cx="{qx}" cy="{ay - 24}" r="9" fill="{WHITE}" stroke="{N100}" stroke-width="1.3"/>')
    c.append(_text(qx, ay - 19.5, "?", 12, 400, N100))
    c.append(_italic(qx, ay - 56, "role", 12, PROC))
    c.append(_italic(qx, ay - 40, "undefined", 12, PROC))

    return svg("".join(c), "Microglia as contributors to neurological disease",
               "Homeostatic microglia undergo aberrant activation. In neurodegenerative diseases such as Alzheimer’s disease, activated microglia, "
               "prolonged inflammation, and neuronal death and damage reinforce one another, alongside amyloid plaques. "
               "In neurodevelopmental disorders such as lysosomal storage disorders, marked by metabolite accumulation and distended lysosomes, the role of microglia is still undefined.",
               vb=f"0 0 {W} {H}")


ALL["disease"] = disease_detailed


# ================================================================== Physiology & behavior, detailed version
WATER_FILL, WATER_EDGE = "#EAF3F9", "#8FB0C9"
PLANT_FILL, PLANT_STROKE = "#CFE6C3", "#5E9150"
ZF_BODY, ZF_EDGE, ZF_STRIPE = "#EFE8D8", "#8C7F62", "#3D6FA3"


def _rot(x, y, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    return lambda u, v: (x + u * ca - v * sa, y + u * sa + v * ca)


def _fish_top(x, y, s=1.0, ang=-math.pi / 2, wiggle=0.0):
    """Adult zebrafish seen from above; head points along `ang`."""
    P = _rot(x, y, ang)
    prof = [(24, 0), (21, 4.2), (14, 6.2), (4, 6.0), (-8, 4.4), (-18, 2.4), (-24, 1.5)]
    pts = []
    for u, v in prof:
        bend = wiggle * ((-u + 24) / 48) ** 2 * 10
        pts.append(P(u * s, (v + bend) * s))
    for u, v in reversed(prof):
        bend = wiggle * ((-u + 24) / 48) ** 2 * 10
        pts.append(P(u * s, (-v + bend) * s))
    tb = wiggle * 10
    tail = [P(-23 * s, (1.4 + tb) * s), P(-35 * s, (6 + tb * 1.3) * s), P(-31 * s, (tb * 1.2) * s), P(-35 * s, (-6 + tb * 1.3) * s), P(-23 * s, (-1.4 + tb) * s)]
    fins = [[P(12 * s, 5.5 * s), P(5 * s, 11 * s), P(7 * s, 5.5 * s)], [P(12 * s, -5.5 * s), P(5 * s, -11 * s), P(7 * s, -5.5 * s)]]
    o = ""
    for f in fins:
        o += f'<path d="M{f[0][0]:.1f},{f[0][1]:.1f} Q{f[1][0]:.1f},{f[1][1]:.1f} {f[2][0]:.1f},{f[2][1]:.1f} Z" fill="{ZF_BODY}" stroke="{ZF_EDGE}" stroke-width="1"/>'
    o += f'<path d="M' + " L".join(f"{a:.1f},{b:.1f}" for a, b in tail) + f' Z" fill="{ZF_BODY}" stroke="{ZF_EDGE}" stroke-width="1" stroke-linejoin="round"/>'
    o += f'<path d="{smooth_closed(pts)}" fill="{ZF_BODY}" stroke="{ZF_EDGE}" stroke-width="1.2"/>'
    mid = [P(u * s, wiggle * ((-u + 24) / 48) ** 2 * 10 * s) for u in (10, 0, -10, -20)]
    o += f'<path d="{smooth_open(mid)}" fill="none" stroke="{ZF_STRIPE}" stroke-width="{2.2 * s:.1f}" stroke-linecap="round"/>'
    for v in (-4.6, 4.6):
        ex, ey = P(17 * s, v * s)
        o += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.1 * s:.1f}" fill="#2b2d33"/>'
    return o


def _fish_side_zf(x, y, s=1.0, flip=False):
    """Adult zebrafish, side view, with its horizontal stripes."""
    o = fish(x, y, s, ZF_BODY, ZF_EDGE, eye=True, flip=flip)
    sx = -1 if flip else 1
    for dy, w in ((-3, 1.6), (2, 2.0), (7, 1.4)):
        o += (f'<path d="M{x + sx * 8 * s:.1f},{y + dy * s:.1f} C{x - sx * 6 * s:.1f},{y + (dy + 0.6) * s:.1f} '
              f'{x - sx * 18 * s:.1f},{y + dy * 0.5 * s:.1f} {x - sx * 30 * s:.1f},{y + dy * 0.15 * s:.1f}" fill="none" '
              f'stroke="{ZF_STRIPE}" stroke-width="{w * s:.1f}" stroke-linecap="round" opacity="0.85"/>')
    return o


def _plant(x, y, h, seed, lean=0.0):
    r = random.Random(seed)
    o = ""
    stem = [(x, y)]
    for i in range(1, 6):
        t = i / 5
        stem.append((x + lean * h * t + math.sin(t * 3 + seed) * 3, y - h * t))
    o += f'<path d="{smooth_open(stem)}" fill="none" stroke="{PLANT_STROKE}" stroke-width="1.6" stroke-linecap="round"/>'
    for i in range(1, 6):
        px, py = stem[i]
        for side in (-1, 1):
            a = -math.pi / 2 + side * r.uniform(0.7, 1.1)
            L = r.uniform(7, 10) * (1.1 - i / 8)
            ex, ey = px + math.cos(a) * L, py + math.sin(a) * L
            mx, my = (px + ex) / 2, (py + ey) / 2
            nx, ny = -(ey - py) / L * 3, (ex - px) / L * 3
            o += (f'<path d="M{px:.1f},{py:.1f} Q{mx + nx:.1f},{my + ny:.1f} {ex:.1f},{ey:.1f} Q{mx - nx:.1f},{my - ny:.1f} {px:.1f},{py:.1f} Z" '
                  f'fill="{PLANT_FILL}" stroke="{PLANT_STROKE}" stroke-width="1"/>')
    return o


def _marble(x, y, r, fill, stroke):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.1" fill-opacity="0.9"/>'
            f'<circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.28:.1f}" fill="{WHITE}" fill-opacity="0.8"/>')


def _droplet(x, y, s=1.0):
    return (f'<path d="M{x:.1f},{y - 5 * s:.1f} C{x + 3.2 * s:.1f},{y - 1 * s:.1f} {x + 3.2 * s:.1f},{y + 3 * s:.1f} {x:.1f},{y + 3 * s:.1f} '
            f'C{x - 3.2 * s:.1f},{y + 3 * s:.1f} {x - 3.2 * s:.1f},{y - 1 * s:.1f} {x:.1f},{y - 5 * s:.1f} Z" fill="#BFDDF0" stroke="{WATER_EDGE}" stroke-width="0.9"/>')


def physiology_detailed():
    c = []
    W, H = 720, 424
    PROC = "#6b7280"
    AY0, AY1 = 66, 142            # horizontal arm of the T
    AX0, AX1 = 30, 690
    SX0, SX1 = 324, 396           # stem
    SY1 = 414
    ZL, ZR = 196, 524             # zone boundaries
    # ---- the T-maze (one outline)
    maze = (f"M{AX0 + 14},{AY0} L{AX1 - 14},{AY0} Q{AX1},{AY0} {AX1},{AY0 + 14} L{AX1},{AY1 - 14} Q{AX1},{AY1} {AX1 - 14},{AY1} "
            f"L{SX1},{AY1} L{SX1},{SY1 - 12} Q{SX1},{SY1} {SX1 - 12},{SY1} L{SX0 + 12},{SY1} Q{SX0},{SY1} {SX0},{SY1 - 12} "
            f"L{SX0},{AY1} L{AX0 + 14},{AY1} Q{AX0},{AY1} {AX0},{AY1 - 14} L{AX0},{AY0 + 14} Q{AX0},{AY0} {AX0 + 14},{AY0} Z")
    c.append(f'<path d="{maze}" fill="{WATER_FILL}"/>')
    # zone tints
    c.append(f'<rect x="{AX0}" y="{AY0}" width="{ZL - AX0}" height="{AY1 - AY0}" rx="14" fill="#DCEFD3" fill-opacity="0.75"/>')
    c.append(f'<rect x="{ZR}" y="{AY0}" width="{AX1 - ZR}" height="{AY1 - AY0}" rx="14" fill="#F9DDD4" fill-opacity="0.75"/>')
    c.append(f'<path d="{maze}" fill="none" stroke="{WATER_EDGE}" stroke-width="2" stroke-linejoin="round"/>')
    for zx in (ZL, ZR):
        c.append(f'<path d="M{zx},{AY0 + 6} L{zx},{AY1 - 6}" stroke="{WATER_EDGE}" stroke-width="1.3" stroke-dasharray="4 5"/>')

    # ---- left arm: sensory enrichment (marbles and plants)
    r = random.Random(5)
    cols = [("#BFE3E8", "#2E8C99"), ("#F6C9B8", "#B5584A"), ("#F3E1A6", "#A47F22"), ("#D9D0EE", "#5C4F86"), ("#C9E4C0", "#5E9150")]
    spots = [(58, 122), (78, 112), (100, 126), (124, 116), (146, 126), (168, 114), (66, 96), (112, 100), (154, 96), (88, 84), (176, 132), (136, 82)]
    for i, (mx, my) in enumerate(spots):
        f, s_ = cols[i % len(cols)]
        c.append(_marble(mx + r.uniform(-2, 2), my + r.uniform(-2, 2), r.uniform(6.2, 7.6), f, s_))
    c.append(_plant(48, 136, 56, 3, 0.15))
    c.append(_plant(102, 138, 48, 7, -0.1))
    c.append(_plant(184, 138, 54, 11, -0.18))
    c.append(_plant(142, 138, 40, 2, 0.12))

    # ---- right arm: punishment zone with the net, seen from above
    nx_, ny_ = 622, 104
    c.append(f'<path d="M{nx_ + 26},{ny_ - 18} L{nx_ + 54},{ny_ - 44}" stroke="#8C7F62" stroke-width="3.4" stroke-linecap="round"/>')
    c.append(f'<ellipse cx="{nx_}" cy="{ny_}" rx="30" ry="26" fill="{WHITE}" fill-opacity="0.55" stroke="#4E6E8E" stroke-width="2"/>')
    for k in range(-3, 4):
        w = math.sqrt(max(0, 1 - (k / 3.6) ** 2))
        c.append(f'<path d="M{nx_ - 30 * w:.1f},{ny_ + k * 7.2:.1f} L{nx_ + 30 * w:.1f},{ny_ + k * 7.2:.1f}" stroke="#8FA6BC" stroke-width="0.8"/>')
        c.append(f'<path d="M{nx_ + k * 8.2:.1f},{ny_ - 26 * w:.1f} L{nx_ + k * 8.2:.1f},{ny_ + 26 * w:.1f}" stroke="#8FA6BC" stroke-width="0.8"/>')

    # ---- fish swimming up the stem, one turning toward enrichment
    c.append(_fish_top(372, 372, 0.95, -math.pi / 2 - 0.08, wiggle=0.25))
    c.append(_fish_top(346, 318, 0.95, -math.pi / 2 + 0.1, wiggle=-0.3))
    c.append(_fish_top(374, 254, 0.95, -math.pi / 2 - 0.05, wiggle=0.2))
    c.append(_fish_top(342, 112, 0.95, math.pi + 0.35, wiggle=-0.35))
    # choice arrows at the junction
    c.append(_hand_arrow(350, 208, 250, 110, bend=-0.22, seed=12, color="#7FA872", w=2.1))
    c.append(_hand_arrow(370, 208, 470, 110, bend=0.22, seed=14, dashed=True, color=ARROW))

    # ---- arm labels (above the arms)
    c.append(_text((AX0 + ZL) / 2, 28, "Sensory enrichment", 15.5, 400, LABEL))
    c.append(_italic((AX0 + ZL) / 2, 50, "marbles and plants", 12.5, PROC))
    c.append(_text((ZR + AX1) / 2, 28, "Punishment", 15.5, 400, LABEL))
    c.append(_italic((ZR + AX1) / 2, 50, "brief air exposure", 12.5, PROC))

    # ---- assay title in the open space, lower left
    c.append(_text(162, 214, "Learning and", 17, 400, N100))
    c.append(_text(162, 236, "memory assay", 17, 400, N100))
    c.append(_italic(162, 266, "Fish learn which arm", 12.5, PROC))
    c.append(_italic(162, 284, "to choose, and remember it.", 12.5, PROC))
    # microglia: the question
    c.append(microglia_t(112, 352, 0.62, seed=53, n=7, length=46, depth=2, soma_r=13, w0=6.5, curl=0.25))
    c.append(_text(214, 346, "How do microglia", 12.5, 400, LABEL2))
    c.append(_text(214, 363, "shape this?", 12.5, 400, LABEL2))

    # ---- side-view inset: lifting the fish out of the water
    IX0, IY0, IX1, IY1 = 450, 196, 700, 412
    c.append(f'<path d="M{nx_ - 22},{ny_ + 30} L{IX0 + 40},{IY0}" stroke="{G30}" stroke-width="1.2" stroke-dasharray="3 4"/>')
    c.append(f'<path d="M{nx_ + 24},{ny_ + 28} L{IX1 - 30},{IY0}" stroke="{G30}" stroke-width="1.2" stroke-dasharray="3 4"/>')
    c.append(f'<rect x="{IX0}" y="{IY0}" width="{IX1 - IX0}" height="{IY1 - IY0}" rx="18" fill="{WHITE}" fill-opacity="0.7" stroke="{G30}" stroke-width="1.3"/>')
    wy = 346
    wave = [(IX0 + 14, wy)]
    for i in range(1, 15):
        wave.append((IX0 + 14 + i * (IX1 - IX0 - 28) / 14, wy + (2.2 if i % 2 else -2.2)))
    water = smooth_open(wave) + f" L{IX1 - 14},{IY1 - 22} Q{IX1 - 14},{IY1 - 12} {IX1 - 24},{IY1 - 12} L{IX0 + 24},{IY1 - 12} Q{IX0 + 14},{IY1 - 12} {IX0 + 14},{IY1 - 22} Z"
    c.append(f'<path d="{water}" fill="{WATER_FILL}" stroke="{WATER_EDGE}" stroke-width="1.5"/>')
    c.append(_fish_side_zf(504, 380, 0.5))
    # the net, lifted, holding a fish in air
    hx, hy = 598, 262
    c.append(f'<path d="M{hx + 36},{hy - 2} L{hx + 82},{hy - 52}" stroke="#8C7F62" stroke-width="3.6" stroke-linecap="round"/>')
    bag = f"M{hx - 38},{hy} C{hx - 34},{hy + 44} {hx + 30},{hy + 46} {hx + 38},{hy}"
    c.append(f'<path d="{bag} Z" fill="{WHITE}" fill-opacity="0.6" stroke="#8FA6BC" stroke-width="1.2"/>')
    for k in range(1, 6):
        t = k / 6
        c.append(f'<path d="M{hx - 38 + 76 * t:.1f},{hy} Q{hx - 38 + 76 * t:.1f},{hy + 30} {hx - 4 + 8 * t:.1f},{hy + 34}" fill="none" stroke="#B3C2D1" stroke-width="0.8"/>')
    c.append(_fish_side_zf(hx - 2, hy + 18, 0.62))
    c.append(f'<ellipse cx="{hx}" cy="{hy}" rx="38" ry="7" fill="none" stroke="#4E6E8E" stroke-width="2"/>')
    for dx, dy in ((-14, 318), (2, 328), (16, 314)):
        c.append(_droplet(hx + dx, dy, 0.9))
    c.append(_hand_arrow(530, 336, 534, 270, bend=0.12, seed=19))
    c.append(_italic(500, 232, "out of the water", 12.5, PROC))
    c.append(_italic(500, 250, "for a few seconds", 12.5, PROC))

    return svg("".join(c), "Impact of microglia on animal physiology and behavior",
               "A T-maze learning and memory assay seen from above. Zebrafish swim up the stem and choose between an arm with sensory enrichment "
               "(colored marbles and plants) and an arm where they are netted and lifted briefly out of the water as punishment. An inset shows the net "
               "holding a fish in the air above the water surface. The question is how microglia shape this learning and memory.",
               vb=f"0 0 {W} {H}")


ALL["physiology"] = physiology_detailed


def _hand_curve(x0, y0, c1, c2, x1, y1, seed=1, color=None, w=2.0, head=10, dashed=False):
    """Hand-drawn cubic arrow with explicit control points (for loops and U-turns)."""
    color = color or ARROW
    r = random.Random(seed)
    dash = ' stroke-dasharray="6 6"' if dashed else ""
    out = (f'<path d="M{x0:.1f},{y0:.1f} C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {x1:.1f},{y1:.1f}" fill="none" '
           f'stroke="{color}" stroke-width="{w}" stroke-linecap="round"{dash}/>')
    a = math.atan2(y1 - c2[1], x1 - c2[0])
    for side in (-1, 1):
        aa = a + math.pi - side * r.uniform(0.42, 0.55)
        hx, hy = x1 + math.cos(aa) * head, y1 + math.sin(aa) * head
        out += (f'<path d="M{x1:.1f},{y1:.1f} Q{(x1 + hx) / 2 + r.uniform(-0.8, 0.8):.1f},{(y1 + hy) / 2 + r.uniform(-0.8, 0.8):.1f} {hx:.1f},{hy:.1f}" '
                f'fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')
    return out


def physiology_two_chamber():
    c = []
    W, H = 720, 330
    X0, X1, Y0, Y1 = 24, 696, 66, 306
    MID = (X0 + X1) / 2
    GAP0, GAP1 = 152, 220                       # doorway in the divider
    RED_T, RED_E = "#F8DCD3", "#C9604B"         # enrichment chamber
    GRN_T, GRN_E = "#DDEFD5", "#5E9E4C"         # negative reinforcement chamber
    # water + chamber tints
    c.append(f'<rect x="{X0}" y="{Y0}" width="{MID - X0}" height="{Y1 - Y0}" rx="18" fill="{RED_T}" fill-opacity="0.8"/>')
    c.append(f'<rect x="{MID}" y="{Y0}" width="{X1 - MID}" height="{Y1 - Y0}" rx="18" fill="{GRN_T}" fill-opacity="0.8"/>')
    # colored walls
    c.append(f'<path d="M{MID},{Y0} L{X0 + 18},{Y0} Q{X0},{Y0} {X0},{Y0 + 18} L{X0},{Y1 - 18} Q{X0},{Y1} {X0 + 18},{Y1} L{MID},{Y1}" fill="none" stroke="{RED_E}" stroke-width="4" stroke-linejoin="round"/>')
    c.append(f'<path d="M{MID},{Y0} L{X1 - 18},{Y0} Q{X1},{Y0} {X1},{Y0 + 18} L{X1},{Y1 - 18} Q{X1},{Y1} {X1 - 18},{Y1} L{MID},{Y1}" fill="none" stroke="{GRN_E}" stroke-width="4" stroke-linejoin="round"/>')
    # divider with a doorway
    c.append(f'<path d="M{MID},{Y0} L{MID},{GAP0}" stroke="#7d8a99" stroke-width="4" stroke-linecap="round"/>')
    c.append(f'<path d="M{MID},{GAP1} L{MID},{Y1}" stroke="#7d8a99" stroke-width="4" stroke-linecap="round"/>')

    # ---- enrichment: marbles and plants along the far left
    r = random.Random(5)
    cols = [("#BFE3E8", "#2E8C99"), ("#F6C9B8", "#B5584A"), ("#F3E1A6", "#A47F22"), ("#D9D0EE", "#5C4F86"), ("#C9E4C0", "#5E9150")]
    spots = [(56, 96), (80, 112), (60, 136), (90, 152), (58, 182), (84, 204), (62, 236), (92, 258), (60, 282), (118, 92), (120, 282), (112, 230)]
    for i, (mx, my) in enumerate(spots):
        f, s_ = cols[i % len(cols)]
        c.append(_marble(mx + r.uniform(-2, 2), my + r.uniform(-2, 2), r.uniform(6.4, 7.8), f, s_))
    for px, py, h, sd, ln in [(140, 150, 50, 3, 0.1), (46, 168, 44, 7, 0.15), (148, 274, 52, 11, -0.12), (110, 196, 40, 2, 0.08)]:
        c.append(_plant(px, py, h, sd, ln))

    # ---- negative reinforcement: the net, seen from above
    nx_, ny_ = 560, 186
    c.append(f'<path d="M{nx_ + 34},{ny_ - 24} L{nx_ + 76},{ny_ - 64}" stroke="#8C7F62" stroke-width="3.6" stroke-linecap="round"/>')
    c.append(f'<ellipse cx="{nx_}" cy="{ny_}" rx="38" ry="34" fill="{WHITE}" fill-opacity="0.55" stroke="#4E6E8E" stroke-width="2"/>')
    for k in range(-4, 5):
        w = math.sqrt(max(0, 1 - (k / 4.6) ** 2))
        c.append(f'<path d="M{nx_ - 38 * w:.1f},{ny_ + k * 7.4:.1f} L{nx_ + 38 * w:.1f},{ny_ + k * 7.4:.1f}" stroke="#8FA6BC" stroke-width="0.8"/>')
        c.append(f'<path d="M{nx_ + k * 8.3:.1f},{ny_ - 34 * w:.1f} L{nx_ + k * 8.3:.1f},{ny_ + 34 * w:.1f}" stroke="#8FA6BC" stroke-width="0.8"/>')

    # ---- fish: gathered on the enrichment side
    c.append(_fish_top(208, 116, 1.1, math.pi - 0.3, wiggle=0.25))
    c.append(_fish_top(262, 196, 1.1, math.pi + 0.25, wiggle=-0.3))
    c.append(_fish_top(196, 256, 1.1, math.pi - 0.15, wiggle=0.2))
    c.append(_fish_top(296, 120, 1.1, math.pi + 0.5, wiggle=-0.2))
    # one fish at the doorway, turning back
    c.append(_fish_top(332, 192, 1.1, math.pi - 0.2, wiggle=0.35))
    c.append(_hand_curve(372, 166, (446, 128), (470, 236), 380, 222, seed=7, color="#5b6b86", w=2.2, head=11))

    # ---- labels
    c.append(_text((X0 + MID) / 2, 34, "Sensory enrichment", 16, 400, LABEL))
    c.append(_text((MID + X1) / 2, 34, "Negative reinforcement", 16, 400, LABEL))

    return svg("".join(c), "Impact of microglia on animal physiology and behavior",
               "A two-chamber learning and memory assay seen from above. The left chamber, outlined in red, holds sensory enrichment (colored marbles and plants); "
               "the right chamber, outlined in green, is paired with negative reinforcement, a net that briefly lifts fish out of the water. "
               "The fish gather on the enrichment side, and one fish at the doorway turns back, avoiding the right chamber.",
               vb=f"0 0 {W} {H}")


ALL["physiology"] = physiology_two_chamber


def physiology_corridor():
    c = []
    W, H = 720, 320
    X0, X1, Y0, Y1 = 26, 694, 74, 270
    ZL, ZR = 214, 506                          # inner edges of the colored ends
    RED_T, RED_E = "#F8DCD3", "#C9604B"
    GRN_T, GRN_E = "#DDEFD5", "#5E9E4C"
    # corridor of water, neutral in the middle
    c.append(f'<rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}" rx="18" fill="{WATER_FILL}"/>')
    c.append(f'<path d="M{ZL},{Y0} L{X0 + 18},{Y0} Q{X0},{Y0} {X0},{Y0 + 18} L{X0},{Y1 - 18} Q{X0},{Y1} {X0 + 18},{Y1} L{ZL},{Y1} Z" fill="{RED_T}" fill-opacity="0.85"/>')
    c.append(f'<path d="M{ZR},{Y0} L{X1 - 18},{Y0} Q{X1},{Y0} {X1},{Y0 + 18} L{X1},{Y1 - 18} Q{X1},{Y1} {X1 - 18},{Y1} L{ZR},{Y1} Z" fill="{GRN_T}" fill-opacity="0.85"/>')
    c.append(f'<rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}" rx="18" fill="none" stroke="{WATER_EDGE}" stroke-width="2"/>')
    # colored outlines around the two ends only
    c.append(f'<path d="M{ZL},{Y0} L{X0 + 18},{Y0} Q{X0},{Y0} {X0},{Y0 + 18} L{X0},{Y1 - 18} Q{X0},{Y1} {X0 + 18},{Y1} L{ZL},{Y1}" fill="none" stroke="{RED_E}" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round"/>')
    c.append(f'<path d="M{ZR},{Y0} L{X1 - 18},{Y0} Q{X1},{Y0} {X1},{Y0 + 18} L{X1},{Y1 - 18} Q{X1},{Y1} {X1 - 18},{Y1} L{ZR},{Y1}" fill="none" stroke="{GRN_E}" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round"/>')
    for zx, col in ((ZL, RED_E), (ZR, GRN_E)):
        c.append(f'<path d="M{zx},{Y0 + 8} L{zx},{Y1 - 8}" stroke="{col}" stroke-opacity="0.55" stroke-width="1.4" stroke-dasharray="5 6"/>')

    # ---- enrichment: marbles and plants
    r = random.Random(5)
    cols = [("#BFE3E8", "#2E8C99"), ("#F6C9B8", "#B5584A"), ("#F3E1A6", "#A47F22"), ("#D9D0EE", "#5C4F86"), ("#C9E4C0", "#5E9150")]
    spots = [(54, 100), (82, 118), (58, 142), (112, 102), (94, 160), (56, 190), (150, 120), (86, 214), (124, 196), (60, 244), (108, 248), (170, 236), (186, 104)]
    for i, (mx, my) in enumerate(spots):
        f, s_ = cols[i % len(cols)]
        c.append(_marble(mx + r.uniform(-2, 2), my + r.uniform(-2, 2), r.uniform(6.4, 7.8), f, s_))
    for px, py, h, sd, ln in [(140, 176, 52, 3, 0.1), (46, 178, 46, 7, 0.15), (192, 262, 50, 11, -0.12), (146, 262, 40, 2, 0.08), (80, 262, 38, 9, 0.1)]:
        c.append(_plant(px, py, h, sd, ln))

    # ---- negative reinforcement: the net, seen from above
    nx_, ny_ = 604, 172
    c.append(f'<path d="M{nx_ + 34},{ny_ - 24} L{nx_ + 70},{ny_ - 60}" stroke="#8C7F62" stroke-width="3.6" stroke-linecap="round"/>')
    c.append(f'<ellipse cx="{nx_}" cy="{ny_}" rx="38" ry="34" fill="{WHITE}" fill-opacity="0.55" stroke="#4E6E8E" stroke-width="2"/>')
    for k in range(-4, 5):
        w = math.sqrt(max(0, 1 - (k / 4.6) ** 2))
        c.append(f'<path d="M{nx_ - 38 * w:.1f},{ny_ + k * 7.4:.1f} L{nx_ + 38 * w:.1f},{ny_ + k * 7.4:.1f}" stroke="#8FA6BC" stroke-width="0.8"/>')
        c.append(f'<path d="M{nx_ + k * 8.3:.1f},{ny_ - 34 * w:.1f} L{nx_ + k * 8.3:.1f},{ny_ + 34 * w:.1f}" stroke="#8FA6BC" stroke-width="0.8"/>')

    # ---- fish: drawn toward enrichment, one turning back from the green end
    c.append(_fish_top(176, 150, 1.1, math.pi - 0.25, wiggle=0.25))
    c.append(_fish_top(258, 214, 1.1, math.pi + 0.2, wiggle=-0.3))
    c.append(_fish_top(318, 124, 1.1, math.pi - 0.1, wiggle=0.2))
    c.append(_fish_top(420, 176, 1.1, math.pi + 0.15, wiggle=0.35))
    c.append(_hand_curve(456, 140, (528, 112), (536, 228), 468, 224, seed=7, color="#5b6b86", w=2.2, head=11))

    # ---- labels
    c.append(_text((X0 + ZL) / 2, 40, "Sensory enrichment", 16, 400, LABEL))
    c.append(_text((ZR + X1) / 2, 40, "Negative reinforcement", 16, 400, LABEL))

    return svg("".join(c), "Impact of microglia on animal physiology and behavior",
               "A learning and memory maze seen from above: a long chamber whose left end, outlined in red, holds sensory enrichment (colored marbles and plants), "
               "and whose right end, outlined in green, is paired with negative reinforcement, a net that briefly lifts fish out of the water. "
               "The fish move toward the enrichment end, and one fish turns back before entering the right end, avoiding it.",
               vb=f"0 0 {W} {H}")


ALL["physiology"] = physiology_corridor


def physiology_dumbbell():
    c = []
    W, H = 720, 350
    S = 196                                    # side of each square chamber
    LX0, RX1 = 24, 696
    LX1, RX0 = LX0 + S, RX1 - S
    Y0, Y1 = 66, 66 + S
    CY0, CY1 = 132, 196                        # narrow hallway
    RED_T, RED_E = "#F8DCD3", "#C9604B"
    GRN_T, GRN_E = "#DDEFD5", "#5E9E4C"
    R = 16
    # hallway first, so the squares sit over its ends
    c.append(f'<rect x="{LX1 - 4}" y="{CY0}" width="{RX0 - LX1 + 8}" height="{CY1 - CY0}" fill="{WATER_FILL}"/>')
    c.append(f'<path d="M{LX1},{CY0} L{RX0},{CY0} M{LX1},{CY1} L{RX0},{CY1}" stroke="{WATER_EDGE}" stroke-width="2.2" stroke-linecap="round"/>')
    for x0, x1, t, e in ((LX0, LX1, RED_T, RED_E), (RX0, RX1, GRN_T, GRN_E)):
        c.append(f'<rect x="{x0}" y="{Y0}" width="{S}" height="{S}" rx="{R}" fill="{WATER_FILL}"/>')
        # three colored sides; the side facing the hallway stays neutral
        if x0 == LX0:
            d = (f"M{x1},{Y0 + R} Q{x1},{Y0} {x1 - R},{Y0} L{x0 + R},{Y0} Q{x0},{Y0} {x0},{Y0 + R} "
                 f"L{x0},{Y1 - R} Q{x0},{Y1} {x0 + R},{Y1} L{x1 - R},{Y1} Q{x1},{Y1} {x1},{Y1 - R}")
            g = f"M{x1},{Y0 + R} L{x1},{CY0} M{x1},{CY1} L{x1},{Y1 - R}"
        else:
            d = (f"M{x0},{Y0 + R} Q{x0},{Y0} {x0 + R},{Y0} L{x1 - R},{Y0} Q{x1},{Y0} {x1},{Y0 + R} "
                 f"L{x1},{Y1 - R} Q{x1},{Y1} {x1 - R},{Y1} L{x0 + R},{Y1} Q{x0},{Y1} {x0},{Y1 - R}")
            g = f"M{x0},{Y0 + R} L{x0},{CY0} M{x0},{CY1} L{x0},{Y1 - R}"
        c.append(f'<path d="{g}" fill="none" stroke="{WATER_EDGE}" stroke-width="2.2" stroke-linecap="round"/>')
        c.append(f'<path d="{d}" fill="none" stroke="{e}" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round"/>')
    c.append(f'<rect x="{LX1 - 3}" y="{CY0 + 2}" width="6" height="{CY1 - CY0 - 4}" fill="{WATER_FILL}"/>')
    c.append(f'<rect x="{RX0 - 3}" y="{CY0 + 2}" width="6" height="{CY1 - CY0 - 4}" fill="{WATER_FILL}"/>')

    # ---- enrichment: marbles and plants
    r = random.Random(5)
    cols = [("#BFE3E8", "#2E8C99"), ("#F6C9B8", "#B5584A"), ("#F3E1A6", "#A47F22"), ("#D9D0EE", "#5C4F86"), ("#C9E4C0", "#5E9150")]
    spots = [(50, 92), (80, 108), (54, 134), (112, 90), (52, 178), (86, 236), (54, 226), (120, 238), (160, 94), (196, 92), (190, 238), (82, 162)]
    for i, (mx, my) in enumerate(spots):
        f, s_ = cols[i % len(cols)]
        c.append(_marble(mx + r.uniform(-2, 2), my + r.uniform(-2, 2), r.uniform(6.2, 7.4), f, s_))
    for px, py, h, sd, ln in [(40, 210, 44, 7, 0.15), (150, 254, 44, 11, -0.12), (104, 254, 36, 2, 0.08), (140, 128, 34, 3, 0.1)]:
        c.append(_plant(px, py, h, sd, ln))

    # ---- negative reinforcement: the net, seen from above
    nx_, ny_ = (RX0 + RX1) / 2 + 4, (Y0 + Y1) / 2 + 6
    c.append(f'<path d="M{nx_ + 34},{ny_ - 24} L{nx_ + 66},{ny_ - 58}" stroke="#8C7F62" stroke-width="3.6" stroke-linecap="round"/>')
    c.append(f'<ellipse cx="{nx_}" cy="{ny_}" rx="40" ry="36" fill="{WHITE}" fill-opacity="0.55" stroke="#4E6E8E" stroke-width="2"/>')
    for k in range(-4, 5):
        w = math.sqrt(max(0, 1 - (k / 4.6) ** 2))
        c.append(f'<path d="M{nx_ - 40 * w:.1f},{ny_ + k * 7.8:.1f} L{nx_ + 40 * w:.1f},{ny_ + k * 7.8:.1f}" stroke="#8FA6BC" stroke-width="0.8"/>')
        c.append(f'<path d="M{nx_ + k * 8.8:.1f},{ny_ - 36 * w:.1f} L{nx_ + k * 8.8:.1f},{ny_ + 36 * w:.1f}" stroke="#8FA6BC" stroke-width="0.8"/>')

    # ---- fish: in the enrichment square, one in the hallway turning back
    c.append(_fish_top(124, 118, 0.9, math.pi - 0.15, wiggle=0.25))
    c.append(_fish_top(176, 176, 0.9, math.pi + 0.45, wiggle=-0.3))
    c.append(_fish_top(110, 200, 0.9, math.pi - 0.35, wiggle=0.2))
    c.append(_fish_top(410, 165, 0.95, math.pi, wiggle=0.3))
    c.append(_hand_curve(448, 148, (512, 132), (514, 200), 452, 184, seed=7, color="#5b6b86", w=2.2, head=10))

    # ---- labels
    c.append(_text((LX0 + LX1) / 2, 40, "Sensory enrichment", 18.5, 400, LABEL))
    c.append(_text((RX0 + RX1) / 2, 40, "Negative reinforcement", 18.5, 400, LABEL))
    # ---- the question, under the hallway

    return svg("".join(c), "Impact of microglia on animal physiology and behavior",
               "A learning and memory maze seen from above: two square chambers joined by a narrow hallway. The left chamber, outlined in red, holds sensory enrichment "
               "(colored marbles and plants); the right chamber, outlined in green, is paired with negative reinforcement, a net that briefly lifts fish out of the water. "
               "The fish gather in the enrichment chamber, and one fish in the hallway turns back before reaching the right chamber, avoiding it.",
               vb=f"0 0 {W} {H}")


ALL["physiology"] = physiology_dumbbell



def _soma(x, y, r=9):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{NEU_FILL}" stroke="{NEU_STROKE}" stroke-width="1.5"/>'
            f'<circle cx="{x - 1:.1f}" cy="{y - 1:.1f}" r="{r * 0.42:.1f}" fill="{NEU_NUC}"/>')


def _link(x1, y1, x2, y2, bend=0.15, seed=1, r=9, dashed=False, extra=0):
    """Axon from one soma to another, ending in a synaptic bouton."""
    rr = random.Random(seed)
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    sx, sy = x1 + ux * r, y1 + uy * r
    ex, ey = x2 - ux * (r + 5), y2 - uy * (r + 5)
    nx, ny = -uy * bend * L, ux * bend * L
    mx, my = (sx + ex) / 2 + nx, (sy + ey) / 2 + ny
    dash = ' stroke-dasharray="4 4"' if dashed else ""
    o = f'<path d="M{sx:.1f},{sy:.1f} Q{mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}" fill="none" stroke="{NEU_STROKE}" stroke-width="1.6" stroke-linecap="round"{dash}/>'
    o += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="3.6" fill="{NEU_NUC}" stroke="{NEU_STROKE}" stroke-width="1.1"/>'
    for k in range(extra):       # surplus, unpruned branches and synapses
        t = 0.35 + 0.22 * k
        bx = (1 - t) ** 2 * sx + 2 * (1 - t) * t * mx + t * t * ex
        by = (1 - t) ** 2 * sy + 2 * (1 - t) * t * my + t * t * ey
        side = -1 if k % 2 else 1
        a = math.atan2(uy, ux) + side * rr.uniform(0.9, 1.3)
        l2 = rr.uniform(14, 20)
        tx, ty = bx + math.cos(a) * l2, by + math.sin(a) * l2
        o += f'<path d="M{bx:.1f},{by:.1f} Q{(bx + tx) / 2 + rr.uniform(-3, 3):.1f},{(by + ty) / 2 + rr.uniform(-3, 3):.1f} {tx:.1f},{ty:.1f}" fill="none" stroke="{NEU_STROKE}" stroke-width="1.3" stroke-linecap="round"/>'
        o += f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="3.2" fill="{NEU_NUC}" stroke="{NEU_STROKE}" stroke-width="1"/>'
    return o


def _circuit(ox, oy, miswired=False):
    A, B, C = (ox - 62, oy - 4), (ox + 4, oy + 44), (ox + 66, oy - 8)
    o = ""
    if miswired:
        o += _link(*A, *B, 0.12, 3, extra=2) + _link(*B, *C, -0.14, 4, extra=2) + _link(*A, *C, 0.22, 5, dashed=True)
        o += _link(*C, *A, 0.3, 6, extra=1)
    else:
        o += _link(*A, *B, 0.12, 3) + _link(*B, *C, -0.14, 4) + _link(*A, *C, 0.22, 5)
    for p in (A, B, C):
        o += _soma(*p)
    return o


def neuron_bio(x, y, s=1.0, seed=3, axon=110, terminals=2, extra=0, fill=NEU_FILL, stroke=NEU_STROKE):
    """Healthy multipolar neuron (BioRender-like): tapered dendrites, axon to the right ending in boutons."""
    r = random.Random(seed)
    shapes, bout = [], []
    for i in range(6):
        a = math.pi * 0.45 + i / 5 * math.pi * 1.1 + r.uniform(-0.12, 0.12)
        L = r.uniform(20, 28) * s
        pts = [(x + math.cos(a) * 6 * s, y + math.sin(a) * 6 * s)]
        aa = a
        for _ in range(4):
            aa += r.uniform(-0.15, 0.15)
            px, py = pts[-1]
            pts.append((px + math.cos(aa) * L / 4, py + math.sin(aa) * L / 4))
        shapes.append(_tapered(pts, 6.5 * s, 1.0 * s))
        bx, by = pts[2]
        fa = aa + r.choice((-1, 1)) * 0.7
        shapes.append(_tapered([(bx, by)] + [(bx + math.cos(fa) * L * 0.4 * k / 3, by + math.sin(fa) * L * 0.4 * k / 3) for k in (1, 2, 3)], 3.2 * s, 0.8 * s))
    ex = x + axon * s
    ax_pts = [(x + 8 * s, y)] + [(x + 8 * s + k * (axon - 18) * s / 4, y + math.sin(k * 1.3) * 2 * s) for k in (1, 2, 3, 4)]
    shapes.append(_tapered(ax_pts, 4.4 * s, 2.4 * s))
    tx, ty = ax_pts[-1]
    n = terminals + extra
    for k in range(n):
        a = (k - (n - 1) / 2) * (1.6 / max(1, n - 1)) if n > 1 else 0
        L = (16 + (6 if k >= terminals else 0)) * s
        bxp, byp = tx + math.cos(a) * L, ty + math.sin(a) * L
        shapes.append(_tapered([(tx, ty), ((tx + bxp) / 2, (ty + byp) / 2 + r.uniform(-2, 2)), (bxp, byp)], 2.4 * s, 1.6 * s))
        bout.append((bxp, byp))
    soma = blob(x, y, 11 * s, 10 * s, seed + 2, 9, 0.08)
    o = "".join(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="2.2" stroke-linejoin="round"/>' for d in shapes)
    o += f'<path d="{soma}" fill="none" stroke="{stroke}" stroke-width="2.2"/>'
    o += "".join(f'<path d="{d}" fill="{fill}"/>' for d in shapes)
    o += f'<path d="{soma}" fill="{fill}"/>'
    o += f'<circle cx="{x}" cy="{y}" r="{4.2 * s:.1f}" fill="{NEU_NUC}" stroke="{stroke}" stroke-width="1"/>'
    for bx, by in bout:
        o += f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{4 * s:.1f}" fill="{NEU_NUC}" stroke="{stroke}" stroke-width="1.3"/>'
    return o



def physiology_full():
    c, top = [], []
    W = 720
    DY = 178
    K = 0.84                                   # maze scale
    PROC = "#6b7280"
    # ---- top: microglia shape circuits early in life (drawn, then centered)
    n1a, ny = 44, 104
    top.append(_text(150, 24, "Early development", 15.5, 400, LABEL))
    top.append(neuron_bio(n1a, ny, 1.0, seed=3, axon=100, terminals=2))
    top.append(neuron_bio(n1a + 130, ny, 1.0, seed=8, axon=60, terminals=1))
    top.append(microglia_t(n1a + 88, ny - 44, 0.42, seed=53, n=7, length=46, depth=2, soma_r=13, w0=6.5, curl=0.25))
    n2a = 404
    top.append(_text(510, 24, "Disrupted microglia", 15.5, 400, LABEL))
    top.append(neuron_bio(n2a, ny, 1.0, seed=3, axon=100, terminals=2, extra=3))
    top.append(neuron_bio(n2a + 130, ny, 1.0, seed=8, axon=60, terminals=1, extra=2))
    top.append(f'<g opacity="0.32">{microglia_t(n2a + 88, ny - 44, 0.42, seed=53, n=7, length=46, depth=2, soma_r=13, w0=6.5, curl=0.25)}</g>')
    top.append(_hand_arrow(286, ny - 2, 356, ny - 2, bend=0.08, seed=23))
    top.append(_italic(510, ny + 56, "altered circuits", 13, PROC))
    TX = 360 - (14 + 610) / 2                  # content spans x 14..610
    c.append(f'<g transform="translate({TX:.1f},0)">{"".join(top)}</g>')
    # arrow down into the behavioral assay (hallway center is x = 360)
    hall_y = DY + K * 132
    c.append(_hand_arrow(452 + TX, ny + 66, 364, hall_y - 8, bend=0.18, seed=29))
    c.append(_italic(400, hall_y - 92, "behavioral changes", 13, PROC, anchor="end"))
    # ---- bottom: the maze, slightly smaller, centered on x = 360
    inner = physiology_dumbbell()
    inner = inner[inner.index('</desc>') + 7: inner.rindex('</svg>')]
    c.append(f'<g transform="translate(360,{DY}) scale({K}) translate(-360,0)">{inner}</g>')
    H = DY + K * 270 + 6
    return svg("".join(c), "Impact of microglia on animal physiology and behavior",
               "Early in development, microglia sit beside connected neurons and help shape their synapses. When microglia are disrupted, circuits are altered, "
               "with surplus synapses. This leads to behavioral changes, measured in a learning and memory maze: two square chambers joined by a narrow hallway, "
               "the left outlined in red for sensory enrichment and the right outlined in green for negative reinforcement, which the fish learn to avoid.",
               vb=f"0 0 {W} {H:.0f}")


ALL["physiology"] = physiology_full


# ================================================================== Evolution: surface vs cave microglia
TISSUE_FILL, TISSUE_EDGE = "#F4F0F8", "#CFC6E0"


def _mg_small(x, y, seed, s=0.3):
    return microglia_t(x, y, s, seed=seed, n=6, length=44, depth=1, soma_r=13, w0=7, curl=0.2)


def _patch(cx, cy, n, seed, r=46):
    """A round patch of brain tissue holding n small microglia, spread out."""
    o = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{TISSUE_FILL}" stroke="{TISSUE_EDGE}" stroke-width="1.5"/>'
    rr = random.Random(seed)
    gap = 30 if n <= 4 else (22 if n <= 6 else 17)
    sc = 0.24 if n <= 4 else (0.2 if n <= 6 else 0.16)
    best = []
    for attempt in range(60):
        pts, tries = [], 0
        while len(pts) < n and tries < 3000:
            tries += 1
            a = rr.uniform(0, math.tau); d = math.sqrt(rr.random()) * (r - 14)
            x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
            if all(math.hypot(x - px, y - py) > gap for px, py in pts):
                pts.append((x, y))
        if len(pts) > len(best):
            best = pts
        if len(best) == n:
            break
    for k, (x, y) in enumerate(best):
        v = (seed * 7 + k) % 4
        rot = rr.uniform(0, 360)
        o += f'<use href="#evo-mg{v}" transform="translate({x:.1f},{y:.1f}) rotate({rot:.0f}) scale({sc / 0.2:.2f})"/>'
    return o


def _mg_defs():
    return "<defs>" + "".join(
        f'<g id="evo-mg{v}">{microglia_t(0, 0, 0.2, seed=101 + v * 13, n=6, length=44, depth=1, soma_r=13, w0=7, curl=0.2)}</g>'
        for v in range(4)) + "</defs>"


def _fish_surface(x, y, s):
    o = fish(x, y, s, SURF_FILL, SURF_STROKE, eye=True)
    # darker back and a lateral stripe: pigmented
    o += (f'<path d="M{x - 28 * s:.1f},{y - 4 * s:.1f} C{x - 10 * s:.1f},{y - 15 * s:.1f} {x + 12 * s:.1f},{y - 16 * s:.1f} {x + 26 * s:.1f},{y - 7 * s:.1f} '
          f'C{x + 10 * s:.1f},{y - 10 * s:.1f} {x - 10 * s:.1f},{y - 9 * s:.1f} {x - 28 * s:.1f},{y - 4 * s:.1f} Z" fill="{SURF_STROKE}" fill-opacity="0.28"/>')
    o += (f'<path d="M{x - 30 * s:.1f},{y + 1 * s:.1f} C{x - 12 * s:.1f},{y + 1 * s:.1f} {x + 2 * s:.1f},{y:.1f} {x + 9 * s:.1f},{y - 1 * s:.1f}" fill="none" '
          f'stroke="{SURF_STROKE}" stroke-opacity="0.55" stroke-width="{1.6 * s:.1f}" stroke-linecap="round"/>')
    return o


def _mg_lyso(cx, cy, lys, seed):
    """One microglia packed with lysosomes; lys = [(dx, dy, r, fill, core)]."""
    o = microglia_t(cx, cy, 1.0, seed=seed, n=6, length=26, depth=1, soma_r=34, w0=11, curl=0.1, nucleus=False)
    o += f'<path d="{blob(cx + 14, cy + 14, 11, 9, seed + 3, 8, 0.08)}" fill="{MG_NUC}" stroke="{MG_STROKE}" stroke-width="1"/>'
    for dx, dy, r, f, core in lys:
        o += f'<circle cx="{cx + dx}" cy="{cy + dy}" r="{r}" fill="{f}" stroke="{LYS_STROKE}" stroke-width="1.3"/>'
        o += f'<circle cx="{cx + dx - r * 0.25:.1f}" cy="{cy + dy - r * 0.2:.1f}" r="{r * 0.3:.1f}" fill="{core}"/>'
        o += f'<circle cx="{cx + dx + r * 0.3:.1f}" cy="{cy + dy + r * 0.28:.1f}" r="{r * 0.2:.1f}" fill="{core}"/>'
    return o


def evolution_detailed():
    c = []
    c.append(_mg_defs())
    W, H = 720, 540
    PROC = "#6b7280"
    FX, P1, P2, LX_ = 104, 296, 420, 600
    R1, R2 = 112, 268
    # ---- column headings
    c.append(_text((P1 + P2) / 2, 22, "Microglia over development", 15.5, 400, LABEL))
    c.append(_hand_arrow(P1 - 30, 40, P2 + 30, 40, bend=0.02, seed=4))
    c.append(_text(LX_, 22, "Microglial lysosomes", 15.5, 400, LABEL))
    c.append(f'<path d="M24,{(R1 + R2) / 2 + 2} L{W - 24},{(R1 + R2) / 2 + 2}" stroke="{G30}" stroke-width="1.2" stroke-dasharray="4 6"/>')

    # ---- row 1: surface fish
    c.append(_fish_surface(FX, R1 - 6, 1.55))
    c.append(_text(FX, R1 + 46, "Surface fish", 15.5, 400, SURF_STROKE))
    c.append(_patch(P1, R1, 2, 11))
    c.append(_patch(P2, R1, 4, 12))
    c.append(_mg_lyso(LX_, R1, [(-14, -10, 7, LYS_FILL, LYS_CORE), (8, -16, 6, LYS_FILL, LYS_CORE), (-16, 12, 6, LYS_FILL, LYS_CORE)], 24))

    # ---- row 2: cavefish
    c.append(fish(FX, R2 - 10, 1.55, CAVE_FILL, CAVE_STROKE, eye=False))
    c.append(_text(FX, R2 + 42, "Cavefish", 15.5, 400, CAVE_STROKE))
    c.append(_italic(FX, R2 + 64, "altered sleep, circadian rhythms,", 11.5, PROC))
    c.append(_italic(FX, R2 + 80, "and sensory processing;", 11.5, PROC))
    c.append(_italic(FX, R2 + 96, "diminished immune responses", 11.5, PROC))
    c.append(_patch(P1, R2, 4, 21))
    c.append(_patch(P2, R2, 10, 22))
    c.append(_text((P1 + P2) / 2, R2 + 72, "more microglia", 13.5, 400, LABEL2))
    deep, deep_core = "#E79BC2", "#9C1E5E"
    c.append(_mg_lyso(LX_, R2, [(-17, -14, 10, deep, deep_core), (6, -21, 9, deep, deep_core), (21, -4, 8.5, deep, deep_core),
                                  (-22, 9, 9, deep, deep_core), (-3, 2, 9.5, deep, deep_core), (-8, 23, 7.5, deep, deep_core)], 24))
    c.append(_text(LX_, R2 + 66, "lower lysosomal pH", 13.5, 400, LABEL2))
    c.append(_text(LX_, R2 + 84, "and expanded proteolytic", 13.5, 400, LABEL2))
    c.append(_text(LX_, R2 + 102, "compartments", 13.5, 400, LABEL2))

    # ---- bottom: shared response to inflammation
    BY = 478
    c.append(_text(356, BY - 84, "Rapid microglial expansion after inflammation", 14.5, 400, LABEL))
    c.append(_italic(356, BY - 64, "in both surface fish and cavefish, distinct from zebrafish", 12.5, PROC))
    c.append(f'<rect x="176" y="{BY - 50}" width="360" height="104" rx="18" fill="#FCF2EE" fill-opacity="0.55" stroke="#F0D5CC" stroke-opacity="0.7" stroke-width="1.3"/>')
    c.append(_patch(238, BY + 2, 3, 31, r=40))
    r = random.Random(9)
    for _ in range(18):
        c.append(f'<circle cx="{r.uniform(318, 384):.1f}" cy="{BY - 22 + r.uniform(-12, 8):.1f}" r="{r.uniform(1.6, 2.8):.1f}" fill="{INFL}" fill-opacity="0.75"/>')
    c.append(_hand_arrow(292, BY - 2, 408, BY - 2, bend=0.06, seed=33))
    c.append(_italic(350, BY + 22, "inflammatory cue", 12.5, PROC))
    c.append(_patch(474, BY + 2, 10, 32, r=40))

    return svg("".join(c), "Evolution of microglia and macrophages",
               "Microglia in surface and cave forms of the Mexican tetra, Astyanax mexicanus. Cavefish, which show altered sleep, circadian rhythms, and sensory processing, "
               "and diminished immune responses, gain more microglia than surface fish over development. Their microglia have lower lysosomal pH and expanded "
               "proteolytic compartments. In both forms, microglia expand rapidly in response to an inflammatory cue, unlike in zebrafish.",
               vb=f"0 0 {W} {H}")


ALL["evolution"] = evolution_detailed


def _macrophage(x, y, seed, s=1.0):
    return (f'<path d="{blob(x, y, 4.6 * s, 3.6 * s, seed, 7, 0.22)}" fill="{MG_FILL}" stroke="{MG_STROKE}" stroke-width="1.3"/>'
            f'<circle cx="{x - 0.6 * s:.1f}" cy="{y - 0.4 * s:.1f}" r="{1.5 * s:.1f}" fill="{MG_STROKE}" fill-opacity="0.7"/>')


def _fish_brain(cx, cy, s=1.0, cave=False):
    """Fish brain seen from above, anterior to the right. Returns (svg, lobes) where lobes are ellipses."""
    tect = (24, 20) if not cave else (19, 15)
    lobes = [
        (cx + 62 * s, cy - 9 * s, 9 * s, 7 * s), (cx + 62 * s, cy + 9 * s, 9 * s, 7 * s),         # olfactory bulbs
        (cx + 38 * s, cy - 14 * s, 18 * s, 13 * s), (cx + 38 * s, cy + 14 * s, 18 * s, 13 * s),   # telencephalon
        (cx + 4 * s, cy - 20 * s, tect[0] * s, tect[1] * s), (cx + 4 * s, cy + 20 * s, tect[0] * s, tect[1] * s),  # optic tecta
        (cx - 28 * s, cy, 17 * s, 15 * s),                                                       # cerebellum
    ]
    hb = (f"M{cx - 34 * s:.1f},{cy - 15 * s:.1f} C{cx - 56 * s:.1f},{cy - 14 * s:.1f} {cx - 72 * s:.1f},{cy - 8 * s:.1f} {cx - 80 * s:.1f},{cy - 5 * s:.1f} "
          f"L{cx - 80 * s:.1f},{cy + 5 * s:.1f} C{cx - 72 * s:.1f},{cy + 8 * s:.1f} {cx - 56 * s:.1f},{cy + 14 * s:.1f} {cx - 34 * s:.1f},{cy + 15 * s:.1f} Z")
    o = f'<path d="{hb}" fill="{TISSUE_FILL}" stroke="{NEU_STROKE}" stroke-opacity="0.55" stroke-width="1.6"/>'
    for (x, y, rx, ry) in lobes[:6]:
        o += f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{TISSUE_FILL}" stroke="{NEU_STROKE}" stroke-opacity="0.55" stroke-width="1.6"/>'
    x, y, rx, ry = lobes[6]
    o += f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{TISSUE_FILL}" stroke="{NEU_STROKE}" stroke-opacity="0.55" stroke-width="1.6"/>'
    return o, lobes


def _brain_microglia(lobes, n, seed, sc=0.2, gap=21):
    rr = random.Random(seed)
    pts, tries = [], 0
    big = [l for l in lobes if l[2] > 12]
    while len(pts) < n and tries < 5000:
        tries += 1
        x0, y0, rx, ry = rr.choice(big)
        a = rr.uniform(0, math.tau); d = math.sqrt(rr.random()) * 0.72
        x, y = x0 + math.cos(a) * rx * d, y0 + math.sin(a) * ry * d
        if all(math.hypot(x - px, y - py) > gap for px, py in pts):
            pts.append((x, y))
    o = ""
    for k, (x, y) in enumerate(pts):
        o += f'<use href="#evo-mg{(seed + k) % 4}" transform="translate({x:.1f},{y:.1f}) rotate({rr.uniform(0, 360):.0f}) scale({sc / 0.2:.2f})"/>'
    return o


def evolution_simple():
    c = [_mg_defs()]
    W, H = 720, 360
    FX, BX, LX_ = 120, 372, 610
    R1, R2 = 108, 268
    # ---- column headings
    c.append(_text(FX, 24, "Macrophages in the tail", 15.5, 400, LABEL))
    c.append(_text((BX + LX_) / 2, 24, "Microglia in the brain", 15.5, 400, LABEL))
    c.append(f'<path d="M24,{(R1 + R2) / 2 + 4} L{W - 24},{(R1 + R2) / 2 + 4}" stroke="{G30}" stroke-width="1.2" stroke-dasharray="4 6"/>')

    fs = 2.0
    surf_m = [(-15, -5), (-19, 5), (-24, -3), (-28, 3), (-36, -6), (-40, 5), (-21, -9), (-33, 1)]
    cave_m = [(-20, 2), (-38, -5)]
    for (row, fbody, fstroke, eye, mlist, name, cave) in (
            (R1, SURF_FILL, SURF_STROKE, True, surf_m, "Surface fish", False),
            (R2, CAVE_FILL, CAVE_STROKE, False, cave_m, "Cavefish", True)):
        fy = row - 8
        c.append(_fish_surface(FX + 6, fy, fs) if not cave else fish(FX + 6, fy, fs, fbody, fstroke, eye=False))
        for k, (u, v) in enumerate(mlist):
            c.append(_macrophage(FX + 6 + u * fs, fy + v * fs, 40 + k + (9 if cave else 0), 1.2))
        c.append(_text(FX, row + 52, name, 15.5, 400, fstroke))
        b, lobes = _fish_brain(BX + 6, row - 8, 1.3, cave=cave)
        c.append(b)
        c.append(_brain_microglia(lobes, 12 if cave else 4, 61 if cave else 17, sc=0.19 if cave else 0.22, gap=17 if cave else 30))

    c.append(_text(FX, R2 + 74, "fewer macrophages", 13.5, 400, LABEL2))
    c.append(_text(BX, R2 + 74, "more microglia", 13.5, 400, LABEL2))
    c.append(_mg_lyso(LX_, R1, [(-14, -10, 7, LYS_FILL, LYS_CORE), (8, -16, 6, LYS_FILL, LYS_CORE), (-16, 12, 6, LYS_FILL, LYS_CORE)], 24))
    deep, deep_core = "#E79BC2", "#9C1E5E"
    c.append(_mg_lyso(LX_, R2, [(-17, -14, 10, deep, deep_core), (6, -21, 9, deep, deep_core), (21, -4, 8.5, deep, deep_core),
                                  (-22, 9, 9, deep, deep_core), (-3, 2, 9.5, deep, deep_core), (-8, 23, 7.5, deep, deep_core)], 24))
    c.append(_text(LX_, R2 + 74, "lower lysosomal pH", 13.5, 400, LABEL2))
    c.append(_text(LX_, R2 + 92, "and larger proteolytic compartments", 13.5, 400, LABEL2))

    return svg("".join(c), "Evolution of microglia and macrophages",
               "Surface fish and cavefish forms of the Mexican tetra compared. Cavefish have fewer macrophages in the tail, more microglia in the brain, "
               "and microglia with lower lysosomal pH and larger proteolytic compartments.",
               vb=f"0 0 {W} {H + 12}")


ALL["evolution"] = evolution_simple


BRAIN_OUTLINE = [(86, 0), (84, -8), (78, -15), (68, -20), (56, -21), (46, -19), (40, -17), (34, -24), (24, -34), (10, -40), (-6, -40), (-18, -34), (-24, -26), (-28, -20), (-34, -22), (-42, -20), (-46, -15), (-56, -12), (-70, -9), (-84, -6), (-88, 0), (-84, 6), (-70, 9), (-56, 12), (-46, 15), (-42, 20), (-34, 22), (-28, 20), (-24, 26), (-18, 34), (-6, 40), (10, 40), (24, 34), (34, 24), (40, 17), (46, 19), (56, 21), (68, 20), (78, 15), (84, 8)]


def _inside(poly, x, y):
    n, ins = len(poly), False
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins


def _brain_outline(cx, cy, s, n_mg, seed, sc, gap):
    poly = [(cx + u * s, cy + v * s) for u, v in BRAIN_OUTLINE]
    inner = [(cx + u * s * 0.8, cy + v * s * 0.72) for u, v in BRAIN_OUTLINE]
    o = f'<path d="{smooth_closed(poly)}" fill="{TISSUE_FILL}" stroke="{NEU_STROKE}" stroke-opacity="0.6" stroke-width="1.8"/>'
    o += f'<path d="M{cx + 82 * s:.1f},{cy:.1f} L{cx - 40 * s:.1f},{cy:.1f}" stroke="{NEU_STROKE}" stroke-opacity="0.28" stroke-width="1.2"/>'
    rr = random.Random(seed)
    pts, tries = [], 0
    while len(pts) < n_mg and tries < 8000:
        tries += 1
        x, y = cx + rr.uniform(-80, 80) * s, cy + rr.uniform(-45, 45) * s
        if _inside(inner, x, y) and all(math.hypot(x - px, y - py) > gap for px, py in pts):
            pts.append((x, y))
    for k, (x, y) in enumerate(pts):
        o += f'<use href="#evo-mg{(seed + k) % 4}" transform="translate({x:.1f},{y:.1f}) rotate({rr.uniform(0, 360):.0f}) scale({sc / 0.2:.2f})"/>'
    _LAST_MG[:] = pts
    return o


_LAST_MG = []


def _larva(x, y, s, body, stroke, cave=False):
    """Larval fish, side view, facing right: fin fold, yolk, notochord, and eye."""
    P = lambda u, v: (x + u * s, y + v * s)
    fold = [P(6, -9), P(-10, -14), P(-36, -14), P(-58, -10), P(-72, 0), P(-58, 10), P(-36, 13), P(-18, 11), P(-6, 8)]
    o = f'<path d="{smooth_closed(fold)}" fill="{WHITE}" fill-opacity="0.75" stroke="{stroke}" stroke-opacity="0.45" stroke-width="1.3"/>'
    bodyp = [P(47, 0), P(43, -8), P(33, -12), P(20, -11), P(2, -8), P(-20, -6.5), P(-42, -4.5), P(-60, -2), P(-65, 0), P(-60, 2),
             P(-42, 4.5), P(-20, 6), P(-4, 7), P(28, 9), P(42, 6)]
    o += f'<path d="{smooth_closed(bodyp)}" fill="{body}" stroke="{stroke}" stroke-width="1.6"/>'
    yx, yy = P(12, 9)
    o += f'<ellipse cx="{yx:.1f}" cy="{yy:.1f}" rx="{18 * s:.1f}" ry="{6.5 * s:.1f}" fill="#F6E7C8" stroke="{stroke}" stroke-opacity="0.7" stroke-width="1.2"/>'
    nx0, ny0 = P(18, -2); nx1, ny1 = P(-56, 0)
    o += f'<path d="M{nx0:.1f},{ny0:.1f} L{nx1:.1f},{ny1:.1f}" stroke="{stroke}" stroke-opacity="0.35" stroke-width="{1.4 * s:.1f}" stroke-linecap="round"/>'
    ex, ey = P(30, -3)
    if cave:
        o += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{3.2 * s:.1f}" fill="{stroke}" fill-opacity="0.25" stroke="{stroke}" stroke-opacity="0.5" stroke-width="1"/>'
    else:
        o += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{6 * s:.1f}" fill="#23324d" stroke="{stroke}" stroke-width="1.1"/>'
        o += f'<circle cx="{ex + 1.5 * s:.1f}" cy="{ey - 1.5 * s:.1f}" r="{1.6 * s:.1f}" fill="{WHITE}"/>'
        for u in range(-50, 20, 9):       # melanophore stripes: pigmented
            for v in (-5.5, 6.5):
                px, py = P(u + (2 if v > 0 else 0), v * (1 - (-u) / 120))
                o += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{1.3 * s:.1f}" fill="#2b2d33" fill-opacity="0.7"/>'
    return o


def _mirror(svg_str, x):
    """Flip a drawing horizontally about x, so the animal faces left."""
    return f'<g transform="translate({2 * x:.1f},0) scale(-1,1)">{svg_str}</g>'


def evolution_larva():
    c = [_mg_defs()]
    W, H = 720, 372
    FX, BX, LX_ = 124, 376, 612
    R1, R2 = 108, 268
    c.append(_text(FX, 24, "Macrophages in larvae", 15.5, 400, LABEL))
    c.append(_text((BX + LX_) / 2, 24, "Microglia in the brain", 15.5, 400, LABEL))
    c.append(f'<path d="M24,{(R1 + R2) / 2 + 4} L{W - 24},{(R1 + R2) / 2 + 4}" stroke="{G30}" stroke-width="1.2" stroke-dasharray="4 6"/>')
    ls = 1.65
    surf_m = [(-22, -2), (-28, 4), (-34, -4), (-40, 3), (-46, -5), (-52, 2), (-58, -2), (-37, 9)]
    cave_m = [(-30, 2), (-50, -3)]
    for (row, fb, fst, mlist, name, cave) in ((R1, SURF_FILL, SURF_STROKE, surf_m, "Surface fish", False),
                                             (R2, CAVE_FILL, CAVE_STROKE, cave_m, "Cavefish", True)):
        lx, ly = FX + 14, row - 6
        lv = _larva(lx, ly, ls, fb, fst, cave)
        for k, (u, v) in enumerate(mlist):
            lv += _macrophage(lx + u * ls, ly + v * ls, 40 + k + (9 if cave else 0), 1.15)
        c.append(_mirror(lv, FX))
        c.append(_text(FX, row + 50, name, 15.5, 400, fst))
        c.append(_mirror(_brain_outline(BX, row - 6, 1.12, 7 if cave else 4, 61 if cave else 17, 0.21 if cave else 0.22, 26 if cave else 34), BX))
        # zoom inset: one microglia, enlarged to show its lysosomes
        mx, my = max(((2 * BX - x, y) for x, y in _LAST_MG), key=lambda p: p[0])
        ix, iy, ir = LX_, row - 6, 62
        c.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="13" fill="none" stroke="{MG_STROKE}" stroke-width="1.4" stroke-dasharray="3 3"/>')
        for sgn in (-1, 1):
            a = math.atan2(iy - my, ix - mx) + sgn * math.pi / 2
            x0, y0 = mx + math.cos(a) * 13, my + math.sin(a) * 13
            x1, y1 = ix + math.cos(a) * ir, iy + math.sin(a) * ir
            c.append(f'<path d="M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}" stroke="{MG_STROKE}" stroke-opacity="0.55" stroke-width="1.2" stroke-dasharray="3 4"/>')
        c.append(f'<circle cx="{ix}" cy="{iy}" r="{ir}" fill="{WHITE}" stroke="{MG_STROKE}" stroke-opacity="0.7" stroke-width="1.6"/>')
        if cave:
            deep, deep_core = "#E79BC2", "#9C1E5E"
            lys = [(-17, -14, 10, deep, deep_core), (6, -21, 9, deep, deep_core), (21, -4, 8.5, deep, deep_core),
                   (-22, 9, 9, deep, deep_core), (-3, 2, 9.5, deep, deep_core), (-8, 23, 7.5, deep, deep_core)]
        else:
            lys = [(-14, -10, 7, LYS_FILL, LYS_CORE), (8, -16, 6, LYS_FILL, LYS_CORE), (-16, 12, 6, LYS_FILL, LYS_CORE)]
        c.append(f'<g transform="translate({ix},{iy}) scale(0.78) translate({-ix},{-iy})">{_mg_lyso(ix, iy, lys, 24)}</g>')
    c.append(_text(FX, R2 + 74, "fewer macrophages", 13.5, 400, LABEL2))
    c.append(_text(BX, R2 + 74, "more microglia", 13.5, 400, LABEL2))
    c.append(_text(LX_, R2 + 74, "lower lysosomal pH", 13.5, 400, LABEL2))
    c.append(_text(LX_, R2 + 92, "and larger proteolytic compartments", 13.5, 400, LABEL2))
    return svg("".join(c), "Evolution of microglia and macrophages",
               "Surface fish and cavefish forms of the Mexican tetra compared. Cavefish larvae have fewer macrophages in the tail; cavefish have more microglia "
               "in the brain, and their microglia have lower lysosomal pH and larger proteolytic compartments.",
               vb=f"0 0 {W} {H}")


ALL["evolution"] = evolution_larva


def evolution_with_fish():
    c = []
    W = 720
    DY = 148
    fy = 58
    xs = (140, 360, 580)
    c.append(_mirror(_fish_side_zf(xs[0], fy, 1.45), xs[0]))
    c.append(_mirror(_fish_surface(xs[1], fy, 1.45), xs[1]))
    c.append(_mirror(fish(xs[2], fy, 1.45, CAVE_FILL, CAVE_STROKE, eye=False), xs[2]))
    c.append(_text(xs[0] + 9, fy + 52, "Zebrafish", 15.5, 400, ZF_STRIPE))
    c.append(_text(xs[1] + 9, fy + 52, "Surface fish", 15.5, 400, SURF_STROKE))
    c.append(_text(xs[2] + 9, fy + 52, "Cavefish", 15.5, 400, CAVE_STROKE))
    # facing left: each arrow centered between tail tip (x + 48s) and the next nose (next x - 36s)
    for a, b, sd in ((xs[0], xs[1], 61), (xs[1], xs[2], 71)):
        mid = (a + 48 * 1.45 + b - 36 * 1.45) / 2
        c.append(_hand_double_len(mid - 30, fy, mid + 30, fy, 56, seed=sd))
    c.append(f'<path d="M24,{DY - 12} L{W - 24},{DY - 12}" stroke="{G30}" stroke-width="1.2"/>')
    inner = evolution_larva()
    vb = inner[inner.index('viewBox="') + 9:].split('"')[0].split()
    h_in = float(vb[3])
    inner = inner[inner.index('</desc>') + 7: inner.rindex('</svg>')]
    c.append(f'<g transform="translate(0,{DY})">{inner}</g>')
    return svg("".join(c), "Evolution of microglia and macrophages",
               "Surface fish and cavefish forms of the Mexican tetra, compared with each other and with zebrafish. Cavefish larvae have fewer macrophages in the tail; "
               "cavefish have more microglia in the brain, and their microglia have lower lysosomal pH and larger proteolytic compartments.",
               vb=f"0 0 {W} {DY + h_in:.0f}")


ALL["evolution"] = evolution_with_fish


# ================================================================== Cell biology: organelles under stress
LYS_DEEP, LYS_DEEP_CORE = "#E79BC2", "#9C1E5E"                      # acidic lysosomes
PEX_FILL, PEX_STROKE, PEX_CORE = "#D9EDCB", "#5E9150", "#8FBF73"    # peroxisomes (green)
ER_FILL, ER_STROKE = "#FFE2BF", "#D4892F"                           # endoplasmic reticulum (orange)
GOL_FILL, GOL_STROKE = "#D3E6F5", "#2F6FA8"                         # Golgi (blue)
MITO_FILL, MITO_STROKE = "#F9D3C6", "#C0583F"                       # mitochondria (salmon)


def _lyso(x, y, r, deep=False):
    f, core = (LYS_DEEP, LYS_DEEP_CORE) if deep else (LYS_FILL, LYS_CORE)
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{f}" stroke="{LYS_STROKE}" stroke-width="1.3"/>'
            f'<circle cx="{x - r * 0.25:.1f}" cy="{y - r * 0.2:.1f}" r="{r * 0.3:.1f}" fill="{core}"/>'
            f'<circle cx="{x + r * 0.3:.1f}" cy="{y + r * 0.28:.1f}" r="{r * 0.2:.1f}" fill="{core}"/>')


def _perox(x, y, r):
    """Peroxisome: a single-membrane vesicle with a dense crystalline core."""
    k = r * 0.42
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{PEX_FILL}" stroke="{PEX_STROKE}" stroke-width="1.3"/>'
            f'<rect x="{x - k:.1f}" y="{y - k:.1f}" width="{2 * k:.1f}" height="{2 * k:.1f}" rx="0.8" fill="{PEX_CORE}" '
            f'transform="rotate(45 {x:.1f} {y:.1f})"/>')


def _mito(x, y, L, ang, w=11):
    """Mitochondrion: a capsule with zigzag cristae."""
    o = f'<g transform="translate({x:.1f},{y:.1f}) rotate({ang})">'
    o += f'<rect x="{-L / 2:.1f}" y="{-w / 2:.1f}" width="{L}" height="{w}" rx="{w / 2:.1f}" fill="{MITO_FILL}" stroke="{MITO_STROKE}" stroke-width="1.3"/>'
    if L > w + 4:
        n = max(2, int((L - w) / 5))
        pts = [(-L / 2 + w / 2 + i * (L - w) / n, (-1) ** i * w * 0.28) for i in range(n + 1)]
        o += f'<path d="M' + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'" fill="none" stroke="{MITO_STROKE}" stroke-width="1" stroke-linejoin="round"/>'
    return o + "</g>"


def _arc_pts(cx, cy, rx, ry, a0, a1, n=14, wave=0.0, waves=5, phase=0.0):
    pts = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        k = 1 + wave * math.sin(t * math.tau * waves / 2 + phase)
        pts.append((cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    return pts


def _er(nx, ny, base_rx, base_ry, swollen=False):
    """Rough ER: wavy sheets wrapped around one side of the nucleus, studded with ribosomes."""
    o = ""
    w = 7.5 if swollen else 4.2
    gap = 13 if swollen else 10
    spans = [(118, 262), (110, 270), (124, 252)]
    for i, (a0, a1) in enumerate(spans):
        rx, ry = base_rx + 12 + i * gap, base_ry + 12 + i * gap
        d = smooth_open(_arc_pts(nx, ny, rx, ry, a0, a1, wave=0.06, waves=6, phase=i))
        o += tube([(d, w)], 0, ER_FILL, ER_STROKE)
        if i == 2 or (swollen and i == 1):
            for j, (px, py) in enumerate(_arc_pts(nx, ny, rx + w / 2 + 2.6, ry + w / 2 + 2.6, a0 + 6, a1 - 6, n=12, wave=0.06, waves=6, phase=i)):
                if j % 2 == 0:
                    o += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.5" fill="{ER_STROKE}"/>'
    return o


def _golgi(x, y, ang, dispersed=False, seed=3):
    """Golgi apparatus: a stack of curved cisternae with budding vesicles; under stress, scattered mini-stacks."""
    r = random.Random(seed)
    o = f'<g transform="translate({x:.1f},{y:.1f}) rotate({ang})">'
    paths = []
    if not dispersed:
        for i in range(4):
            L = 44 - i * 6
            off = i * 7
            paths.append((smooth_open([(-L / 2, off + 6), (0, off - 3), (L / 2, off + 6)]), 4.6))
        ves = [(-27, 10), (27, 9), (-22, 24), (24, 26)]
    else:
        for (px, py) in [(-24, 0), (8, -6), (26, 16), (-8, 24), (-30, 30)]:
            a = r.uniform(-0.5, 0.5)
            for i in range(2):
                L = 15 - i * 3
                ca, sa = math.cos(a), math.sin(a)
                pts = [(-L / 2, 3 + i * 6), (0, -1 + i * 6), (L / 2, 3 + i * 6)]
                pts = [(px + u * ca - v * sa, py + u * sa + v * ca) for u, v in pts]
                paths.append((smooth_open(pts), 3.8))
        ves = [(-38, 8), (20, -14), (40, 6), (12, 36), (-20, 42), (34, 32), (-4, 8)]
    o += tube(paths, 0, GOL_FILL, GOL_STROKE)
    for vx, vy in ves:
        o += f'<circle cx="{vx}" cy="{vy}" r="3" fill="{GOL_FILL}" stroke="{GOL_STROKE}" stroke-width="1.1"/>'
    return o + "</g>"


def _phagocyte_body(cx, cy, rx, ry, seed):
    """Rounded phagocyte with a few broad, ruffled lobes (generic: microglia or macrophage)."""
    r = random.Random(seed)
    k = 22
    pts = []
    for i in range(k):
        a = i / k * math.tau
        f = 1 + 0.07 * math.sin(3 * a + seed) + 0.04 * math.sin(7 * a + 2 * seed) + r.uniform(-0.015, 0.015)
        pts.append((cx + math.cos(a) * rx * f, cy + math.sin(a) * ry * f))
    return f'<path d="{smooth_closed(pts)}" fill="{MG_FILL}" stroke="{MG_STROKE}" stroke-width="2.2"/>'


def _organelle_cell(cx, cy, stressed=False):
    o = _phagocyte_body(cx, cy, 128, 106, 4 if not stressed else 6)
    nx, ny = cx + 14, cy + 6
    o += _er(nx, ny, 34, 28, swollen=stressed)
    o += f'<path d="{blob(nx, ny, 34, 28, 12, 10, 0.05)}" fill="{MG_NUC}" stroke="{MG_STROKE}" stroke-width="1.5"/>'
    o += f'<circle cx="{nx + 8}" cy="{ny - 4}" r="7" fill="{MG_STROKE}" fill-opacity="0.35"/>'
    o += _golgi(cx + 62, cy - 46, 40, dispersed=stressed)
    if not stressed:
        for x, y, L, a in [(-62, -62, 30, 28), (78, 44, 30, -22), (-14, 76, 28, 6), (104, -4, 24, 84)]:
            o += _mito(cx + x, cy + y, L, a)
        lys = [(-104, -14, 7), (18, -78, 7), (44, 74, 6.5)]
        pex = [(-56, 70, 5.5), (98, 24, 5), (-20, -82, 5)]
        dots = [(-90, 40), (-30, -64), (60, 52), (-106, 20), (30, -60)]
    else:
        for x, y, L, a in [(-66, -66, 11, 0), (-54, -56, 13, 40), (82, 46, 12, 0), (70, 38, 11, 30), (-18, 78, 12, 10),
                           (-6, 70, 11, 60), (104, -10, 11, 0), (106, 6, 11, 80)]:
            o += _mito(cx + x, cy + y, L, a, w=10)
        lys = [(-106, -18, 9), (-96, 14, 8), (20, -80, 8.5), (40, 76, 8), (62, 68, 7), (-38, -78, 7.5), (88, 64, 6.5), (-104, 42, 7)]
        pex = [(-58, 72, 5.5), (98, 26, 5), (-16, -88, 5), (-76, 58, 5)]
        dots = [(-6, -5), (3, 5), (-4, 10), (8, -4), (-12, 4)]
    for x, y, r in lys:
        o += _lyso(cx + x, cy + y, r, deep=stressed)
    for x, y, r in pex:
        o += _perox(cx + x, cy + y, r)
    base = (nx, ny) if stressed else (cx, cy)
    for x, y in dots:
        o += f'<circle cx="{base[0] + x:.1f}" cy="{base[1] + y:.1f}" r="2.4" fill="{N100}"/>'
    return o


def _bacterium(x, y, ang, L=22, w=9):
    return (f'<rect x="{x - L / 2:.1f}" y="{y - w / 2:.1f}" width="{L}" height="{w}" rx="{w / 2}" fill="{G30}" stroke="{G60}" '
            f'stroke-width="1.2" transform="rotate({ang} {x} {y})"/>')


def cellbio_organelles():
    c = []
    W, H = 720, 336
    PROC = "#6b7280"
    LC, RC, CY = 152, 568, 160
    c.append(_text(LC, 24, "At rest", 15.5, 400, LABEL))
    c.append(_text(RC, 24, "Under stress", 15.5, 400, LABEL))
    c.append(_organelle_cell(LC, CY))
    c.append(_organelle_cell(RC, CY, stressed=True))
    # stress cues between the two cells
    c.append(f'<path d="M372,86 L358,110 L368,110 L356,132 L380,102 L369,102 Z" fill="{STRESS}" stroke="{BOX_STROKE}" stroke-width="1.1" stroke-linejoin="round"/>')
    c.append(_bacterium(334, 112, -25, L=20))
    c.append(_bacterium(398, 124, 20, L=18))
    c.append(_hand_arrow(300, 176, 420, 176, bend=0.05, seed=12))
    c.append(_italic(360, 160, "extracellular stress", 13, PROC))
    c.append(_italic(360, 202, "organelles", 12.5, PROC))
    c.append(_italic(360, 218, "remodel", 12.5, PROC))
    # legend
    ly = 306
    items = [("er", "ER"), ("golgi", "Golgi"), ("mito", "mitochondria"), ("lys", "lysosomes"), ("pex", "peroxisomes"), ("tf", "Tfeb / Tfe3")]
    widths = [int(len(n) * 6.6 + 44) for _, n in items]
    x = (W - sum(widths)) / 2
    for (kind, name), wd in zip(items, widths):
        ix = x + 10
        if kind == "er":
            c.append(tube([(f"M{ix - 8},{ly - 2} q4,-6 8,0 t8,0", 4.2)], 0, ER_FILL, ER_STROKE))
        elif kind == "golgi":
            c.append(tube([(f"M{ix - 9},{ly - 1} q9,-8 18,0", 3.6), (f"M{ix - 6},{ly + 5} q6,-6 12,0", 3.2)], 0, GOL_FILL, GOL_STROKE))
        elif kind == "mito":
            c.append(_mito(ix + 2, ly - 2, 22, 0, w=10))
            ix += 6
        elif kind == "lys":
            c.append(_lyso(ix, ly - 2, 6.5))
        elif kind == "pex":
            c.append(_perox(ix, ly - 2, 5.5))
        else:
            c.append(f'<circle cx="{ix}" cy="{ly - 2}" r="2.6" fill="{N100}"/>')
        c.append(_text(ix + (18 if kind == "golgi" else 14), ly + 3, name, 12.5, 400, LABEL2, anchor="start"))
        x += wd
    return svg("".join(c), "Cell biology of microglia and macrophages",
               "A phagocyte at rest beside the same cell under extracellular stress, such as injury or infection. Each cell holds a nucleus, endoplasmic reticulum, "
               "Golgi apparatus, mitochondria, lysosomes, and peroxisomes. Under stress, the transcription factors Tfeb and Tfe3 move into the nucleus, lysosomes "
               "become more numerous and more acidic, mitochondria fragment, the ER swells, the Golgi breaks into scattered mini-stacks, and peroxisomes increase in number.",
               vb=f"0 0 {W} {H}")


ALL["cell-biology"] = cellbio_organelles
