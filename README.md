# onnxscibroccoli.github.io

**Status:** Public static publishing hub  
**Repository:** `onnxscibroccoli/onnxscibroccoli.github.io`  
**Documentation snapshot:** 2026-09-28 23:12 EDT

This repository is the account's GitHub Pages publication hub. It contains static output for several projects rather than one conventional application.

## Published areas

Approximately 31 tracked files are present, including:

- root publication pages and shared CSS;
- `desk/` — Newsroom Desk static publication;
- `desk/story/` — published investigations;
- `desk/record/` — reporting record;
- `law/` and `sources/` — Half a Mile supporting pages;
- `omnikali/` — OmniKali public door and discovery/security pages;
- shared images and favicons.

## Development cycle

**PUBLISHED / ACTIVE DEPLOYMENT SURFACE.**

Recent commits have refreshed public OmniKali status material and the published static sites.

This repository is generally a deployment/publication artifact, not the authoritative application source.

## Local inspection

```bash
git clone https://github.com/onnxscibroccoli/onnxscibroccoli.github.io.git
cd onnxscibroccoli.github.io
python -m http.server 8000
```

Open the required path in a browser.

## AI model instructions

Before editing a page, identify its source repository.

- Newsroom Desk source: `newsroom-desk`.
- Half a Mile source: `half-a-mile`.
- OmniKali workstation implementation: current workstation/control-plane repositories.
- OmniKali public door: `omnikali`.

Do not treat generated HTML as the architectural source of truth. Change the source project first, then regenerate/publish the Pages material when appropriate.

**Bottom line:** this is the public edge/publication layer for several projects.
