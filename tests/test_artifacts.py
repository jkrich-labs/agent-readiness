from __future__ import annotations

from agent_readiness.artifacts import write_artifacts
from agent_readiness.runner import ReadinessRunner, RunOptions


def test_artifacts_writer_creates_three_outputs(tmp_path, sample_repo) -> None:
    out = tmp_path / "out"
    runner = ReadinessRunner(repo_path=sample_repo, options=RunOptions(execute_commands=False))
    envelope = runner.evaluate()
    write_artifacts(envelope, runner.rubric, out)

    assert (out / "readiness-report.json").exists()
    assert (out / "readiness-report.md").exists()
    assert (out / "readiness-actions.json").exists()


def test_write_html_dashboard_creates_file(tmp_path, sample_repo) -> None:
    from agent_readiness.artifacts import write_html_dashboard
    from agent_readiness.rubric import load_frozen_rubric, load_remediation_templates
    from agent_readiness.runner import ReadinessRunner, RunOptions

    out = tmp_path / "out"
    runner = ReadinessRunner(repo_path=sample_repo, options=RunOptions(execute_commands=False))
    envelope = runner.evaluate()
    rubric = load_frozen_rubric()
    templates = load_remediation_templates()

    path = write_html_dashboard(envelope, rubric, templates, out)
    assert path.exists()
    assert path.name == "readiness-dashboard.html"


def test_write_html_dashboard_contains_embedded_data(tmp_path, sample_repo) -> None:
    from agent_readiness.artifacts import write_html_dashboard
    from agent_readiness.rubric import load_frozen_rubric, load_remediation_templates
    from agent_readiness.runner import ReadinessRunner, RunOptions

    out = tmp_path / "out"
    runner = ReadinessRunner(repo_path=sample_repo, options=RunOptions(execute_commands=False))
    envelope = runner.evaluate()
    rubric = load_frozen_rubric()
    templates = load_remediation_templates()

    path = write_html_dashboard(envelope, rubric, templates, out)
    html = path.read_text(encoding="utf-8")

    assert "lint_config" in html
    assert "<!DOCTYPE html>" in html or "<!doctype html>" in html


def test_write_html_dashboard_is_valid_html(tmp_path, sample_repo) -> None:
    from agent_readiness.artifacts import write_html_dashboard
    from agent_readiness.rubric import load_frozen_rubric, load_remediation_templates
    from agent_readiness.runner import ReadinessRunner, RunOptions

    out = tmp_path / "out"
    runner = ReadinessRunner(repo_path=sample_repo, options=RunOptions(execute_commands=False))
    envelope = runner.evaluate()
    rubric = load_frozen_rubric()
    templates = load_remediation_templates()

    path = write_html_dashboard(envelope, rubric, templates, out)
    html = path.read_text(encoding="utf-8")

    assert "</html>" in html
    assert "<script>" in html
