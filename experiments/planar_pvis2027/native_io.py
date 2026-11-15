"""Pinned project-native TTK frame adapter, no external experiment imports."""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))   # repository root
import anchormtm_paths as AP  # noqa: E402
from pathlib import Path
import numpy as np
from experiments.volume3d.paper_trees import Frame as NativeFrame
R=AP.ROOT
RAW=AP.DATA/'real/ERA5_MSLP/ERA5_MSLP_19991117_20000114.nc'
BIN=AP.TTK_BIN
if not BIN.exists():BIN=Path(__file__).resolve().parent/'native/rgmtm_ttk_volume_macos_arm64'
class Frame(NativeFrame):
 def __init__(self,t,directory,coords):
  super().__init__(t,directory);self.coordinates=coords;self.domain_min=coords.min(0);self.domain_max=coords.max(0);self.sample_ids=np.arange(len(coords));self.kind='join'
 def leaf_centroid(self,k):return self.coordinates[self.leaf_feature_vertices(k)].mean(0)
 def leaf_size(self,k):return len(self.leaf_feature_vertices(k))
