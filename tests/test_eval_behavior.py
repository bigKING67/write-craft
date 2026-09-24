from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.eval_behavior import (
    ContractError,
    extract_final_assistant,
    parse_judgment,
    rejudge_case,
    select_cases,
    validate_payload,
)


def sample_case() -> dict[str, object]:
    return {
        "id": "sample",
        "suite": "smoke",
        "tags": ["rewrite"],
        "request": "改写",
        "source": "原始材料",
        "expected": {
            "must": ["保留事实"],
            "must_not": ["编造数据"],
        },
    }


class BehaviorEvaluationTests(unittest.TestCase):
    def test_contract_requires_safe_single_source(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            (root / "evals" / "fixtures").mkdir(parents=True)
            valid = {"schema": "write-craft.behavior-cases.v2", "cases": [sample_case()]}
            self.assertEqual(validate_payload(valid, root), [])

            invalid_case = sample_case()
            invalid_case.pop("source")
            invalid_case["source_file"] = "../outside.md"
            errors = validate_payload(
                {"schema": "write-craft.behavior-cases.v2", "cases": [invalid_case]},
                root,
            )
            self.assertTrue(any("evals/fixtures" in error for error in errors), errors)

    def test_suite_selection_and_explicit_cases(self) -> None:
        smoke = sample_case()
        full = {**sample_case(), "id": "full", "suite": "full"}
        cases = [smoke, full]
        self.assertEqual([case["id"] for case in select_cases(cases, "smoke", [])], ["sample"])
        self.assertEqual([case["id"] for case in select_cases(cases, "full", [])], ["sample", "full"])
        self.assertEqual([case["id"] for case in select_cases(cases, "smoke", ["full"])], ["full"])
        with self.assertRaises(ContractError):
            select_cases(cases, "smoke", ["missing"])

    def test_extracts_last_assistant_message_and_fails_closed(self) -> None:
        lines = [
            {"type": "message_end", "message": {"role": "assistant", "content": [{"type": "text", "text": "draft"}]}},
            {"type": "message_end", "message": {"role": "assistant", "content": [{"type": "text", "text": "final"}], "stopReason": "stop"}},
        ]
        parsed = extract_final_assistant("\n".join(json.dumps(line) for line in lines))
        self.assertEqual(parsed["text"], "final")
        with self.assertRaises(ContractError):
            extract_final_assistant('{"type":"agent_end","messages":[]}')
        with self.assertRaises(ContractError):
            extract_final_assistant("not-json")
        error_line = json.dumps(
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "content": [],
                    "stopReason": "error",
                    "errorMessage": "model_not_found",
                },
            }
        )
        with self.assertRaisesRegex(ContractError, "model_not_found"):
            extract_final_assistant(error_line)

    def test_judgment_must_cover_contract_and_match_status(self) -> None:
        case = sample_case()
        judgment = {
            "schema": "write-craft.judgment.v1",
            "case_id": "sample",
            "status": "PASS",
            "must": [
                {"criterion": "保留事实", "status": "PASS", "evidence": "候选稿保留了事实"}
            ],
            "must_not": [
                {"criterion": "编造数据", "status": "PASS", "evidence": "未出现编造数据"}
            ],
            "blocking_issues": [],
        }
        parsed = parse_judgment(json.dumps(judgment, ensure_ascii=False), case)
        self.assertEqual(parsed["status"], "PASS")

        judgment["must"][0]["status"] = "UNCERTAIN"
        with self.assertRaises(ContractError):
            parse_judgment(json.dumps(judgment, ensure_ascii=False), case)

    def test_rejudge_requires_existing_input_and_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            with self.assertRaises(ContractError):
                rejudge_case(
                    case_dir=Path(raw_dir),
                    judge_model="example/model",
                    judge_thinking="low",
                    timeout=1,
                )


if __name__ == "__main__":
    unittest.main()
