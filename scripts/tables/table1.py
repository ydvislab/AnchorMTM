"""Table 1: SNS, TW and NPE of every map on the six sequences, assembled from the result files and checked against the paper.

Sources (all in results/):
  planar_pvis2027/<seq>/{Exact,Balanced}/summary.json      AnchorMTM on Ring, Wildfires, Storms
  baseline_metrics/<seq>.json                               TMTM and ST-MTM on Ring, Wildfires, Storms (scripts/analyses/baseline_sns_tw.py)
  space_filling/comparison_with_space_filling.csv           Hilbert and Morton on Ring, Wildfires, Storms
  pm25_hourly/comparison_metrics.json                       every map on hourly PM2.5
  figdata/volumes/{cylinder,tangaroa}_x.json            every map on the two volumes (scripts/analyses/volumes.py), except
  metrics_n1c/{cylinder,tangaroa}.json                      SNS and TW (k = 1) of TMTM and ST-MTM on the volumes
Output: output/tables/table1_values.csv and output/tables/table1_rows.tex (bold = best, underline = second, among the merge tree maps;
TW is not ranked on Ring, Wildfires and Storms, which have too few eligible frames; the curves are not ranked).
Run:  python scripts/tables/table1.py
"""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import anchormtm_paths as AP  # noqa: E402

R = AP.RESULTS
PLANAR, VOLUMES = ('Ring', 'Wildfires', 'Storms'), {'Cylinder': 'cylinder_x', 'Tangaroa': 'tangaroa_x'}
MAPS = ('TMTM', 'ST-MTM', 'Exact', 'Balanced')

# Values printed in Table 1 of the paper, four decimals: (SNS, TW, NPE); curves have no NPE.
PAPER = {
 'Ring':      dict(Hilbert=(.1252, .9048), Morton=(.1489, .7619), TMTM=(.1970, .4762, .1756), **{'ST-MTM': (.0794, .9286, .2463)}, Exact=(.1485, .8571, .0471), Balanced=(.1334, .8571, .0395)),
 'Wildfires': dict(Hilbert=(.1883, .8303), Morton=(.1304, .8758), TMTM=(.1220, .8444, .2280), **{'ST-MTM': (.0186, .8968, .3180)}, Exact=(.0426, .9136, .0131), Balanced=(.0447, .8989, .0116)),
 'Storms':    dict(Hilbert=(.1290, .7403), Morton=(.1180, .7251), TMTM=(.1420, .6515, .5753), **{'ST-MTM': (.0608, .8377, .4579)}, Exact=(.0790, .8463, .0399), Balanced=(.0743, .8766, .0140)),
 'PM2.5':     dict(Hilbert=(.2386, .8887), Morton=(.1760, .8277), TMTM=(.3018, .7781, .5241), **{'ST-MTM': (.1897, .8224, .5577)}, Exact=(.1964, .7884, .1390), Balanced=(.1636, .7657, .0468)),
 'Cylinder':  dict(Hilbert=(.2798, .7902), Morton=(.2071, .8008), TMTM=(.2956, .8017, .4769), **{'ST-MTM': (.1346, .8989, .5160)}, Exact=(.1097, .8136, .0918), Balanced=(.0405, .8998, .0133)),
 'Tangaroa':  dict(Hilbert=(.3429, .9222), Morton=(.3627, .8893), TMTM=(.5255, .6701, .3866), **{'ST-MTM': (.1655, .8137, .3286)}, Exact=(.1518, .8061, .0861), Balanced=(.1364, .8476, .0465)),
}


