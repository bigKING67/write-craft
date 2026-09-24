#!/usr/bin/env python3
"""Run isolated Write Craft behavior evaluations through Pi.

The generator loads only the repository Skill and may use the read tool so the
Skill can open its progressive references. The judge runs in a fresh context
without tools or skills. Model calls are opt-in and never run in CI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals" / "cases.json"
FIXTURES_ROOT = ROOT / "evals" / "fixtures"
SKILL_ROOT = ROOT / "skills" / "write-craft"
SCHEMA = "write-craft.behavior-cases.v2"
JUDGMENT_SCHEMA = "write-craft.judgment.v1"
VALID_SUITES = {"smoke", "full"}
VALID_STATUSES = {"PASS", "FAIL", "UNCERTAIN"}


class ContractError(ValueError):
    """Raised when an evaluation contract or model response is invalid."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def skill_digest(skill_root: Path = SKILL_ROOT) -> str:
    digest = hashlib.sha256()
    for path in sorted(skill_root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(skill_root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def resolve_fixture(root: Path, raw_path: str) -> Path:
    fixture_root = (root / "evals" / "fixtures").resolve()
    candidate = (root / raw_path).resolve()
    try:
        candidate.relative_to(fixture_root)
    except ValueError as exc:
        raise ContractError(f"source_file must stay under evals/fixtures: {raw_path}") from exc
    if not candidate.is_file():
        raise ContractError(f"source_file does not exist: {raw_path}")
    return candidate


def validate_payload(payload: object, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["behavior cases must contain a JSON object"]
    if payload.get("schema") != SCHEMA:
        errors.append(f"behavior cases schema must be {SCHEMA}")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["behavior cases must contain a non-empty cases array"]

    ids: set[str] = set()
    for index, case in enumerate(cases):
        label = f"case[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{label}.id must be a non-empty string")
            case_id = label
        elif case_id in ids:
            errors.append(f"duplicate behavior case id: {case_id}")
        else:
            ids.add(case_id)
        suite = case.get("suite")
        if suite not in VALID_SUITES:
            errors.append(f"{case_id}.suite must be one of {sorted(VALID_SUITES)}")
        tags = case.get("tags")
        if (
            not isinstance(tags, list)
            or not tags
            or not all(isinstance(tag, str) and tag.strip() for tag in tags)
            or len(tags) != len(set(tags))
        ):
            errors.append(f"{case_id}.tags must be unique non-empty strings")
        if not isinstance(case.get("request"), str) or not case["request"].strip():
            errors.append(f"{case_id}.request must be a non-empty string")

        has_source = isinstance(case.get("source"), str) and bool(case["source"].strip())
        has_source_file = isinstance(case.get("source_file"), str) and bool(
            case["source_file"].strip()
        )
        if has_source == has_source_file:
            errors.append(f"{case_id} must define exactly one of source or source_file")
        elif has_source_file:
            try:
                resolve_fixture(root, case["source_file"])
            except ContractError as exc:
                errors.append(f"{case_id}: {exc}")

        expected = case.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{case_id}.expected must be an object")
            continue
        for field in ("must", "must_not"):
            values = expected.get(field)
            if (
                not isinstance(values, list)
                or not values
                or not all(isinstance(value, str) and value.strip() for value in values)
                or len(values) != len(set(values))
            ):
                errors.append(f"{case_id}.expected.{field} must be unique non-empty strings")
    return errors


def load_cases(path: Path = CASES_PATH, root: Path = ROOT) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"unable to read behavior cases: {exc}") from exc
    errors = validate_payload(payload, root)
    if errors:
        raise ContractError("; ".join(errors))
    return payload["cases"]


def case_source(case: dict[str, Any], root: Path = ROOT) -> str:
    if "source" in case:
        return case["source"]
    return resolve_fixture(root, case["source_file"]).read_text(encoding="utf-8")


def select_cases(
    cases: list[dict[str, Any]], suite: str, case_ids: list[str]
) -> list[dict[str, Any]]:
    if case_ids:
        requested = set(case_ids)
        available = {case["id"] for case in cases}
        missing = sorted(requested - available)
        if missing:
            raise ContractError(f"unknown case ids: {missing}")
        return [case for case in cases if case["id"] in requested]
    if suite == "smoke":
        return [case for case in cases if case["suite"] == "smoke"]
    if suite == "full":
        return list(cases)
    raise ContractError(f"unknown suite: {suite}")


def message_text(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return ""
    parts = [
        block.get("text", "")
        for block in content
        if isinstance(block, dict)
        and block.get("type") == "text"
        and isinstance(block.get("text"), str)
    ]
    return "".join(parts).strip()


def extract_final_assistant(jsonl: str) -> dict[str, Any]:
    final: dict[str, Any] | None = None
    malformed: list[int] = []
    for line_number, line in enumerate(jsonl.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            malformed.append(line_number)
            continue
        if (
            isinstance(event, dict)
            and event.get("type") == "message_end"
            and isinstance(event.get("message"), dict)
            and event["message"].get("role") == "assistant"
        ):
            final = event["message"]
    if malformed:
        raise ContractError(f"Pi JSONL contains malformed lines: {malformed}")
    if final is None:
        raise ContractError("Pi JSONL contains no final assistant message")
    if final.get("errorMessage") or final.get("stopReason") in {"error", "aborted"}:
        raise ContractError(
            f"assistant message ended with an error: {final.get('errorMessage') or final.get('stopReason')}"
        )
    text = message_text(final)
    if not text:
        raise ContractError("final assistant message contains no text")
    return {"text": text, "message": final}


def strip_json_fence(text: str) -> str:
    match = re.fullmatch(r"\s*```(?:json)?\s*(.*?)\s*```\s*", text, flags=re.S | re.I)
    return match.group(1) if match else text.strip()


def parse_judgment(text: str, case: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = json.loads(strip_json_fence(text))
    except json.JSONDecodeError as exc:
        raise ContractError(f"judge did not return valid JSON: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema") != JUDGMENT_SCHEMA:
        raise ContractError(f"judge schema must be {JUDGMENT_SCHEMA}")
    if payload.get("case_id") != case["id"]:
        raise ContractError("judge case_id does not match the evaluated case")

    expected = case["expected"]
    for field in ("must", "must_not"):
        checks = payload.get(field)
        if not isinstance(checks, list) or len(checks) != len(expected[field]):
            raise ContractError(f"judge {field} checks do not cover every criterion")
        for criterion, check in zip(expected[field], checks, strict=True):
            if not isinstance(check, dict) or check.get("criterion") != criterion:
                raise ContractError(f"judge {field} criteria changed or reordered")
            if check.get("status") not in VALID_STATUSES:
                raise ContractError(f"judge {field} status is invalid")
            if not isinstance(check.get("evidence"), str) or not check["evidence"].strip():
                raise ContractError(f"judge {field} evidence must be non-empty")

    blocking = payload.get("blocking_issues")
    if not isinstance(blocking, list) or not all(isinstance(item, str) for item in blocking):
        raise ContractError("judge blocking_issues must be a string array")

    statuses = [
        check["status"]
        for field in ("must", "must_not")
        for check in payload[field]
    ]
    computed = (
        "PASS"
        if all(status == "PASS" for status in statuses)
        else "FAIL"
        if "FAIL" in statuses
        else "UNCERTAIN"
    )
    if payload.get("status") != computed:
        raise ContractError(
            f"judge status {payload.get('status')!r} does not match computed status {computed}"
        )
    payload["status"] = computed
    return payload


def generator_prompt(case: dict[str, Any], source: str) -> str:
    return f"""/skill:write-craft

这是一次隔离的真实写作任务。请直接完成用户请求，不要讨论评测过程，也不要提及隐藏的验收标准。

【用户请求】
{case['request']}

【原始材料】
{source}
"""


def judge_prompt(case: dict[str, Any], source: str, candidate: str) -> str:
    contract = json.dumps(case["expected"], ensure_ascii=False, indent=2)
    return f"""你是一个独立的文档行为验收员。你没有参与候选稿的生成，只能根据本消息中的请求、原始材料、候选稿和验收合同判分。不要重写候选稿。

判分规则：
- must 项只有在候选稿明确满足且没有越过原始材料证据边界时才为 PASS。
- must_not 项只有在对应禁用行为没有出现时才为 PASS；出现则为 FAIL。
- 无法确定时使用 UNCERTAIN。不要用常识替候选稿补齐。
- evidence 必须引用或准确指出候选稿中的依据；缺少依据时说明缺失。
- 每一个 status 字段的值必须精确等于 PASS、FAIL 或 UNCERTAIN 三者之一，禁止在 status 中添加解释、空格或其他文字；所有解释只能写进 evidence。
- 最终只输出一个 JSON 对象，不要使用 Markdown 代码块或附加说明。

JSON 结构：
{{
  "schema": "{JUDGMENT_SCHEMA}",
  "case_id": "{case['id']}",
  "status": "PASS | FAIL | UNCERTAIN",
  "must": [{{"criterion": "原样复制验收项", "status": "PASS | FAIL | UNCERTAIN", "evidence": "候选稿依据或缺失说明"}}],
  "must_not": [{{"criterion": "原样复制验收项", "status": "PASS | FAIL | UNCERTAIN", "evidence": "未出现或出现的依据"}}],
  "blocking_issues": ["阻止通过的问题；没有则为空数组"]
}}

【用户请求】
{case['request']}

【原始材料】
{source}

【候选稿】
{candidate}

【验收合同】
{contract}
"""


def run_command(args: list[str], timeout: int) -> dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            args,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
        return {
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "duration_seconds": round(time.monotonic() - started, 3),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else exc.stdout or ""
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else exc.stderr or ""
        return {
            "returncode": None,
            "stdout": stdout,
            "stderr": stderr,
            "duration_seconds": round(time.monotonic() - started, 3),
            "timed_out": True,
        }
    except FileNotFoundError as exc:
        return {
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "duration_seconds": round(time.monotonic() - started, 3),
            "timed_out": False,
        }


def pi_args(
    *, prompt: str, model: str, thinking: str, with_skill: bool
) -> list[str]:
    args = [
        "pi",
        "--mode",
        "json",
        "--no-session",
        "--no-skills",
        "--no-extensions",
        "--no-context-files",
        "--no-approve",
        "--model",
        model,
        "--thinking",
        thinking,
    ]
    if with_skill:
        args.extend(["--tools", "read", "--skill", str(SKILL_ROOT)])
    else:
        args.append("--no-tools")
    args.append(prompt)
    return args


def safe_message_metadata(message: dict[str, Any]) -> dict[str, Any]:
    return {
        key: message[key]
        for key in ("provider", "model", "usage", "stopReason", "timestamp")
        if key in message
    }


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git_state() -> dict[str, Any]:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    return {
        "revision": revision.stdout.strip() if revision.returncode == 0 else None,
        "dirty": bool(status.stdout.strip()) if status.returncode == 0 else None,
    }


def pi_version() -> str | None:
    completed = subprocess.run(
        ["pi", "--version"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def evaluate_case(
    *,
    case: dict[str, Any],
    run_index: int,
    output_root: Path,
    model: str,
    judge_model: str,
    thinking: str,
    judge_thinking: str,
    timeout: int,
) -> dict[str, Any]:
    source = case_source(case)
    case_dir = output_root / f"{case['id']}--{run_index}"
    case_dir.mkdir(parents=True)
    input_payload = {
        "case": case,
        "source": source,
        "case_digest": sha256_text(canonical_json({"case": case, "source": source})),
        "run_index": run_index,
    }
    write_json(case_dir / "input.json", input_payload)

    generated = run_command(
        pi_args(
            prompt=generator_prompt(case, source),
            model=model,
            thinking=thinking,
            with_skill=True,
        ),
        timeout,
    )
    (case_dir / "generator.jsonl").write_text(generated["stdout"], encoding="utf-8")
    (case_dir / "generator.stderr.txt").write_text(generated["stderr"], encoding="utf-8")
    result: dict[str, Any] = {
        "case_id": case["id"],
        "run_index": run_index,
        "status": "ERROR",
        "case_digest": input_payload["case_digest"],
        "generator": {
            "model": model,
            "thinking": thinking,
            "returncode": generated["returncode"],
            "duration_seconds": generated["duration_seconds"],
            "timed_out": generated["timed_out"],
        },
        "judge": {"model": judge_model, "thinking": judge_thinking},
    }
    if generated["timed_out"]:
        result["error"] = "generator timed out"
        write_json(case_dir / "result.json", result)
        return result
    if generated["returncode"] != 0:
        result["error"] = f"generator exited with {generated['returncode']}"
        write_json(case_dir / "result.json", result)
        return result
    try:
        final = extract_final_assistant(generated["stdout"])
    except ContractError as exc:
        result["error"] = str(exc)
        write_json(case_dir / "result.json", result)
        return result

    candidate = final["text"]
    (case_dir / "candidate.md").write_text(candidate + "\n", encoding="utf-8")
    result["generator"]["message"] = safe_message_metadata(final["message"])
    result["candidate_sha256"] = sha256_text(candidate)

    judged = run_command(
        pi_args(
            prompt=judge_prompt(case, source, candidate),
            model=judge_model,
            thinking=judge_thinking,
            with_skill=False,
        ),
        timeout,
    )
    (case_dir / "judge.jsonl").write_text(judged["stdout"], encoding="utf-8")
    (case_dir / "judge.stderr.txt").write_text(judged["stderr"], encoding="utf-8")
    result["judge"].update(
        {
            "returncode": judged["returncode"],
            "duration_seconds": judged["duration_seconds"],
            "timed_out": judged["timed_out"],
        }
    )
    if judged["timed_out"]:
        result["error"] = "judge timed out"
        write_json(case_dir / "result.json", result)
        return result
    if judged["returncode"] != 0:
        result["error"] = f"judge exited with {judged['returncode']}"
        write_json(case_dir / "result.json", result)
        return result
    try:
        judge_final = extract_final_assistant(judged["stdout"])
        judgment = parse_judgment(judge_final["text"], case)
    except ContractError as exc:
        result["error"] = str(exc)
        write_json(case_dir / "result.json", result)
        return result

    write_json(case_dir / "judgment.json", judgment)
    result["judge"]["message"] = safe_message_metadata(judge_final["message"])
    result["judgment_sha256"] = sha256_text(canonical_json(judgment))
    result["status"] = judgment["status"]
    result["blocking_issues"] = judgment["blocking_issues"]
    write_json(case_dir / "result.json", result)
    return result


def rejudge_case(
    *,
    case_dir: Path,
    judge_model: str,
    judge_thinking: str,
    timeout: int,
) -> dict[str, Any]:
    case_dir = case_dir.resolve()
    input_path = case_dir / "input.json"
    candidate_path = case_dir / "candidate.md"
    if not input_path.is_file() or not candidate_path.is_file():
        raise ContractError("--rejudge directory must contain input.json and candidate.md")
    try:
        input_payload = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"unable to read rejudge input: {exc}") from exc
    case = input_payload.get("case")
    source = input_payload.get("source")
    if not isinstance(case, dict) or not isinstance(source, str):
        raise ContractError("rejudge input.json is missing case or source")
    contract_errors = validate_payload({"schema": SCHEMA, "cases": [case]})
    if contract_errors:
        raise ContractError("invalid rejudge case: " + "; ".join(contract_errors))
    candidate = candidate_path.read_text(encoding="utf-8").strip()
    if not candidate:
        raise ContractError("rejudge candidate.md is empty")

    index = 1
    while (case_dir / f"rejudge-{index}").exists():
        index += 1
    output_dir = case_dir / f"rejudge-{index}"
    output_dir.mkdir()
    judged = run_command(
        pi_args(
            prompt=judge_prompt(case, source, candidate),
            model=judge_model,
            thinking=judge_thinking,
            with_skill=False,
        ),
        timeout,
    )
    (output_dir / "judge.jsonl").write_text(judged["stdout"], encoding="utf-8")
    (output_dir / "judge.stderr.txt").write_text(judged["stderr"], encoding="utf-8")
    result: dict[str, Any] = {
        "schema": "write-craft.rejudge.v1",
        "case_id": case.get("id"),
        "source_case_dir": str(case_dir),
        "candidate_sha256": sha256_text(candidate),
        "judge": {
            "model": judge_model,
            "thinking": judge_thinking,
            "returncode": judged["returncode"],
            "duration_seconds": judged["duration_seconds"],
            "timed_out": judged["timed_out"],
        },
        "status": "ERROR",
    }
    if judged["timed_out"]:
        result["error"] = "judge timed out"
    elif judged["returncode"] != 0:
        result["error"] = f"judge exited with {judged['returncode']}"
    else:
        try:
            judge_final = extract_final_assistant(judged["stdout"])
            judgment = parse_judgment(judge_final["text"], case)
        except ContractError as exc:
            result["error"] = str(exc)
        else:
            write_json(output_dir / "judgment.json", judgment)
            result["judge"]["message"] = safe_message_metadata(judge_final["message"])
            result["judgment_sha256"] = sha256_text(canonical_json(judgment))
            result["status"] = judgment["status"]
            result["blocking_issues"] = judgment["blocking_issues"]
    write_json(output_dir / "result.json", result)
    result["output"] = str(output_dir)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="Pi generator model, e.g. anthropic/claude-sonnet-4-6")
    parser.add_argument(
        "--judge-model",
        required=True,
        help="Pi judge model, e.g. anthropic/claude-sonnet-4-6",
    )
    parser.add_argument("--suite", choices=sorted(VALID_SUITES), default="smoke")
    parser.add_argument("--case", action="append", default=[], dest="case_ids")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--thinking", default="medium")
    parser.add_argument("--judge-thinking", default="high")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--rejudge",
        type=Path,
        help="explicitly rejudge an existing case artifact without regenerating it",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.runs < 1:
        print("ERROR: --runs must be at least 1", file=sys.stderr)
        return 2
    if args.timeout < 1:
        print("ERROR: --timeout must be at least 1", file=sys.stderr)
        return 2
    if args.rejudge:
        try:
            result = rejudge_case(
                case_dir=args.rejudge,
                judge_model=args.judge_model,
                judge_thinking=args.judge_thinking,
                timeout=args.timeout,
            )
        except ContractError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["status"] == "PASS" else 1
    if not args.model:
        print("ERROR: --model is required unless --rejudge is used", file=sys.stderr)
        return 2
    try:
        cases = select_cases(load_cases(), args.suite, args.case_ids)
    except ContractError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_root = (
        args.output_dir.resolve()
        if args.output_dir
        else ROOT / ".artifacts" / "write-craft-evals" / timestamp
    )
    if output_root.exists():
        print(f"ERROR: output directory already exists: {output_root}", file=sys.stderr)
        return 2
    output_root.mkdir(parents=True)

    started_at = utc_now()
    results: list[dict[str, Any]] = []
    aborted = False
    for case in cases:
        for run_index in range(1, args.runs + 1):
            print(f"RUN {case['id']} #{run_index}", file=sys.stderr, flush=True)
            result = evaluate_case(
                case=case,
                run_index=run_index,
                output_root=output_root,
                model=args.model,
                judge_model=args.judge_model,
                thinking=args.thinking,
                judge_thinking=args.judge_thinking,
                timeout=args.timeout,
            )
            results.append(result)
            print(f"  {result['status']}", file=sys.stderr, flush=True)
            if result["status"] == "ERROR":
                aborted = True
                break
        if aborted:
            break

    summary = {
        "schema": "write-craft.eval-run.v1",
        "started_at": started_at,
        "finished_at": utc_now(),
        "pi_version": pi_version(),
        "git": git_state(),
        "skill_sha256": skill_digest(),
        "cases_schema": SCHEMA,
        "suite": args.suite,
        "selected_case_ids": [case["id"] for case in cases],
        "runs_per_case": args.runs,
        "generator": {"model": args.model, "thinking": args.thinking},
        "judge": {"model": args.judge_model, "thinking": args.judge_thinking},
        "timeout_seconds": args.timeout,
        "aborted_after_system_error": aborted,
        "status": "PASS" if results and all(item["status"] == "PASS" for item in results) else "FAIL",
        "results": results,
    }
    write_json(output_root / "run.json", summary)
    print(json.dumps({"status": summary["status"], "output": str(output_root)}, ensure_ascii=False))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
