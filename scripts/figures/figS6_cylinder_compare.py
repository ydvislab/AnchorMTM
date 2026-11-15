"""Figure S6: Cylinder (102 frames) drawn by the central-tree variant of AnchorMTM (guidance weight 16), TMTM and ST-MTM
on the same simplified trees.

The three maps are rasters rendered from the Cylinder runs, saved in results/figdata/cylinder_compare/; their time extent
0-162 and layout range 0-1 are fixed in this script. One shared time axis and axis label, method names inside the panels.
Run:  python scripts/figures/figS6_cylinder_compare.py      Output: output/figures/supp_cylinder_compare.{pdf,png}
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # repository root
import anchormtm_paths as AP  # noqa: E402
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import figure_common as v

HERE = Path(__file__).resolve().parent
RASTER = AP.FIGDATA / 'cylinder_compare'
OUT = AP.FIGURES_OUT
ROWS = [('anchormtm_central_g16', 'AnchorMTM, central-tree variant (guidance weight 16)'), ('tmtm', 'TMTM'), ('stmtm', 'ST-MTM')]
TIMES = [32.1, 56.1, 80.2, 120.3, 162.0]   # snapshot times of the paper's Cylinder figure


def main():
    v.use_times()
    fig, axes = plt.subplots(3, 1, figsize=(7.05, 2.9), sharex=True)
    fig.subplots_adjust(left=.065, right=.975, top=.985, bottom=.135, hspace=.22)
    for ax, (f, name) in zip(axes, ROWS):
        ax.imshow(plt.imread(RASTER / f'{f}.png'), extent=[0, 162, 0, 1], aspect='auto', interpolation='bilinear', rasterized=True)
        for t in TIMES[:-1]: ax.axvline(t, color='#888', lw=.4, ls=(0, (2, 2)))
        ax.text(.006, .9, name, transform=ax.transAxes, ha='left', va='top', fontsize=8.5,
                bbox=dict(facecolor='white', edgecolor='none', alpha=.85, pad=1.2))
        ax.set_yticks([0, .5, 1]); ax.set_yticklabels(['0', '0.5', '1']); ax.tick_params(labelsize=8, length=2, pad=1)
        for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    axes[-1].set_xticks([0] + TIMES); axes[-1].set_xlim(0, 162)
    axes[-1].set_xlabel('simulation time $t$', fontsize=8.5, labelpad=1)
    fig.text(.014, .56, '1D layout position', rotation=90, ha='center', va='center', fontsize=8.5)
    for ext in ('pdf', 'png'): fig.savefig(OUT / f'supp_cylinder_compare.{ext}', dpi=300)


if __name__ == '__main__':
    main()
