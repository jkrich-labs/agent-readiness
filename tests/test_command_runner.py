from __future__ import annotations

from agent_readiness.command_runner import run_command


def test_command_runner_captures_exit_code_and_output() -> None:
    result = run_command(["bash", "-lc", "echo ok"])
    assert result.exit_code == 0
    assert "ok" in result.stdout
