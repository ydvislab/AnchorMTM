# AnchorMTM

Code, intermediate results and figure/table scripts for the paper
**AnchorMTM: Spatially Anchored Merge Tree Maps with Topology–Position Tradeoffs** (PacificVis 2027, paper 1037).

The repository supports two levels of reproduction:

- **Level 1, figures and tables (about one minute, no raw data).** Every figure and table of the paper and the
  supplement is rebuilt from the intermediate results bundled in `results/` and checked against the submitted version.
- **Level 2, the bundled results.** The experiments in `experiments/` and the analyses in `scripts/analyses/` regenerate
  `results/` from the raw data (`data/README.md`). This needs the raw inputs, a TTK build and hours of computation; it was
  not rerun for this release (see the section on Level 2 for what is and is not covered).

## Layout

| Folder | Contents |
|---|---|
| `src/rgmtm/` | core library: merge trees, order certificates, interval order, budgeted layout (`unified.py`, `error_budget.py`, `reference_guided.py`), TMTM, ST-MTM and space-filling baselines |
| `analysis/` | AnchorMTM entry point (`anchormtm.py`), automatic reference (`general_method.py`), dataset loaders, ERA5 download scripts |
| `experiments/` | experiment pipelines; `planar_pvis2027/` produces the planar rows of Table 1 (see its `PROTOCOL.md`) |
| `scripts/figures/`, `scripts/tables/` | one script per figure or table of the paper (Level 1) |
| `scripts/analyses/` | analyses that produce the files in `results/figdata/` and `results/supplement_analyses/` (Level 2) |
| `scripts/run_all.py` | runs every Level 1 step |
| `results/` | bundled intermediate results read by the figure and table scripts |
| `figures_src/` | hand-made figures and overlays: PDF exports used in the paper, TikZ overlays, editable PowerPoint sources (`figures_src/editable/`) |
| `tests/` | unit tests of the library and of the data preparation |
| `tools/` | download and preparation of the OLR and PM2.5 inputs |
| `anchormtm_paths.py` | every location used by the scripts, configurable by environment variables |

## Installation

