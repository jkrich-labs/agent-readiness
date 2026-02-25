from __future__ import annotations

from agent_readiness.runner import ReadinessRunner, RunOptions


def test_runner_produces_81_criterion_report(sample_repo) -> None:
    runner = ReadinessRunner(repo_path=sample_repo, options=RunOptions(execute_commands=False))
    report = runner.evaluate()
    assert len(report.report) == 81
