"""Figure 2 (workflow): export the PowerPoint slide figures_src/fig02_workflow.pptx to PDF and crop it to its content.

The slide is drawn by hand. Export it either with LibreOffice (found automatically) or with PowerPoint (File > Save As > PDF) and
pass the exported PDF:  python scripts/figures/fig02_workflow.py [SLIDE.pdf]
Needs tectonic or pdflatex. Output: output/figures/anchor_framework.pdf
"""
import shutil, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import anchormtm_paths as AP  # noqa: E402
from east_arrows import compile_tex  # noqa: E402

SRC = AP.ROOT / 'figures_src'


def main():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        if len(sys.argv) > 1: shutil.copy(sys.argv[1], d / 'fig2_workflow_slide.pdf')
        elif shutil.which('soffice'):
            subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', str(d), str(SRC / 'fig02_workflow.pptx')], check=True, capture_output=True)
            (d / 'fig02_workflow.pdf').rename(d / 'fig2_workflow_slide.pdf')
        else: sys.exit('export figures_src/fig02_workflow.pptx to PDF and pass its path')
        shutil.copy(SRC / 'fig02_crop.tex', d / 'fig2_crop.tex')
        compile_tex('fig2_crop.tex', d)
        shutil.copy(d / 'fig2_crop.pdf', AP.FIGURES_OUT / 'anchor_framework.pdf')
    print('wrote', AP.FIGURES_OUT / 'anchor_framework.pdf')


if __name__ == '__main__':
    main()