Tested with Python 3.12.7 on macOS (Apple silicon).

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .                       # Level 1
.venv/bin/python -m pip install -e '.[solvers,volume3d,era5]'  # Level 2
```

External tools for Level 1: `pdftocairo` (poppler) for the PNG export, and `tectonic` or `pdflatex` with the
`standalone` and `tikz` packages for the overlays of Figs. 1, 2 and 7. Figure 2 also needs a PDF export of its slide
(PowerPoint or LibreOffice). Level 2 additionally needs CMake, Ninja and a C++ compiler to build the TTK 0.9.9 adapter.

## Paths

All scripts take their locations from `anchormtm_paths.py`. Each can be overridden with an environment variable:

| Variable | Default | Meaning |
|---|---|---|
| `ANCHORMTM_RESULTS` | `results/` | bundled intermediate results; the experiments of Level 2 also write their runs here |
| `ANCHORMTM_OUTPUT` | `output/` | everything the scripts write: `output/figures/`, `output/figures/png/`, `output/tables/` |
| `ANCHORMTM_DATA` | `data/` | raw data (`data/README.md`) |
| `ANCHORMTM_INPUTS` | `inputs/` | prepared inputs that are too large to bundle (`inputs/package01`, the planar preparation folders) |
| `ANCHORMTM_TTK_BIN` | `tmp/volume3d/native-build/rgmtm_ttk_volume` | TTK adapter built by `python -m experiments.volume3d.build_native_ttk` |

Example: `ANCHORMTM_OUTPUT=/tmp/anchormtm python scripts/run_all.py`.

## Level 1: all figures and tables

```bash
.venv/bin/python scripts/run_all.py
```

This writes the figure PDFs to `output/figures/`, PNGs at 600 dpi of the printed width to `output/figures/png/` (the files
the LaTeX source includes) and the tables to `output/tables/`. The table scripts compare every value with the paper and
exit with an error if one differs. Figure 2 is included when LibreOffice is installed; otherwise run its script with a
PDF export of the slide (below). Each step can also be run on its own, as listed below.

### Figures

| Paper | Script | Reads | Origin of the inputs | Check against the submitted figure |
|---|---|---|---|---|
| Fig. 1 Storms overview | `scripts/figures/east_arrows.py` | `figures_src/fig01_storms_overview_base.pdf` | laid out by hand (`figures_src/editable/Fig1_storms_overview.pptx`); the script adds the East arrow (`fig01_east_arrow.tex`) | identical |
| Fig. 2 Workflow | `scripts/figures/fig02_workflow.py [SLIDE.pdf]` | PDF export of `figures_src/fig02_workflow.pptx` | drawn by hand; the script crops the exported slide (`fig02_crop.tex`) | crop verified on the slide size of the paper; needs the PowerPoint export |
| Fig. 3 Selective flattening | `scripts/figures/fig03_selective_flattening.py` | none (analytic example) | — | identical |
| Fig. 4 Forced and chosen error | `scripts/figures/fig04_forced_error.py` | `results/figdata/{plane_her20261109, plane20261108, frontier20261027, orientation20261106, reference_direction20261027, volumes}` | `scripts/analyses/plane_her.py`, `plane_data.py`, `best_mirror.py`, `volumes.py`; `experiments/frontier/run.py`, `experiments/reference_direction/run.py` | identical |
| Fig. 5 Volume positions | `scripts/figures/fig05_volume_positions.py` | `results/figdata/volume_gallery20261108`, `results/figdata/volumes/*_x_gallery.json` | `scripts/analyses/volume_gallery_data.py`, `volumes.py` | identical |
| Fig. 6 Budget response | `scripts/figures/fig06_budget_response.py` | `results/package01/*_per_frame_recomputed.csv`, `results/figdata/volumes/tangaroa_x_budget.json` | per-frame records of the budget sweeps (package 01); `volumes.py` | identical |
| Fig. 7 Storms event window | `scripts/figures/east_arrows.py` | `figures_src/fig07_storms_budget_maps_base.pdf` | finished by hand (`figures_src/editable/Fig7_storms_budget_maps.pptx`) from the maps in `results/storms_structure/`; `scripts/figures/fig07_storms_budget_maps.py` redraws those map panels in a plain layout for checking | identical |
| Figs. S1-S3 | `scripts/figures/export_png.py` (copies) | `figures_src/anchor_{related_work_mapping,node_mapping,leaf_correspondence}.pdf` | drawn by hand (`figures_src/editable/FigS1-S3_*.pptx`) | identical |
| Fig. S4 Budget sweep | `scripts/figures/figS4_budget_sweep.py` | `results/budget_tradeoff/planar_per_frame/` | per-frame records of the planar budget sweeps | identical with matplotlib 3.11.2 (see below) |
| Fig. S5 Cylinder variant | `scripts/figures/export_png.py` (copies) | `figures_src/figS5_cylinder_variant.pdf` | finished by hand (`figures_src/editable/FigS5_cylinder_variant.pptx`); `scripts/figures/figS5_cylinder_variant.py` renders its map and snapshots from `results/cylinder_variant/` | identical |
| Fig. S6 Cylinder maps | `scripts/figures/figS6_cylinder_compare.py` | `results/figdata/cylinder_compare/` | rasters of the three Cylinder maps | identical with matplotlib 3.11.2 |
| Fig. S7 PM2.5 maps | `scripts/figures/figS7_pm25_compare.py` | `results/pm25_hourly/figure_cache.npz`, `results/package03/` | PM2.5 case study; TMTM and ST-MTM columns of package 03 | 0.17% of the pixels differ by sub-pixel interpolation (matplotlib 3.11.2) |

`scripts/figures/export_png.py` renders all of them to PNG. `figure_common.py`, `plane_fig.py`, `fig_plane_her.py` and
`budget_distribution.py` are shared helpers of these scripts; importing `figure_common.py` loads
`results/figdata/{frontier20261027, orientation20261106, plane20261108}`, so these folders are needed by every figure script.
`results/supplement_analyses/{reference_sns,ties}.json` hold numbers quoted in the text, and the remaining files of
`results/planar_pvis2027/` record the protocol, the Balanced selection and the verification of that run.

### Tables

| Paper | Script | Reads | Check |
|---|---|---|---|
| Table 1 | `scripts/tables/table1.py` | `results/planar_pvis2027/<seq>/{Exact,Balanced}/summary.json`, `results/baseline_metrics/`, `results/space_filling/`, `results/pm25_hourly/comparison_metrics.json`, `results/figdata/volumes/`, `results/metrics_n1c/` | 96 of 96 values and the bold/underline marks equal the paper; `output/tables/table1_rows.tex` reproduces its 12 data rows verbatim |
| Table 2 | — | definitions of the measures; no data | — |
| Table S1 | `scripts/tables/tableS1.py` | `results/planar_pvis2027/anchor_{parameters,runtime}.csv`, `results/pm25_hourly/{anchor_parameters,timing}.json` | 16 of 16 values equal the paper; the volume values in its note are not assembled |
| Tables S2-S4 | `scripts/tables/tableS2_S4.py` (runs `tables_s2_s3_base.py`) | `results/figdata/family_sweep20261109/`, `results/figdata/volumes/tangaroa_x_extras.json`, `results/metrics_n1c/` | LaTeX identical to the paper |
| Tables S5-S8 | `scripts/tables/tableS5_S8.py` | `results/supplement_analyses/` | LaTeX identical to the paper |

Notes on Table 1. TW of TMTM and ST-MTM on the two volumes is taken from `results/metrics_n1c` (k = 1); the
recomputation in `scripts/analyses/volumes.py` differs in the fourth decimal (Cylinder TMTM 0.8018 instead of 0.8017,
Tangaroa ST-MTM 0.8134 instead of 0.8137). Runtimes in Table S1 depend on the machine (Apple M4, one thread).

### Matplotlib versions

Figs. 3-6 were rendered with matplotlib 3.9.4 (the version in `pyproject.toml`), Figs. S4, S6 and S7 with matplotlib 3.11.2.
With the other version the content is the same and about 1-2.5% of the pixels differ at line and text edges. To reproduce
the three supplementary figures pixel for pixel:

```bash
.venv/bin/python -m pip install --target /tmp/mpl311 --no-deps matplotlib==3.11.2
for s in figS4_budget_sweep figS6_cylinder_compare figS7_pm25_compare; do PYTHONPATH=/tmp/mpl311 .venv/bin/python scripts/figures/$s.py; done
.venv/bin/python scripts/figures/export_png.py
```

### Figure 2

Export `figures_src/fig02_workflow.pptx` to PDF (PowerPoint: File > Save As > PDF; or LibreOffice, found automatically),
then:

```bash
.venv/bin/python scripts/figures/fig02_workflow.py path/to/fig02_workflow.pdf
.venv/bin/python scripts/figures/export_png.py
```

## Level 2: regenerating the bundled results

Run from the repository root with `PYTHONPATH=src:.`. The experiments write their runs into `results/<run>` (for example
`results/volume3d/`, `results/stmtm_completion20261026/`), where the analysis scripts read them; those folders do not clash
with the bundled ones.

| Bundled result | Generator | Inputs |
|---|---|---|
| `results/planar_pvis2027/` | `experiments/planar_pvis2027/` (`run.py`, `assemble.py`, `verify.py`; see `PROTOCOL.md`) | Ring generator, Wildfires, hourly ERA5 (`data/README.md`); TTK adapter |
| `results/baseline_metrics/` | `scripts/analyses/baseline_sns_tw.py NAME PREP OUT STORED` | preparation and `baseline_npe` folders of the planar run |
| `results/supplement_analyses/reference_sns.json` | `scripts/analyses/reference_sns.py` | same as above |
| `results/metrics_n1c/` | `experiments/metrics_n1c/run.py` (writes `results/metrics_n1c20261027/`) | earlier runs, see below |
| `results/figdata/volumes/` | `scripts/analyses/volumes.py run NAME AXIS`, `tangaroa_x_extras.py` | runs of `experiments/volume3d`, `experiments/paper1_suite`, `experiments/stmtm_completion`, `experiments/order_layout` |
| `results/figdata/volume_gallery20261108/` | `scripts/analyses/volume_gallery_data.py` | as above, plus `experiments/frontier` |
| `results/figdata/family_sweep20261109/` | `scripts/analyses/family_sweep.py`, `temporal_reference.py` | as above, plus `results/metrics_n1c` |
| `results/figdata/plane20261108/` | `scripts/analyses/plane_data.py` | runs of `experiments/order_budget` and the order-model datasets |
| `results/figdata/plane_her20261109/` | `scripts/analyses/plane_her.py` | `inputs/package01` (per-frame merge matrices, references and widths) |
| `results/figdata/orientation20261106/` | `scripts/analyses/best_mirror.py` | outputs of `scripts/analyses/stmtm_threshold.py` and of the space-filling evaluation |
| `results/figdata/reference_direction20261027/` | `experiments/reference_direction/run.py` | Tangaroa and Cylinder runs |
| `results/supplement_analyses/` | `scripts/analyses/supplement_analyses.py TASK [NAME]` | `inputs/package01`, the volume runs |
| `results/figdata/budget_her20261109/` | `scripts/figures/fig06_budget_response.py` (summary of package 01) | `results/package01/` |

Not regenerated by this repository; bundled as data products:

- `results/package01/`, `results/package03/`: per-frame records of the budget sweeps and the TMTM / ST-MTM columns of the
  PM2.5 window, exported from the experiment runs.
- `results/budget_tradeoff/planar_per_frame/`: per-frame records of AnchorMTM at 14-21 budgets on the planar sequences.
- `results/space_filling/comparison_with_space_filling.csv`: Hilbert and Morton on the planar sequences.
- `results/pm25_hourly/`: the hourly PM2.5 case study (maps, metrics, parameters and timing).
- `results/storms_structure/`, `results/cylinder_variant/`: rendered map panels and render caches of Figs. 7 and S5.
- `results/figdata/cylinder_compare/`: rasters of Fig. S6.

Several experiments also read results of earlier runs that are not produced here: `results/final_performance.json`,
`results/framework20261025/`, `results/unified20261025/`, `results/pm25_2000/` and `results/submission20261023/`. Copy them
from the original working copy of the experiments into `results/` before running the order-model and volume experiments.
Scripts that need them stop with a `FileNotFoundError` naming the file.

`scripts/analyses/bound_allowance.py` and `scripts/analyses/stmtm_threshold.py` are additional checks (the bound at the
numerical allowance, ST-MTM's reordering threshold); their outputs are not bundled.

## Tests

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -q
```

70 tests; they need neither raw data nor the TTK adapter (two of them write temporary files under `tmp/`).
