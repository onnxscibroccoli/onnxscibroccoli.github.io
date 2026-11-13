#!/usr/bin/env python3
"""
Critical analysis helper for the engineering portfolio.

Reads the local projects.json and produces a concise gap report.
Does not contact the network. Intended to be extended with API calls
in a controlled CI context.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

def load_catalog() -> dict:
    return json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))

def analyze(catalog: dict) -> list[str]:
    lines = []
    lines.append(f"# Critical Analysis Snapshot — {datetime.utcnow().date().isoformat()}")
    lines.append("")
    lines.append(f"Catalog generated_at: {catalog.get('generated_at', 'unknown')}")
    lines.append(f"Public projects: {len(catalog.get('projects', []))}")
    lines.append(f"Flagships: {sum(1 for p in catalog.get('projects', []) if p.get('tier') == 'flagship')}")
    lines.append("")
    lines.append("## Flagship evidence boundaries")
    for p in catalog.get("projects", []):
        if p.get("tier") != "flagship":
            continue
        lines.append(f"- **{p['name']}** ({p.get('status', 'unknown')})")
        lines.append(f"  - Evidence limits: {p.get('evidence_limits', 'none stated')}")
        if not p.get("workflow"):
            lines.append("  - GAP: no workflow link")
        if not p.get("source"):
            lines.append("  - GAP: no source link")
    lines.append("")
    lines.append("## Cross-cutting gaps (static)")
    lines.append("- Knowledge graph freshness not encoded in catalog")
    lines.append("- Open issue counts not encoded")
    lines.append("- Workflow run dates not encoded (historical only)")
    lines.append("- No external review metrics")
    lines.append("")
    lines.append("See CRITICAL_EVALUATION.md for full inquiry and recommended implementations.")
    return lines

def main() -> None:
    catalog = load_catalog()
    report = "\n".join(analyze(catalog))
    out = ROOT / "critical_analysis_report.md"
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nWrote {out}")

if __name__ == "__main__":
    main()
