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
- **Continuity concentration:** Check whether repository governance, review, and resumption procedures survive an unavailable maintainer; infer no personal circumstances.

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


## Evidence re-check: 2026-11-12 Eastern / 2026-11-13 UTC

The following is a **bounded verification**, not a full independent code audit. On 2026-11-12 ET the public GitHub metadata, current default-branch commit SHA, and the seven workflow run IDs cited in the portfolio were individually retrieved. Of the seven cited runs, **three** point to the current default branch head and **four** do not. This count says nothing about required-job completeness, security, live devices, release readiness, or third-party review.

| Flagship | Default HEAD observed | Cited workflow binding | Critical qualification |
| --- | --- | --- | --- |
| bank-it-operations-lab | e115cf089d9d | Same main SHA, run on Nov 4 | About eight days old; offline lab coverage is not governance acceptance |
| Grasshopper | 3fc518ae762d | Different SHA and docs/update-readme branch | Historical success cannot close multiprocess lost-update or external side-effect fencing |
| broccoli-core | b20d5fe04f18 | Different SHA and Parallax feature branch | APK build is not an installed/live Android acceptance test |
| helix | 8f687036344e | Same main SHA | Run is not KVM runtime evidence; live path was explicitly skipped |
| accubook | 1d45d8829457 | Different SHA and import feature branch | Imported Android build is not proof of current main or field usability |
| TCL-orc | b8becda20631 | Historical main SHA from Oct 24 | Neither consensus under partition nor vOS sandbox behavior is attested |
| civicpatch | cd94213ec270 | Same main SHA | Data validation does not establish jurisdiction completeness |

GitHub's repository open_issues_count metadata includes pull requests; values such as 89 for broccoli-core and 80 for Grasshopper are therefore **not** validated defect counts. Stars/forks cannot establish either presence or absence of independent audit. A missing GitHub-recognized license field is likewise not conclusive proof of missing licensing.

### Falsifiable inquiry matrix: every public portfolio entry

These are **tests to implement or demand**, not claims that defects exist. The evaluation targets all 21 catalogued public original repositories; private repositories and forked code are excluded from published analysis.

| Repository | Assumption to challenge / hidden variable | Required disconfirming evidence |
| --- | --- | --- |
| bank-it-operations-lab | A synthetic restore result generalizes to recovery under operational failure | Fresh SHA-bound restore with injected corruption, rollback evidence, and separate human governance acceptance |
| Grasshopper | SQLite or generation checks imply safe external retries | Multi-process fault tests plus idempotent external side-effect fencing, crash/restart trace and reviewer sign-off |
| broccoli-core | Green CI predicts safe no-root Android operation | Permission-denied, disconnected-Shizuku, API-level, latency, and real device acceptance matrix |
| helix | Static validation predicts a bootable KVM guest | Live KVM boot/shutdown/recovery log and explicit environment constraints |
| accubook | A compilable APK proves offline field workflows | Device install, contacts consent, transaction restore, invoice/PDF, attachment migration, accessibility and conflict tests |
| TCL-orc | Ledger simulation establishes trustworthy consensus | Partition, equivocation, replay, Sybil, resource exhaustion, deterministic WASM and non-custodial boundary tests |
| civicpatch | Valid input data implies accurate jurisdiction coverage | Source provenance, jurisdiction/date completeness, conflicts, expirations and adversarial records |
| broccoli-rish | Shell access implies stable Shizuku permission flow | Explicit consent and denied/revoked/disconnected rish tests without root fallback |
| systems-intake | Ingestion accepts realistic schema and ownership changes | Duplicate, partial, stale and malformed input replay with deterministic resumption |
| omnikali | Orchestration metadata reflects current code | Commit-pinned provenance, minimal privilege and bounded self-healing experiments |
| omn-kali-knowledge-graph-master | The knowledge graph accurately represents recent architectural state | Generated-at freshness plus per-source commit manifest and diff-based regeneration |
| kiln | Local build output is reproducible on a clean host | Cold clean-room build, dependency pinning, artifact hashes and license inventory |
| Androidd-cloud-computing-compainion | Host/device integration works beyond a developer setup | Cold-start, API/CPU compatibility, microphone/display permissions, disconnect and recovery validation |
| dectalk-live | Audio demos establish accessibility and reliability | Real screen reader, audio focus/latency, interruption and user-consent tests |
| onnxscibroccoli.github.io | A static portal is published and keyboard accessible | Real Pages URL, mobile keyboard/screen-reader audit and link/claim freshness proof |
| omnikali-link | Linked evidence remains available and authoritative | Broken/stale-link checker and per-link source SHA/provenance |
| half-a-mile | A prose project may be described as software assurance | Separate authorship/provenance checks and editorial accessibility; no engineering readiness inference |
| newsroom-desk | News aggregation implies dependable source attribution | Citation-to-source trace, corrected reports, dates, duplicates and false-content handling |
| lattice-audit | Backtesting provides investable predictive validity | Strict as-of-time feature availability, no look-ahead, costs/slippage, out-of-sample and live-paper divergence audit |
| shizuku-silent-mic | Permission tooling can safely modify mic state on all supported devices | Explicit user consent, Android policy compliance, indicator and denied-permission behavior |
| trash | Repository presence means an actively supported product | Determine purpose, provenance, safe publication and archive/maintenance classification |

