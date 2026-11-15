"""TD and ME of the reference positions themselves (x = q) on the sequences of the metrics_n1c runs (data of Table S3).

TD sums the displayed motion of matched anchors, so a map that follows real motion has a large TD by construction. The value
for x = q tells how much displayed motion the data themselves imply along the axis. Volumes: see family_sweep.py.
Run from the repository root:  python scripts/analyses/temporal_reference.py
Output: results/figdata/family_sweep20261109/temporal_reference.json
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # repository root
import anchormtm_paths as AP  # noqa: E402
import importlib.util, json, sys
from pathlib import Path
import numpy as np
ROOT = AP.ROOT; CODE = AP.ROOT
sys.path[:0] = [str(ROOT), str(CODE / 'src'), str(CODE / 'analysis'), str(CODE)]
s = importlib.util.spec_from_file_location('metrics_n1c_run', CODE / 'experiments/metrics_n1c/run.py'); nc = importlib.util.module_from_spec(s); s.loader.exec_module(nc)
from rgmtm.error_budget import Parameters   # noqa: E402
out = {}
for name in nc.PLANAR:
    d = nc.n1.DATASETS[name](); p = Parameters(**{k: v for k, v in d['parameters'].items() if k in nc.n1.PARAM_FIELDS})
    _, _, feats = nc.landmarks(name)
    diag = json.loads((CODE / f'results/metrics_n1c20261027/{name.replace(".", "").lower()}.json').read_text())['diagonal']['value']
    r = nc.score(d, [np.asarray(q, float) for q in d['references']], p, feats, diag, True)
    out[name] = {k: r[k] for k in ('SNS', 'TW1', 'TD', 'ME_errors', 'ME_clear')}; print(name, out[name], flush=True)
(AP.FIGDATA / 'family_sweep20261109/temporal_reference.json').write_text(json.dumps(out, indent=1) + '\n')
