"""SNS of the reference map (every feature drawn exactly at its reference, NPE = 0) on Ring, Wildfires and Storms.

Same inputs and the same SNS formula as Table 1 (planar_pvis2027/run.py evaluate, baseline_sns_tw.py): stress of the 1-D
positions against support-centroid distances, with the optimal scale, averaged over frames with at least two features.
Also rescored: ST-MTM from its stored anchors, as a check against Table 1.
Usage (repository root):  python scripts/analyses/reference_sns.py INPUTS OUT.json
INPUTS holds <name>/preparation and <name>/baseline_npe for each sequence (not bundled).
Bundled output: results/supplement_analyses/reference_sns.json
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # repository root
import anchormtm_paths as AP  # noqa: E402
import importlib.util, json, sys
from pathlib import Path
import numpy as np
from scipy.spatial.distance import pdist

REPO = AP.ROOT; SRC = REPO / 'experiments/planar_pvis2027'


def sns(c, u):
    src = pdist(c); dst = pdist(np.asarray(u, float)[:, None])
    if not len(src) or np.sum(src * src) == 0: return None
    a = np.sum(src * dst) / np.sum(dst * dst) if np.sum(dst * dst) > 0 else 0.
    return float(np.sum((src - a * dst) ** 2) / np.sum(src * src))


def main(inputs, out):
    sys.path[:0] = [str(SRC)]
    spec = importlib.util.spec_from_file_location('run', SRC / 'run.py'); run = importlib.util.module_from_spec(spec); spec.loader.exec_module(run)
    res = {}
    for name in ('Ring', 'Wildfires', 'Storms'):
        prep = Path(inputs) / name / 'preparation'
        d = run.load(name, np.load(prep / 'fields.npy'), np.load(prep / 'coordinates.npy'), json.loads((prep / 'protocol.json').read_text())['sample_measure'], prep / 'trees')
        C = d['scene']['centers']; Q = d['reference']['qs']
        U = [np.asarray(u, float) for u in json.loads((Path(inputs) / name / 'baseline_npe' / 'temporal_anchors.json').read_text())]
        q = [s for s in (sns(c, x) for c, x in zip(C, Q)) if s is not None]
        st = [s for s in (sns(c, x) for c, x in zip(C, U)) if s is not None]
        res[name] = dict(reference_SNS=float(np.mean(q)), frames=len(q), STMTM_SNS_check=float(np.mean(st)))
        print(name, res[name], flush=True)
    Path(out).write_text(json.dumps(res, indent=1) + '\n')


if __name__ == '__main__':
    main(*sys.argv[1:3])
