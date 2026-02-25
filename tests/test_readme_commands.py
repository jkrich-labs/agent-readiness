from __future__ import annotations

from pathlib import Path


def test_readme_documents_cli_commands() -> None:
    text = Path("README.md").read_text(encoding="utf-8")
    assert "agent-readiness run" in text
    assert "agent-readiness self-check" in text