def load():
    T = {}
    curves = {}
    with open(R / 'space_filling/comparison_with_space_filling.csv') as f:
        for r in csv.DictReader(f):
            if r['Method'] in ('Hilbert', 'Morton'): curves[(r['Dataset'], r['Method'])] = (float(r['SNS']), float(r['TW']))
    for s in PLANAR:
        b = json.loads((R / f'baseline_metrics/{s}.json').read_text())['baselines']
        row = {m: (curves[(s, m)]) for m in ('Hilbert', 'Morton')}
        for m in ('TMTM', 'ST-MTM'): row[m] = tuple(b[m][k] for k in ('SNS', 'TW', 'NPE'))
        for m in ('Exact', 'Balanced'):
            d = json.loads((R / f'planar_pvis2027/{s}/{m}/summary.json').read_text()); row[m] = (d['SNS'], d['TW'], d['NPE'])
        T[s] = row
    p = json.loads((R / 'pm25_hourly/comparison_metrics.json').read_text())
    T['PM2.5'] = {m: tuple(p[k][q] for q in (('SNS', 'TW') if m in ('Hilbert', 'Morton') else ('SNS', 'TW', 'NPE')))
                  for m, k in (('Hilbert', 'Hilbert'), ('Morton', 'Morton'), ('TMTM', 'TMTM'), ('ST-MTM', 'ST-MTM'), ('Exact', 'Exact'), ('Balanced', '5%'))}
    for s, f in VOLUMES.items():
        v = json.loads((R / f'figdata/volumes/{f}.json').read_text())
        row = {m: (v['curves'][m]['SNS'], v['curves'][m]['TW']) for m in ('Hilbert', 'Morton')}
        n1c = json.loads((R / f'metrics_n1c/{s.lower()}.json').read_text())['baselines']
        for m in ('TMTM', 'ST-MTM'): row[m] = (n1c[m]['SNS'], n1c[m]['TW1'], v['baselines'][m]['NPE'])   # SNS, TW as in metrics_n1c (k = 1)
        for m in ('Exact', 'Balanced'): row[m] = tuple(v['maps'][m][k] for k in ('SNS', 'TW', 'NPE'))
        T[s] = row
    return T


def emphasis(seq, j, vals):
    """bold / underline per column among the four merge tree maps; TW unranked on the three benchmark sequences."""
    if j == 1 and seq in PLANAR: return {m: '' for m in MAPS}
    d = sorted({round(vals[m], 4) for m in MAPS}, reverse=(j == 1))
    return {m: 'bold' if round(vals[m], 4) == d[0] else ('under' if round(vals[m], 4) == d[1] else '') for m in MAPS}


def main():
    T = load(); bad = 0; rows = []; tex = []
    fmt = lambda x, e='': (r'$\mathbf{%.4f}$' if e == 'bold' else r'$\underline{%.4f}$' if e == 'under' else '$%.4f$') % x
    for s, row in T.items():
        for m, vals in row.items():
            for k, (got, want) in enumerate(zip(vals, PAPER[s][m])):
                ok = abs(round(got, 4) - want) < 5e-5; bad += not ok
                rows.append(dict(sequence=s, map=m, measure=('SNS', 'TW', 'NPE')[k], value=f'{got:.6f}', paper=f'{want:.4f}', match=ok))
        em = [emphasis(s, j, {m: row[m][j] for m in MAPS}) for j in range(3)]
        cells = [fmt(row[c][j]) for c in ('Hilbert', 'Morton') for j in range(2)]
        cells += [fmt(row[m][j], em[j][m]) for m in ('TMTM', 'ST-MTM') for j in range(3)]
        mr = lambda x: r'\multirow{2}{*}{%s}' % x   # cells shared by the Exact and Balanced rows
        tex.append(' & '.join(mr(x) for x in [s] + cells) + ' & Exact & ' + ' & '.join(fmt(row['Exact'][j], em[j]['Exact']) for j in range(3)) + r' \\')
        tex.append(' &' * 11 + ' Balanced & ' + ' & '.join(fmt(row['Balanced'][j], em[j]['Balanced']) for j in range(3)) + r' \\')
        print(f'{s:9s} ' + '  '.join(f"{m} {'/'.join(f'{x:.4f}' for x in row[m])}" for m in row))
    with open(AP.TABLES_OUT / 'table1_values.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (AP.TABLES_OUT / 'table1_rows.tex').write_text('\n'.join(tex) + '\n')
    print(f'{len(rows) - bad} of {len(rows)} values match the paper' + ('' if not bad else f'; {bad} differ (see table1_values.csv)'))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
