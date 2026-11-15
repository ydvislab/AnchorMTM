"""Analyses behind Tables S5-S8 and the related statements of the supplement. Reads the stored inputs; writes JSON only.

  ties        merge levels closer than 2*eps0 per sequence, and the merge error of Exact w.r.t. the original tree
  strict      Cylinder Exact with eps0 = 0 (ties broken): NPE, SNS, TW and merge error w.r.t. the original tree
  depth NAME  displayed depth of every leaf basin in the stored layouts of package 01 (Proposition 4 can flatten a basin)
  ablation NAME   width bound, tau of the midpoint (point) order, tau of threshold flattening only, tau of the full search
  motion      projected displacement error and direction reversals of matched features on the volumes
Run from the repository root:  python scripts/analyses/supplement_analyses.py TASK [NAME]
Output: results/supplement_analyses/<task>[_<name>].json
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # repository root
import anchormtm_paths as AP  # noqa: E402
import glob, importlib.util, json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path[:0] = [str(HERE), str(AP.ROOT / 'src')]
import volumes as v5                                                    # noqa: E402  (loaders of the volume runs)
from rgmtm.error_budget import Parameters                                  # noqa: E402
from rgmtm.order_certificate import budget_order, hierarchy, _parents       # noqa: E402
from rgmtm.interval_order import width_order, _search                       # noqa: E402
from rgmtm.unified import Controls, solve_unified_frame                      # noqa: E402
from rgmtm.framework import interval_costs                                   # noqa: E402
OUT = AP.RESULTS / 'supplement_analyses'; FIG = AP.FIGDATA
PKG = AP.INPUTS / 'package01'
TIE = v5.n1.TIE
BAL = {'Ring': .01, 'Wildfires': .05, 'Storms': .10, 'PM25': .05, 'Cylinder': .01, 'Tangaroa': .09}   # Balanced budgets of Table 1


def planar(name):
    m = json.loads((PKG / name / 'metadata.json').read_text()); F = json.loads((PKG / name / 'per_frame_inputs.json').read_text())
    p = Parameters(**{k: v for k, v in m['parameters'].items() if k in v5.n1.PARAM_FIELDS})
    return [np.array(f['merge_matrix'], float) for f in F], [np.array(f['reference_q'], float) for f in F], [np.array(f['width_w'], float) for f in F], p, m['scalar_range']


def volume(name):
    d, p, _ = v5.load(name, 'x')
    return [np.asarray(V, float) for V in d['merge']], [np.asarray(q, float) for q in d['references']], \
           [p.width_scale * np.asarray(m, float) for m in d['measures']], p, d['scalar_range']


def threshold_only(V, q, w, p, limit):
    nodes, root = hierarchy(V)
    if root is None or len(V) < 2: return float(interval_costs(np.array([list(range(len(V)))]), w, q, p)[0])
    parent = _parents(nodes); inner = [k for k, d in nodes.items() if d['children'] and k in parent]
    gap = {k: nodes[parent[k]]['level'] - nodes[k]['level'] for k in inner}
    levels = {0.} | {g for g in gap.values() if 0 < g <= 2 * limit}
    best = np.inf
    for s in levels:
        r = _search(nodes, root, frozenset(k for k in inner if gap[k] <= s), q, w, V, p, limit, 0)
        if r: best = min(best, r['tau'])
    return best


def ablation(name):
    V, Q, W, p, R = volume(name) if name in ('Cylinder', 'Tangaroa') else planar(name); L = p.canvas; out = {}
    for e in (0., BAL[name]):
        rows = []
        for v, q, w in zip(V, Q, W):
            if len(v) < 2:      # one feature: only the canvas term, the same for every method
                t1 = float(interval_costs(np.array([[0]]), w, q, p)[0]); rows.append((t1, t1, t1, t1)); continue
            pt = budget_order(v, q, L, e * R, TIE * R); full = width_order(v, q, w, p, e * R, TIE * R, point=pt)
            rows.append((full['lower'], threshold_only(v, q, w, p, e * R + TIE * R), full['point_tau'], full['tau']))
        a = 100 * np.array(rows) / L
        out[f'{e:g}'] = dict(frames=len(rows), width_bound=a[:, 0].mean(), threshold_only=a[:, 1].mean(), point_order=a[:, 2].mean(),
                             full_search=a[:, 3].mean(), at_bound=int(np.sum(a[:, 3] <= a[:, 0] + 1e-7)))
        print(name, e, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out[f'{e:g}'].items()}, flush=True)
    return out


def depth(name):
    m = json.loads((PKG / name / 'metadata.json').read_text()); R = m['scalar_range']; F = json.loads((PKG / name / 'per_frame_inputs.json').read_text())
    files = sorted(PKG.glob(f'{name}/AnchorMTM_*_layouts.json'))
    out = {}
    for fpath in files:
        J = json.loads(fpath.read_text()); tag = fpath.stem.replace('AnchorMTM_', '').replace('_layouts', '')
        n = vanish = small = halved = 0
        for f, lay in zip(F, J):
            V = np.array(f['merge_matrix'], float); fv = np.diag(V); o = lay['order']; b = lay['barriers']
            if len(o) < 2: continue
            for k, i in enumerate(o):
                deeper = [j for j in range(len(fv)) if fv[j] < fv[i] or (fv[j] == fv[i] and j < i)]
                if not deeper: continue                                          # the global minimum has no finite depth
                pers = min(V[i, j] for j in deeper) - fv[i]
                d = min(b[k - 1] if k > 0 else np.inf, b[k] if k < len(o) - 1 else np.inf) - fv[i]
                n += 1; vanish += d <= 1e-9 * R; small += d < .01 * R; halved += d < .5 * pers
        out[tag] = dict(leaves=n, vanishing=int(vanish), below_1pct=int(small), below_half_persistence=int(halved))
        print(name, tag, out[tag], flush=True)
    return out


def ties():
    out = {}
    for name in ('Ring', 'Wildfires', 'Storms', 'PM25', 'Cylinder', 'Tangaroa'):
        m = json.loads((PKG / name / 'metadata.json').read_text()); R = m['scalar_range']; F = json.loads((PKG / name / 'per_frame_inputs.json').read_text())
        tied = 0; gaps = []
        for f in F:
            V = np.array(f['merge_matrix'], float); off = np.unique(V[np.triu_indices(len(V), 1)])
            d = np.diff(off); d = d[(d > 0) & (d <= 2e-7 * R)]
            if len(d): tied += 1; gaps += list(d / R)
        out[name] = dict(frames=len(F), frames_with_near_ties=tied, smallest=min(gaps) if gaps else None, largest=max(gaps) if gaps else None)
    g = json.loads((FIG / 'volume_gallery20261108/cylinder.json').read_text())
    out['Cylinder']['exact_merge_error_original_tree'] = g['maps']['eps=0']['NMLE_max']
    print(out); return out


def strict():
    d, p, feats = v5.load('Cylinder', 'x'); R = d['scalar_range']; L = p.canvas; rows = []
    for t, (V, q) in enumerate(zip(d['merge'], d['references'])):
        w = p.width_scale * np.asarray(d['measures'][t], float)
        o = width_order(V, q, w, p, 0., 0., point=budget_order(V, q, L, 0., 0.))['order']
        tau = float(interval_costs(np.array([o]), w, np.asarray(q, float), p)[0]); prev = prevq = mask = None
        if t:
            old = {k: i for i, k in enumerate(d['tracks'][t - 1])}; mask = np.array([k in old for k in d['tracks'][t]])
            prev = np.array([rows[-1]['x'][old[k]] if k in old else 0. for k in d['tracks'][t]]); prevq = np.array([d['references'][t - 1][old[k]] if k in old else 0. for k in d['tracks'][t]])
        c = Controls(topology_budget=0., position_budget=(tau + p.extra_budget) / L)
        rows.append(solve_unified_frame(d['centers'][t], d['measures'][t], d['hierarchies'][t], np.asarray(q, float), d['merge'][t], R, c, p,
                                        candidate_orders=[o], previous=prev, previous_q=prevq, matched=mask))
    s = v5.score(d, p, [r['x'] for r in rows]); s['merge_max'] = float(max(r['measured_topology'] for r in rows))
    s['nu_strict'] = v5.nu_mean(d, p); print(s); return s


def motion():
    out = {}
    for name, gpath in (('Tangaroa', FIG / 'volumes/tangaroa_x_gallery.json'), ('Cylinder', FIG / 'volume_gallery20261108/cylinder.json')):
        d, p, _ = v5.load(name, 'x'); G = json.loads(gpath.read_text()); L = G['canvas']; Q = [np.asarray(q, float) for q in G['q']]; tr = d['tracks']
        assert [len(q) for q in Q] == [len(t) for t in tr]
        out[name] = {}
        for key, lab in (('TMTM', 'TMTM'), ('ST-MTM', 'ST-MTM'), ('eps=0', 'Exact'), ('eps=0.1', '10%'), ('q', 'reference')):
            X = Q if key == 'q' else [np.asarray(x, float) for x in G['maps'][key]['x']]
            err, rev, clear, sw, nsw, sw_err, nsw_err, matched, total = [], 0, 0, 0, 0, [], [], 0, 0
            for t in range(1, len(Q)):
                old = {k: i for i, k in enumerate(tr[t - 1])}; pairs = [(old[k], i) for i, k in enumerate(tr[t]) if k in old]
                matched += len(pairs); total += len(tr[t])
                if not pairs: continue
                a, b = np.array([j for j, _ in pairs]), np.array([i for _, i in pairs])
                dq = Q[t][b] - Q[t - 1][a]; dx = X[t][b] - X[t - 1][a]; e = np.abs(dx - dq) / L; err += list(e)
                c = np.abs(dq) >= .005 * L; clear += int(c.sum()); rev += int(np.sum(c & (dx * dq <= 0)))
                switched = len(pairs) > 1 and not np.array_equal(np.argsort(X[t - 1][a], kind='stable'), np.argsort(X[t][b], kind='stable'))
                (sw_err if switched else nsw_err).extend(e); sw += switched; nsw += not switched
            out[name][lab] = dict(coverage=matched / total, mean_step_error=100 * float(np.mean(err)), reversal_rate=100 * rev / max(clear, 1), clear_steps=clear,
                                  error_order_switch=100 * float(np.mean(sw_err)) if sw_err else None, error_no_switch=100 * float(np.mean(nsw_err)) if nsw_err else None,
                                  steps_with_switch=int(sw), steps_without=int(nsw))
            print(name, lab, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out[name][lab].items()}, flush=True)
    return out


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True); task = sys.argv[1]; name = sys.argv[2] if len(sys.argv) > 2 else None
    res = {'ablation': ablation, 'depth': depth}.get(task, None)
    res = res(name) if res else {'ties': ties, 'strict': strict, 'motion': motion}[task]()
    (OUT / (f'{task}_{name}.json' if name else f'{task}.json')).write_text(json.dumps(res, indent=1, default=float) + '\n')
