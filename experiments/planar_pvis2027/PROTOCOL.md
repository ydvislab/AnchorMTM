# Planar experiments: Ring, Wildfires, Storms

This pipeline produces the AnchorMTM rows of Table 1 for Ring, Wildfires and Storms, the Balanced budget selection and
the runtimes of Table S1. The bundled summaries of the run used in the paper are in `results/planar_pvis2027/`.

## Run

From the repository root, with the raw inputs of `data/README.md` and the TTK adapter built
(`python -m experiments.volume3d.build_native_ttk`, see the main README):

```bash
PYTHONPATH=src:. python experiments/planar_pvis2027/run.py                # all datasets; --dataset NAME for one
PYTHONPATH=src:. python experiments/planar_pvis2027/assemble.py           # tables of the run
PYTHONPATH=src:. python experiments/planar_pvis2027/verify.py             # independent checks of every map
PYTHONPATH=src:. python experiments/planar_pvis2027/finalize_delivery.py  # fingerprints of the outputs
```

Everything is written to `$ANCHORMTM_OUTPUT/planar_pvis2027` (default `output/planar_pvis2027`). `run.py` also records the
SHA-256 of the core files it used (`config/core_sha256.json`); `verify.py` checks that they are unchanged. Gaussian is
computed by the pipeline but not reported in the paper.

## Protocol

- Inputs. Ring is rebuilt from the archived generator of the original authors (`experiments/ring`). Wildfires uses the
  daily FRP of `wildfire.json`, aggregated into 32 equal-duration bins over 1 Nov 2019 - 1 Jan 2020 on fixed 64 x 64
  spatial bins. Storms uses hourly ERA5 mean sea level pressure of December 1999 (744 frames, 30-75 N, 30 W-40 E), as the
  anomaly from a 192-hour moving mean, smoothed with a Gaussian of sigma 2 cells. The source file and its SHA-256 are
  recorded in each `protocol.json`.
- Simplification. Persistence threshold p per dataset as a fraction of each preprocessed frame range:
  Gaussian 0.001, Ring 0.001, Wildfires 0.15, Storms 0.105 (0.1%, 0.1%, 15%, 10.5%). The fractions are multiplied with
  the frame range directly. Cache metadata and the threshold of every tree are checked.
- Exact: merge budget epsilon = 0 (numerical allowance eps0 = 1e-7 of the range).
- Balanced: the budget is chosen on the chronologically first 25% of the frames among epsilon = 1..10% in 1% steps,
  minimising J = 0.5 NPE_norm + 0.5 SNS_norm over the candidates whose attained merge error stays within the budget;
  within 0.01 of the minimum the smaller budget, then the smaller attained error is preferred. There is no fallback to
  epsilon = 0 and no retuning on the test frames.
- Reuse. Raw source fields may be reused only when unchanged; simplified trees, layouts and scores are never reused.
- Baselines. `run.py` computes only the NPE of TMTM and ST-MTM (`baseline_npe`). Their SNS, TW and TD in Table 1 come from
  `scripts/analyses/baseline_sns_tw.py`, which scores the stored baseline anchors with the formulas used for AnchorMTM.
- Timing. Single runs on one thread without a tree cache (`results/planar_pvis2027/anchor_runtime.csv`, Apple M4):
  `t_opt` covers ordering and placement, `t_total` the full pipeline.
