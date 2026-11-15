"""Table S1: parameter settings and runtime of AnchorMTM (Balanced) on Ring, Wildfires, Storms and PM2.5, checked against the paper.

Sources (all in results/):
  planar_pvis2027/anchor_parameters.csv     N_r (L_pixels) and s_w (width_scale) on Ring, Wildfires, Storms
  planar_pvis2027/anchor_runtime.csv        t_opt and t_total of the Balanced runs (single runs, no tree cache)
  pm25_hourly/anchor_parameters.json        s_w on PM2.5
  pm25_hourly/timing.json                   t_opt and t_total on PM2.5
  pm25_hourly/figure_cache.npz              N_r on PM2.5 (rows of the map raster)
The volume values in the table note (s_w, gaps, slack and times on Tangaroa and Cylinder) are not assembled here.
Run:  python scripts/tables/tableS1.py      Output: output/tables/table_parameters_runtime.csv
"""
import csv, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import anchormtm_paths as AP  # noqa: E402

R = AP.RESULTS
COLS = ('Ring', 'Wildfires', 'Storms', 'PM2.5')
# Values printed in Table S1: (N_r, s_w, t_opt, t_total)
PAPER = {'Ring': (196, .00328, .150, .486), 'Wildfires': (4096, .00053, 3.324, 4.424),
         'Storms': (4096, .01170, 2.600, 63.447), 'PM2.5': (4096, .00073, 199.975, 231.177)}
DIGITS = (0, 5, 3, 3)


def load():
    T = {}
    par = {r['Dataset']: r for r in csv.DictReader(open(R / 'planar_pvis2027/anchor_parameters.csv'))}
    run = {r['Dataset']: r for r in csv.DictReader(open(R / 'planar_pvis2027/anchor_runtime.csv')) if r['Method'] == 'AnchorMTM Balanced'}
    for s in COLS[:3]:
        T[s] = (int(par[s]['L_pixels']), float(par[s]['width_scale']), float(run[s]['t_opt']), float(run[s]['t_total']))
    p = json.loads((R / 'pm25_hourly/anchor_parameters.json').read_text()); t = json.loads((R / 'pm25_hourly/timing.json').read_text())
    T['PM2.5'] = (np.load(R / 'pm25_hourly/figure_cache.npz')['map'].shape[0], p['width_scale'], t['t_opt'], t['t_total'])
    return T


def main():
    T = load(); bad = 0; rows = []
    for s in COLS:
        for k, (name, d) in enumerate(zip(('N_r', 's_w', 't_opt', 't_total'), DIGITS)):
            got, want = T[s][k], PAPER[s][k]
            ok = round(got, d) == round(want, d); bad += not ok
            rows.append(dict(sequence=s, parameter=name, value=got, paper=want, match=ok))
        print(f'{s:9s} N_r {T[s][0]}  s_w {T[s][1]:.5f}  t_opt {T[s][2]:.3f}  t_total {T[s][3]:.3f}')
    with open(AP.TABLES_OUT / 'table_parameters_runtime.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f'{len(rows) - bad} of {len(rows)} values match the paper')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
