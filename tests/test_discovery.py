from __future__ import annotations

from pathlib import Path

from agent_readiness.discovery import discover_repository


def test_discovery_detects_backend_and_frontend_apps(tmp_path: Path) -> None:
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend" / "pyproject.toml").write_text("[project]\nname='backend'\n")

    (tmp_path / "frontend").mkdir()
    (tmp_path / "frontend" / "package.json").write_text('{"name":"frontend"}\n')
    (tmp_path / "frontend" / "tsconfig.json").write_text('{"compilerOptions":{"strict":true}}\n')

    result = discover_repository(tmp_path)
    assert "backend" in result.apps
    assert "frontend" in result.apps
