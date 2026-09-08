# Fresh source checkout verification — 1f8b4b9

**Result: clean generation and both GLB exports pass; the reopened master retains complete foliage, all 102 canopy placements match their ground and height constraints, and the corrected geometry checker passes.** The original checker's 1 mm rounding-boundary failure and the subsequent tolerance correction are recorded below. This check does not establish photographic fidelity or finished-video quality.

Verified on September 7, 2026, from exact commit `1f8b4b95d377e30ea9ac1c49cb656b060af5b1cc`, tree `4fab9f4a4298fb7dc533337ffaec61541fc50310`. A clean `git archive --format=tar` snapshot of 68 tracked files was extracted with Python's `tarfile` data filter into `work/fresh-scene-v06`. The archive SHA256 is `210cf7dca28df3a4dcb41047b96394061aa2dc7c92da38d3dda5cb30d8b4d2c2`. No existing scene binaries or uncommitted files were copied.

## Current run and artifacts

The Blender 4.2.9 LTS executable, build `a10f621e649a`, was invoked with an absolute script path, `--background --threads 1 --python-exit-code 1`, and `-- --export`. `OMP_NUM_THREADS=1` and `OPENBLAS_NUM_THREADS=1` bounded auxiliary thread use. This is the same command pattern shown in the retained previous verification below, with `VERIFY_ROOT` pointing to `work/fresh-scene-v06`.

Generation and both exports completed in **226.347 seconds**, exit code **0**, and emitted `SCENE_READY 2303`. No render, browser build, Sites action, dependency installation, lidar reprocessing, reference download or network access was performed. The generated master was then reopened read-only for checks and was not resaved or repaired.

| Regenerated artifact | Size | SHA256 |
| --- | ---: | --- |
| `scene/protolabs-campus.blend` | 34,647,664 bytes | `9f568c491a9058421930177f43a1a2c86c9dfd631dd3040601edb59d33da2f51` |
| `scene/protolabs-campus.glb` | 33,423,040 bytes | `8729cc49119d6428af9fd3f1b16ec2d55ff805bbce2efe274985bee433fba4c2` |
| `scene/protolabs-campus-viewer.glb` | 30,940,416 bytes | `4c981dc4138a232a8571fc26287c6e436842bb5bd681b8ba10e55fc32f5783e3` |

Both GLBs have valid `glTF` magic, version 2, matching declared and actual byte lengths, and parseable JSON chunks. Each has 1,972 meshes and 2,290 nodes. These are the uncompressed exports; a later meshopt packaging step is outside this verification. Binary hashes identify this run, not a promise of byte-for-byte determinism across Blender environments.

The regenerated four-camera `scene/cameras.json` and 21-entry `scene/materials.json` parse identically to their committed baselines. The reopened reference camera retains its fitted position, orientation and 25.872181 mm lens to Blender floating-point storage precision. Exposure is −0.850000024. All 15 identity-bearing checked objects are present, including the new `North context ground | lidar` mesh. The seven populated collections contain architecture 820, roof structure 154, site 883, vegetation 214, details 220, context 8, and cameras 4 objects; the default collection is empty.

## Canopy and retained master foliage

The reopened master contains exactly **102** `North canopy envelope …` objects with IDs matching the 102 eligible research rows. The maximum error across measured bottoms, heights, and tops calculated as `ground_z + canopy_height` is **0.000001534 m**. No omitted research candidate was instantiated.

The three full source tree meshes each retain **8,000 individual leaves and 18,212 triangles**. No mesh named `browser foliage` is saved in the reopened master. Its visible vegetation triangle count remains **3,328,852**, matching the exporter metadata's before count; the temporary browser export records **1,276,636** triangles after foliage reduction. `scene/viewer-export.json` records a master SHA256 matching the generated master, and that hash remains unchanged after read-only inspection. These checks show that the browser foliage reduction did not leak into the saved editable master.

The distant surround's highest vertex is at z=−12.453000069 m, below the lowest measured terrain vertex at z=−12.031000137 m, providing about 0.422 m clearance. The source cube winding regression and all three representative closed scene boxes pass, with the same outward signed volumes as the previous corrected run.

## Archived checker rounding failure

The exact archived `scripts/check_geometry.py` returned exit code **1** in **4.467 seconds** because it compares actual canopy tops to the independently rounded `top_z` field using a strict 0.001 m threshold. Nine rows exceed this by floating-point storage precision. For example, candidate 015 has `ground_z=-11.467` and `canopy_height=14.248`, which imply top z=2.781 m, while its independently rounded source `top_z` is 2.782 m. Its reopened top is 2.780999184 m. The largest such difference is **0.001000816 m**.

This failure concerns the redundant field's independent millimetre rounding and the comparison threshold. The independent read-only inspection compares the geometry to the actual construction inputs, checks the redundant top with a 1.5 mm tolerance, and passes in **4.731 seconds**, exit code **0**. No scene or source file was changed to obtain that result. The archived checker remains unchanged in the verification archive, and its original failure receipt is preserved.

The root project's checker correction in exact commit `6208e82ced0b9358bca75d0e9a26917dc265b47f` increases the redundant `top_z` comparison tolerance to **0.0016 m (1.6 mm)**: 1.5 mm for independent three-decimal rounding, plus a small allowance for Blender floating-point storage. The corrected checker, SHA256 `336019b35c0c752d1dd4413f1878075be45b450fedd93382e14d7d1369555588`, was run against this same unmodified clean master and the archived source cube helper. It **passed in 8.130 seconds, exit code 0**. The generator, vegetation, vehicle and export helpers were verified byte-identical to the fresh archive. The only committed changes from `1f8b4b9` through `7a656db64c9e0a15b0c377502872d50dba9306ea` were this checker correction and the viewer page, so another full scene generation was unnecessary. This corrected run is a check of the `1f8b4b9` clean master with the `6208e82` checker, not a claim that the original archived checker passed.

Structured receipts and logs are retained in `work/fresh-scene-v06`: `verification-source.json`, `verification-build.log/json`, `verification-artifacts.json`, `geometry-check.json/log`, `geometry-check-execution.json`, `geometry-check-corrected.json/log`, `geometry-check-corrected-execution.json`, `verification-inspection.json`, `verification-inspect.log`, and `verification-inspect-execution.json`. The earlier passing and failing verifications remain below.

---

## Historical passing check — f9ec36f

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
