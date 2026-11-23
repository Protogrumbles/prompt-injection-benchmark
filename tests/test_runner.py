"""Tests for the prompt-injection-benchmark runner — scoring logic only.

The dummy rules file is deliberately incomplete. These tests assert the
runner reports exactly that: some found, some missed, and a false
positive on a clean control. Nothing here is a RAILGUARD score.
"""
import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run as runner

ROOT = Path(__file__).resolve().parents[1]

class TestRunner(unittest.TestCase):
    def test_dummy_rules_self_test(self):
        rules = runner.parse_rules(ROOT / "rules" / "dummy-rules.txt")
        cases = runner.load_cases(ROOT / "cases")
        results, totals = runner.score(rules, cases)
        self.assertEqual(totals["total_scored"], 12)
        self.assertEqual(totals["total_controls"], 3)
        # Dummy prompt-injection rule matches PI-01 and PI-02 (SYSTEM_PROMPT +)
        by_id = {r["id"]: r for r in results}
        self.assertEqual(by_id["PI-01"]["result"], "found")
        self.assertEqual(by_id["PI-02"]["result"], "found")
        # Dummy SQL rule matches SQ-01
        self.assertEqual(by_id["SQ-01"]["result"], "found")
        # Dummy hardcoded-credentials rule matches HC-01
        self.assertEqual(by_id["HC-01"]["result"], "found")
        # No rule covers path traversal / SSRF / auth / logs / permissions
        for cid in ("AU-01", "AU-02", "PT-01", "SS-01", "LG-01", "PM-01"):
            self.assertEqual(by_id[cid]["result"], "missed", cid)
        # Over-broad dummy rule ("system" substring) flags the CL-03 control
        self.assertEqual(by_id["CL-03"]["result"], "false_positive")
        self.assertEqual(by_id["CL-01"]["result"], "clean")
        self.assertEqual(by_id["CL-02"]["result"], "clean")
        self.assertEqual(totals["false_positives"], 1)

    def test_full_run_writes_score_sheet(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "score.md"
            self.assertEqual(runner.main(["--rules", str(ROOT / "rules" / "dummy-rules.txt"),
                "--cases", str(ROOT / "cases"), "--out", str(out),
                "--json-out", str(Path(td) / "score.json")]), 0)
            text = out.read_text()
            self.assertIn("Found", text)
            self.assertIn("PI-01", text)
            saved = json.loads((Path(td) / "score.json").read_text())
            self.assertEqual(saved["totals"]["total_scored"], 12)

    def test_bad_rules_file_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.txt"
            bad.write_text("rule: x\npatterns:\n  - foo\n")  # missing category
            self.assertEqual(runner.main(["--rules", str(bad),
                "--cases", str(ROOT / "cases"), "--out", str(Path(td) / "s.md")]), 2)

    def test_case_files_are_complete(self):
        cases = runner.load_cases(ROOT / "cases")
        self.assertEqual(len(cases), 15)  # 12 scored + 3 controls
        for c in cases:
            for key in ("id", "category", "severity", "title", "snippet", "expected_finding", "is_control"):
                self.assertIn(key, c, c.get("id"))
        self.assertEqual(sum(1 for c in cases if not c["is_control"]), 12)
        self.assertEqual(sum(1 for c in cases if c["is_control"]), 3)

if __name__ == "__main__":
    unittest.main()
