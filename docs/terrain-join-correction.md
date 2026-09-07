# Main/north terrain join correction

Full-size inspection of the v07b overview revealed a thin dark diagonal line beginning near pixel `(606,35)` and crossing the upper field. The [v07b verification note](nlcd-fresh-v07b-verification.md) preserves that failed condition and image hashes. The exported main and north meshes shared 81 vertices along `y=220`, but the north side stood 0.119908–0.120754 m above the main side.

The cause was a rendering offset mismatch: the main surface uses `tz−0.12`, while the north surface's existing 10 m transition began at unlowered, slightly clamped `ground()`. The bounded source correction starts that same transition at the actual rendered main edge:

```python
main_edge_z = tz[-1][tx.index(x)] - .12
z = main_edge_z * (1 - blend) + nz[j][i] * blend
```

The main terrain and all source JSON measurements remain unchanged. The correction changes only 162 north mesh vertices at `y=220` and `y=225`; north vertices at and beyond `y=230` remain byte-identical. Rebuilding the existing regional transition from the corrected boundary changes only two external vertices, at most 0.060226 m. It creates no new platform or boundary concealment.

An independent scratch test loaded master `7dd2ff5a1253f1153e70c4ba09a1bb7806c3d326b950d91c629635bb5cc43cc0`, applied precisely that north transition and rebuilt the regional sheet. All 81 shared vertices then matched with **0 m vertical error**. Every other mesh's coordinate/topology hash, and every original nonregional object's transform/data link, remained unchanged. All tree objects were preserved. Eight existing lidar-rooted trees fall within the narrow transition; the rendered surface beneath them changes by 0.006–0.115 m while their recorded positions/heights remain unchanged. This is disclosed rather than treated as a new tree measurement.

The test rendered only overview pixels `[550,0,1600,350]` at the native 1600×1067 projection, 32 Cycles samples and six CPU threads. The 1050×350 crop took 46.78 seconds. Inspection confirmed that the long dark join line was removed, with no new visible step or tree crowding in the crop. This accepts the bounded correction for a fresh build; it does not certify the next full stills, browser package or motion.

Scratch image: `work/terrain-join-fix/corrected-seam-crop.png`, SHA-256 `81f3387743f3a6a53ffd1ef5642c2ff36657d08cd425a068c075954e34b3aa63`. Reproduction fixture and measured results: `work/terrain-join-fix/preview.py` and `preview-report.json`. No master save, main-output overwrite or camera/material change occurred; the original master hash remained unchanged after the crop render.