### Engineering disposition and guardrails

1. **P0 — Evidence integrity:** Merge a read-only observer before changing any release label. Verify public catalog coverage, default HEAD versus cited run SHA/branch, bounded issue samples, current-HEAD run observations, and source-path existence. Missing API data is unknown, never a pass.
2. **P0 — Security / state correctness:** For Grasshopper, TCL-orc, rish and audio/microphone projects, demand explicit failure tests, permission-aware degradation and side-effect fencing before exposure to real users. A snapshot has no authority to waive these gates.
3. **P1 — Hardware / user acceptance:** Prioritize live physical Android acceptance for broccoli-core and accubook, true KVM execution for helix, and independent restore verification for bank-it-operations-lab.
4. **P1 — Knowledge provenance:** Build a generated-at and source-commit manifest for OmniKali, then update portfolio entries only from evidence at the exact claimed revision; historical links remain available and are labelled historical.
5. **P2 — Backlog and maintenance:** Separate PRs from issues, then sample issue age, severity and labels without misclassifying unreviewed items as defects. Encourage external review without treating popularity as a reliability metric.

Implementation companion: [public evidence probe](evidence_probe.py), [offline contract tests](test_evidence_probe.py), and the daily Actions workflow at [portfolio-critical-evidence.yml](../.github/workflows/portfolio-critical-evidence.yml). The workflow writes a reviewable artifact; it does not automatically promote the static portfolio or publish private information. See [README](README.md) for manual and CI execution.

**Caveat:** Actual production hardening, live device testing, independent review and knowledge-graph regeneration are still unverified here. Treat the results as a prioritized engineering program, not a completed acceptance campaign.


### Second-order CI challenge: multiple workflows at the same HEAD

The first live collection (2026-11-13 01:25 UTC, run 43344736845) demonstrated that even a valid, successful **cited** run does not guarantee that **other** workflows at that commit passed. The bounded recent-run snapshot found:

- bank-it-operations-lab: current-HEAD integration-gate **failed**, while offline-validation, acceptance, and documentation workflows succeeded.
- helix: current-HEAD agent-container-validation **failed**, while the cited validate workflow succeeded.
- TCL-orc: current-HEAD Docs-as-Code Quality Gates **failed**, while CI and physical-notes succeeded.
- broccoli-core: a current-HEAD CI run was **queued** when the sample was captured.

These are observed workflow outcomes, **not** conclusions about the severity of the code underneath; some runs can be optional or have subsequent reruns. They establish why a one-run green badge is not a project-wide verdict. The observer now retains the most recent run per workflow identity in its bounded window, explicitly surfaces failures/cancellations/pending results, and makes the opt-in strict promotion check fail closed on such flagship exceptions. The collector remains non-promotional and does not auto-edit published readiness labels.
