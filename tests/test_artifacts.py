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
