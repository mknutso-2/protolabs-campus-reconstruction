# Version 0.1 delivery verification

The v07c research reconstruction includes the private GitHub source and reproduction workflow, an editable Blender master and animated scene, an interactive exterior walkthrough available locally and through the subsequent public deployment, four inspected stills, the accepted six-second film, and an attributed comparison gallery with six preserved earlier iterations. The [accuracy account](accuracy-summary.md) records remaining approximations; this release does not claim photorealism, surveyed accuracy or complete current-day coverage.

## Verified production inputs

The [clean static build](fresh-checkout-v07c.md) started from source `e29ad4b9` and pinned derived evidence, the bundled font and 11 verified material/HDRI files. It generated master `3d861d6c…`, both exports and the four 1600 × 1067 / 64-sample images. Later generator/asset/input source remained unchanged. The gentler motion path came from `69a7594`; the sample and endpoints passed before the complete film was rendered.

The [full-film acceptance](../research/v07c-cinematic-review.json) was recorded at 01:55:53 UTC on 8 September 2026. All 144 frames were verified, native crop sequences and reuse joins inspected, and the actual 1280 × 720 / 24 fps / six-second MP4 played normally and in fullscreen. Both MP4s fully decoded with continuous timestamps. The motion scene reopened in background Blender 4.2.9 with its animated camera and complete frame range. Blender's graphical editor was not tested.

The [local viewer receipt](../research/v07c-final-viewer-review.json) binds all 12 runtime assets, the final build and the actual film panel. The unchanged app/model also passed all four saved views, walk/reset, fullscreen entry/exit, three reference pairs and four full-size image loads. Browser shading, reduced vegetation and shallow-angle aliasing remain different from Cycles. The gallery's 58 local links/assets and current/history image hashes were checked; reference caches matched their pinned provenance.

## Extracted delivery check

The actual **0.1.0-rc1** archive was extracted into a fresh directory and verified independently: **202 files**, exact archive membership, every SHA-256 and byte size, matching source/history bundle, all 12 runtime payload files, original copies, still-to-JPEG source bindings and accepted movie/master/review bindings. Candidate source was `4c3dc5b2a538c9bdf8dfb794836964c56b50c2f9`; its 205,330,353-byte ZIP hash is `e80c38d5fdf9417288906d860008f63bedf7e8eae2f5a577ea20b5046ff337dc`. [The portable release check](../research/v07c-release-verification.json) records the exact scope.

Inside that extracted viewer, a fresh `npm ci --offline --no-audit --no-fund` installed 746 locked packages from the existing host cache, followed by a successful `npm run build` and two prerendered routes. An initial sandbox child-process restriction was resolved by the authorized host retry; it was not an archive defect. All 202 original files, including every runtime payload, remained unchanged after the build. This was an actual extracted production build, not a synthetic packaging fixture. The earlier local UI inspection applies to the byte-identical source and assets; no separate UI playback test is claimed for the extracted copy.

The final `protolabs-campus-0.1.0.zip` was generated from frozen source `aff1401b3406423c897d0f0117b9be67ee559ec4` using the same production assets and packaging code. Its 204 files passed exact membership, SHA-256 and byte-size verification, and all 34 required production artifacts match the tested candidate. The ZIP is 205,343,442 bytes, SHA-256 `5655eecc0d76f81929dcda9e02f21fcc02981aff006157b938d343b3543f0ef0`. It remains unchanged after public publication. `DELIVERY-MANIFEST.json` inside it identifies the exact source revision and every included file's size and SHA-256. The adjacent `.json` and `.sha256` identify the complete ZIP. These receipts are written after packaging and readback; they are the authoritative final archive identifiers rather than a self-referential source document.

The archive includes source and its Git history bundle, both native scenes, both full/raw browser exports, the optimized viewer payload, final stills and film, accepted sample, comparison assets, references, licensed material inputs and reproduction records. Full frame PNG sequences, raw LAZ tiles, Blender/FFmpeg executables and installed npm dependencies are excluded. Render/research scripts document their recreation or acquisition. Cached dependency installation does not promise offline setup without a populated cache.

## Open the delivered copy

Extract the ZIP, open `protolabs-campus/scene/protolabs-campus.blend` in a compatible Blender installation, or open `deliverables/comparison/index.html` for the reference and iteration gallery. The still PNGs are in `deliverables/stills/`; the completed movie is `deliverables/flythrough.mp4` and its editable motion scene is `scene/protolabs-motion.blend`.

For the exterior walkthrough, enter the extracted `protolabs-campus/viewer/` directory and run `npm ci`, `npm run build`, then `npm start`. All model, image and movie payload files are included; repackaging or rerendering is unnecessary. The [reproduction guide](reproduction.md) covers a source-only checkout.

## Hosting and remaining work

The [public walkthrough](https://protolabs-campus-mknutso.mknutso2.chatgpt.site) was deployed on September 8, 2026 after the user explicitly authorized public Sites publication. The exact version and public verification are recorded in [site publication](site-publication.md). The source repository remains private. Two viewer links now open the public accuracy page instead of private GitHub; the inspected model, images and film are unchanged.

At the original 0.1.0 archive checkpoint (02:20 UTC on September 8), delivery was local and external hosting approval was pending after automatic approval review rejected the upload. That historical checkpoint remains in the immutable archive and its receipts. The later public authorization and deployment supersede the pending hosting status in current documentation; they do not rewrite the archive or its review evidence.

UE5 requirements were evaluated against the GTX 660M / 8 GB host; a UE5 application and complete raw-lidar reacquisition are optional follow-up work. Current source builds use the committed, attributed derived evidence. GPU rendering is inactive on this Ubuntu installation, and no driver changes or performance claims are included. Remaining visual improvements continue in GitHub issues #2 and #3.
