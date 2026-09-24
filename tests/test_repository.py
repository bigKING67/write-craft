from __future__ import annotations

import json
from copy import deepcopy
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import validate as source_validator


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
        case_ids = {case["id"] for case in cases}
        tags = {tag for case in cases for tag in case["tags"]}
        self.assertTrue({"rewrite", "diagnose", "evidence", "routing", "reader-test"} <= tags)
        self.assertIn("decision-entry-preserves-engineering-source", case_ids)
        length_case = next(
            case for case in cases if case["id"] == "strict-total-length-budget"
        )
        self.assertEqual(length_case["limits"], {"max_han_characters": 500})
        self.assertTrue(
            any("附注" in item for item in length_case["expected"]["must_not"])
        )
        self.assertTrue(
            any("责任人" in item for item in length_case["expected"]["must_not"])
        )
        prohibited = " ".join(
            item for case in cases for item in case["expected"]["must_not"]
        )
        for invariant in ("编造", "生产上线", "独立通过", "飞书写入", "嵌入电子表格"):
            self.assertIn(invariant, prohibited)

    def test_source_validator_rejects_stale_behavior_baseline(self) -> None:
        original_read_json = source_validator.read_json

        def read_with_drift(path: Path) -> dict[str, object]:
            payload = original_read_json(path)
            if path == ROOT / "evals" / "cases.json":
                payload = deepcopy(payload)
                cases = payload["cases"]
                self.assertIsInstance(cases, list)
                cases[0]["expected"]["must"][0] += "（已变更）"
            return payload

        with patch.object(source_validator, "read_json", side_effect=read_with_drift):
            errors = source_validator.validate()
        self.assertTrue(
            any("case_digest does not match current case" in error for error in errors),
            errors,
        )

    def test_source_validator_rejects_incomplete_behavior_baseline(self) -> None:
        original_read_json = source_validator.read_json
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        baseline_path = ROOT / "evals" / "baselines" / f"pi-v{version}.json"

        def read_without_one_result(path: Path) -> dict[str, object]:
            payload = original_read_json(path)
            if path == baseline_path:
                payload = deepcopy(payload)
                results = payload["results"]
                self.assertIsInstance(results, list)
                results.pop()
            return payload

        with patch.object(source_validator, "read_json", side_effect=read_without_one_result):
            errors = source_validator.validate()
        self.assertTrue(
            any("exactly one result for every current case" in error for error in errors),
            errors,
        )

    def test_source_validator_rejects_overlength_behavior_candidate(self) -> None:
        original_read_json = source_validator.read_json
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        baseline_path = ROOT / "evals" / "baselines" / f"pi-v{version}.json"

        def read_with_overlength_candidate(path: Path) -> dict[str, object]:
            payload = original_read_json(path)
            if path == baseline_path:
                payload = deepcopy(payload)
                results = payload["results"]
                self.assertIsInstance(results, list)
                result = next(
                    item
                    for item in results
                    if item["case_id"] == "strict-total-length-budget"
                )
                result["candidate"] += "超" * 500
                result["candidate_sha256"] = source_validator.sha256_text(
                    result["candidate"]
                )
                result["candidate_metrics"] = {
                    "han_characters": source_validator.han_character_count(
                        result["candidate"]
                    )
                }
            return payload

        with patch.object(
            source_validator,
            "read_json",
            side_effect=read_with_overlength_candidate,
        ):
            errors = source_validator.validate()
        self.assertTrue(
            any("exceeds max_han_characters" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
