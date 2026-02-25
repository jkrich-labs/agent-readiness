from __future__ import annotations

from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_readme_documents_cli_commands() -> None:
    text = (_PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "agent-readiness run" in text
    assert "agent-readiness self-check" in text
