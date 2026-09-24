from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_source_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_local_upstream_status_is_current(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/upstream_status.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["local_valid"])
        self.assertFalse(payload["remote_checked"])
        self.assertEqual(len(payload["upstreams"]), 4)

    def test_behavior_contract_covers_core_failure_modes(self) -> None:
        payload = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
        cases = payload["cases"]
        tags = {tag for case in cases for tag in case["tags"]}
        self.assertTrue({"rewrite", "diagnose", "evidence", "routing", "reader-test"} <= tags)
        prohibited = " ".join(
            item for case in cases for item in case["expected"]["must_not"]
        )
        for invariant in ("编造", "生产上线", "独立通过", "飞书写入"):
            self.assertIn(invariant, prohibited)


if __name__ == "__main__":
    unittest.main()
