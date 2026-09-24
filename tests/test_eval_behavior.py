from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.eval_behavior import (
    ContractError,
    canonical_json,
    extract_final_assistant,
    judge_prompt,
    parse_judgment,
    rejudge_case,
    select_cases,
    sha256_text,
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

        judgment["blocking_issues"] = ["存在阻断问题"]
        with self.assertRaisesRegex(ContractError, "does not match computed status"):
            parse_judgment(json.dumps(judgment, ensure_ascii=False), case)
        judgment["status"] = "FAIL"
        parsed = parse_judgment(json.dumps(judgment, ensure_ascii=False), case)
        self.assertEqual(parsed["status"], "FAIL")

        judgment["blocking_issues"] = []
        judgment["status"] = "PASS"
        judgment["must"][0]["status"] = "UNCERTAIN"
        with self.assertRaises(ContractError):
            parse_judgment(json.dumps(judgment, ensure_ascii=False), case)

    def test_judge_prompt_defines_must_not_status_as_compliance(self) -> None:
        prompt = judge_prompt(sample_case(), "原始材料", "候选稿")
        self.assertIn("status 表示候选稿是否符合该条合同", prompt)
        self.assertIn("候选稿没有编造时，status 必须是 PASS", prompt)

    def test_rejudge_requires_existing_source_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            with self.assertRaises(ContractError):
                rejudge_case(
                    case_dir=Path(raw_dir),
                    judge_model="example/model",
                    judge_thinking="low",
                    timeout=1,
                )

    def test_rejudge_rejects_drifted_source_artifacts(self) -> None:
        case = sample_case()
        source = case["source"]
        case_digest = sha256_text(canonical_json({"case": case, "source": source}))
        candidate = "保留原始事实"
        with tempfile.TemporaryDirectory() as raw_dir:
            case_dir = Path(raw_dir)
            (case_dir / "input.json").write_text(
                json.dumps(
                    {"case": case, "source": source, "case_digest": case_digest},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (case_dir / "candidate.md").write_text(candidate + "\n", encoding="utf-8")
            (case_dir / "result.json").write_text(
                json.dumps(
                    {
                        "case_id": case["id"],
                        "case_digest": case_digest,
                        "candidate_sha256": sha256_text(candidate),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            (case_dir / "candidate.md").write_text("事后替换的候选稿\n", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "original result hash"):
                rejudge_case(
                    case_dir=case_dir,
                    judge_model="example/model",
                    judge_thinking="low",
                    timeout=1,
                )

            (case_dir / "candidate.md").write_text(candidate + "\n", encoding="utf-8")
            input_payload = json.loads((case_dir / "input.json").read_text(encoding="utf-8"))
            input_payload["case_digest"] = "0" * 64
            (case_dir / "input.json").write_text(
                json.dumps(input_payload, ensure_ascii=False), encoding="utf-8"
            )
            with self.assertRaisesRegex(ContractError, "input case_digest"):
                rejudge_case(
                    case_dir=case_dir,
                    judge_model="example/model",
                    judge_thinking="low",
                    timeout=1,
                )


if __name__ == "__main__":
    unittest.main()
