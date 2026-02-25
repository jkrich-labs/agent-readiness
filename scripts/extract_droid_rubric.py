#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

PROMPT_MARKER = "You are the Agent Readiness Droid"
IDS_MARKER = "You used ONLY these exact IDs:"
REPO_HEADER = "### Repository Scope Criteria"
APP_HEADER = "### Application Scope Criteria"


@dataclass(frozen=True)
class ParsedPrompt:
    source_path: Path
    extracted_at: str
    repository_scope: list[str]
    application_scope: list[str]
    all_ids_ordered: list[str]
    metadata: dict[str, dict[str, object]]
    source_sha256: str


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _run_command(cmd: list[str]) -> str | None:
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except Exception:
        return None
    return cp.stdout.strip()


def _iter_prompt_texts(jsonl_path: Path) -> Iterable[str]:
    for line in jsonl_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = obj.get("message") or {}
        for content in message.get("content") or []:
            if isinstance(content, dict) and content.get("type") == "text":
                text = content.get("text")
                if isinstance(text, str):
                    yield text


def _parse_criterion_line(line: str) -> tuple[str, dict[str, object]] | None:
    # Format:
    # - **criterion_id** (Level 3) [Skippable]: Description
    # - **criterion_id** (Level 3): Description
    match = re.match(
        r"^- \*\*([a-z0-9_]+)\*\* \(Level (\d)\)(?: \[(Skippable)\])?: (.+)$",
        line.strip(),
    )
    if not match:
        return None

    criterion_id, level, skippable, description = match.groups()
    return (
        criterion_id,
        {
            "level": int(level),
            "skippable": bool(skippable),
            "description": description.strip(),
        },
    )


def _parse_prompt(text: str, source_path: Path) -> ParsedPrompt | None:
    if PROMPT_MARKER not in text or IDS_MARKER not in text:
        return None

    if REPO_HEADER not in text or APP_HEADER not in text:
        return None

    try:
        repo_section = text.split(REPO_HEADER, 1)[1].split(APP_HEADER, 1)[0]
        app_section = text.split(APP_HEADER, 1)[1].split("**For each criterion, provide:**", 1)[0]
    except IndexError:
        return None

    repository_scope: list[str] = []
    application_scope: list[str] = []
    metadata: dict[str, dict[str, object]] = {}

    for raw_line in repo_section.splitlines():
        parsed = _parse_criterion_line(raw_line)
        if parsed is None:
            continue
        criterion_id, item = parsed
        item["scope"] = "repository"
        repository_scope.append(criterion_id)
        metadata[criterion_id] = item

    for raw_line in app_section.splitlines():
        parsed = _parse_criterion_line(raw_line)
        if parsed is None:
            continue
        criterion_id, item = parsed
        item["scope"] = "application"
        application_scope.append(criterion_id)
        metadata[criterion_id] = item

    id_line = None
    for line in text.splitlines():
        if IDS_MARKER in line:
            id_line = line
            break
    if id_line is None:
        return None

    all_ids_ordered = [
        part.strip()
        for part in id_line.split(IDS_MARKER, 1)[1].split(",")
        if part.strip()
    ]

    # Guardrail: exact rubric expected.
    if len(repository_scope) != 43 or len(application_scope) != 38:
        return None
    if len(all_ids_ordered) != 81:
        return None
    if all_ids_ordered != repository_scope + application_scope:
        return None

    return ParsedPrompt(
        source_path=source_path,
        extracted_at=datetime.now(UTC).isoformat(),
        repository_scope=repository_scope,
        application_scope=application_scope,
        all_ids_ordered=all_ids_ordered,
        metadata=metadata,
        source_sha256=_sha256_text(text),
    )


def _find_prompt(sessions_root: Path) -> ParsedPrompt:
    candidates: list[tuple[float, ParsedPrompt]] = []

    for jsonl_path in sessions_root.rglob("*.jsonl"):
        try:
            mtime = jsonl_path.stat().st_mtime
        except OSError:
            continue

        for text in _iter_prompt_texts(jsonl_path):
            parsed = _parse_prompt(text, jsonl_path)
            if parsed is not None:
                candidates.append((mtime, parsed))

    if not candidates:
        raise RuntimeError(
            f"No Droid readiness prompt found under {sessions_root}"
        )

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def _write_rubric(parsed: ParsedPrompt, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    criteria_order_path = out_dir / "criteria_order.txt"
    criteria_scope_path = out_dir / "criteria_scope.json"
    scoring_rules_path = out_dir / "scoring_rules.json"
    provenance_path = out_dir / "provenance.json"

    criteria_order_path.write_text("\n".join(parsed.all_ids_ordered) + "\n", encoding="utf-8")

    criteria_scope = {
        "version": out_dir.name,
        "repository_scope": parsed.repository_scope,
        "application_scope": parsed.application_scope,
        "criteria": parsed.metadata,
    }
    criteria_scope_path.write_text(json.dumps(criteria_scope, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    scoring_rules = {
        "skip_policy": "exclude_null_numerator",
        "pass_rate_formula": "average(numerator/denominator) over non-skipped criteria",
        "level_bands": [
            {"level": 1, "min_inclusive": 0.0, "max_exclusive": 0.2},
            {"level": 2, "min_inclusive": 0.2, "max_exclusive": 0.4},
            {"level": 3, "min_inclusive": 0.4, "max_exclusive": 0.6},
            {"level": 4, "min_inclusive": 0.6, "max_exclusive": 0.8},
            {"level": 5, "min_inclusive": 0.8, "max_inclusive": 1.0},
        ],
    }
    scoring_rules_path.write_text(json.dumps(scoring_rules, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    droid_version = _run_command(["droid", "--version"])
    provenance = {
        "rubric_version": out_dir.name,
        "extracted_at": parsed.extracted_at,
        "source": {
            "path": str(parsed.source_path),
            "kind": "factory_session_prompt",
            "sha256": parsed.source_sha256,
            "marker": PROMPT_MARKER,
        },
        "tooling": {
            "extract_script": "scripts/extract_droid_rubric.py",
            "droid_version": droid_version,
        },
        "artifacts": {
            "criteria_order_sha256": _sha256_text(criteria_order_path.read_text(encoding="utf-8")),
            "criteria_scope_sha256": _sha256_text(criteria_scope_path.read_text(encoding="utf-8")),
            "scoring_rules_sha256": _sha256_text(scoring_rules_path.read_text(encoding="utf-8")),
        },
    }
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract frozen Droid readiness rubric from local session evidence")
    parser.add_argument(
        "--sessions-root",
        type=Path,
        default=Path.home() / ".factory" / "sessions",
        help="Path containing Factory session *.jsonl files",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("rubric/droid/v0.62.1"),
        help="Output directory for frozen rubric artifacts",
    )
    args = parser.parse_args()

    parsed = _find_prompt(args.sessions_root)
    _write_rubric(parsed, args.out_dir)

    print(f"Wrote rubric to {args.out_dir}")
    print(f"source: {parsed.source_path}")
    print(f"criteria: {len(parsed.all_ids_ordered)} ({len(parsed.repository_scope)} repo, {len(parsed.application_scope)} app)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
