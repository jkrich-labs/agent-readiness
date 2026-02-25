from __future__ import annotations

from agent_readiness.cli import main


def test_cli_self_check_returns_zero() -> None:
    code = main(["self-check"])
    assert code == 0


def test_cli_run_writes_outputs(sample_repo, tmp_path) -> None:
    out = tmp_path / "out"
    code = main(["run", "--repo", str(sample_repo), "--out-dir", str(out), "--no-command-execution"])
    assert code == 0
    assert (out / "readiness-report.json").exists()


def test_cli_run_writes_dashboard(sample_repo, tmp_path) -> None:
    out = tmp_path / "out"
    code = main(["run", "--repo", str(sample_repo), "--out-dir", str(out), "--no-command-execution"])
    assert code == 0
    assert (out / "readiness-dashboard.html").exists()


def test_cli_explain_known_criterion_returns_zero() -> None:
    code = main(["explain", "lint_config"])
    assert code == 0
