"""Figures 1 and 7: add the upward East arrow to the storm figures (TikZ overlay on the vector figures).

Both figures were laid out by hand in PowerPoint (figures_src/editable/Fig1_storms_overview.pptx, Fig7_storms_budget_maps.pptx);
their PDF exports are figures_src/fig01_storms_overview_base.pdf and figures_src/fig07_storms_budget_maps_base.pdf.
Needs tectonic or pdflatex with the standalone and tikz packages.
Output: output/figures/anchor_storms_overview.pdf, output/figures/anchor_storms_budget_maps.pdf
Run:  python scripts/figures/east_arrows.py
"""
import shutil, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import anchormtm_paths as AP  # noqa: E402

SRC = AP.ROOT / 'figures_src'
JOBS = [('fig01_east_arrow.tex', 'fig1_east', SRC / 'fig01_storms_overview_base.pdf', 'anchor_storms_overview_original.pdf', 'anchor_storms_overview.pdf'),
        ('fig07_east_arrow.tex', 'fig7_east', SRC / 'fig07_storms_budget_maps_base.pdf', 'anchor_storms_budget_maps_original.pdf', 'anchor_storms_budget_maps.pdf')]


def compile_tex(tex, cwd):
    if shutil.which('tectonic'): cmd = ['tectonic', '-X', 'compile', tex]
    elif shutil.which('pdflatex'): cmd = ['pdflatex', '-interaction=nonstopmode', tex]
    else: sys.exit('needs tectonic or pdflatex')
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)


def main():
    for tex, stem, base, base_name, out in JOBS:
        if not base.exists(): sys.exit(f'missing {base}')
        with tempfile.TemporaryDirectory() as d:
            shutil.copy(SRC / tex, Path(d) / (stem + '.tex')); shutil.copy(base, Path(d) / base_name)
            compile_tex(stem + '.tex', d)
            shutil.copy(Path(d) / (stem + '.pdf'), AP.FIGURES_OUT / out)
        print('wrote', AP.FIGURES_OUT / out)


if __name__ == '__main__':
    main()
