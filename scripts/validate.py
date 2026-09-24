#!/usr/bin/env python3
"""Validate the Write Craft source tree and pinned upstream contract."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "write-craft"
EVAL_FIXTURES = ROOT / "evals" / "fixtures"
EVAL_BASELINES = ROOT / "evals" / "baselines"
EXPECTED_UPSTREAMS = {
    "agent-skills",
    "anthropic-skills",
    "awesome-claude-skills",
    "elements-of-style",
}
EXPECTED_PACKAGE_FILES = {
    "skills/write-craft",
    "LICENSE",
    "LICENSES",
    "README.md",
    "THIRD_PARTY_NOTICES.md",
    "VERSION",
}
REQUIRED_FILES = {
    ROOT / ".gitmodules",
    ROOT / "AGENTS.md",
    ROOT / "LICENSE",
    ROOT / "README.md",
    ROOT / "THIRD_PARTY_NOTICES.md",
    ROOT / "VERSION",
    ROOT / "package.json",
    ROOT / "upstreams.lock.json",
    ROOT / "docs" / "upstream-absorption.md",
    ROOT / "evals" / "cases.json",
    SKILL / "SKILL.md",
    SKILL / "VERSION",
    SKILL / "agents" / "openai.yaml",
}
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
PUBLIC_HOME = re.compile(
    r"(?:/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\)"
)
PLACEHOLDER = re.compile(r"\b(?:TODO|TBD|FILL_ME)\b|\[(?:To be written|Content here)\]", re.I)
TEXT_SUFFIXES = {"", ".json", ".md", ".txt", ".yaml", ".yml"}


def read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return payload


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def han_character_count(value: str) -> int:
    return len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", value))


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def behavior_case_digest(case: dict[str, object]) -> str:
    source = case.get("source")
    source_file = case.get("source_file")
    has_source = isinstance(source, str) and bool(source.strip())
    has_source_file = isinstance(source_file, str) and bool(source_file.strip())
    if has_source == has_source_file:
        raise ValueError("behavior case must define exactly one source")
    if has_source_file:
        fixture = (ROOT / source_file).resolve()
        try:
            fixture.relative_to(EVAL_FIXTURES.resolve())
        except ValueError as exc:
            raise ValueError("behavior case source_file escapes evals/fixtures") from exc
        source = fixture.read_text(encoding="utf-8")
    return sha256_text(canonical_json({"case": case, "source": source}))


def run(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=cwd, text=True, capture_output=True, check=False
    )


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    parsed: dict[str, str] = {}
    for line in lines[1:end]:
        if not line or line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip().strip('"').strip("'")
    return parsed


def product_text_files() -> list[Path]:
    roots = [
        ROOT / "AGENTS.md",
        ROOT / "README.md",
        ROOT / "THIRD_PARTY_NOTICES.md",
        ROOT / "VERSION",
        ROOT / "package.json",
        ROOT / "upstreams.lock.json",
        ROOT / "docs",
        ROOT / "evals",
        ROOT / "scripts",
        ROOT / "tests",
        ROOT / ".github",
        SKILL,
    ]
    files: list[Path] = []
    for candidate in roots:
        if candidate.is_file():
            files.append(candidate)
        elif candidate.is_dir():
            files.extend(
                path
                for path in candidate.rglob("*")
                if path.is_file()
                and path.suffix in TEXT_SUFFIXES
                and "__pycache__" not in path.parts
            )
    return sorted(set(files))


def validate() -> list[str]:
    errors: list[str] = []

    for path in sorted(REQUIRED_FILES):
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    if errors:
        return errors

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    leaf_version = (SKILL / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        errors.append("VERSION must be semantic x.y.z")
    if leaf_version != version:
        errors.append("skills/write-craft/VERSION must match root VERSION")

    try:
        package = read_json(ROOT / "package.json")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
        package = {}
    if package.get("name") != "@bigking67/write-craft":
        errors.append("package name must be @bigking67/write-craft")
    if package.get("version") != version:
        errors.append("package.json version must match VERSION")
    if package.get("private") is not True:
        errors.append("V0.2 package must remain private to prevent accidental publish")
    if package.get("homepage") != "https://github.com/bigKING67/write-craft#readme":
        errors.append("package homepage must point to the canonical GitHub repository")
    repository = package.get("repository")
    if not isinstance(repository, dict) or repository != {
        "type": "git",
        "url": "git+https://github.com/bigKING67/write-craft.git",
    }:
        errors.append("package repository metadata must point to the canonical Git remote")
    configured_files = package.get("files")
    if not isinstance(configured_files, list) or set(configured_files) != EXPECTED_PACKAGE_FILES:
        errors.append("package.json files must expose only the Skill and legal metadata")
    pi = package.get("pi")
    if not isinstance(pi, dict) or pi.get("skills") != ["skills/write-craft"]:
        errors.append("package.json pi.skills must expose only skills/write-craft")

    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    metadata = frontmatter(skill_text)
    if metadata.get("name") != "write-craft":
        errors.append("SKILL.md frontmatter name must be write-craft")
    description = metadata.get("description", "")
    for required_phrase in ("非技术决策者", "老板版", "不要用于"):
        if required_phrase not in description:
            errors.append(f"SKILL.md description must discriminate routing with: {required_phrase}")

    linked_refs = set(re.findall(r"\(references/([^)]+\.md)\)", skill_text))
    actual_refs = {
        path.name for path in (SKILL / "references").glob("*.md") if path.is_file()
    }
    if linked_refs != actual_refs:
        errors.append(
            "SKILL.md reference links must exactly cover reference files: "
            f"linked={sorted(linked_refs)} actual={sorted(actual_refs)}"
        )

    openai_text = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if "$write-craft" not in openai_text:
        errors.append("openai.yaml default_prompt must mention $write-craft")
    if "allow_implicit_invocation: true" not in openai_text:
        errors.append("write-craft must allow implicit invocation")

    try:
        lock = read_json(ROOT / "upstreams.lock.json")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
        lock = {}
    if lock.get("schema") != "write-craft.upstreams-lock.v1":
        errors.append("unexpected upstream lock schema")
    upstreams = lock.get("upstreams")
    if not isinstance(upstreams, dict) or set(upstreams) != EXPECTED_UPSTREAMS:
        errors.append("upstream lock must contain the four approved upstreams")
        upstreams = {}

    modules = run(
        "git",
        "config",
        "-f",
        ".gitmodules",
        "--get-regexp",
        r"^submodule\..*\.path$",
    )
    if modules.returncode != 0:
        errors.append("unable to read .gitmodules")
        module_paths: set[str] = set()
    else:
        module_paths = {
            line.split(maxsplit=1)[1]
            for line in modules.stdout.splitlines()
            if len(line.split(maxsplit=1)) == 2
        }

    for name, raw_entry in sorted(upstreams.items()):
        if not isinstance(raw_entry, dict):
            errors.append(f"upstream {name} must be an object")
            continue
        relative = raw_entry.get("path")
        pinned = raw_entry.get("commit")
        if not isinstance(relative, str) or relative not in module_paths:
            errors.append(f"upstream {name} path is not registered in .gitmodules")
            continue
        if not isinstance(pinned, str) or not COMMIT.fullmatch(pinned):
            errors.append(f"upstream {name} commit must be a 40-character SHA")
            continue
        checkout = ROOT / relative
        if not checkout.is_dir():
            errors.append(f"upstream {name} checkout is missing")
            continue
        head = run("git", "rev-parse", "HEAD", cwd=checkout)
        if head.returncode != 0 or head.stdout.strip() != pinned:
            errors.append(f"upstream {name} checkout does not match the pinned commit")
        dirty = run("git", "status", "--porcelain", cwd=checkout)
        if dirty.returncode != 0 or dirty.stdout.strip():
            errors.append(f"upstream {name} checkout must remain pristine")

    try:
        evals = read_json(ROOT / "evals" / "cases.json")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
        evals = {}
    cases = evals.get("cases")
    if evals.get("schema") != "write-craft.behavior-cases.v2":
        errors.append("unexpected behavior-cases schema")
    current_cases: dict[str, dict[str, object]] = {}
    current_case_digests: dict[str, str] = {}
    if not isinstance(cases, list) or len(cases) < 10:
        errors.append("behavior suite must contain at least ten cases")
    else:
        ids: set[str] = set()
        required_tags: set[str] = set()
        smoke_cases = 0
        for case in cases:
            if not isinstance(case, dict):
                errors.append("every behavior case must be an object")
                continue
            case_id = case.get("id")
            if not isinstance(case_id, str) or not case_id or case_id in ids:
                errors.append("behavior case ids must be non-empty and unique")
            else:
                ids.add(case_id)
                current_cases[case_id] = case
            tags = case.get("tags")
            if (
                isinstance(tags, list)
                and tags
                and all(isinstance(tag, str) and tag.strip() for tag in tags)
                and len(tags) == len(set(tags))
            ):
                required_tags.update(tags)
            else:
                errors.append(f"behavior case {case_id!r} has invalid tags")
            limits = case.get("limits")
            if limits is not None and (
                not isinstance(limits, dict)
                or set(limits) != {"max_han_characters"}
                or type(limits.get("max_han_characters")) is not int
                or limits["max_han_characters"] < 1
            ):
                errors.append(f"behavior case {case_id!r} has invalid limits")
            suite = case.get("suite")
            if suite not in {"smoke", "full"}:
                errors.append(f"behavior case {case_id!r} has invalid suite")
            elif suite == "smoke":
                smoke_cases += 1

            source = case.get("source")
            source_file = case.get("source_file")
            has_source = isinstance(source, str) and bool(source.strip())
            has_source_file = isinstance(source_file, str) and bool(source_file.strip())
            if has_source == has_source_file:
                errors.append(
                    f"behavior case {case_id!r} must define exactly one of source or source_file"
                )
            elif has_source_file:
                fixture = (ROOT / source_file).resolve()
                try:
                    fixture.relative_to(EVAL_FIXTURES.resolve())
                except ValueError:
                    errors.append(
                        f"behavior case {case_id!r} source_file escapes evals/fixtures"
                    )
                else:
                    if not fixture.is_file():
                        errors.append(
                            f"behavior case {case_id!r} source_file does not exist"
                        )
            expected = case.get("expected")
            if (
                not isinstance(case.get("request"), str)
                or not case["request"].strip()
                or not isinstance(expected, dict)
                or not isinstance(expected.get("must"), list)
                or not isinstance(expected.get("must_not"), list)
            ):
                errors.append(f"behavior case {case_id!r} has an incomplete contract")
            elif any(
                not values
                or not all(isinstance(value, str) and value.strip() for value in values)
                or len(values) != len(set(values))
                for values in (expected["must"], expected["must_not"])
            ):
                errors.append(f"behavior case {case_id!r} has invalid expectations")
            if isinstance(case_id, str) and case_id in current_cases:
                try:
                    current_case_digests[case_id] = behavior_case_digest(case)
                except (OSError, ValueError) as exc:
                    errors.append(f"behavior case {case_id!r} digest failed: {exc}")
        for tag in {"rewrite", "diagnose", "evidence", "routing", "reader-test"}:
            if tag not in required_tags:
                errors.append(f"behavior suite is missing required coverage tag: {tag}")
        if smoke_cases != 4:
            errors.append("behavior suite must contain exactly four smoke cases")

    baseline_path = EVAL_BASELINES / f"pi-v{version}.json"
    if not baseline_path.is_file():
        errors.append(f"missing current behavior baseline: {baseline_path.relative_to(ROOT)}")
        baseline = {}
    else:
        try:
            baseline = read_json(baseline_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
            baseline = {}
    if baseline.get("schema") != "write-craft.behavior-baseline.v1":
        errors.append("unexpected behavior baseline schema")
    if baseline.get("version") != version:
        errors.append("behavior baseline version must match VERSION")
    raw_artifact_roots: list[str] = []
    provenance = baseline.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("behavior baseline provenance must be an object")
    else:
        if provenance.get("skill_sha256") != tree_digest(SKILL):
            errors.append("behavior baseline skill_sha256 does not match the current Skill")
        if provenance.get("independent_contexts") is not True:
            errors.append("behavior baseline must record independent contexts")
        if provenance.get("cross_model_verification") is not False:
            errors.append("behavior baseline must not overclaim cross-model verification")
        if provenance.get("run_mode") not in {
            "single_full_run",
            "segmented_full_with_explicit_rejudge",
        }:
            errors.append("behavior baseline must declare an accepted full-suite run mode")
        raw_artifact_roots = provenance.get("raw_artifact_roots")
        if (
            not isinstance(raw_artifact_roots, list)
            or not raw_artifact_roots
            or len(raw_artifact_roots) != len(set(raw_artifact_roots))
            or not all(
                isinstance(path, str)
                and path.startswith(".artifacts/write-craft-evals/")
                and ".." not in Path(path).parts
                for path in raw_artifact_roots
            )
        ):
            errors.append("behavior baseline raw artifact roots must be unique eval paths")
            raw_artifact_roots = []
    acceptance = baseline.get("acceptance")
    expected_full_result = f"{len(current_cases)}/{len(current_cases)} PASS"
    if (
        not isinstance(acceptance, dict)
        or acceptance.get("full_cases") != expected_full_result
    ):
        errors.append(
            "behavior baseline acceptance must record every current case as PASS"
        )
    baseline_results = baseline.get("results")
    if not isinstance(baseline_results, list):
        errors.append("behavior baseline results must be an array")
    else:
        result_ids = [
            result.get("case_id") if isinstance(result, dict) else None
            for result in baseline_results
        ]
        if Counter(result_ids) != Counter(current_cases.keys()):
            errors.append(
                "behavior baseline must contain exactly one result for every current case"
            )
        rejudge_count = sum(
            isinstance(result, dict)
            and isinstance(result.get("lineage"), str)
            and result["lineage"].startswith("explicit_rejudge_after_")
            for result in baseline_results
        )
        if isinstance(acceptance, dict) and acceptance.get(
            "explicit_rejudges"
        ) != f"{rejudge_count}/{rejudge_count} PASS":
            errors.append(
                "behavior baseline acceptance must match explicit rejudge lineage"
            )
        for result in baseline_results:
            if not isinstance(result, dict) or result.get("status") != "PASS":
                errors.append("every behavior baseline result must be PASS")
                continue
            case_id = result.get("case_id")
            current_case = current_cases.get(case_id) if isinstance(case_id, str) else None
            current_digest = (
                current_case_digests.get(case_id) if isinstance(case_id, str) else None
            )
            if current_case is None or current_digest is None:
                errors.append(f"behavior baseline references an invalid case: {case_id!r}")
            elif result.get("case_digest") != current_digest:
                errors.append(
                    f"behavior baseline case_digest does not match current case: {case_id}"
                )
            source_artifact = result.get("source_artifact")
            source_input_sha256 = result.get("source_input_sha256")
            source_result_sha256 = result.get("source_result_sha256")
            lineage = result.get("lineage")
            if (
                not isinstance(source_artifact, str)
                or not source_artifact.startswith(".artifacts/write-craft-evals/")
                or ".." in Path(source_artifact).parts
            ):
                errors.append(f"behavior baseline source artifact is invalid: {case_id}")
            elif raw_artifact_roots and not any(
                source_artifact.startswith(f"{artifact_root}/")
                for artifact_root in raw_artifact_roots
            ):
                errors.append(
                    f"behavior baseline source artifact is outside its declared roots: {case_id}"
                )
            if not isinstance(source_input_sha256, str) or not SHA256.fullmatch(
                source_input_sha256
            ):
                errors.append(f"behavior baseline input hash is invalid: {case_id}")
            if not isinstance(source_result_sha256, str) or not SHA256.fullmatch(
                source_result_sha256
            ):
                errors.append(f"behavior baseline result hash is invalid: {case_id}")
            if lineage == "original":
                if "original_failure" in result:
                    errors.append(
                        f"behavior baseline original result must not claim a failure: {case_id}"
                    )
            elif (
                isinstance(lineage, str)
                and lineage.startswith("explicit_rejudge_after_")
                and lineage != "explicit_rejudge_after_"
            ):
                original_failure = result.get("original_failure")
                if (
                    not isinstance(original_failure, dict)
                    or original_failure.get("status") != "ERROR"
                    or not isinstance(original_failure.get("error"), str)
                    or not original_failure["error"].strip()
                    or not isinstance(original_failure.get("result_sha256"), str)
                    or not SHA256.fullmatch(original_failure["result_sha256"])
                ):
                    errors.append(
                        f"behavior baseline rejudge lineage is incomplete: {case_id}"
                    )
            else:
                errors.append(f"behavior baseline lineage is invalid: {case_id}")
            candidate = result.get("candidate")
            judgment = result.get("judgment")
            if not isinstance(candidate, str) or not candidate.strip():
                errors.append("behavior baseline candidate must be non-empty")
            elif result.get("candidate_sha256") != sha256_text(candidate):
                errors.append("behavior baseline candidate_sha256 mismatch")
            elif current_case is not None and isinstance(current_case.get("limits"), dict):
                maximum = current_case["limits"].get("max_han_characters")
                actual = han_character_count(candidate)
                metrics = result.get("candidate_metrics")
                if type(maximum) is int and actual > maximum:
                    errors.append(
                        f"behavior baseline candidate exceeds max_han_characters: {case_id}"
                    )
                if not isinstance(metrics, dict) or metrics.get("han_characters") != actual:
                    errors.append(
                        f"behavior baseline candidate metrics are invalid: {case_id}"
                    )
            if (
                not isinstance(judgment, dict)
                or judgment.get("schema") != "write-craft.judgment.v1"
                or judgment.get("status") != "PASS"
            ):
                errors.append("behavior baseline judgment must be a PASS judgment.v1")
            elif result.get("judgment_sha256") != sha256_text(canonical_json(judgment)):
                errors.append("behavior baseline judgment_sha256 mismatch")
            elif current_case is not None:
                if judgment.get("case_id") != case_id:
                    errors.append("behavior baseline judgment case_id mismatch")
                expected = current_case.get("expected")
                if not isinstance(expected, dict):
                    errors.append(f"behavior baseline current case contract is invalid: {case_id}")
                    continue
                for field in ("must", "must_not"):
                    criteria = expected.get(field)
                    checks = judgment.get(field)
                    if not isinstance(criteria, list) or not isinstance(checks, list):
                        errors.append(
                            f"behavior baseline judgment {field} is incomplete: {case_id}"
                        )
                        continue
                    if len(checks) != len(criteria) or any(
                        not isinstance(check, dict)
                        or check.get("criterion") != criterion
                        or check.get("status") != "PASS"
                        or not isinstance(check.get("evidence"), str)
                        or not check["evidence"].strip()
                        for criterion, check in zip(criteria, checks)
                    ):
                        errors.append(
                            f"behavior baseline judgment {field} does not match current contract: {case_id}"
                        )
                if judgment.get("blocking_issues") != []:
                    errors.append(
                        f"behavior baseline PASS judgment contains blocking issues: {case_id}"
                    )

    for path in product_text_files():
        text = path.read_text(encoding="utf-8")
        if PUBLIC_HOME.search(text):
            errors.append(f"public text contains an absolute user-home path: {path.relative_to(ROOT)}")
        if PLACEHOLDER.search(text):
            errors.append(f"unfinished scaffold placeholder: {path.relative_to(ROOT)}")

    notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for marker in ("agent-skills", "doc-coauthoring", "the-elements-of-style", "awesome-claude-skills"):
        if marker not in notices:
            errors.append(f"THIRD_PARTY_NOTICES.md is missing {marker}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("FAIL Write Craft source validation")
        for error in errors:
            print(f"  ERROR: {error}")
        return 1
    print("PASS Write Craft source validation")
    print("  PASS: Skill metadata and progressive references")
    print("  PASS: version and package identity")
    print("  PASS: pinned pristine upstreams and license notices")
    print("  PASS: behavior-case coverage and public-text hygiene")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
