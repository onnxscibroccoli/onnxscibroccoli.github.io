"""Dependency-free, offline contract tests for the portfolio evidence probe."""
import importlib.util
from datetime import datetime, timezone, timedelta
from pathlib import Path
import unittest

path = Path(__file__).resolve().parent / "evidence_probe.py"
spec = importlib.util.spec_from_file_location("evidence_probe", path)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
NOW = datetime(2026, 11, 12, 20, tzinfo=timezone.utc)
NAME = "example"
ENTRY = {"name": NAME, "url": "https://github.com/onnxscibroccoli/example",
         "visibility": "public", "tier": "flagship", "status": "EXPERIMENTAL",
         "source": "https://github.com/onnxscibroccoli/example/blob/main/src/main.py",
         "workflow": "https://github.com/onnxscibroccoli/example/actions/runs/123",
         "evidence_limits": "simulation only"}


class Fake:
    def __init__(self, head="abc", run_head="abc", run_branch="main", days=1, private=False, broken=None):
        self.head, self.run_head, self.run_branch, self.days = head, run_head, run_branch, days
        self.private, self.broken = private, broken
        self.seen = []

    def get(self, path):
        self.seen.append(path)
        if path == self.broken:
            raise probe.APIError("simulated HTTP 403")
        if path.startswith("/users/"):
            return [{"name": NAME, "owner": {"login": "onnxscibroccoli"}, "private": False, "fork": False},
                    {"name": "sample-fork", "owner": {"login": "onnxscibroccoli"}, "private": False, "fork": True}]
        if path.endswith("/branches/main"):
            return {"commit": {"sha": self.head}}
        if "/actions/runs/123" in path:
            return {"status": "completed", "conclusion": "success", "event": "push",
                    "head_sha": self.run_head, "head_branch": self.run_branch,
                    "created_at": (NOW - timedelta(days=self.days)).isoformat()}
        if "/actions/runs?" in path:
            return {"workflow_runs": [{"head_sha": self.head, "name": "unit", "status": "completed", "conclusion": "success"},
                                      {"head_sha": "older", "name": "unit", "conclusion": "failure"}]}
        if "/issues?" in path:
            return [{"created_at": (NOW - timedelta(days=20)).isoformat(), "pull_request": {}},
                    {"created_at": (NOW - timedelta(days=12)).isoformat(), "labels": [{"name": "severity:high"}]},
                    {"created_at": (NOW - timedelta(days=6)).isoformat(), "labels": [{"name": "documentation"}]}]
        if "/contents/src/main.py" in path:
            return {"sha": "fileblob"}
        if path.endswith("/example") or path.endswith("/out-of-date"):
            return {"full_name": f"onnxscibroccoli/{path.rsplit('/', 1)[-1]}", "private": self.private,
                    "fork": False, "default_branch": "main", "open_issues_count": 5,
                    "stargazers_count": 0, "forks_count": 0, "license": None,
                    "pushed_at": NOW.isoformat()}
        raise AssertionError(f"unmocked endpoint: {path}")


class EvidenceTests(unittest.TestCase):
    def test_catalog_rejects_private_or_duplicate(self):
        p = dict(ENTRY, visibility="private")
        with self.assertRaises(ValueError):
            probe.validate_catalog({"schema_version": 1, "projects": [p]})
        with self.assertRaises(ValueError):
            probe.validate_catalog({"schema_version": 1, "projects": [ENTRY, ENTRY]})

    def test_head_bound_and_pr_excluded(self):
        api = Fake()
        row = probe.examine(api, ENTRY, NOW, 7)
        self.assertTrue(row["observed"])
        self.assertEqual(row["linked_workflow"]["state"], "head_bound")
        self.assertEqual(row["source_anchor"], "exists_on_main")
        self.assertEqual(row["issue_sample"]["issues_in_sample"], 2)
        self.assertEqual(row["issue_sample"]["triage_labeled_in_sample"], 1)
        self.assertEqual(row["issue_sample"]["oldest_issue_in_sample_days"], 12)
        self.assertEqual(len(row["default_head_workflows"]["most_recent_per_workflow"]), 1)
        self.assertEqual(row["open_issue_and_pr_count"], 5)
        self.assertNotIn("repository", row)

    def test_stale_and_other_branch_not_promoted(self):
        row = probe.examine(Fake(run_head="older"), ENTRY, NOW, 7)
        self.assertEqual(row["linked_workflow"]["state"], "historical")
        row = probe.examine(Fake(run_branch="feature"), ENTRY, NOW, 7)
        self.assertEqual(row["linked_workflow"]["state"], "historical")
        row = probe.examine(Fake(days=8), ENTRY, NOW, 7)
        self.assertEqual(row["linked_workflow"]["state"], "aged_head_bound")

    def test_errors_and_private_never_promoted(self):
        row = probe.examine(Fake(private=True), ENTRY, NOW, 7)
        self.assertFalse(row["observed"])
        self.assertTrue(row["errors"])
        row = probe.examine(Fake(broken="/repos/onnxscibroccoli/example/actions/runs/123"), ENTRY, NOW, 7)
        self.assertIsNone(row["linked_workflow"])
        self.assertTrue(row["errors"])

    def test_catalog_coverage_discrepancy_and_gate(self):
        entry = dict(ENTRY, name="out-of-date", url="https://github.com/onnxscibroccoli/out-of-date")
        snap = probe.snapshot({"schema_version": 1, "projects": [entry]}, Fake(), NOW, 7)
        self.assertEqual(snap["coverage"]["state"], "drift")
        self.assertIn("example", snap["coverage"]["missing_from_catalog"])
        self.assertTrue(probe.gates(snap))
        self.assertTrue(probe.collection_failures(snap))
        self.assertIn("unverified", probe.markdown(snap).lower())

    def test_head_bound_full_gate(self):
        snap = probe.snapshot({"schema_version": 1, "projects": [ENTRY]}, Fake(), NOW, 7)
        self.assertEqual(snap["coverage"]["state"], "complete")
        self.assertEqual(probe.gates(snap), [])
        self.assertEqual(probe.collection_failures(snap), [])

    def test_head_workflow_exception_not_masked_by_older_success(self):
        payload = {"workflow_runs": [
            {"head_sha": "abc", "workflow_id": 14, "name": "integration-gate", "status": "completed", "conclusion": "failure"},
            {"head_sha": "abc", "workflow_id": 14, "name": "integration-gate", "status": "completed", "conclusion": "success"},
            {"head_sha": "older", "workflow_id": 15, "name": "ci", "status": "completed", "conclusion": "failure"},
            {"head_sha": "abc", "workflow_id": 16, "name": "security", "status": "queued", "conclusion": None},
        ]}
        observed = probe.head_workflow_observation(payload, "abc")
        self.assertEqual(len(observed["most_recent_per_workflow"]), 2)
        self.assertEqual(len(observed["head_run_exceptions"]), 2)
        self.assertEqual(observed["head_run_exceptions"][0]["conclusion"], "failure")
        self.assertEqual(observed["head_run_exceptions"][1]["status"], "queued")

    def test_reject_bad_anchor_and_date(self):
        self.assertIsNone(probe.utc("2026-X-X"))
        self.assertEqual(probe.source_anchor(Fake(), dict(ENTRY, source="https://bad.test/")), "not_default_branch_path")
        self.assertEqual(probe.linked_workflow(Fake(), dict(ENTRY, workflow="bad"), "main", "abc", NOW, 7)["state"], "invalid_catalog_link")


if __name__ == "__main__":
    unittest.main()
