# Critical Evaluation of Portfolio Repositories

**Date:** 2026-11-13
**Scope:** Public original repositories targeted in the engineering portfolio (`onnxscibroccoli.github.io/portfolio/`), with particular focus on the seven flagship projects.
**Method:** Source inspection of READMEs, knowledge graph, portfolio catalog (`projects.json`), index presentation, recent commits, open issue counts, and documented boundaries. No live runtime re-verification performed in this pass.

This document shifts from the portfolio's already-careful evidence-scoped presentation to explicit critical inquiry. It challenges assumptions, surfaces information gaps and hidden variables, and outlines implementable next steps. It is itself subject to the same scrutiny: claims here are based on public source and metadata available at the time of writing; they are not independent audits.

## Challenged Assumptions

1. **Evidence links remain current and representative.**
   - Portfolio cards bind to specific workflow run IDs and source paths. These are frozen at generation time (catalog dated 2026-11-11). Subsequent commits (e.g., Grasshopper concurrency work on 2026-11-04) may diverge from the linked runs. A green historical run does not attest to the current default branch.
   - **Challenge:** Treat linked runs as historical snapshots, not living proof. Require fresh confirmation before any readiness narrative.

2. **The OmniKali knowledge graph is a current authoritative map.**
   - Canonical snapshot is dated 2026-09-28. Multiple repositories have been updated since (Grasshopper, broccoli-core, systems-intake, etc.). The graph itself warns agents to update it after material changes.
   - **Challenge:** An outdated graph becomes a source of incorrect architectural assumptions. Freshness is an unstated dependency.

3. **Open issue volume signals healthy activity rather than accumulated debt.**
   - broccoli-core: ~89 open issues. Grasshopper: ~80. These numbers are public metadata. Without triage metadata, they can equally indicate unresolved defects, feature backlog, or documentation debt.
   - **Challenge:** Issue count alone is not a quality signal. Hidden variable is the age, severity, and owner distribution of open items.

4. **Zero external stars/forks and single-author history are irrelevant to evaluation.**
   - All inspected public repositories show 0 stars and 0 forks. Authorship is concentrated. For a public portfolio aimed at inspectability, the absence of external review is a measurable gap in independent validation.
   - **Challenge:** Personal or experimental status is fine; claiming broader robustness without external signals requires stronger internal evidence.

5. **Documented "not claimed" boundaries are sufficient to prevent over-interpretation.**
   - The portfolio and READMEs are unusually disciplined about evidence limits (HELIX_SKIP_LIVE, concurrency defects, historical vs production). This is a strength. The residual risk is that secondary surfaces (issue titles, commit messages, knowledge-graph prose) can still be read as stronger than the explicit limits.
   - **Challenge:** Consistency of language across all artifacts matters more than a single disclaimer.

6. **Private repository exclusion is complete and accurate.**
   - Catalog correctly withholds 8 private originals and excludes 17 forks. Spot-check of authenticated listing aligns with the stated 21+8=29 original count. Residual risk is future private creation without catalog update.

## Information Gaps

- Current (not historical) CI status on default branches for each flagship.
- Age and severity distribution of open issues; presence or absence of triage labels.
- Automated dependency and vulnerability scanning results (Dependabot, CodeQL, etc.).
- Freshness metric for the knowledge graph and portfolio catalog.
- Independent or external review evidence beyond self-authored tests.
- Live device or cloud acceptance evidence more recent than the dated proofs cited in READMEs.
- Quantitative performance, reliability, or recovery metrics for the control-plane and desktop components.
- License and third-party code provenance completeness across the historical broccoli-core mirror.

## Hidden Variables

- **Concurrency and storage safety in Grasshopper:** Explicitly documented lost-update defect on the default JSON store; opt-in SQLite and generation fencing are under test but external side-effect fencing remains unproven. A green test suite does not close this gap.
- **Historical volume in broccoli-core:** ~5,900 tree entries, large mirrors, and explicit warnings about credential-like paths. Extraction and provenance rules exist, but the size itself is a hidden operational risk for agents and reviewers.
- **Knowledge-graph staleness:** Dated snapshot vs. subsequent architecture work creates a latent inconsistency hazard for any agent following the graph rule.
- **Portfolio publication state:** The portfolio directory is presented as a draft pending review and Pages configuration. The public site root remains the Half a Mile essay.
- **Single-maintainer consistency:** Development velocity is high, but the personal context of the maintainer (documented elsewhere) implies variable availability; no automated health or resumption protocol is visible in the portfolio itself beyond the linked campaign issue.

## Recommended Solutions (Implementable)

1. **Living critical evaluation artifact.**
   - This file. Update it on a cadence or after material changes. Link it from `portfolio/README.md` and the portal.

2. **Evidence freshness gate.**
   - Extend `portfolio/check.py` (or a companion script) to optionally record the date of linked workflow runs and flag those older than a threshold. Fail closed on catalog generation if freshness cannot be established.

3. **Knowledge-graph freshness marker.**
   - Add a machine-readable `generated_at` and `source_commits` field to the graph. Require an update step in the agent instructions already present in READMEs.

4. **Issue health summary.**
   - Add optional `open_issues`, `oldest_issue_age_days`, and `has_triage_labels` fields to `projects.json` for flagships. Populate from API at catalog generation time. Surface as a non-claiming metric in the portal.

5. **Concurrency and defect visibility.**
   - Keep the existing "Not claimed" language. Add a permanent link from the Grasshopper card to the concurrency baseline document. Do not promote the SQLite path until external fencing is demonstrated.

6. **External signal tracking (optional).**
   - Periodically record stars/forks/watchers. Treat sustained zeros as a prompt for documentation or onboarding improvements, not as a failure.

7. **Publication clarity.**
   - Complete the Pages review checklist already listed in `portfolio/README.md` before treating `/portfolio/` as the canonical public engineering entry point.

## Validation of This Evaluation

- Source: direct retrieval of READMEs, `projects.json`, portfolio `index.html`, knowledge graph, and selected recent commits.
- No runtime tests were re-executed.
- No private repository contents were inspected.
- All quantitative claims (issue counts, dates) are approximate from the tools available at evaluation time and should be re-verified.

## Next Steps

- Merge or publish the portfolio directory if the review checklist is satisfied.
- Implement the freshness extension to `check.py`.
- Schedule a knowledge-graph refresh across affected repositories.
- Triage a representative sample of open issues in broccoli-core and Grasshopper to quantify the debt vs. feature mix.

This evaluation is an input to engineering judgment, not a substitute for it. Preserve the existing fail-closed and provenance discipline; the goal is deeper robustness, not broader claims.
