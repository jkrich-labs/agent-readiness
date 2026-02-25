from __future__ import annotations

from agent_readiness.artifacts import write_artifacts
from agent_readiness.runner import ReadinessRunner, RunOptions


def test_artifacts_writer_creates_four_outputs(tmp_path, sample_repo) -> None:
    from agent_readiness.rubric import load_remediation_templates

    out = tmp_path / "out"
    runner = ReadinessRunner(repo_path=sample_repo, options=RunOptions(execute_commands=False))
    envelope = runner.evaluate()
    remediation = load_remediation_templates()
    report_json, report_md, actions_json, dashboard_html = write_artifacts(
        envelope, runner.rubric, out, remediation_templates=remediation,
    )
    assert (out / "readiness-report.json").exists()
    assert (out / "readiness-report.md").exists()
    assert (out / "readiness-actions.json").exists()
    assert (out / "readiness-dashboard.html").exists()
    assert dashboard_html is not None


def test_artifacts_writer_without_remediation_skips_dashboard(tmp_path, sample_repo) -> None:
    out = tmp_path / "out"
    runner = ReadinessRunner(repo_path=sample_repo, options=RunOptions(execute_commands=False))
    envelope = runner.evaluate()
    report_json, report_md, actions_json, dashboard_html = write_artifacts(
        envelope, runner.rubric, out,
    )
    assert (out / "readiness-report.json").exists()
    assert not (out / "readiness-dashboard.html").exists()
    assert dashboard_html is None


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
