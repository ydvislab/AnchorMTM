"""Render every paper figure in output/figures to a PNG at 600 dpi of its printed width (the files used by the LaTeX source).

Also copies the hand-made Figures S1-S3 and the hand-finished Figure S5 from figures_src/. Needs pdftocairo (poppler).
Run:  python scripts/figures/export_png.py      Output: output/figures/png/<name>.png
"""
import shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import anchormtm_paths as AP  # noqa: E402

DPI, TEXT_IN, COLUMN_IN = 600, 7.0, 3.4
HANDMADE = {   # figures drawn or finished by hand; their PDF exports are copied unchanged
    'anchor_related_work_mapping.pdf': 'anchor_related_work_mapping', 'anchor_node_mapping.pdf': 'anchor_node_mapping',
    'anchor_leaf_correspondence.pdf': 'anchor_leaf_correspondence', 'figS5_cylinder_variant.pdf': 'anchor_cylinder_centered_blue'}
WIDTH = {   # printed width in inches: text width, column width or a fraction of the text width
    'anchor_storms_overview': TEXT_IN, 'anchor_framework': TEXT_IN, 'anchor_relaxation_open': 4.0, 'forced_plane': TEXT_IN,
    'volume_gallery': TEXT_IN, 'budget_response_v30': TEXT_IN, 'anchor_storms_budget_maps': TEXT_IN,
    'anchor_related_work_mapping': .86 * TEXT_IN, 'anchor_node_mapping': COLUMN_IN, 'anchor_leaf_correspondence': .72 * TEXT_IN,
    'supp_budget_sweep': TEXT_IN, 'anchor_cylinder_centered_blue': .92 * TEXT_IN, 'supp_cylinder_compare': TEXT_IN, 'supp_pm25_compare': TEXT_IN}


def main():
    for src, name in HANDMADE.items():
        shutil.copy(AP.ROOT / 'figures_src' / src, AP.FIGURES_OUT / f'{name}.pdf')
    out = AP.FIGURES_OUT / 'png'; out.mkdir(exist_ok=True); missing = []
    for name, w in WIDTH.items():
        pdf = AP.FIGURES_OUT / f'{name}.pdf'
        if not pdf.exists(): missing.append(name); continue
        subprocess.run(['pdftocairo', '-png', '-singlefile', '-scale-to-x', str(round(w * DPI)), '-scale-to-y', '-1', str(pdf), str(out / name)], check=True)
    print(f'{len(WIDTH) - len(missing)} PNG files in {out}' + (f'; missing PDFs: {missing}' if missing else ''))


if __name__ == '__main__':
    main()
