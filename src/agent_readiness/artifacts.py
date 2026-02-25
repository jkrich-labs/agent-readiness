from __future__ import annotations

import json
import re
from pathlib import Path

from .models import ReadinessReportEnvelope
from .rubric import FrozenRubric
from .scoring import level_from_pass_rate, pass_rate


def _report_to_json_dict(envelope: ReadinessReportEnvelope) -> dict[str, object]:
    return {
        "repoUrl": envelope.repoUrl,
        "rubricVersion": envelope.rubricVersion,
        "branch": envelope.branch,
        "commitHash": envelope.commitHash,
        "hasLocalChanges": envelope.hasLocalChanges,
        "hasNonRemoteCommits": envelope.hasNonRemoteCommits,
        "apps": {
            path: {"description": app.description, "languages": list(app.languages)}
            for path, app in envelope.apps.items()
        },
        "report": {
            criterion_id: {
                "numerator": value.numerator,
                "denominator": value.denominator,
                "rationale": value.rationale,
                "evidence": list(value.evidence),
            }
            for criterion_id, value in envelope.report.items()
        },
    }


def _build_actions(envelope: ReadinessReportEnvelope, rubric: FrozenRubric) -> list[dict[str, object]]:
    actions: list[dict[str, object]] = []
    for criterion_id, value in envelope.report.items():
        if value.numerator is None:
            continue
        if value.numerator >= value.denominator:
            continue

        definition = rubric.definitions[criterion_id]
        ratio = value.numerator / value.denominator
        actions.append(
            {
                "criterion": criterion_id,
                "scope": definition.scope,
                "level": definition.level,
                "ratio": round(ratio, 4),
                "description": definition.description,
                "rationale": value.rationale,
            }
        )

    actions.sort(key=lambda item: (int(item["level"]), float(item["ratio"])))
    return actions


def _build_markdown(envelope: ReadinessReportEnvelope, rubric: FrozenRubric) -> str:
    rate = pass_rate(envelope.report)
    level = level_from_pass_rate(rate)
    failed = [
        (cid, value)
        for cid, value in envelope.report.items()
        if value.numerator is not None and value.numerator < value.denominator
    ]
    skipped = [cid for cid, value in envelope.report.items() if value.numerator is None]

    lines = [
        "# Readiness Report",
        "",
        f"- Repository: {envelope.repoUrl}",
        f"- Rubric: {envelope.rubricVersion}",
        f"- Pass Rate: {rate:.1%}",
        f"- Level: {level}",
        f"- Applications: {len(envelope.apps)}",
        "",
        "## Failed Criteria",
    ]

    if not failed:
        lines.append("- None")
    else:
        for criterion_id, value in failed:
            definition = rubric.definitions[criterion_id]
            lines.append(
                f"- `{criterion_id}` ({value.numerator}/{value.denominator}, level {definition.level}): {value.rationale}"
            )

    lines.append("")
    lines.append("## Skipped Criteria")
    if not skipped:
        lines.append("- None")
    else:
        for criterion_id in skipped:
            lines.append(f"- `{criterion_id}`")

    return "\n".join(lines) + "\n"


def write_artifacts(
    envelope: ReadinessReportEnvelope,
    rubric: FrozenRubric,
    out_dir: Path,
    remediation_templates: dict[str, str] | None = None,
) -> tuple[Path, Path, Path, Path | None]:
    out_dir.mkdir(parents=True, exist_ok=True)

    report_json_path = out_dir / "readiness-report.json"
    report_md_path = out_dir / "readiness-report.md"
    actions_json_path = out_dir / "readiness-actions.json"

    report_json_path.write_text(
        json.dumps(_report_to_json_dict(envelope), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_md_path.write_text(_build_markdown(envelope, rubric), encoding="utf-8")
    actions_json_path.write_text(
        json.dumps({"actions": _build_actions(envelope, rubric)}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    dashboard_path = None
    if remediation_templates is not None:
        dashboard_path = write_html_dashboard(envelope, rubric, remediation_templates, out_dir)

    return report_json_path, report_md_path, actions_json_path, dashboard_path


def _rubric_to_json_dict(rubric: FrozenRubric) -> dict[str, object]:
    """Serialize rubric definitions for embedding in HTML."""
    return {
        "criteria": {
            cid: {
                "scope": d.scope,
                "level": d.level,
                "skippable": d.skippable,
                "description": d.description,
            }
            for cid, d in rubric.definitions.items()
        },
        "criteria_order": list(rubric.criteria_order),
        "repository_scope": sorted(rubric.repository_scope),
        "application_scope": sorted(rubric.application_scope),
    }


def _inject_data(template: str, marker: str, data: str) -> str:
    """Replace /*__MARKER__*/ {} /*__END__*/ with /*__MARKER__*/ {data} /*__END__*/."""
    pattern = rf"/\*{re.escape(marker)}\*/.*?/\*__END__\*/"
    replacement = f"/*{marker}*/ {data} /*__END__*/"
    return re.sub(pattern, lambda _: replacement, template, count=1, flags=re.DOTALL)


def write_html_dashboard(
    envelope: ReadinessReportEnvelope,
    rubric: FrozenRubric,
    remediation_templates: dict[str, str],
    out_dir: Path,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    template_path = Path(__file__).parent / "templates" / "dashboard.html"
    template = template_path.read_text(encoding="utf-8")

    report_json = json.dumps(_report_to_json_dict(envelope), sort_keys=True)
    rubric_json = json.dumps(_rubric_to_json_dict(rubric), sort_keys=True)
    remediation_json = json.dumps(remediation_templates, sort_keys=True)

    html = _inject_data(template, "__REPORT_DATA__", report_json)
    html = _inject_data(html, "__RUBRIC_DATA__", rubric_json)
    html = _inject_data(html, "__REMEDIATION_DATA__", remediation_json)

    dashboard_path = out_dir / "readiness-dashboard.html"
    dashboard_path.write_text(html, encoding="utf-8")
    return dashboard_path
