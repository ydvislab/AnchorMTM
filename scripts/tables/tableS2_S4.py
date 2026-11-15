"""Tables S2-S4: tables_s2_s3_base.py with Tangaroa along the streamwise x axis, plus Tangaroa along its motion direction.

Tables S2 (moving within the common model) and S3 (TW / TD / ME): the Tangaroa columns/row come from
figdata/volumes/tangaroa_x_extras.json (tangaroa_x_extras.py); the Cylinder entries come from tables_s2_s3_base.py.
Table S4 (Tangaroa along its motion direction): SNS, TW and NPE of the motion-axis runs (transcribed below), the
reference row of figdata/family_sweep20261109 and TD / ME of metrics_n1c.
Run:  python scripts/tables/tableS2_S4.py      Output: output/tables/table_family.tex, table_temporal.tex, table_tangaroa_motion.tex
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # repository root
import anchormtm_paths as AP  # noqa: E402
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent; FIG = AP.FIGDATA; OUT = AP.TABLES_OUT
N1C = AP.RESULTS / 'metrics_n1c'
read = lambda p: json.loads(Path(p).read_text())
X = read(FIG / 'volumes/tangaroa_x_extras.json')
src = (HERE / 'tables_s2_s3_base.py').read_text(encoding='utf-8')
# 1. Tangaroa instances of the family sweep on the x reference
old = "C, T = read(FIG / 'cylinder.json')['instances'], read(FIG / 'tangaroa.json')['instances']"
assert src.count(old) == 1
src = src.replace(old, "C, T = read(FIG / 'cylinder.json')['instances'], X_FAMILY")
# 2. Exact and 10% of the temporal table on the x reference (baselines do not depend on the axis)
old = "    d = read(N1C / f'{f}.json'); row = [label]"
assert src.count(old) == 1
src = src.replace(old, old + "\n    if name == 'Tangaroa': d = dict(d, settings={'eps=0': X_TEMP['Exact'], 'eps=0.1': X_TEMP['10%']})")
g = dict(__file__=str(HERE / 'tables_s2_s3_base.py'), __name__='tables_s2_s3_base', X_FAMILY=X['family'], X_TEMP=X['temporal'])
exec(compile(src, 'tables_s2_s3_base.py (streamwise x for Tangaroa)', 'exec'), g)

# 3. Tangaroa along its motion direction
M = read(FIG / 'family_sweep20261109/tangaroa.json')['instances']; n = read(N1C / 'tangaroa.json')
curves = {'Hilbert': (0.3429, 0.9222, 0.5897), 'Morton': (0.3627, 0.8893, 0.5924)}      # volumes/tangaroa_motion.json
t1 = {'TMTM': (0.5255, 0.6701, 0.3063), 'ST-MTM': (0.1655, 0.8137, 0.3418),            # SNS, TW, NPE of the motion-axis runs
      'Exact': (0.3621, 0.7260, 0.1118), '10%': (0.3408, 0.7540, 0.0615)}
me = lambda s: f"{100 * s['ME_errors'] / s['ME_clear']:.0f}"
rows = [('Reference, $x=q$', f"{M['reference']['SNS']:.4f} & {M['reference']['TW1']:.4f} & 0 & {M['reference']['TD']:.1f} & {me(M['reference'])}")]
rows += [(k, f'{a:.4f} & {b:.4f} & -- & -- & --') for k, (a, b, c) in curves.items()]   # no NPE for the curves: an index has no spatial direction
for k, s in (('TMTM', n['baselines']['TMTM']), ('ST-MTM', n['baselines']['ST-MTM']), ('Exact', n['settings']['eps=0']), ('10%', n['settings']['eps=0.1'])):
    a, b, c = t1[k]; label = {'Exact': 'AnchorMTM, Exact', '10%': r'AnchorMTM, Balanced (10\%)'}.get(k, k)
    rows.append((label, f"{a:.4f} & {b:.4f} & {c:.4f} & {s['TD']:.1f} & {me(s)}"))
L = [r'\begin{table}[!h]', r'\centering', r'\caption{Tangaroa with the reference along its motion direction (Eq.~2) instead of the streamwise axis. TD and ME as in Table~\ref{tab:temporal}.}',
     r'\label{tab:tangaroa-motion}', r'\footnotesize', r'\setlength{\tabcolsep}{3pt}', r'\begin{tabular}{@{}lccccc@{}}', r'\toprule',
     r'Method & SNS$\downarrow$ & TW$\uparrow$ & NPE$\downarrow$ & TD & ME (\%)$\downarrow$ \\', r'\midrule']
L += [f'{a} & {b} \\\\' for a, b in rows]
L += [r'\bottomrule', r'\end{tabular}', r'\vspace{2pt}',
      r'\begin{minipage}{0.94\columnwidth}\footnotesize On this axis the Balanced rule selects 10\% (attained merge error 9.97\%). SNS, TW, TD and ME of TMTM, ST-MTM and the curves do not depend on the axis.\end{minipage}',
      r'\end{table}']
(OUT / 'table_tangaroa_motion.tex').write_text('\n'.join(L) + '\n')
print('ok')
