#!/usr/bin/env python3
"""Validate the Write Craft source tree and pinned upstream contract."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "write-craft"
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
        errors.append("V0.1 package must remain private to prevent accidental publish")
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
    if evals.get("schema") != "write-craft.behavior-cases.v1":
        errors.append("unexpected behavior-cases schema")
    if not isinstance(cases, list) or len(cases) < 8:
        errors.append("behavior suite must contain at least eight cases")
    else:
        ids: set[str] = set()
        required_tags: set[str] = set()
        for case in cases:
            if not isinstance(case, dict):
                errors.append("every behavior case must be an object")
                continue
            case_id = case.get("id")
            if not isinstance(case_id, str) or not case_id or case_id in ids:
                errors.append("behavior case ids must be non-empty and unique")
            else:
                ids.add(case_id)
            tags = case.get("tags")
            if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
                required_tags.update(tags)
            expected = case.get("expected")
            if (
                not isinstance(case.get("request"), str)
                or not isinstance(case.get("source"), str)
                or not isinstance(expected, dict)
                or not isinstance(expected.get("must"), list)
                or not isinstance(expected.get("must_not"), list)
            ):
                errors.append(f"behavior case {case_id!r} has an incomplete contract")
        for tag in {"rewrite", "diagnose", "evidence", "routing", "reader-test"}:
            if tag not in required_tags:
                errors.append(f"behavior suite is missing required coverage tag: {tag}")

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
