# Protolabs • Maple Plain campus reconstruction

An evidence-led, editable Blender reconstruction of Protolabs headquarters at **5540 Pioneer Creek Drive, Maple Plain, Minnesota**. Research acquired 2026-09-07. This is a reconstruction under development, not a surveyed digital twin. Capture dates and uncertain geometry remain explicit.

## Workflow

1. Acquire the documented public references (`research/`).
2. Generate the master using Blender 4.2 LTS and `scripts/build_scene.py`.
3. Render fixed cameras, inspect side-by-side reference comparisons, correct the largest discrepancies.
4. Export glTF for the exterior viewer; render a delivery-resolution motion sample before the cinematic.

Generated `.blend`, glTF, renders and video are intentionally excluded from Git. They can be regenerated from source, and distributed in versioned deliverable archives with SHA-256 manifests. Do not commit proprietary reference photography; keep attribution in the reference ledger and fetch locally.

See `docs/brief.md`, `docs/backlog.md`, and `research/` for scope and fidelity status. Setup and rendering instructions will be completed alongside the working pipeline.
