#!/usr/bin/env python3
"""Read-only, fail-closed portfolio evidence audit (stdlib only).

No local secrets or private repositories are enumerated. A GitHub token is required
for live checks; the token is never written to reports. A successful workflow run
attests only to that workflow, not to an entire repository or a production release.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
OWNER = "onnxscibroccoli"
API = "https://api.github.com"
TRIAGE = re.compile(r"(^|[-_ /:])(bug|security|priority|severity|p[0-3]|critical|high|blocked|type)([-_ /:]|$)", re.I)


def utc(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def age_days(value: str | None, now: datetime) -> int | None:
    parsed = utc(value)
    return max(0, int((now - parsed).total_seconds() // 86400)) if parsed else None


class APIError(Exception):
    pass


class GitHub:
    def __init__(self, token: str, retries: int = 2):
        if not token:
            raise ValueError("GH_TOKEN or GITHUB_TOKEN is required for online audit")
        self.token, self.retries = token, retries

    def get(self, path: str):
        if not path.startswith("/") or "//" in path:
            raise APIError("invalid API path")
        request = Request(API + path, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "portfolio-readonly-evidence-probe",
        })
        for attempt in range(self.retries + 1):
            try:
                with urlopen(request, timeout=15) as response:
                    return json.load(response)
            except HTTPError as exc:
                if exc.code in (429, 500, 502, 503, 504) and attempt < self.retries:
                    time.sleep(min(2 ** attempt, 4))
                    continue
                raise APIError(f"GitHub API HTTP {exc.code} for {path.split('?')[0]}") from None
            except (URLError, TimeoutError, json.JSONDecodeError) as exc:
                if attempt < self.retries:
                    time.sleep(min(2 ** attempt, 4))
                    continue
                raise APIError(f"GitHub API request failed for {path.split('?')[0]} ({type(exc).__name__})") from None
        raise APIError("request retry exhausted")


def validate_catalog(catalog: dict) -> list[dict]:
    if catalog.get("schema_version") != 1 or not isinstance(catalog.get("projects"), list):
        raise ValueError("unsupported or missing portfolio catalog")
    projects = catalog["projects"]
    names: set[str] = set()
    if not projects:
        raise ValueError("empty portfolio catalog")
    for project in projects:
        name = project.get("name", "")
        if (not re.fullmatch(r"[A-Za-z0-9_.-]+", name) or name in names or
                project.get("visibility") != "public" or
                project.get("url") != f"https://github.com/{OWNER}/{name}"):
            raise ValueError("catalog has duplicate, non-public or invalid repository entry")
        names.add(name)
    return projects


def public_originals(api) -> list[str]:
    """Enumerate public originals only; forked and private repos never enter results."""
    originals: list[str] = []
    for page in range(1, 11):
        batch = api.get(f"/users/{OWNER}/repos?type=owner&sort=full_name&per_page=100&page={page}")
        if not isinstance(batch, list):
            raise APIError("public repository enumeration was not a list")
        for repo in batch:
            if repo.get("owner", {}).get("login", "").lower() != OWNER.lower():
                raise APIError("unexpected owner in public repository enumeration")
            if not repo.get("fork") and not repo.get("private"):
                originals.append(repo["name"])
        if len(batch) < 100:
            return sorted(set(originals), key=str.lower)
    raise APIError("public repository pagination exceeded cap; cannot verify coverage")


def issue_sample(items: list, now: datetime) -> dict:
    """The issues endpoint includes PRs; never misrepresent its count as issue count."""
    issues = [item for item in items if "pull_request" not in item]
    labeled = sum(any(TRIAGE.search(label.get("name", "")) for label in item.get("labels", [])) for item in issues)
    ages = [age_days(item.get("created_at"), now) for item in issues]
    ages = [age for age in ages if age is not None]
    return {"open_items_sampled": len(items), "issues_in_sample": len(issues),
            "triage_labeled_in_sample": labeled,
            "oldest_issue_in_sample_days": max(ages) if ages else None,
            "sample_is_exhaustive": len(items) < 30}


def linked_workflow(api, p: dict, branch: str, sha: str, now: datetime, max_age: int) -> dict:
    href = p.get("workflow")
    if not href:
        return {"state": "not_cited"}
    prefix = f"https://github.com/{OWNER}/{p['name']}/actions/runs/"
    if not href.startswith(prefix) or not href[len(prefix):].isdigit():
        return {"state": "invalid_catalog_link"}
    run = api.get(f"/repos/{OWNER}/{quote(p['name'])}/actions/runs/{href[len(prefix):]}")
    days = age_days(run.get("created_at"), now)
    state = "historical"
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        state = "not_successful"
    elif run.get("head_sha") == sha and run.get("head_branch") == branch:
        state = "head_bound" if days is not None and days <= max_age else "aged_head_bound"
    return {"state": state, "url": href, "event": run.get("event"),
            "head_branch": run.get("head_branch"), "head_sha": run.get("head_sha"),
            "conclusion": run.get("conclusion"), "status": run.get("status"), "age_days": days}


def source_anchor(api, p: dict) -> str:
    href = p.get("source")
    if not href:
        return "not_cited"
    prefix = f"https://github.com/{OWNER}/{p['name']}/blob/main/"
    if not href.startswith(prefix) or not href[len(prefix):]:
        return "not_default_branch_path"
    path = href[len(prefix):]
    # prevent encoded path traversal, fragments and alternate authorities
    if any(part in ("", ".", "..") for part in path.split("/")) or "?" in path or "#" in path:
        return "invalid_catalog_link"
    api.get(f"/repos/{OWNER}/{quote(p['name'])}/contents/{quote(path, safe='/')}?ref=main")
    return "exists_on_main"  # existence, not content or behavior attestation


def head_workflow_observation(payload: dict, sha: str) -> dict:
    """Bounded latest-per-workflow evidence at HEAD, never an aggregate CI verdict.

    GitHub returns recent runs newest-first. Older duplicates of the same workflow
    must not hide the latest failure, cancellation or pending run.
    """
    if not isinstance(payload, dict) or not isinstance(payload.get("workflow_runs"), list):
        raise ValueError("workflow list missing or malformed")
    latest: dict[str, dict] = {}
    for run in payload["workflow_runs"]:
        if run.get("head_sha") != sha:
            continue
        identity = str(run.get("workflow_id") or run.get("name") or run.get("id"))
        if identity in latest:
            continue
        latest[identity] = {
            "workflow": run.get("name"), "id": run.get("id"),
            "url": run.get("html_url"), "event": run.get("event"),
            "status": run.get("status"), "conclusion": run.get("conclusion"),
            "created_at": run.get("created_at"),
        }
    runs = list(latest.values())
    exceptions = [run for run in runs if run["status"] != "completed" or
                  run["conclusion"] not in ("success", "neutral", "skipped")]
    return {"observation_limit": 30, "most_recent_per_workflow": runs,
            "head_run_exceptions": exceptions,
            "completeness": "bounded: not a required-workflow inventory"}


def examine(api, p: dict, now: datetime, max_age: int) -> dict:
    name = p["name"]
    path = f"/repos/{OWNER}/{quote(name)}"
    row = {"name": name, "tier": p.get("tier"), "catalog_status": p.get("status"),
           "observed": False, "errors": [], "evidence_limits": p.get("evidence_limits")}

    def attempt(key, fn):
        try:
            row[key] = fn()
        except (APIError, ValueError, KeyError, TypeError) as exc:
            row[key] = None
            row["errors"].append(f"{key}: {type(exc).__name__}: {exc}")

    attempt("repository", lambda: api.get(path))
    repo = row.get("repository")
    if not isinstance(repo, dict):
        row["repository"] = None
        return row
    if (repo.get("full_name") != f"{OWNER}/{name}" or repo.get("private") or repo.get("fork")):
        row["errors"].append("repository identity, visibility or originality mismatch")
        row["repository"] = None
        return row
    row["observed"] = True
    branch = repo.get("default_branch")
    row["default_branch"] = branch
    row["pushed_at"] = repo.get("pushed_at")
    row["open_issue_and_pr_count"] = repo.get("open_issues_count")  # GitHub includes PRs
    row["stars"] = repo.get("stargazers_count")  # popularity, not independent review
    row["forks"] = repo.get("forks_count")
    row["license_spdx"] = (repo.get("license") or {}).get("spdx_id")
    row.pop("repository")  # do not publish raw repository metadata
    if not isinstance(branch, str) or not branch:
        row["errors"].append("missing default branch")
        return row

    attempt("branch", lambda: api.get(f"{path}/branches/{quote(branch, safe='')}"))
    sha = ((row.get("branch") or {}).get("commit") or {}).get("sha")
    row["default_head_sha"] = sha
    row.pop("branch", None)
    if not sha:
        row["errors"].append("missing current default-branch SHA")

    attempt("issue_sample", lambda: issue_sample(api.get(
        f"{path}/issues?state=open&sort=created&direction=asc&per_page=30"), now))
    if sha:
        attempt("default_head_workflows", lambda: head_workflow_observation(
            api.get(f"{path}/actions/runs?branch={quote(branch, safe='')}&per_page=30"), sha))
        attempt("linked_workflow", lambda: linked_workflow(api, p, branch, sha, now, max_age))
    else:
        row["linked_workflow"] = {"state": "unverified"}
    attempt("source_anchor", lambda: source_anchor(api, p))
    return row


def snapshot(catalog: dict, api, now: datetime, max_age: int) -> dict:
    projects = validate_catalog(catalog)
    result = {"schema_version": 1, "checked_at_utc": now.isoformat(),
              "catalog_generated_at": catalog.get("generated_at"),
              "max_evidence_age_days": max_age, "scope": "public originals in portfolio catalog",
              "coverage": {"state": "unknown", "catalog_count": len(projects)},
              "projects": [], "errors": []}
    try:
        known = {p["name"] for p in projects}
        public = set(public_originals(api))
        result["coverage"] = {"state": "complete" if public == known else "drift",
                              "catalog_count": len(known), "observed_public_original_count": len(public),
                              "missing_from_catalog": sorted(public - known),
                              "missing_on_github": sorted(known - public)}
    except (APIError, ValueError, KeyError) as exc:
        result["errors"].append(f"public scope discovery: {type(exc).__name__}: {exc}")
    for project in projects:
        result["projects"].append(examine(api, project, now, max_age))
    return result


def collection_failures(snap: dict) -> list[str]:
    """Operational integrity: data collection complete, independent of readiness."""
    failures = []
    if snap["coverage"]["state"] != "complete" or snap["errors"]:
        failures.append("public inventory drifted or could not be enumerated")
    for p in snap["projects"]:
        required = ("default_head_sha", "issue_sample", "default_head_workflows", "linked_workflow", "source_anchor")
        if not p["observed"] or p["errors"] or any(p.get(k) is None for k in required):
            failures.append(f"{p['name']}: missing or incomplete live data")
    return failures


def gates(snap: dict) -> list[str]:
    """Fail closed in strict mode; never treat missing observations as passing."""
    failures = []
    if snap["coverage"]["state"] != "complete" or snap["errors"]:
        failures.append("portfolio inventory unverified or drifted")
    for p in snap["projects"]:
        if p["errors"] or not p["observed"] or not p.get("default_head_sha"):
            failures.append(f"{p['name']}: incomplete API evidence")
        if p["tier"] == "flagship":
            if (p.get("linked_workflow") or {}).get("state") != "head_bound":
                failures.append(f"{p['name']}: cited workflow does not attest to fresh default HEAD")
            if p.get("source_anchor") != "exists_on_main":
                failures.append(f"{p['name']}: default-branch source anchor not verified")
            for r in (p.get("default_head_workflows") or {}).get("head_run_exceptions", []):
                failures.append(f"{p['name']}: HEAD workflow {r.get('workflow') or r.get('id')} has status={r.get('status')} conclusion={r.get('conclusion')}")
    return failures


def markdown(snap: dict) -> str:
    lines = ["# Portfolio critical evidence audit", "",
             f"Observed (UTC): {snap['checked_at_utc']}",
             f"Scope: {snap['coverage']['catalog_count']} catalogued public original repositories; private names excluded.",
             f"Catalog-to-GitHub coverage: **{snap['coverage']['state']}**.", "",
             "Evidence is *not* a production certification. A successful Actions run covers only the named workflow at its recorded SHA.",
             "An issues endpoint count includes pull requests; sampled labels and ages are not a complete debt classification.", "",
             "| Repository | Tier | Default head | Linked workflow | HEAD workflow exceptions | Open issues + PRs | Oldest sampled issue (days) | Inquiry |",
             "| --- | --- | --- | --- | --- | ---: | ---: | --- |"]
    for p in snap["projects"]:
        s = (p.get("linked_workflow") or {}).get("state", "unknown")
        issue = (p.get("issue_sample") or {}).get("oldest_issue_in_sample_days")
        days = "unknown" if issue is None else str(issue)
        count = p.get("open_issue_and_pr_count")
        count = "unknown" if count is None else str(count)
        inquiry = "API incomplete" if p["errors"] else ("Test freshness/attestation" if p["tier"] == "flagship" else "Assess scope and proof")
        observed = p.get("default_head_workflows") or {}
        exceptions = observed.get("head_run_exceptions") or []
        exception_names = ", ".join(str(r.get("workflow") or "unknown").replace("|", "/") + ":" + str(r.get("conclusion") or r.get("status")) for r in exceptions[:2])
        if len(exceptions) > 2:
            exception_names += f" (+{len(exceptions) - 2} more)"
        if not observed:
            exception_names = "unknown"
        lines.append(f"| {p['name']} | {p['tier']} | {(p.get('default_head_sha') or 'unknown')[:12]} | {s} | {exception_names or 'none observed'} | {count} | {days} | {inquiry} |")
    lines += ["", "## Inventory exceptions"]
    coverage = snap["coverage"]
    for key in ("missing_from_catalog", "missing_on_github"):
        lines.append(f"- {key}: {', '.join(coverage.get(key, [])) or 'none detected / unknown'}")
    lines += ["", "## Evidence exceptions"]
    errors = gates(snap)
    lines.extend(f"- {e}" for e in errors) if errors else lines.append("- None under configured freshness policy")
    lines += ["", "## Interpretation", "", "- HEAD-linked success is a narrow signal, not aggregate CI or acceptance proof.",
              "- Repository popularity is not a measure of code safety or external peer review.",
              "- HEAD workflow exceptions come from up to 30 recent runs, de-duplicated by workflow. This does not prove all required workflows ran.",
              "- Missing API responses and stale links remain unverified; never convert them to green.",
              "- Evaluate the hypotheses in CRITICAL_EVALUATION.md before changing readiness labels.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online", action="store_true", help="query only public GitHub endpoints")
    parser.add_argument("--strict", action="store_true", help="exit nonzero on any unverified evidence (requires --online)")
    parser.add_argument("--fail-on-incomplete-collection", action="store_true", help="fail on API/inventory gaps, not historical evidence (requires --online)")
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "evidence-output")
    args = parser.parse_args(argv)
    if args.max_age_days < 0 or ((args.strict or args.fail_on_incomplete_collection) and not args.online):
        parser.error("strict mode requires --online and max age cannot be negative")
    catalog = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))
    validate_catalog(catalog)
    if not args.online:
        print("OFFLINE: public catalog schema checked; no live evidence verified. Pass --online to audit.")
        return 0
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        print("UNVERIFIED: GH_TOKEN or GITHUB_TOKEN required; no remote checks made", file=sys.stderr)
        return 2
    checked = snapshot(catalog, GitHub(token), datetime.now(timezone.utc), args.max_age_days)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "evidence.json").write_text(json.dumps(checked, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "EVIDENCE_REPORT.md").write_text(markdown(checked), encoding="utf-8")
    failures = gates(checked)
    print(f"AUDIT: checked {len(checked['projects'])} public projects; coverage={checked['coverage']['state']}; exceptions={len(failures)}")
    print(f"Reports: {args.output_dir.resolve()}")
    return 2 if ((args.strict and failures) or (args.fail_on_incomplete_collection and collection_failures(checked))) else 0


if __name__ == "__main__":
    sys.exit(main())
