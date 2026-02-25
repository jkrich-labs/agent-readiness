from __future__ import annotations

import argparse
import json
from pathlib import Path

from .artifacts import write_artifacts
from .evaluators import build_registry
from .rubric import DEFAULT_RUBRIC_VERSION, load_frozen_rubric, load_remediation_templates
from .runner import ReadinessRunner, RunOptions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local Droid-compatible readiness report evaluator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run readiness evaluation")
    run_parser.add_argument("--repo", type=Path, default=Path("."), help="Repository path to evaluate")
    run_parser.add_argument("--out-dir", type=Path, default=Path("."), help="Output directory for artifacts")
    run_parser.add_argument("--repo-url", default=None, help="Override repository URL in output envelope")
    run_parser.add_argument("--rubric-version", default=DEFAULT_RUBRIC_VERSION)
    run_parser.add_argument(
        "--no-command-execution",
        action="store_true",
        help="Disable shell command execution during checks",
    )

    explain_parser = subparsers.add_parser("explain", help="Explain a rubric criterion")
    explain_parser.add_argument("criterion_id")
    explain_parser.add_argument("--rubric-version", default=DEFAULT_RUBRIC_VERSION)

    self_check_parser = subparsers.add_parser("self-check", help="Validate local readiness installation")
    self_check_parser.add_argument("--rubric-version", default=DEFAULT_RUBRIC_VERSION)

    return parser


def _cmd_run(args: argparse.Namespace) -> int:
    runner = ReadinessRunner(
        repo_path=args.repo,
        repo_url=args.repo_url,
        rubric_version=args.rubric_version,
        options=RunOptions(execute_commands=not args.no_command_execution),
    )
    envelope = runner.evaluate()
    remediation = load_remediation_templates(args.rubric_version)
    report_json, report_md, actions_json, dashboard_html = write_artifacts(
        envelope, runner.rubric, args.out_dir, remediation_templates=remediation,
    )
    rate, level = runner.summarize(envelope)

    artifacts_dict = {
        "readiness-report.json": str(report_json),
        "readiness-report.md": str(report_md),
        "readiness-actions.json": str(actions_json),
    }
    if dashboard_html:
        artifacts_dict["readiness-dashboard.html"] = str(dashboard_html)

    output = {
        "repoUrl": envelope.repoUrl,
        "rubricVersion": envelope.rubricVersion,
        "criteriaCount": len(envelope.report),
        "passRate": round(rate, 4),
        "level": level,
        "artifacts": artifacts_dict,
    }
    print(json.dumps(output, indent=2))
    return 0


def _cmd_explain(args: argparse.Namespace) -> int:
    rubric = load_frozen_rubric(args.rubric_version)
    definition = rubric.definitions.get(args.criterion_id)
    if not definition:
        print(f"Unknown criterion: {args.criterion_id}")
        return 1

    output = {
        "criterion": definition.id,
        "scope": definition.scope,
        "level": definition.level,
        "skippable": definition.skippable,
        "description": definition.description,
    }
    print(json.dumps(output, indent=2))
    return 0


def _cmd_self_check(args: argparse.Namespace) -> int:
    rubric = load_frozen_rubric(args.rubric_version)
    registry = build_registry(rubric)

    coverage_ok = set(registry.keys()) == set(rubric.criteria_order)
    output = {
        "rubricVersion": rubric.version,
        "criteriaCount": len(rubric.criteria_order),
        "repositoryScopeCount": len(rubric.repository_scope),
        "applicationScopeCount": len(rubric.application_scope),
        "registryCoverageOk": coverage_ok,
    }
    print(json.dumps(output, indent=2))
    return 0 if coverage_ok else 1


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "run":
        return _cmd_run(args)
    if args.command == "explain":
        return _cmd_explain(args)
    if args.command == "self-check":
        return _cmd_self_check(args)

    raise RuntimeError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
