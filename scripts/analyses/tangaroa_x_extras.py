"""Tangaroa along the streamwise x axis: the moves within the common model and TW / TD / ME (Tangaroa entries of Tables S2, S3).

family_sweep.py and metrics_n1c measure Tangaroa along its motion direction (Table S4). The paper uses the streamwise x axis
for both volumes, so this script reruns the same functions with the x reference of volumes.load (canvas = projected domain,
length parameters scaled with it), and the best affine alignment of the baselines. The experiment code is not changed;
the dataset loader is replaced in memory only.
Run from the repository root:  python scripts/analyses/tangaroa_x_extras.py
Output: results/figdata/volumes/tangaroa_x_extras.json
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # repository root
import anchormtm_paths as AP  # noqa: E402
import importlib.util, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = AP.ROOT; OUT = AP.FIGDATA / 'volumes'


def module(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


vol = module('volumes', HERE / 'volumes.py')
fs = module('family_sweep', HERE / 'family_sweep.py')

from scipy.optimize import linprog   # noqa: E402
from scipy import sparse             # noqa: E402


def fit(U, Q, L):   # identical to baseline_affine_alignment.fit
    T = len(Q); R, C, V, b = [], [], [], []; k = 0
    for t, (u, q) in enumerate(zip(U, Q)):
        for ui, qi in zip(u, q):
            for sg in (1, -1):
                R += [k] * 3; C += [0, 1, 2 + t]; V += [sg * ui, sg, -L]; b.append(sg * qi); k += 1
    r = linprog(np.r_[0, 0, np.ones(T) / T], A_ub=sparse.csr_matrix((V, (R, C)), shape=(k, 2 + T)), b_ub=b,
                bounds=[(None, None)] * 2 + [(0, None)] * T, method='highs')
    assert r.status == 0; return float(r.fun), [float(v) for v in r.x[:2]]


def main():
    name = 'Tangaroa'; dx, px, feats = vol.load(name, 'x'); L = px.canvas; Q = [np.asarray(q, float) for q in dx['references']]
    res = dict(dataset=name, axis='x', canvas=L, origin=px.canvas_origin)
    # 1. best affine alignment of the stored baseline anchors (favours the baselines)
    nat = json.loads((AP.RESULTS / 'stmtm_completion20261026/tangaroa/landmarks.json').read_text())['positions']
    tab = json.loads((OUT / 'tangaroa_x.json').read_text())
    res['affine'] = {}
    for m in ('TMTM', 'ST-MTM'):
        U = [np.asarray(a, float) for a in nat[m]]
        raw = min(float(np.mean([np.max(np.abs(px.canvas_origin + L * ((1 - a) if s else a) - q)) / L for a, q in zip(U, Q)])) for s in (0, 1))
        v, x = fit(U, Q, L); res['affine'][m] = dict(table1_NPE=raw, stored_table_NPE=tab['baselines'][m]['NPE'], best_affine_NPE=v, slope=x[0], intercept=x[1])
        print('affine', m, res['affine'][m], flush=True)
    # 2. TW/TD/ME (metrics_n1c.score) of the Balanced and 10% maps of tangaroa_x.json
    folder, _, occupied = fs.nc.VOLUME[name]
    diag = json.loads((ROOT / 'code' / folder / 'reference.json').read_text())['domain_diagonal']
    res['temporal'] = {}
    for tag in ('Exact', 'Balanced', '10%'):
        s = fs.nc.score(dx, [np.asarray(x, float) for x in tab['maps'][tag]['x']], px, feats, float(diag), occupied)
        res['temporal'][tag] = {k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in s.items() if k in ('SNS', 'TW1', 'TD', 'ME_errors', 'ME_clear')}
        print('temporal', tag, res['temporal'][tag], flush=True)
    (OUT / 'tangaroa_x_extras.json').write_text(json.dumps(res, indent=1) + '\n')
    # 3. the family sweep on the x reference (reference, ST-MTM, default, geometry, uncapped, ST order)
    fs.n1.DATASETS[name] = lambda: dx
    res['family'] = fs.run(name)['instances']
    (OUT / 'tangaroa_x_extras.json').write_text(json.dumps(res, indent=1, default=float) + '\n')
    print('saved', flush=True)


if __name__ == '__main__':
    main()
