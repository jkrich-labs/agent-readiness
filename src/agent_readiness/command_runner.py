from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool = False


def run_command(command: list[str], cwd: Path | None = None, timeout: int = 20) -> CommandResult:
    start = time.perf_counter()
    workdir = str((cwd or Path.cwd()).resolve())

    try:
        completed = subprocess.run(
            command,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        elapsed = int((time.perf_counter() - start) * 1000)
        return CommandResult(
            command=tuple(command),
            cwd=workdir,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            duration_ms=elapsed,
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = int((time.perf_counter() - start) * 1000)
        return CommandResult(
            command=tuple(command),
            cwd=workdir,
            exit_code=124,
            stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
            stderr=(exc.stderr or "") if isinstance(exc.stderr, str) else "",
            duration_ms=elapsed,
            timed_out=True,
        )
