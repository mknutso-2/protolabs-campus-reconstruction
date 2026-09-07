# Fresh source checkout verification — 52eff10

**Result: source generation and export reproduced, but the archived scene fails the closed-box winding check. This revision does not pass geometry acceptance.**

Verified on September 7, 2026, from exact local commit `52eff105a26fff1c385c09b7d52a1c484243a075`, tree `cb8ec08a0095abb69648a6e54542d6414f78520f`. A `git archive --format=tar` snapshot contained 40 tracked files and was extracted into the separate workspace directory `work/fresh-scene-verification`. Neither a Blender master nor a GLB existed in that clean directory before generation. Uncommitted workspace files were not copied.

## Commands and scope

The archive was created with `git archive --format=tar 52eff105a26fff1c385c09b7d52a1c484243a075` and extracted with Python's `tarfile` data filter. The existing Blender executable was the workspace's `work/tools/blender-4.2.9-linux-x64/blender` (Blender 4.2.9 LTS, build hash `a10f621e649a`).

The successful generation command used absolute executable and script paths. In the following equivalent command, `VERIFY_ROOT` is the absolute clean archive directory and `BLENDER_BIN` is the absolute executable above:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 "$BLENDER_BIN" \
  --background --threads 2 --python-exit-code 1 \
  --python "$VERIFY_ROOT/scripts/build_scene.py" -- --export
```

Generation/export took **145.148 seconds**, returned exit code **0**, and emitted `SCENE_READY 2443`. No render was requested. No lidar processing, image retrieval, browser build, film encoding or network access was needed. The main project master, viewer and source branch were not modified by this isolated run.

An initial launch using the relative argument `--python scripts/build_scene.py` resolved against the outer workspace in this bundled runtime and reported that the script was missing, despite Blender returning exit code 0. That attempt did not generate a scene. The corrected launch used the absolute archived script path and `--python-exit-code 1`; these options should be retained in automated verification.

## Regenerated artifacts

| Artifact | Size | SHA256 |
| --- | ---: | --- |
| `scene/protolabs-campus.blend` | 34,561,752 bytes | `eac5103f3d3bc5e38ccad740f76e1487ea476df9f535151fc159e3b4e69daea1` |
| `scene/protolabs-campus.glb` | 33,167,388 bytes | `f9e7ebbb39383e9a35bd808c0e21a434533432e8ede6773f39f0a8b2cd93be2d` |

The GLB header has magic `glTF`, version 2, and a declared byte length matching the file size. These checks establish a generated, structurally readable artifact, not rendering fidelity. Binary hashes identify this particular run; byte-for-byte determinism across Blender environments is not claimed.

The regenerated `scene/cameras.json` parses identically to the committed baseline, with four cameras. Regenerated `scene/materials.json` also parses identically, with 21 material fallback entries. After reopening the generated master, the `reference_aerial` camera matches the committed photographic fit to floating-point storage precision:

- Maximum position difference: `1.0767117686327765e-06` metres.
- Maximum Euler XYZ difference: `3.041349061483345e-08` radians.
- Lens difference: `7.007226408006773e-07` mm; horizontal sensor width 36 mm.

## Read-only scene inspection

The generated master was reopened in Blender for inspection. Its seven populated named collections were present: architecture (820 objects), roof structure (154), site (882), vegetation (355), details (220), context (8), and cameras (4). The default `Collection` was empty. Counts are inventory checks, not a measure of visual quality.

All 14 checked identity-bearing objects were present in the expected collections: `Main block occupied volume`, `Main roof aggregate`, `NE wing enclosed volume`, `NE aggregate flat roof`, `Measured canted ribbon roof`, `Roof leading edge`, `Fan brace`, `Recessed triangular clerestory`, `Vestibule interior`, `Measured rolling ground`, `Dark monument sign`, `Flagpole`, `US flag cloth`, and `Current fascia wordmark`.

## Confirmed winding defect

The archived cube helper assigns every face inward winding. Independently executing that actual source helper for a 2 × 2 × 2 unit box gives signed volume **−8 m³**, whereas outward winding gives **+8 m³**. Every face's normal dot outward-centroid direction is negative. This was then confirmed on actual closed meshes reopened from the generated Blender master:

| Closed mesh | Signed local volume | Expected outward volume | Result |
| --- | ---: | ---: | --- |
| `Main block occupied volume` | −28,282.228624 m³ | +28,282.228624 m³ | Fail |
| `Long lower logo canopy` | −145.800006 m³ | +145.800006 m³ | Fail |
| `Dark monument sign` | −4.306500 m³ | +4.306500 m³ | Fail |

All three are closed manifold boxes; manifold status alone does not detect the inverted orientation. This can affect exported back-face visibility and shading. The script `scripts/check_geometry.py` now checks the actual cube source helper mathematically and selected closed Blender meshes with signed volume and outward face-normal tests. It does not alter normals or recalculate arbitrary flat surfaces. Invoking the checker directly against the archived master with `--python-exit-code 1` returned the expected exit code **1**, confirming that the regression failure is actionable by automation.

The working generator's subsequent face-order correction passes the source-only unit-box regression with signed volume **+8 m³** and six positive outward normal tests. That corrected working source was outside archived commit `52eff10` and is **not** covered by this generation run. A new clean run against the next committed source is required before accepting its master and GLB.

```bash
python scripts/check_geometry.py --source-only
"$BLENDER_BIN" --background "$VERIFY_ROOT/scene/protolabs-campus.blend" \
  --python-exit-code 1 --python /absolute/path/to/scripts/check_geometry.py \
  -- --root "$VERIFY_ROOT" --output "$VERIFY_ROOT/geometry-check.json"
```

Logs and structured receipts remain in the isolated verification directory: `verification-source.json`, `verification-build-attempt1.log/json`, `verification-build.log/json`, `verification-artifacts.json`, `verification-inspection.json`, and `geometry-check.json/log`. The read-only inspection did not save or repair the archived master.

**Not verified here:** photographic resemblance, finished still-image quality, full-resolution motion samples, complete flythrough frames, browser interaction or publication. This run makes no claim of photorealism or full site fidelity.
