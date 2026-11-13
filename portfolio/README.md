# Engineering portfolio (draft)

The public site is intended to serve **`/portfolio/`** after this PR is reviewed and merged into the branch from which GitHub Pages is published. The existing homepage, investigative pages, and other site assets are unchanged.

## Purpose

Provide an accessible, **evidence-scoped** entry point to original engineering work. Source links and workflow run IDs bind claims to concrete source or executed CI; descriptive text is not an independent verification. The public-facing cards intentionally do not include private projects. The public catalog in `projects.json` lists **21 public original repositories**. The other **8 original repositories are private**; their names, URLs, and code are intentionally excluded. The original 17 forks are also excluded from claims of authorship.

## Local check

```sh
python3 portfolio/check.py
```

This checks HTML landmarks, skip navigation, fragment links, no JavaScript dependencies, the public catalog's 21 distinct entries and the eight-private-repository metadata count, seven public flagship source and CI links, and verification boundaries. It is **not** a browser/assistive-technology audit, and does not fetch remote links. Manual keyboard/screen-reader and narrow-viewport tests remain outstanding.

## Critical evaluation

See [CRITICAL_EVALUATION.md](CRITICAL_EVALUATION.md) for a deeper inquiry that challenges assumptions, identifies information gaps and hidden variables, and recommends concrete next steps. A companion script `critical_analysis.py` can generate a static snapshot report.

## Reference

- [Campaign ledger](https://github.com/onnxscibroccoli/broccoli-core/issues/102) — ordered cross-repository work and resumption protocol.
- [Project registry](projects.json) — explicitly scoped capabilities.
- [Portal](index.html) — semantic static HTML and evidence-linked case studies.
- [Critical evaluation](CRITICAL_EVALUATION.md) — assumption challenges and gap analysis.

## Reviewer checkpoints

- [ ] Confirm GitHub Pages is publishing the intended branch and `/portfolio/` renders correctly on the public domain.
- [ ] Test keyboard navigation, screen reader labeling and color contrast using actual browsers and assistive technology.
- [ ] Re-check source and workflow URLs before any readiness claims.
- [ ] Verify all linked CI runs apply to the exact described source branch, not to an unrelated default-branch state.
- [ ] Keep private project contents and personal employment history out of the published site.

**Operational limit:** This PR creates reviewable source, not a completed site publication or verified release.

## Living critical-inquiry evidence

CRITICAL_EVALUATION.md now records **falsifiable experiments for all 21 public portfolio repositories**, not inferred readiness or personal details. The new **evidence_probe.py** is a dependency-free, read-only public GitHub observer. It checks catalog drift against public originals (forks excluded), repository default HEAD, historical workflow SHA/branch/date bindings, current-HEAD workflow observations, source anchor existence and **bounded** issue triage samples. It does not enumerate authenticated private repositories.

### Local, reproducible validation

Run from the repository root in Termux, Linux, or a GitHub Actions runner:

    python3 portfolio/check.py
    python3 portfolio/critical_analysis.py
    python3 -m unittest discover -s portfolio -p 'test_evidence_probe.py' -v
    python3 portfolio/evidence_probe.py

Optional live audit (requires a read-only-access GitHub token; never commit or print the token):

    GH_TOKEN="$(gh auth token)" python3 portfolio/evidence_probe.py --online \
      --max-age-days 7 --fail-on-incomplete-collection

A deliberately stronger promotion gate, which **fails** if a cited flagship workflow does not attest to a fresh default HEAD, is:

    GH_TOKEN="$(gh auth token)" python3 portfolio/evidence_probe.py --online \
      --strict --max-age-days 7

The live observer writes `portfolio/evidence-output/evidence.json` and `EVIDENCE_REPORT.md`; generated outputs are for inspection, not automatic publication. The separate workflow `.github/workflows/portfolio-critical-evidence.yml` runs offline tests on pull requests and collects a **daily public evidence artifact** after merge to the default branch. A successful collection run means the observer gathered data; it never certifies a release. Historical/stale links remain explicitly historical and do not turn green just because another workflow ran successfully.

Important measurement limits: GitHub's `open_issues_count` includes pull requests; the oldest open issue and triage labels are sampled rather than exhaustively classified; stars/forks are not independent technical review. HTTP failures, mismatched source anchors, new uncatalogued public originals, and missing default-head SHA are reported as unknown or drift. The observer is read-only, and no private names or credentials enter its artifact.
