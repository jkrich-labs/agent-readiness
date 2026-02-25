from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from .models import ReadinessReportEnvelope


class LocalReadinessPersister:
    """Local-only persistence for readiness reports.

    This replaces Factory API writes for this custom implementation.
    """

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def store_report(self, envelope: ReadinessReportEnvelope) -> dict[str, str]:
        report_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        target = self.base_dir / f"{report_id}.json"
        payload = {
            "repoUrl": envelope.repoUrl,
            "rubricVersion": envelope.rubricVersion,
            "apps": {k: asdict(v) for k, v in envelope.apps.items()},
            "report": {k: asdict(v) for k, v in envelope.report.items()},
            "branch": envelope.branch,
            "commitHash": envelope.commitHash,
            "hasLocalChanges": envelope.hasLocalChanges,
            "hasNonRemoteCommits": envelope.hasNonRemoteCommits,
            "droidVersion": envelope.droidVersion,
            "metadata": envelope.metadata,
            "storedAt": datetime.now(UTC).isoformat(),
        }
        target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {"success": "true", "reportId": report_id, "path": str(target)}

    def list_reports(self, limit: int = 10) -> dict[str, object]:
        files = sorted(self.base_dir.glob("*.json"), reverse=True)
        selected = files[: max(limit, 0)]
        return {
            "reports": [
                {
                    "reportId": path.stem,
                    "path": str(path),
                    "size": path.stat().st_size,
                    "modifiedAt": datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat(),
                }
                for path in selected
            ]
        }
