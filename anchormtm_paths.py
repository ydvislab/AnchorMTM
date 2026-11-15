"""Locations used by every script. Each one can be overridden with an environment variable.

RESULTS  bundled intermediate results that the figure and table scripts read (in this repository)
INPUTS   prepared inputs that are too large to bundle (see data/README.md)
DATA     raw data downloaded from their public sources (see data/README.md)
OUTPUT   everything the scripts write: figures, tables, logs
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = Path(os.environ.get('ANCHORMTM_RESULTS', ROOT / 'results'))
INPUTS = Path(os.environ.get('ANCHORMTM_INPUTS', ROOT / 'inputs'))
DATA = Path(os.environ.get('ANCHORMTM_DATA', ROOT / 'data'))
OUTPUT = Path(os.environ.get('ANCHORMTM_OUTPUT', ROOT / 'output'))
TTK_BIN = Path(os.environ.get('ANCHORMTM_TTK_BIN', ROOT / 'tmp/volume3d/native-build/rgmtm_ttk_volume'))

FIGDATA = RESULTS / 'figdata'
FIGURES_OUT = OUTPUT / 'figures'
TABLES_OUT = OUTPUT / 'tables'
for _d in (FIGURES_OUT, TABLES_OUT, OUTPUT / 'preview'):
    _d.mkdir(parents=True, exist_ok=True)
