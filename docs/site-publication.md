# Public site publication — September 8, 2026

The [Protolabs campus walkthrough](https://protolabs-campus-mknutso.mknutso2.chatgpt.site) was published with the user's explicit authorization for public Sites access. Its [accuracy and sources page](https://protolabs-campus-mknutso.mknutso2.chatgpt.site/accuracy.html) is also public. The GitHub repository remains private.

## Deployed version

| Record | Value |
| --- | --- |
| Successful deployment | `2026-09-08T03:20:18.446851+00:00` |
| Public access | Revision 2, set `2026-09-08T03:14:26.146990+00:00` |
| Site | `appgprj_6a9eeb81b61c8191b86c2fc4a289787a` |
| Saved version | 1: `appgprj_6a9eeb81b61c8191b86c2fc4a289787a~appgver_239b44d013248191a71f7fd7376f1d48` |
| Deployment | `appgdep_6a9f7e8eabe4819193d0ea3c25c03963` |
| Pushed standalone Site source | `f39ba1919e06027aee2b77c45257b46dca987718` |
| Local upload archive | 22,471,840 bytes; SHA-256 `f28aa42ec0a0c6e53fea50fbce8c1a4ea555e9d0b711fbab501c5f16203a8f38` |
| Backend normalized archive | 31,641,600 bytes; SHA-256 `50a2e9937d556863775abc74ec82bd81c67b164d9752ac05e6c48b7e14c4bbef` |

Both hosting archives contain the same 34 verified files. The production build passed, and all 12 model/data/image/movie payload files remain byte-identical to the inspected v07c local delivery. The publication changes replace two private GitHub links with `/accuracy.html` and add that public evidence page; scene geometry, materials, model exports, stills and movie are unchanged.

## Verification scope

Sites reported successful deployment, and a subsequent service readback confirmed public access, active status, latest version 1 and the exact live URL above. At `2026-09-08T03:23:08.217093+00:00`, 14 unauthenticated GET requests passed: the root page, accuracy page and all 12 runtime assets. The requests used no Authorization header, cookie jar, signed-in session or bypass token. Every runtime asset matched its expected byte count and SHA-256.

The accuracy route redirects from `/accuracy.html` to `/accuracy`. The provider appends a 938-character Cloudflare challenge script to its HTML; after removing that specifically verified appended content, the served accuracy source matched the original SHA-256. The earlier strict HTML comparison failure is retained separately and was attributable to this transformation, not changed project content.

The deployed page was opened in the existing browser tab, and its accessibility snapshot showed the Motion panel, all four section tabs and accuracy links. This publication checkpoint does not claim a fresh complete live-site interaction or performance pass; the earlier bounded local checks remain recorded in [viewer verification](viewer-verification.md).

Workspace evidence is `work/site-public-v1-archive-validation.json` and `work/site-public-v1-anonymous-verification.json`. Its source/build identity is separate from the private reconstruction repository's connector-mirrored commit identity.

## Preserved local release and limits

The immutable local `protolabs-campus-0.1.0.zip` remains 205,343,442 bytes, SHA-256 `5655eecc0d76f81929dcda9e02f21fcc02981aff006157b938d343b3543f0ef0`, from source `aff1401b3406423c897d0f0117b9be67ee559ec4`. Its 204-file verification and extracted candidate build are documented in [delivery verification](delivery-verification.md). The original archive recorded local delivery with hosting pending; the later public authorization and deployment supersede that status only for the current project. No scene/movie regeneration or replacement archive was performed.

Publication does not change the [accuracy limits](accuracy-summary.md), the browser's mean-color materials and distant canopy proxies, shallow-angle aliasing, or the bounded nature of the existing interaction/performance checks. Reference photographs retain their source attribution; public availability is not represented as a general redistribution license. Remaining visual-fidelity work stays open in GitHub issues #2 and #3.
