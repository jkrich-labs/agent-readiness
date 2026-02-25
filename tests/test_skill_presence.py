from __future__ import annotations

from pathlib import Path


def test_skill_wrapper_exists() -> None:
    assert Path(".claude/skills/readiness-report/SKILL.md").exists()
