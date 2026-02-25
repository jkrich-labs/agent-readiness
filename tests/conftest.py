from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.fixture()
def sample_repo(tmp_path: Path) -> Path:
    (tmp_path / "README.md").write_text("# Sample Repo\n\nThis repository is used for readiness tests.\n")
    (tmp_path / "AGENTS.md").write_text("# Agent Notes\n\nUse `python3 -m pytest` and `npm run build`.\n")
    (tmp_path / ".gitignore").write_text(".env\nnode_modules\n.venv\ndist\nbuild\n")
    (tmp_path / ".env.example").write_text("API_KEY=\n")

    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "pyproject.toml").write_text(
        """
[project]
name = "backend"
version = "0.1.0"

[tool.pytest.ini_options]
addopts = "--durations=10"
""".strip()
        + "\n"
    )
    (backend / "tests").mkdir()
    (backend / "tests" / "test_basic.py").write_text("def test_ok():\n    assert True\n")
    (backend / "models.py").write_text("class Widget:\n    pass\n")

    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text(
        '{"name":"frontend","scripts":{"build":"vite build","test":"vitest"},"devDependencies":{"vitest":"^1.0.0"}}\n'
    )
    (frontend / "tsconfig.json").write_text('{"compilerOptions":{"strict":true}}\n')
    (frontend / "src").mkdir()
    (frontend / "src" / "main.ts").write_text("export const ready = true;\n")
    (frontend / "src" / "main.spec.ts").write_text("import { describe, it, expect } from 'vitest';\n")

    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text(
        """
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo test
""".strip()
        + "\n"
    )

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True, text=True)

    return tmp_path
