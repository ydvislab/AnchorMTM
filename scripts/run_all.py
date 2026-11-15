"""Regenerate every figure and table of the paper from the bundled results (no raw data needed).

Run from the repository root:  python scripts/run_all.py
Writes output/figures/*.pdf, output/figures/png/*.png and output/tables/*. Figure 2 needs a PDF export of its PowerPoint slide
(see scripts/figures/fig02_workflow.py); it is skipped here when LibreOffice is not installed.
"""
import shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = [
    ('Figure 3', ['scripts/figures/fig03_selective_flattening.py']),
    ('Figure 4', ['scripts/figures/fig04_forced_error.py']),
    ('Figure 5', ['scripts/figures/fig05_volume_positions.py']),
    ('Figure 6', ['scripts/figures/fig06_budget_response.py']),
    ('Figure 7 map panels (check)', ['scripts/figures/fig07_storms_budget_maps.py']),
    ('Figures 1 and 7 (East arrow)', ['scripts/figures/east_arrows.py']),
    ('Figure S4', ['scripts/figures/figS4_budget_sweep.py']),
    ('Figure S5 panels (check)', ['scripts/figures/figS5_cylinder_variant.py']),
    ('Figure S6', ['scripts/figures/figS6_cylinder_compare.py']),
    ('Figure S7', ['scripts/figures/figS7_pm25_compare.py']),
    ('Table 1', ['scripts/tables/table1.py']),
    ('Table S1', ['scripts/tables/tableS1.py']),
    ('Tables S2-S4', ['scripts/tables/tableS2_S4.py']),
    ('Tables S5-S8', ['scripts/tables/tableS5_S8.py']),
]


def main():
    steps = list(STEPS)
    if shutil.which('soffice'): steps.insert(1, ('Figure 2', ['scripts/figures/fig02_workflow.py']))
    steps.append(('PNG export', ['scripts/figures/export_png.py']))
    failed = []
    for name, cmd in steps:
        r = subprocess.run([sys.executable, *cmd], cwd=ROOT, capture_output=True, text=True)
        print(f"{'ok  ' if r.returncode == 0 else 'FAIL'} {name}")
        if r.returncode: failed.append(name); print(r.stderr[-1500:])
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
