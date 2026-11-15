"""SNS, TW, TD and NPE of TMTM and ST-MTM on Ring, Wildfires and Storms (the baseline rows of Table 1).

The planar pipeline (experiments/planar_pvis2027/run.py, baseline_npe) computes only NPE for the baselines. This script reruns
that function unchanged on the stored preparation of one sequence, then scores the baseline anchors with the formulas the
pipeline uses for AnchorMTM (run.py, evaluate): SNS against support-centroid distances, TW with the per-sequence k and the
0 < k < n/2 rule, TD as summed matched displacement, NPE as the mean per-frame worst displacement over the canvas.
Nothing in the repository is written; outputs go to OUT.

Input: the preparation folder of one sequence, as the pipeline writes it:
  PREP/fields.npy  PREP/coordinates.npy  PREP/protocol.json  PREP/trees/frame_###.*
Usage (repository root):
  python scripts/analyses/baseline_sns_tw.py NAME PREP OUT [STORED]
STORED, if given, is the baseline_npe folder of the original run: its anchors are scored instead of rerunning the baselines
(on Storms the rerun of ST-MTM differs slightly from the stored run over 744 temporally chained frames; Table 1 uses the stored one).
NAME is Ring, Wildfires, Storms or Gaussian. Needs numpy, scipy, osqp, clarabel, threadpoolctl, netCDF4.
Check: the recomputed NPE must equal the NPE of Table 1 (printed as PASS/FAIL).
The bundled results/baseline_metrics/<NAME>.json are the outputs of this script.
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # repository root
import anchormtm_paths as AP  # noqa: E402
import importlib.util, json, sys
from pathlib import Path
import numpy as np
from scipy.spatial.distance import pdist

REPO = AP.ROOT
SRC = REPO / 'experiments/planar_pvis2027'
TABLE1_NPE = {'Gaussian': (0.1118, 0.1154), 'Ring': (0.1756, 0.2463), 'Wildfires': (0.2280, 0.3180), 'Storms': (0.5753, 0.4579)}   # TMTM, ST-MTM


def main(name, prep, out, stored=None):
    prep, out = Path(prep), Path(out); out.mkdir(parents=True, exist_ok=True)
    sys.path[:0] = [str(SRC)]
    spec = importlib.util.spec_from_file_location('run', SRC / 'run.py'); run = importlib.util.module_from_spec(spec); spec.loader.exec_module(run)
    run.O = out                                                   # the pipeline writes its baseline files under OUT only
    F = np.load(prep / 'fields.npy'); xy = np.load(prep / 'coordinates.npy'); meta = json.loads((prep / 'protocol.json').read_text())
    d = run.load(name, F, xy, meta['sample_measure'], prep / 'trees')
    # STORED (optional): the baseline_npe folder of the original run; its anchors are the ones behind Table 1 and are scored as they are
    res = 'scored stored anchors from ' + str(stored) if stored else run.baseline_npe(name, d)
    anchors = Path(stored) if stored else out / 'results' / name / 'baseline_npe'
    sc = d['scene']; p = d['parameters']; k = run.PARAMS[name]['k']; qs = d['reference']['qs']; result = {}
    for (label, mode), table in zip((('TMTM', 'tmtm'), ('ST-MTM', 'temporal')), TABLE1_NPE[name]):
        U = [np.asarray(u, float) for u in json.loads((anchors / f'{mode}_anchors.json').read_text())]
        ss, ww, motion, count = [], [], 0., 0
        for t, (u, c, tr) in enumerate(zip(U, sc['centers'], sc['tracks'])):
            src = pdist(c); dst = pdist(u[:, None])
            if len(src) and np.sum(src * src) > 0:
                a = np.sum(src * dst) / np.sum(dst * dst) if np.sum(dst * dst) > 0 else 0.
                ss.append(float(np.sum((src - a * dst) ** 2) / np.sum(src * src)))
            if 0 < k < len(u) / 2: ww.append(float(run.st.trustworthiness(c, u, k)))
            if t:
                old = dict(zip(sc['tracks'][t - 1], U[t - 1]))
                for key, x in zip(tr, u):
                    if key in old: motion += abs(x - old[key]) / p.canvas; count += 1
        npe = float(np.mean([np.max(np.abs(u - np.asarray(q))) / p.canvas for u, q in zip(U, qs)]))
        result[label] = dict(SNS=float(np.mean(ss)) if ss else None, SNS_frames=len(ss), TW=float(np.mean(ww)) if ww else None, TW_frames=len(ww),
                             TW_k=k, TD=float(motion), matched_steps=count, NPE=npe, frames=len(U), NPE_table1=table,
                             NPE_check='PASS' if abs(npe - table) < 5e-4 else 'FAIL')
        print(name, label, {kk: (round(v, 4) if isinstance(v, float) else v) for kk, v in result[label].items()}, flush=True)
    (out / f'{name}_baseline_metrics{"_stored" if stored else ""}.json').write_text(json.dumps(dict(dataset=name, preparation=str(prep), baselines=result, pipeline_status=res), indent=1, default=str) + '\n')


if __name__ == '__main__':
    main(*sys.argv[1:5])
