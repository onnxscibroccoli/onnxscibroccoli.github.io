#!/usr/bin/env python3
"""Static, dependency-free reviewer portal integrity checks; never accesses GitHub."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import json
import sys
import urllib.parse

ROOT = Path(__file__).resolve().parent

class Portal(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.landmarks: dict[str, int] = {}
        self.has_lang = False
        self.has_title = False
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        a = dict(attrs)
        if "id" in a:
            assert a["id"] not in self.ids, f"duplicate id {a['id']}"
            self.ids.add(a["id"])
        if tag in ("nav", "main", "h1"):
            self.landmarks[tag] = self.landmarks.get(tag, 0) + 1
        if tag == "html":
            self.has_lang = bool(a.get("lang"))
        if tag == "title":
            self.in_title = True
        if tag == "a":
            assert a.get("href"), "link missing href"
            self.links.append(a["href"] or "")
        if tag == "script":
            raise AssertionError("portal must not depend on scripts or third-party telemetry")

    def handle_endtag(self, tag: str):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str):
        if self.in_title and data.strip():
            self.has_title = True

def main() -> int:
    raw = (ROOT / "index.html").read_text(encoding="utf-8")
    manifest = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    projects = manifest["projects"]
    assert len(projects) == 29, "campaign registry must have 29 original repositories"
    names = [p["name"] for p in projects]
    assert len(set(names)) == len(names), "duplicate repository"
    featured = [p for p in projects if p["tier"] == "flagship"]
    assert len(featured) == 7
    page = Portal()
    page.feed(raw)
    assert page.has_lang and page.has_title
    assert all(page.landmarks.get(name) == 1 for name in ("main", "h1")), "one main and h1 required"
    assert page.landmarks.get("nav", 0) >= 1
    assert "#main" in page.links, "skip link missing"
    for url in page.links:
        parsed = urllib.parse.urlsplit(url)
        if url.startswith("#"):
            assert url[1:] in page.ids, f"broken fragment {url}"
        elif parsed.scheme:
            assert parsed.scheme == "https", f"insecure link {url}"
            assert parsed.netloc in {"github.com", "onnxscibroccoli.github.io"}, f"unexpected external link {url}"
        else:
            assert url == "/", f"unexpected local path {url}"
    for p in featured:
        assert p["visibility"] == "public"
        assert p["url"] in raw, f"missing case study for {p['name']}"
        assert p["source"] in raw, f"missing source anchor for {p['name']}"
        assert p["workflow"] in raw, f"missing CI anchor for {p['name']}"
        assert "Not claimed:" in raw, "verification limitation labels missing"
    for p in projects:
        assert p["url"] == f"https://github.com/onnxscibroccoli/{p['name']}"
        assert p["status"] not in {"PRODUCTION_VERIFIED", "HUMAN_APPROVED"}, "unsubstantiated status"
        if p["visibility"] == "private":
            assert p["tier"] != "flagship"
            assert p["source"] is None and p["workflow"] is None
    assert "HELIX_SKIP_LIVE=1" in raw
    assert "No external scripts" not in raw or "<script" not in raw
    print(f"PASS: accessible static portal, {len(projects)} source-tracked repositories, {len(featured)} scoped evidence cards")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
