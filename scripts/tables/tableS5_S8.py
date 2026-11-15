"""Tables S5-S8 from results/supplement_analyses (scripts/analyses/supplement_analyses.py).

Run:  python scripts/tables/tableS5_S8.py      Output: output/tables/table_cylinder_exact.tex, table_ablation.tex, table_depth.tex, table_motion.tex
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # repository root
import anchormtm_paths as AP  # noqa: E402
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent; D = AP.RESULTS / 'supplement_analyses'; OUT = AP.TABLES_OUT
rd = lambda n: json.loads((D / n).read_text())
# Table 1 NPE of AnchorMTM (Exact, Balanced), % of the axis
NPE = {'Ring': (4.71, 3.95), 'Wildfires': (1.31, 1.16), 'Storms': (3.99, 1.40), 'PM25': (13.90, 4.68), 'Cylinder': (9.18, 1.33), 'Tangaroa': (8.61, 4.65)}
LAB = {'PM25': r'PM$_{2.5}$'}
def table(label, caption, cols, rows, spec):
    return '\n'.join([r'\begin{table}[!htb]', r'\centering', rf'\caption{{{caption}}}', rf'\label{{{label}}}', r'\footnotesize', r'\setlength{\tabcolsep}{3pt}',
                      rf'\begin{{tabular}}{{@{{}}{spec}@{{}}}}', r'\toprule', ' & '.join(cols) + r' \\', r'\midrule', *[' & '.join(map(str, r)) + r' \\' for r in rows],
                      r'\bottomrule', r'\end{tabular}', r'\end{table}']) + '\n'
s = rd('strict.json')
(OUT / 'table_cylinder_exact.tex').write_text(table('tab:cylinder-exact', r'Cylinder with and without the tolerance $\varepsilon_0$. Merge error is measured against the original tree, in units of the scalar range; $\nu^*$ and NPE in \% of the axis.',
    ['Merge levels', r'$\nu^*$', 'NPE', 'Merge error', 'SNS', 'TW'],
    [[r'kept distinct ($\varepsilon_0=0$)', '12.2', f"{100 * s['NPE']:.1f}", '0', f"{s['SNS']:.4f}", f"{s['TW']:.4f}"],
     [r'within $2\varepsilon_0$ equal (paper)', '7.7', '9.2', r'$1.0\times10^{-7}$', '0.1097', '0.8136']], 'lccccc'))
rows = []
for n in ('Ring', 'Wildfires', 'Storms', 'PM25', 'Cylinder', 'Tangaroa'):
    a = rd(f'ablation_{n}.json'); (e0, b), (z, bal) = list(a.items())
    for e, r, npe in ((e0, b, NPE[n][0]), (z, bal, NPE[n][1])):
        rows.append([LAB.get(n, n) if e == e0 else '', f'{100 * float(e):g}\\%', f"{r['width_bound']:.2f}", f"{r['threshold_only']:.2f}", f"{r['point_order']:.2f}", f"{r['full_search']:.2f}", f'{npe:.2f}'])
(OUT / 'table_ablation.tex').write_text(table('tab:ablation', r'What each step of the method adds, in mean \% of the axis, at zero budget and at the Balanced budget of Table~1. Bound: width-aware (Propositions~2 and~3); Threshold: best threshold flattening with midpoint ordering (at 0\%, midpoint ordering of the exact tree); Selective: with selective flattening; Search: the selected order after refinement; $\tau$ columns are the fixed-order cost of Eq.~4. NPE is the final map of Table~1; Cylinder at 0\% uses the tolerance $\varepsilon_0$ (strict reading in Table~\ref{tab:cylinder-exact}).',
    ['Sequence', r'$\varepsilon$', 'Bound', 'Threshold', 'Selective', 'Search', 'NPE'], rows, 'llccccc'))
B = {'Exact': '0', 'epsilon_0': '0', 'epsilon_0.01': '1', 'epsilon_0.02': '2', 'epsilon_0.05': '5', 'epsilon_0.1': '10', 'epsilon_0.2': '20'}
rows = []
for n in ('Ring', 'Wildfires', 'Storms', 'PM25', 'Cylinder', 'Tangaroa'):
    d = rd(f'depth_{n}.json'); leaves = next(iter(d.values()))['leaves']; byb = {B[k]: v for k, v in d.items()}
    cells = [f"{byb[b]['vanishing']}" if b in byb else '--' for b in ('0', '1', '2', '5', '10', '20')]
    rows.append([LAB.get(n, n) + (' (motion axis)' if n == 'Tangaroa' else ''), leaves, *cells])
(OUT / 'table_depth.tex').write_text(table('tab:depth', r'Leaf basins whose depth in the continuous profile vanishes (adjacent barrier equal to the leaf value), out of all leaves other than the deepest one of each frame, for the stored layouts at each budget; counts. The rendering clearance keeps their barriers above the leaf value, but not visibly.',
    ['Sequence', 'Leaves', '0', '1', '2', '5', '10', '20'], rows, 'lrrrrrrr'))
m = rd('motion.json'); rows = []
for n in ('Tangaroa', 'Cylinder'):
    for k in ('TMTM', 'ST-MTM', 'Exact', '10%'):
        r = m[n][k]; rows.append([n if k == 'TMTM' else '', k.replace('%', r'\%'), f"{100 * r['coverage']:.0f}\\%" if k == 'TMTM' else '', f"{r['reversal_rate']:.1f}", f"{r['mean_step_error']:.2f}",
                                  f"{r['error_order_switch']:.2f}" if r['error_order_switch'] is not None else '--', f"{r['error_no_switch']:.2f}" if r['error_no_switch'] is not None else '--'])
(OUT / 'table_motion.tex').write_text(table('tab:motion', r'Displayed motion of matched features between consecutive frames, along the streamwise axis. Coverage: share of features with a match. Reversal: share of clear steps ($|\Delta q|\ge0.5\%$ of the axis) whose displayed step has the opposite sign or none (\%). Step error: mean $|\Delta x-\Delta q|$ (\% of the axis), overall and over the steps in which the axis order of the matched features changes or not.',
    ['Volume', 'Map', 'Coverage', 'Reversal', 'Step error', 'Order changes', 'Unchanged'], rows, 'llccccc'))
print('tables ok')
