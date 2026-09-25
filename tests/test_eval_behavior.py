from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.eval_behavior import (
    FACT_JUDGMENT_TOOL,
    READER_JUDGMENT_TOOL,
    READER_RESPONSE_TOOL,
    STRUCTURED_OUTPUT_EXTENSION,
    ContractError,
    aggregate_status,
    apply_deterministic_checks,
    assistant_usage_summary,
    calibrate_judge,
    case_sources,
    candidate_limit_issues,
    canonical_json,
    evaluator_metadata,
    evaluate_case,
    extract_final_assistant,
    extract_final_tool_call,
    format_sources,
    generator_prompt,
    han_character_count,
    judge_prompt,
    load_judge_fixtures,
    normalize_fact_tool_arguments,
    parse_judgment,
    parse_reader_judgment,
    parse_reader_response,
    pi_args,
    persist_raw_jsonl,
    reader_prompt,
    reader_judgment_prompt,
    rejudge_case,
    revision_prompt,
    resolved_case_digest,
    select_cases,
    sha256_text,
    structured_output_metadata,
    validate_payload,
)


def pi_text_output(text: str) -> dict[str, object]:
    return pi_message_output(
        [{"type": "text", "text": text}],
        stop_reason="stop",
    )


def pi_tool_output(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return pi_message_output(
        [
            {
                "type": "toolCall",
                "id": f"call-{tool_name}",
                "name": tool_name,
                "arguments": arguments,
            }
        ],
        stop_reason="toolUse",
    )


def fact_tool_arguments(judgment: dict[str, object]) -> dict[str, object]:
    return {
        "schema": judgment["schema"],
        "case_id": judgment["case_id"],
        "must": [
            {
                "criterion_index": index,
                "status": check["status"],
                "evidence": check["evidence"],
            }
            for index, check in enumerate(judgment["must"], start=1)
        ],
        "must_not": [
            {
                "criterion_index": index,
                "presence": {
                    "PASS": "ABSENT",
                    "FAIL": "PRESENT",
                    "UNCERTAIN": "UNCERTAIN",
                }[check["status"]],
                "evidence": check["evidence"],
            }
            for index, check in enumerate(judgment["must_not"], start=1)
        ],
        "blocking_issues": judgment["blocking_issues"],
    }


def pi_message_output(
    content: list[dict[str, object]], *, stop_reason: str
) -> dict[str, object]:
    return {
        "returncode": 0,
        "stdout": json.dumps(
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "content": content,
                    "stopReason": stop_reason,
                },
            },
            ensure_ascii=False,
        ),
        "stderr": "",
        "duration_seconds": 0.01,
        "timed_out": False,
    }


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


