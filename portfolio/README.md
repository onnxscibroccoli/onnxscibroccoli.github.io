# Engineering portfolio (draft)

The public site is intended to serve **`/portfolio/`** after this PR is reviewed and merged into the branch from which GitHub Pages is published. The existing homepage, investigative pages, and other site assets are unchanged.

## Purpose

Provide an accessible, **evidence-scoped** entry point to original engineering work. Source links and workflow run IDs bind claims to concrete source or executed CI; descriptive text is not an independent verification. The public-facing cards intentionally do not include private projects. The full 29-repository campaign registry lives in `projects.json`, while the original 17 forks are excluded from claims of authorship.

## Local check

```sh
python3 portfolio/check.py
```

This checks HTML landmarks, skip navigation, fragment links, no JavaScript dependencies, the catalog's 29 distinct entries, seven public flagship source and CI links, and verification boundaries. It is **not** a browser/assistive-technology audit, and does not fetch remote links. Manual keyboard/screen-reader and narrow-viewport tests remain outstanding.

## Reference

- [Campaign ledger](https://github.com/onnxscibroccoli/broccoli-core/issues/102) — ordered cross-repository work and resumption protocol.
- [Project registry](projects.json) — explicitly scoped capabilities.
- [Portal](index.html) — semantic static HTML and evidence-linked case studies.

## Reviewer checkpoints

- [ ] Confirm GitHub Pages is publishing the intended branch and `/portfolio/` renders correctly on the public domain.
- [ ] Test keyboard navigation, screen reader labeling and color contrast using actual browsers and assistive technology.
- [ ] Re-check source and workflow URLs before any readiness claims.
- [ ] Verify all linked CI runs apply to the exact described source branch, not to an unrelated default-branch state.
- [ ] Keep private project contents and personal employment history out of the published site.

**Operational limit:** This PR creates reviewable source, not a completed site publication or verified release.