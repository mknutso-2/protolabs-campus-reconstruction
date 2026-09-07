# Fresh source checkout verification — f9ec36f

**Result: clean source generation, GLB export, committed camera/material baselines, essential object inventory, and the bounded closed-box winding regression all pass for `f9ec36f`.** This is a reproducibility and geometry regression check; it does not establish photographic fidelity or validate finished renders/video.

Verified on September 7, 2026, from exact local commit `f9ec36f70210d0cbcf308cc5a2dde7c8857b32bb`, tree `f02ba780007b5b9767ce008550062fd66aea8f98`. A `git archive --format=tar` snapshot contained 42 tracked files and was extracted into the separate workspace directory `work/fresh-scene-v05`. Neither a Blender master nor a GLB existed in that directory before generation. Uncommitted workspace files were not copied. The earlier failing `52eff10` verification is retained below as history.

## Commands and scope

The archive was created with `git archive --format=tar f9ec36f70210d0cbcf308cc5a2dde7c8857b32bb` and extracted with Python's `tarfile` data filter. The existing executable was the workspace's `work/tools/blender-4.2.9-linux-x64/blender` (Blender 4.2.9 LTS, build hash `a10f621e649a`). The commands used absolute executable and script paths. In these equivalent commands, `VERIFY_ROOT` is the absolute clean archive directory and `BLENDER_BIN` is the absolute Blender executable:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$BLENDER_BIN" \
  --background --threads 1 --python-exit-code 1 \
  --python "$VERIFY_ROOT/scripts/build_scene.py" -- --export

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$BLENDER_BIN" \
  --background "$VERIFY_ROOT/scene/protolabs-campus.blend" \
  --threads 1 --python-exit-code 1 \
  --python "$VERIFY_ROOT/scripts/check_geometry.py" \
  -- --root "$VERIFY_ROOT" --output "$VERIFY_ROOT/geometry-check.json"
```

Generation/export took **242.919 seconds**, returned exit code **0**, and emitted `SCENE_READY 2443`. The archived geometry checker returned exit code **0** in 2.689 seconds. A separate read-only Blender inventory/camera inspection returned exit code **0** in 1.734 seconds.

No render was requested. No lidar processing, image retrieval, browser build, film encoding or network access was needed. The main project's master, viewer and source branch were not changed by this isolated verification. Reopened inspection did not save or repair the generated master.

## Regenerated artifacts and baselines

| Artifact | Size | SHA256 |
| --- | ---: | --- |
| `scene/protolabs-campus.blend` | 34,561,752 bytes | `cd62b4155be34de1b7b71140f2915e801e78c0a73a665832edccfdb520635660` |
| `scene/protolabs-campus.glb` | 33,138,720 bytes | `942396ec967a29361b52e42ac168041a0aa241c9a5710f1371f4b0c3bfcf0ec2` |

The GLB header has magic `glTF`, version 2, and a declared byte length matching the actual file size. These checks establish generated, structurally readable artifacts. Binary hashes identify this particular run; byte-for-byte determinism across Blender environments is not claimed.

The regenerated `scene/cameras.json` parses identically to the committed baseline, with four cameras. Regenerated `scene/materials.json` also parses identically, with 21 material fallback entries. After reopening the master, `reference_aerial` matches `research/reference_drone_camera_fit.json` to floating-point storage precision:

- Maximum position difference: `1.0767117686327765e-06` metres.
- Maximum Euler XYZ difference: `3.041349061483345e-08` radians.
- Lens difference: `7.007226408006773e-07` mm; horizontal sensor width 36 mm.

## Read-only scene inspection

The master contains 2,443 objects. Its seven populated named collections are present: architecture (820 objects), roof structure (154), site (882), vegetation (355), details (220), context (8), and cameras (4). The default `Collection` is empty. Counts are inventory checks, not a measure of visual quality.

All 14 checked identity-bearing objects are present in the expected collections: `Main block occupied volume`, `Main roof aggregate`, `NE wing enclosed volume`, `NE aggregate flat roof`, `Measured canted ribbon roof`, `Roof leading edge`, `Fan brace`, `Recessed triangular clerestory`, `Vestibule interior`, `Measured rolling ground`, `Dark monument sign`, `Flagpole`, `US flag cloth`, and `Current fascia wordmark`.

## Closed-box winding regression

The checker executes only the actual archived source `cube` helper with a mesh recorder. Its 2 × 2 × 2 unit box has signed volume **+8 m³**, and all six normal-dot-outward-centroid values are **+4**. It also checks three known closed box meshes reopened from the regenerated master:

| Closed mesh | Signed local volume | Expected outward volume | Result |
| --- | ---: | ---: | --- |
| `Main block occupied volume` | +28,282.228624 m³ | +28,282.228624 m³ | Pass |
| `Long lower logo canopy` | +145.800006 m³ | +145.800006 m³ | Pass |
| `Dark monument sign` | +4.306500 m³ | +4.306500 m³ | Pass |

Every checked box has eight vertices, six faces, closed manifold edges, positive signed volume matching its expected box volume, and six outward-facing polygon normals. The checker neither changes normals nor recalculates arbitrary flat surfaces. Its scope is these representative boxes and the shared cube helper; it is not a full-scene topology audit.

Logs and structured receipts remain in `work/fresh-scene-v05`: `verification-source.json`, `verification-build.log/json`, `verification-artifacts.json`, `geometry-check.json/log`, `geometry-check-execution.json`, `verification-inspection.json`, `verification-inspect.log`, and `verification-inspect-execution.json`.

## Historical failure — 52eff10

An earlier isolated archive verified exact commit `52eff105a26fff1c385c09b7d52a1c484243a075`, tree `cb8ec08a0095abb69648a6e54542d6414f78520f`, in `work/fresh-scene-verification`. That 40-file archive generated and exported 2,443 objects in **145.148 seconds** with two Blender threads, exit code **0**, but **failed** geometry acceptance: the source helper's signed unit-box volume was **−8 m³** and all six face normals pointed inward. The same three actual scene boxes had signed volumes **−28,282.228624**, **−145.800006**, and **−4.306500 m³**. All were closed manifold meshes, illustrating why manifold status alone did not detect the orientation defect. The checker returned the expected exit code **1** against that archived master.

The earlier master was 34,561,752 bytes (SHA256 `eac5103f3d3bc5e38ccad740f76e1487ea476df9f535151fc159e3b4e69daea1`); its GLB was 33,167,388 bytes (SHA256 `f9e7ebbb39383e9a35bd808c0e21a434533432e8ede6773f39f0a8b2cd93be2d`). Camera and material baselines and the required inventory passed at that revision. The face-order correction committed in `f9ec36f` is covered by the new passing clean run above. The historical artifacts were not repaired in place.

That older run's first launch used relative `--python scripts/build_scene.py`; this bundled runtime resolved it against the outer workspace, reported the missing script, and still returned exit code 0. It generated no scene. Subsequent launches used the absolute script path and `--python-exit-code 1`, as shown above. Retain those options in automated verification.

**Not verified here:** photographic resemblance, finished still-image quality, full-resolution motion samples, complete flythrough frames, browser interaction or publication. Neither run claims photorealism or full site fidelity.