def sample_reader_case() -> dict[str, object]:
    case = sample_case()
    case["reader_test"] = {
        "persona": "不了解项目的业务负责人",
        "questions": [
            {
                "id": "scope",
                "question": "首期范围是什么？",
                "answer_key": ["覆盖 20 名在线客服", "不含电话客服"],
            }
        ],
    }
    return case


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

            limited_case = sample_case()
            limited_case["limits"] = {"max_han_characters": 500}
            self.assertEqual(
                validate_payload(
                    {"schema": "write-craft.behavior-cases.v2", "cases": [limited_case]},
                    root,
                ),
                [],
            )
            limited_case["limits"] = {"max_han_characters": True}
            errors = validate_payload(
                {"schema": "write-craft.behavior-cases.v2", "cases": [limited_case]},
                root,
            )
            self.assertTrue(any("max_han_characters" in error for error in errors), errors)

            revisable_case = sample_case()
            revisable_case["max_revisions"] = 1
            self.assertEqual(
                validate_payload(
                    {"schema": "write-craft.behavior-cases.v2", "cases": [revisable_case]},
                    root,
                ),
                [],
            )
            revisable_case["max_revisions"] = 2
            errors = validate_payload(
                {"schema": "write-craft.behavior-cases.v2", "cases": [revisable_case]},
                root,
            )
            self.assertTrue(any("max_revisions" in error for error in errors), errors)

            ambiguous_case = sample_case()
            ambiguous_case["source_file"] = "evals/fixtures/also-present.md"
            with self.assertRaisesRegex(ContractError, "exactly one"):
                case_sources(ambiguous_case, root)

    def test_v3_contract_resolves_multiple_sources_with_stable_locations(self) -> None:
        case = {
            **sample_case(),
            "track": "exploration",
            "sources": [
                {"source_id": "approved", "text": "第一行\n第二行"},
                {"source_id": "draft", "text": "另一个版本"},
            ],
        }
        case.pop("source")
        payload = {"schema": "write-craft.behavior-cases.v3", "cases": [case]}
        self.assertEqual(validate_payload(payload), [])
        sources = case_sources(case)
        self.assertEqual([item["source_id"] for item in sources], ["approved", "draft"])
        formatted = format_sources(sources)
        self.assertIn("source_id=approved", formatted)
        self.assertIn(f"text_sha256={sha256_text('第一行\n第二行')}", formatted)
        self.assertIn("L1: 第一行", formatted)
        self.assertIn("L2: 第二行", formatted)
        self.assertEqual(len(resolved_case_digest(case, sources)), 64)

        duplicate = json.loads(json.dumps(case, ensure_ascii=False))
        duplicate["sources"][1]["source_id"] = "approved"
        errors = validate_payload(
            {"schema": "write-craft.behavior-cases.v3", "cases": [duplicate]}
        )
        self.assertTrue(any("source_id values must be unique" in error for error in errors))

    def test_v3_requires_regression_or_exploration_track(self) -> None:
        case = sample_case()
        errors = validate_payload(
            {"schema": "write-craft.behavior-cases.v3", "cases": [case]}
        )
        self.assertTrue(any(".track" in error for error in errors), errors)
        case["track"] = "regression"
        self.assertEqual(
            validate_payload(
                {"schema": "write-craft.behavior-cases.v3", "cases": [case]}
            ),
            [],
        )

    def test_judge_calibration_contains_positive_and_negative_fixtures(self) -> None:
        fixtures = load_judge_fixtures()
        self.assertGreaterEqual(len(fixtures), 11)
        self.assertEqual(
            {fixture["expected_status"] for fixture in fixtures}, {"PASS", "FAIL"}
        )
        self.assertTrue(
            all(fixture["case"]["request"].strip() for fixture in fixtures)
        )
        self.assertIn(
            "reject-invented-approval-process",
            {fixture["id"] for fixture in fixtures},
        )
        self.assertIn(
            "reject-policy-as-capability",
            {fixture["id"] for fixture in fixtures},
        )
        self.assertIn(
            "reject-expanded-gap-list",
            {fixture["id"] for fixture in fixtures},
        )
        self.assertIn(
            "reject-component-gaps-as-explanation",
            {fixture["id"] for fixture in fixtures},
        )
        self.assertIn(
            "reject-trial-implies-rollout-decision",
            {fixture["id"] for fixture in fixtures},
        )
        self.assertIn(
            "accept-ledger-bounded-term-explanation",
            {fixture["id"] for fixture in fixtures},
        )
        self.assertIn(
            "reject-ledger-not-stated-as-undetermined",
            {fixture["id"] for fixture in fixtures},
        )

    def test_judge_calibration_aborts_after_first_system_error(self) -> None:
        fixtures = [
            {
                "id": fixture_id,
                "case": sample_case(),
                "source": "原始材料",
                "candidate": "候选稿",
                "expected_status": "PASS",
            }
            for fixture_id in ("first", "second")
        ]
        failed_call = {
            "returncode": 7,
            "stdout": "",
            "stderr": "provider error",
            "duration_seconds": 0.01,
            "timed_out": False,
        }
        with tempfile.TemporaryDirectory() as raw_dir, patch(
            "scripts.eval_behavior.run_command", return_value=failed_call
        ) as mocked:
            summary = calibrate_judge(
                fixtures=fixtures,
                output_root=Path(raw_dir),
                judge_model="judge/model",
                judge_thinking="high",
                timeout=1,
            )
        self.assertEqual(mocked.call_count, 1)
        self.assertEqual(summary["status"], "ERROR")
        self.assertTrue(summary["aborted_after_system_error"])
        self.assertEqual(summary["not_run_fixture_ids"], ["second"])

    def test_semantic_contract_is_validated_and_hidden_from_generator(self) -> None:
        case = sample_case()
        case["track"] = "regression"
        case["semantic_contract"] = {
            "facts": ["来源只说明当前值"],
            "allowed_inferences": ["可以把当前值称为比较基线"],
            "forbidden_inferences": ["不得把未说明写成尚未确定"],
            "unknowns": [{"topic": "正式阈值", "state": "not_stated"}],
            "reader_truths": ["读者应知道阈值未说明"],
            "reader_misreadings": ["阈值尚未确定"],
        }
        payload = {"schema": "write-craft.behavior-cases.v3", "cases": [case]}
        self.assertEqual(validate_payload(payload), [])

        generated = generator_prompt(case, "原始材料")
        judged = judge_prompt(case, "原始材料", "候选稿")
        self.assertNotIn("不得把未说明写成尚未确定", generated)
        self.assertIn("不得把未说明写成尚未确定", judged)
        self.assertIn("not_stated", judged)
        self.assertIn("缺失声明本身就算禁用行为 PRESENT", judged)

        case["semantic_contract"]["unknowns"][0]["state"] = "unknown"
        errors = validate_payload(payload)
        self.assertTrue(any("unknowns state" in error for error in errors), errors)

    def test_suite_selection_and_explicit_cases(self) -> None:
        smoke = sample_case()
        full = {**sample_case(), "id": "full", "suite": "full"}
        cases = [smoke, full]
        self.assertEqual([case["id"] for case in select_cases(cases, "smoke", [])], ["sample"])
        self.assertEqual([case["id"] for case in select_cases(cases, "full", [])], ["sample", "full"])
        self.assertEqual([case["id"] for case in select_cases(cases, "smoke", ["full"])], ["full"])
        with self.assertRaises(ContractError):
            select_cases(cases, "smoke", ["missing"])

        smoke["track"] = "regression"
        full["track"] = "exploration"
        self.assertEqual(
            [case["id"] for case in select_cases(cases, "full", [], "exploration")],
            ["full"],
        )

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

    def test_extracts_exactly_one_structured_tool_call_and_fails_closed(self) -> None:
        payload = {"schema": "write-craft.judgment.v1", "case_id": "sample"}
        output = pi_tool_output(FACT_JUDGMENT_TOOL, payload)
        parsed = extract_final_tool_call(output["stdout"], FACT_JUDGMENT_TOOL)
        self.assertEqual(parsed["arguments"], payload)

        wrong = pi_tool_output(READER_RESPONSE_TOOL, payload)
        with self.assertRaisesRegex(ContractError, "expected"):
            extract_final_tool_call(wrong["stdout"], FACT_JUDGMENT_TOOL)

        duplicate = pi_message_output(
            [
                {
                    "type": "toolCall",
                    "id": "call-1",
                    "name": FACT_JUDGMENT_TOOL,
                    "arguments": payload,
                },
                {
                    "type": "toolCall",
                    "id": "call-2",
                    "name": FACT_JUDGMENT_TOOL,
                    "arguments": payload,
                },
            ],
            stop_reason="toolUse",
        )
        with self.assertRaisesRegex(ContractError, "exactly one"):
            extract_final_tool_call(duplicate["stdout"], FACT_JUDGMENT_TOOL)

        with self.assertRaisesRegex(ContractError, "exactly one"):
            extract_final_tool_call(pi_text_output("{}")["stdout"], FACT_JUDGMENT_TOOL)

    def test_usage_and_tool_summaries_cover_same_run_schema_corrections(self) -> None:
        first = json.loads(
            pi_tool_output(FACT_JUDGMENT_TOOL, {"attempt": 1})["stdout"]
        )
        first["message"]["usage"] = {
            "input": 2,
            "output": 5,
            "totalTokens": 7,
            "cost": {"total": 0.2},
        }
        second = json.loads(
            pi_tool_output(FACT_JUDGMENT_TOOL, {"attempt": 2})["stdout"]
        )
        second["message"]["usage"] = {
            "input": 3,
            "output": 11,
            "reasoning": 4,
            "totalTokens": 14,
            "cost": {"total": 0.4},
        }
        failed_execution = {
            "type": "tool_execution_end",
            "toolName": FACT_JUDGMENT_TOOL,
            "isError": True,
            "result": {"content": [{"type": "text", "text": "invalid"}]},
        }
        successful_execution = {
            "type": "tool_execution_end",
            "toolName": FACT_JUDGMENT_TOOL,
            "isError": False,
            "result": {"content": [{"type": "text", "text": "submitted"}]},
        }
        jsonl = "\n".join(
            json.dumps(event)
            for event in (first, failed_execution, second, successful_execution)
        )

        usage = assistant_usage_summary(jsonl)
        self.assertEqual(usage["responses"], 2)
        self.assertEqual(usage["usage"]["totalTokens"], 21)
        self.assertEqual(usage["usage"]["reasoning"], 4)
        self.assertAlmostEqual(usage["cost"]["total"], 0.6)

        protocol = structured_output_metadata(FACT_JUDGMENT_TOOL, jsonl)
        self.assertEqual(protocol["tool_calls"], 2)
        self.assertEqual(protocol["failed_executions"], 1)
        self.assertEqual(protocol["successful_executions"], 1)

    def test_tool_summary_accepts_legacy_nested_error_marker(self) -> None:
        jsonl = json.dumps(
            {
                "type": "tool_execution_end",
                "toolName": FACT_JUDGMENT_TOOL,
                "result": {"isError": True},
            }
        )

        protocol = structured_output_metadata(FACT_JUDGMENT_TOOL, jsonl)
        self.assertEqual(protocol["failed_executions"], 1)
        self.assertEqual(protocol["successful_executions"], 0)

    def test_pi_arguments_separate_generator_and_review_tools(self) -> None:
        generator = pi_args(
            prompt="generate", model="example/model", thinking="medium", with_skill=True
        )
        reviewer = pi_args(
            prompt="review",
            model="example/model",
            thinking="high",
            with_skill=False,
            structured_tool=FACT_JUDGMENT_TOOL,
        )
        self.assertIn("--no-context-files", generator)
        self.assertIn("--no-extensions", generator)
        self.assertIn("--skill", generator)
        self.assertEqual(generator[generator.index("--tools") + 1], "read")
        self.assertIn("--extension", reviewer)
        self.assertEqual(
            reviewer[reviewer.index("--tools") + 1], FACT_JUDGMENT_TOOL
        )
        self.assertNotIn("--no-tools", reviewer)
        self.assertNotIn("--skill", reviewer)
        with self.assertRaises(ValueError):
            pi_args(
                prompt="invalid",
                model="example/model",
                thinking="low",
                with_skill=True,
                structured_tool=FACT_JUDGMENT_TOOL,
            )

    def test_raw_jsonl_is_opt_in_and_bounded(self) -> None:
        raw = "\n".join(
            json.dumps({"type": "event", "index": index, "text": "x" * 40})
            for index in range(20)
        )
        with tempfile.TemporaryDirectory() as raw_dir:
            disabled_path = Path(raw_dir) / "disabled.jsonl"
            disabled = persist_raw_jsonl(
                disabled_path, raw, enabled=False, max_bytes=320
            )
            self.assertFalse(disabled["persisted"])
            self.assertFalse(disabled_path.exists())

            bounded_path = Path(raw_dir) / "bounded.jsonl"
            bounded = persist_raw_jsonl(
                bounded_path, raw, enabled=True, max_bytes=320
            )
            self.assertTrue(bounded["persisted"])
            self.assertTrue(bounded["truncated"])
            self.assertLessEqual(bounded_path.stat().st_size, 320)
            events = [
                json.loads(line)
                for line in bounded_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(events[0]["type"], "write_craft_raw_log_truncated")
            self.assertEqual(events[-1]["index"], 19)

    def test_structured_output_extension_matches_python_tool_contract(self) -> None:
        extension = STRUCTURED_OUTPUT_EXTENSION.read_text(encoding="utf-8")
        for tool_name in (
            FACT_JUDGMENT_TOOL,
            READER_RESPONSE_TOOL,
            READER_JUDGMENT_TOOL,
        ):
            self.assertEqual(extension.count(f'name: "{tool_name}"'), 1)
        self.assertEqual(extension.count("terminate: true"), 3)
        self.assertIn('StringEnum(["PASS", "FAIL", "UNCERTAIN"]', extension)
        self.assertIn('["ABSENT", "PRESENT", "UNCERTAIN"]', extension)
        self.assertIn("criterion_index: Type.Integer", extension)
        self.assertIn("presence: ProhibitedBehaviorPresence", extension)
        self.assertIn("Do not supply an overall status", extension)
        self.assertIn("must_not: Type.Array(MustNotCheck", extension)
        metadata = evaluator_metadata()
        self.assertEqual(
            set(metadata),
            {
                "scripts/eval_behavior.py",
                "scripts/eval_contracts.py",
                "scripts/eval_structured_output.ts",
            },
        )
        self.assertTrue(all(len(digest) == 64 for digest in metadata.values()))

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

        malformed = (
            '{"schema":"write-craft.judgment.v1","case_id":"sample",'
            '"status":"PASS","must":[{"criterion":"保留事实",'
            '"status":"PASS","evidence":"候选稿写"原句""}],'
            '"must_not":[],"blocking_issues":[]}'
        )
        with self.assertRaisesRegex(ContractError, "valid JSON"):
            parse_judgment(malformed, case)

    def test_fact_tool_protocol_normalizes_presence_and_computes_status(self) -> None:
        normalized = normalize_fact_tool_arguments(
            {
                "schema": "write-craft.judgment.v1",
                "case_id": "sample",
                "must": [
                    {
                        "criterion_index": 1,
                        "status": "PASS",
                        "evidence": "已保留",
                    }
                ],
                "must_not": [
                    {
                        "criterion_index": 1,
                        "presence": "ABSENT",
                        "evidence": "未出现",
                    }
                ],
                "blocking_issues": [],
            },
            sample_case(),
        )
        self.assertEqual(normalized["status"], "PASS")
        self.assertEqual(normalized["must_not"][0]["status"], "PASS")
        with self.assertRaisesRegex(ContractError, "criterion_index"):
            normalize_fact_tool_arguments(
                {
                    "must": [
                        {
                            "criterion_index": 2,
                            "status": "PASS",
                            "evidence": "已满足",
                        }
                    ],
                    "must_not": [
                        {
                            "criterion_index": 1,
                            "presence": "ABSENT",
                            "evidence": "未出现",
                        }
                    ],
                    "blocking_issues": [],
                },
                sample_case(),
            )
        with self.assertRaisesRegex(ContractError, "must_not presence"):
            normalize_fact_tool_arguments(
                {
                    "must": [
                        {
                            "criterion_index": 1,
                            "status": "PASS",
                            "evidence": "已满足",
                        }
                    ],
                    "must_not": [{"criterion_index": 1, "status": "PASS"}],
                    "blocking_issues": [],
                },
                sample_case(),
            )

    def test_judge_prompt_defines_must_not_status_as_compliance(self) -> None:
        prompt = judge_prompt(sample_case(), "原始材料", "候选稿")
        self.assertIn("criterion_index 标识", prompt)
        self.assertIn("must 数组必须恰好有 1 项", prompt)
        self.assertIn("must_not 数组必须恰好有 1 项", prompt)
        self.assertIn("criterion_index 依次为 [1]", prompt)
        self.assertIn("没有出现填 ABSENT，出现填 PRESENT", prompt)
        self.assertIn("工具不接收顶层 status", prompt)
        self.assertIn("听起来合理或不与来源冲突", prompt)
        self.assertIn("仍应判为无依据新增", prompt)
        self.assertIn("不等于系统永久", prompt)
        self.assertIn("其他常见项目字段", prompt)
        self.assertIn(FACT_JUDGMENT_TOOL, prompt)

        limited_case = sample_case()
        limited_case["limits"] = {"max_han_characters": 500}
        prompt = judge_prompt(limited_case, "原始材料", "候选稿")
        self.assertIn('"max_han_characters": 500', prompt)

    def test_revision_prompt_uses_only_failed_review_feedback(self) -> None:
        case = sample_case()
        judgment = {
            "schema": "write-craft.judgment.v1",
            "case_id": "sample",
            "status": "FAIL",
            "must": [
                {
                    "criterion": "保留事实",
                    "status": "PASS",
                    "evidence": "已保留",
                }
            ],
            "must_not": [
                {
                    "criterion": "编造数据",
                    "status": "FAIL",
                    "evidence": "初稿新增了比例",
                }
            ],
            "blocking_issues": ["删除无来源比例"],
        }
        prompt = revision_prompt(case, "原始材料", "初稿", judgment)
        self.assertIn("唯一允许的一次纠正", prompt)
        self.assertIn("删除无来源比例", prompt)
        self.assertIn("编造数据", prompt)
        self.assertNotIn('"criterion": "保留事实"', prompt)

    def test_deterministic_length_limit_counts_the_whole_candidate(self) -> None:
        case = sample_case()
        case["limits"] = {"max_han_characters": 4}
        candidate = "正文四字\n\n附注两字"
        self.assertEqual(han_character_count(candidate), 8)
        issues = candidate_limit_issues(case, candidate)
        self.assertEqual(len(issues), 1)
        self.assertIn("8 个汉字", issues[0])

        judgment = {
            "schema": "write-craft.judgment.v1",
            "case_id": "sample",
            "status": "PASS",
            "must": [],
            "must_not": [],
            "blocking_issues": [],
        }
        checked = apply_deterministic_checks(judgment, case, candidate)
        self.assertEqual(checked["status"], "FAIL")
        self.assertEqual(checked["blocking_issues"], issues)

    def test_reader_stage_hides_answer_key_and_validates_understanding(self) -> None:
        case = sample_reader_case()
        prompt = reader_prompt(case, "候选文档")
        self.assertIn("首期范围是什么", prompt)
        self.assertNotIn("覆盖 20 名在线客服", prompt)
        self.assertIn("不要把并列出现的事实推断成因果关系", prompt)
        self.assertIn(READER_RESPONSE_TOOL, prompt)

        judgment_prompt = reader_judgment_prompt(
            case,
            "原始材料",
            "候选文档",
            {
                "schema": "write-craft.reader-response.v1",
                "case_id": "sample",
                "restatement": "自由复述",
                "answers": [
                    {
                        "question_id": "scope",
                        "answer": "回答",
                        "evidence": "依据",
                    }
                ],
                "ambiguities": [],
                "natural_questions": [],
            },
        )
        self.assertIn("自由复述、全部答案和歧义列表", judgment_prompt)
        self.assertIn("确定性因果", judgment_prompt)
        self.assertIn(READER_JUDGMENT_TOOL, judgment_prompt)

        response = {
            "schema": "write-craft.reader-response.v1",
            "case_id": "sample",
            "restatement": "文档说明了首期范围。",
            "answers": [
                {
                    "question_id": "scope",
                    "answer": "覆盖 20 名在线客服，不含电话客服。",
                    "evidence": "候选文档的范围段落。",
                }
            ],
            "ambiguities": [],
            "natural_questions": ["预算是多少？"],
        }
        parsed_response = parse_reader_response(
            json.dumps(response, ensure_ascii=False), case
        )
        self.assertEqual(parsed_response["answers"][0]["question_id"], "scope")

        judgment = {
            "schema": "write-craft.reader-judgment.v1",
            "case_id": "sample",
            "status": "PASS",
            "answers": [
                {
                    "question_id": "scope",
                    "status": "PASS",
                    "evidence": "回答与答案要点一致。",
                }
            ],
            "blocking_issues": [],
        }
        parsed_judgment = parse_reader_judgment(
            json.dumps(judgment, ensure_ascii=False), case
        )
        self.assertEqual(parsed_judgment["status"], "PASS")
        judgment["answers"][0]["status"] = "UNCERTAIN"
        with self.assertRaisesRegex(ContractError, "computed status"):
            parse_reader_judgment(json.dumps(judgment, ensure_ascii=False), case)

    def test_aggregate_status_keeps_execution_and_content_failures_distinct(self) -> None:
        self.assertEqual(aggregate_status([]), "NOT_RUN")
        self.assertEqual(aggregate_status(["PASS", "PASS"]), "PASS")
        self.assertEqual(aggregate_status(["PASS", "UNCERTAIN"]), "UNCERTAIN")
        self.assertEqual(aggregate_status(["PASS", "FAIL"]), "FAIL")
        self.assertEqual(aggregate_status(["FAIL", "ERROR"]), "ERROR")

    def test_evaluate_case_runs_reader_only_after_fact_pass(self) -> None:
        case = sample_reader_case()
        case["track"] = "regression"
        candidate = "首期覆盖 20 名在线客服，不含电话客服。"
        fact_judgment = {
            "schema": "write-craft.judgment.v1",
            "case_id": "sample",
            "status": "PASS",
            "must": [
                {
                    "criterion": "保留事实",
                    "status": "PASS",
                    "evidence": "候选稿保留了范围事实。",
                }
            ],
            "must_not": [
                {
                    "criterion": "编造数据",
                    "status": "PASS",
                    "evidence": "候选稿没有新增数据。",
                }
            ],
            "blocking_issues": [],
        }
        reader_response = {
            "schema": "write-craft.reader-response.v1",
            "case_id": "sample",
            "restatement": "这是首期范围说明。",
            "answers": [
                {
                    "question_id": "scope",
                    "answer": "覆盖 20 名在线客服，不含电话客服。",
                    "evidence": "候选稿唯一一句。",
                }
            ],
            "ambiguities": [],
            "natural_questions": [],
        }
        reader_judgment = {
            "schema": "write-craft.reader-judgment.v1",
            "case_id": "sample",
            "status": "PASS",
            "answers": [
                {
                    "question_id": "scope",
                    "status": "PASS",
                    "evidence": "回答与答案要点一致。",
                }
            ],
            "blocking_issues": [],
        }

        outputs = [
            pi_text_output(candidate),
            pi_tool_output(FACT_JUDGMENT_TOOL, fact_tool_arguments(fact_judgment)),
            pi_tool_output(READER_RESPONSE_TOOL, reader_response),
            pi_tool_output(READER_JUDGMENT_TOOL, reader_judgment),
        ]
        with tempfile.TemporaryDirectory() as raw_dir, patch(
            "scripts.eval_behavior.run_command", side_effect=outputs
        ) as mocked:
            result = evaluate_case(
                case=case,
                run_index=1,
                output_root=Path(raw_dir),
                model="generator/model",
                judge_model="judge/model",
                reader_model="reader/model",
                reader_judge_model="reader-judge/model",
                thinking="medium",
                judge_thinking="high",
                reader_thinking="medium",
                reader_judge_thinking="high",
                timeout=1,
            )
            self.assertEqual(mocked.call_count, 4)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(
                result["stages"],
                {
                    "generation": "PASS",
                    "fact_review": "PASS",
                    "revision": "NOT_RUN",
                    "reader": "PASS",
                    "reader_review": "PASS",
                },
            )
            case_dir = Path(raw_dir) / "sample--1"
            self.assertTrue((case_dir / "reader-response.json").is_file())
            self.assertTrue((case_dir / "reader-judgment.json").is_file())
            self.assertEqual(list(case_dir.rglob("*.jsonl")), [])
            self.assertFalse(result["generator"]["raw_log"]["persisted"])

    def test_evaluate_case_skips_reader_after_fact_failure(self) -> None:
        case = sample_reader_case()
        case["track"] = "regression"
        failed_judgment = {
            "schema": "write-craft.judgment.v1",
            "case_id": "sample",
            "status": "FAIL",
            "must": [
                {
                    "criterion": "保留事实",
                    "status": "FAIL",
                    "evidence": "候选稿遗漏事实。",
                }
            ],
            "must_not": [
                {
                    "criterion": "编造数据",
                    "status": "PASS",
                    "evidence": "没有新增数据。",
                }
            ],
            "blocking_issues": [],
        }

        outputs = [
            pi_text_output("候选稿"),
            pi_tool_output(FACT_JUDGMENT_TOOL, fact_tool_arguments(failed_judgment)),
        ]
        with tempfile.TemporaryDirectory() as raw_dir, patch(
            "scripts.eval_behavior.run_command", side_effect=outputs
        ) as mocked:
            result = evaluate_case(
                case=case,
                run_index=1,
                output_root=Path(raw_dir),
                model="generator/model",
                judge_model="judge/model",
                reader_model="reader/model",
                reader_judge_model="reader-judge/model",
                thinking="medium",
                judge_thinking="high",
                reader_thinking="medium",
                reader_judge_thinking="high",
                timeout=1,
            )
            self.assertEqual(mocked.call_count, 2)
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["stages"]["reader"], "NOT_RUN")
            self.assertEqual(result["stages"]["reader_review"], "NOT_RUN")

    def test_evaluate_case_allows_one_fact_correction_then_reader(self) -> None:
        case = sample_reader_case()
        case["track"] = "regression"
        case["max_revisions"] = 1
        failed_judgment = {
            "schema": "write-craft.judgment.v1",
            "case_id": "sample",
            "status": "FAIL",
            "must": [
                {
                    "criterion": "保留事实",
                    "status": "FAIL",
                    "evidence": "初稿遗漏范围。",
                }
            ],
            "must_not": [
                {
                    "criterion": "编造数据",
                    "status": "PASS",
                    "evidence": "没有新增数据。",
                }
            ],
            "blocking_issues": ["补回来源中的范围"],
        }
        passed_judgment = {
            "schema": "write-craft.judgment.v1",
            "case_id": "sample",
            "status": "PASS",
            "must": [
                {
                    "criterion": "保留事实",
                    "status": "PASS",
                    "evidence": "修订稿保留了范围。",
                }
            ],
            "must_not": [
                {
                    "criterion": "编造数据",
                    "status": "PASS",
                    "evidence": "修订稿没有新增数据。",
                }
            ],
            "blocking_issues": [],
        }
        reader_response = {
            "schema": "write-craft.reader-response.v1",
            "case_id": "sample",
            "restatement": "这是首期范围说明。",
            "answers": [
                {
                    "question_id": "scope",
                    "answer": "覆盖 20 名在线客服，不含电话客服。",
                    "evidence": "修订稿的范围句。",
                }
            ],
            "ambiguities": [],
            "natural_questions": [],
        }
        reader_judgment = {
            "schema": "write-craft.reader-judgment.v1",
            "case_id": "sample",
            "status": "PASS",
            "answers": [
                {
                    "question_id": "scope",
                    "status": "PASS",
                    "evidence": "回答准确。",
                }
            ],
            "blocking_issues": [],
        }

        revised_candidate = "首期覆盖 20 名在线客服，不含电话客服。"
        outputs = [
            pi_text_output("遗漏范围的初稿"),
            pi_tool_output(FACT_JUDGMENT_TOOL, fact_tool_arguments(failed_judgment)),
            pi_text_output(revised_candidate),
            pi_tool_output(FACT_JUDGMENT_TOOL, fact_tool_arguments(passed_judgment)),
            pi_tool_output(READER_RESPONSE_TOOL, reader_response),
            pi_tool_output(READER_JUDGMENT_TOOL, reader_judgment),
        ]
        with tempfile.TemporaryDirectory() as raw_dir, patch(
            "scripts.eval_behavior.run_command", side_effect=outputs
        ) as mocked:
            result = evaluate_case(
                case=case,
                run_index=1,
                output_root=Path(raw_dir),
                model="generator/model",
                judge_model="judge/model",
                reader_model="reader/model",
                reader_judge_model="reader-judge/model",
                thinking="medium",
                judge_thinking="high",
                reader_thinking="medium",
                reader_judge_thinking="high",
                timeout=1,
            )
            self.assertEqual(mocked.call_count, 6)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["revisions_used"], 1)
            self.assertEqual(result["initial_attempt"]["status"], "FAIL")
            self.assertEqual(result["stages"]["revision"], "PASS")
            self.assertEqual(result["stages"]["fact_review"], "PASS")
            self.assertEqual(result["candidate_sha256"], sha256_text(revised_candidate))
            case_dir = Path(raw_dir) / "sample--1"
            self.assertTrue((case_dir / "initial" / "candidate.md").is_file())
            self.assertTrue((case_dir / "revision-1" / "candidate.md").is_file())
            self.assertEqual(
                (case_dir / "candidate.md").read_text(encoding="utf-8").strip(),
                revised_candidate,
            )

    def test_evaluate_case_stops_after_one_failed_correction(self) -> None:
        case = sample_case()
        case["track"] = "regression"
        case["max_revisions"] = 1

        def failed_judgment(evidence: str) -> dict[str, object]:
            return {
                "schema": "write-craft.judgment.v1",
                "case_id": "sample",
                "status": "FAIL",
                "must": [
                    {
                        "criterion": "保留事实",
                        "status": "FAIL",
                        "evidence": evidence,
                    }
                ],
                "must_not": [
                    {
                        "criterion": "编造数据",
                        "status": "PASS",
                        "evidence": "没有新增数据。",
                    }
                ],
                "blocking_issues": [evidence],
            }

        outputs = [
            pi_text_output("初稿"),
            pi_tool_output(
                FACT_JUDGMENT_TOOL,
                fact_tool_arguments(failed_judgment("初稿仍遗漏事实")),
            ),
            pi_text_output("修订稿"),
            pi_tool_output(
                FACT_JUDGMENT_TOOL,
                fact_tool_arguments(failed_judgment("修订稿仍遗漏事实")),
            ),
        ]
        with tempfile.TemporaryDirectory() as raw_dir, patch(
            "scripts.eval_behavior.run_command", side_effect=outputs
        ) as mocked:
            result = evaluate_case(
                case=case,
                run_index=1,
                output_root=Path(raw_dir),
                model="generator/model",
                judge_model="judge/model",
                reader_model="reader/model",
                reader_judge_model="reader-judge/model",
                thinking="medium",
                judge_thinking="high",
                reader_thinking="medium",
                reader_judge_thinking="high",
                timeout=1,
            )
            self.assertEqual(mocked.call_count, 4)
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["revisions_used"], 1)
            self.assertEqual(result["stages"]["revision"], "PASS")
            self.assertEqual(result["stages"]["fact_review"], "FAIL")

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
