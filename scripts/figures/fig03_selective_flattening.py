"""Figure 3: selective flattening with optimal barriers (Proposition 4), on a four-leaf example.

Levels: root h_R = 3.6, relaxed A-B node h_u = 2.4, C-D node h_w = 1.0, extrema 0.15. Order A, C, D, B gives
C = (h_u, h_w, h_u) and delta* = (h_R - h_u)/2 = 0.6, so the barriers are b = C + delta* = (3.0, 1.6, 3.0):
the merges across the relaxed node fall by delta* to the midpoint 3.0, the C-D merge rises by the same delta*.
Run:  python scripts/figures/fig03_selective_flattening.py [OUT_STEM]   (default output/figures/anchor_relaxation_open.{pdf,png})
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # repository root
import anchormtm_paths as AP  # noqa: E402
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
from matplotlib.path import Path
from matplotlib.patches import PathPatch

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman', 'Times', 'Nimbus Roman', 'DejaVu Serif'],
                     'mathtext.fontset': 'stix', 'pdf.fonttype': 42})
hR, hu, hw, f0 = 3.6, 2.4, 1.0, 0.15
d = (hR - hu) / 2                                  # delta*
new_root, new_cd = hu + d, hw + d                  # 3.0, 1.6
COL = dict(A='#0B5ED7', B='#FF7F0E', C='#0E9C8E', D='#8E5BB5')
L, PS, TS = 4.3, 0.8, 0.85                         # tree leaf row, profile scale, tree level scale
T = lambda h: L + TS * h
FS = 17

fig, ax = plt.subplots(figsize=(9.0, 5.6)); ax.set_xlim(-0.55, 13.55); ax.set_ylim(-1.05, T(hR) + 0.42); ax.set_aspect('equal'); ax.axis('off')

def diamond(x, y, s=0.17, z=6):
    ax.add_patch(plt.Polygon([(x, y + s), (x + s, y), (x, y - s), (x - s, y)], closed=True, fc='white', ec='black', lw=1.3, zorder=z))

def leaf(x, y, k, r=0.17):
    ax.add_patch(Circle((x, y), r, fc=COL[k], ec='black', lw=1.1, zorder=6))
    ax.text(x, y - 0.33, k, ha='center', va='top', fontsize=FS + 1, style='italic', zorder=6)

def line(p, q, **kw):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=kw.pop('color', 'black'), lw=kw.pop('lw', 1.6), zorder=kw.pop('zorder', 3), **kw)

def dotted(y, x0, x1):
    ax.plot([x0, x1], [y, y], color='0.6', lw=0.9, ls=(0, (1, 2.2)), zorder=1)

# ---- tree before relaxation
xA, xB, xC, xD = 0.6, 2.0, 3.4, 4.6
root, u, w = (2.45, T(hR)), (1.3, T(hu)), (4.0, T(hw))
line(root, u); line(root, w); line(w, (xC, L)); line(w, (xD, L))
line(u, (xA, L), color='0.55', ls=(0, (4, 3)), lw=1.4); line(u, (xB, L), color='0.55', ls=(0, (4, 3)), lw=1.4)
for p in (root, u, w): diamond(*p)
for x, k in zip((xA, xB, xC, xD), 'ABCD'): leaf(x, L, k)
ax.add_patch(Circle(u, 0.38, fc='none', ec='#B0552E', lw=1.4, zorder=5))
ax.plot([u[0] - 0.33, u[0] - 0.62], [u[1] + 0.2, u[1] + 0.45], color='#B0552E', lw=1.1)
ax.text(u[0] - 0.66, u[1] + 0.5, 'Relaxed', ha='right', va='bottom', fontsize=FS)

# ---- tree after relaxation: A, (C, D), B under the new root at the midpoint
yA, yC, yD, yB = 8.4, 9.8, 11.0, 12.4
r2, cd2 = (10.4, T(new_root)), (10.4, T(new_cd))
for xl, sgn in ((yA, -1), (yB, 1)):
    verts = [r2, (r2[0] + sgn * 1.25, r2[1] - 0.05), (xl, T(1.7)), (xl, L)]
    ax.add_patch(PathPatch(Path(verts, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc='none', ec='black', lw=1.6, zorder=3))
line(r2, cd2); line(cd2, (yC, L)); line(cd2, (yD, L))
for p in (r2, cd2): diamond(*p)
for x, k in zip((yA, yC, yD, yB), 'ACDB'): leaf(x, L, k)

# ---- barrier changes between the panels: both by delta*
xa = 7.0
for y0, y1, col, band, txt in ((T(hR), T(new_root), '#9B4FC0', '#F4EAFA', 'Lower merge\nbarrier by $\\delta^*$'),
                               (T(hw), T(new_cd), '#1E7FE0', '#E6F2FC', 'Raise merge\nbarrier by $\\delta^*$')):
    ax.add_patch(Rectangle((xa - 0.24, min(y0, y1)), 0.48, abs(y1 - y0), fc=band, ec='none', zorder=0))
    ax.add_patch(FancyArrowPatch((xa, y0), (xa, y1), arrowstyle='-|>', mutation_scale=13, color=col, lw=1.6, zorder=4))
    ax.text(xa - 0.36, (y0 + y1) / 2, txt, ha='right', va='center', fontsize=FS - 1, linespacing=1.05, zorder=4,
            bbox=dict(fc='white', ec='none', pad=0.6))
dotted(T(hR), root[0] + 0.2, xa + 0.24); dotted(T(new_root), xa - 0.24, r2[0] - 0.2)
dotted(T(hw), w[0] + 0.2, xa + 0.24);   dotted(T(new_cd), xa - 0.24, cd2[0] - 0.2)

# ---- profiles: minima at the leaves, half-cosine bumps, peaks at the barriers
def profile(x0, xs, peaks, edge, label):
    pts = [(x0, edge)]
    for i, x in enumerate(xs):
        pts.append((x, f0))
        if i < len(peaks): pts.append(((x + xs[i + 1]) / 2, peaks[i]))
    x1 = xs[-1] + (xs[0] - x0); pts.append((x1, edge))
    X, Y = [], []
    for (a, ya), (b, yb) in zip(pts[:-1], pts[1:]):
        t = np.linspace(0, 1, 60); X += list(a + (b - a) * t); Y += list(ya + (yb - ya) * (1 - np.cos(np.pi * t)) / 2)
    X, Y = np.array(X), PS * np.array(Y)
    ax.fill_between(X, 0, Y, color='#EAF4FC', zorder=1); ax.plot(X, Y, color='black', lw=1.6, zorder=3)
    ax.annotate('', xy=(x0 - 0.05, PS * 4.15), xytext=(x0 - 0.05, -0.02), arrowprops=dict(arrowstyle='-|>', lw=1.2, color='black', mutation_scale=11))
    ax.annotate('', xy=(x1 + 0.45, 0), xytext=(x0 - 0.07, 0), arrowprops=dict(arrowstyle='-|>', lw=1.2, color='black', mutation_scale=11))
    drawn = set()
    for i, pk in enumerate(peaks):
        xm = (xs[i] + xs[i + 1]) / 2; diamond(xm, PS * pk, s=0.13)
        if pk not in drawn: ax.plot([xm, x1], [PS * pk, PS * pk], color='0.6', lw=0.9, ls=(0, (3, 2.5)), zorder=2); drawn.add(pk)
    ax.text((x0 + x1) / 2, -0.55, label, ha='center', va='top', fontsize=FS + 1)
    return x1

xe = profile(-0.05, [xA, xB, xC, xD], [hu, hR, hw], 2.3, 'Before relaxation')
profile(7.75, [yA, yC, yD, yB], [new_root, new_cd, new_root], 2.3, 'After relaxation')
for xs, ks in (((xA, xB, xC, xD), 'ABCD'), ((yA, yC, yD, yB), 'ACDB')):
    for x, k in zip(xs, ks):
        ax.plot([x, x], [L - 0.74, PS * f0 + 0.12], color='0.6', lw=0.9, ls=(0, (3, 2.5)), zorder=1)
        ax.add_patch(Circle((x, PS * f0), 0.11, fc=COL[k], ec='black', lw=0.9, zorder=6))
ax.add_patch(FancyArrowPatch((xe + 0.75, 1.15), (7.45, 1.15), connectionstyle='arc3,rad=-0.3', arrowstyle='-|>', mutation_scale=16, color='0.4', lw=2.0))

out = sys.argv[1] if len(sys.argv) > 1 else str(AP.FIGURES_OUT / 'anchor_relaxation_open')
fig.savefig(out + '.pdf', bbox_inches='tight', pad_inches=0.02)
fig.savefig(out + '.png', dpi=400, bbox_inches='tight', pad_inches=0.02)
print('saved', out)
