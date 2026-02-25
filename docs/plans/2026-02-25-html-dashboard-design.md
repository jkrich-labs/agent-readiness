# HTML Readiness Dashboard — Design Document

**Date:** 2026-02-25
**Status:** Approved

## Overview

Produce a local HTML dashboard as a 4th artifact of the `agent-readiness run` pipeline. It replaces the Factory.ai web dashboard with a self-contained file that shows readiness state and generates copy-pasteable LLM remediation prompts for each failing criterion.

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Remediation prompt style | Fixed templates, criterion-specific | Each of 81 criteria gets tailored fix guidance for maximum LLM effectiveness |
| External dependencies | CDN references allowed | Enables Tailwind CSS, Chart.js for rich UI |
| Pipeline integration | 4th artifact via `artifacts.py` | Auto-generated alongside existing 3 artifacts, no extra CLI step |
| Dashboard features | All 6 views | Summary, level breakdown, scope breakdown, criteria table, actions priority, remediation panel |
| Template storage | Individual `.md` files per criterion | `rubric/droid/v0.62.1/remediation/{criterion_id}.md` — 81 files, most readable/editable |
| Prompt target | Agentic coding tools | Assumes LLM has file access, can run commands, can create PRs |
| Frontend architecture | Standalone HTML template + data injection | Real `.html` file with placeholders, Python injects JSON at generation time |

## Data Architecture

Three JSON blobs embedded in the HTML via `<script>` tag:

```html
<script>
  const REPORT_DATA = /*__REPORT_DATA__*/ {} /*__END__*/;
  const RUBRIC_DATA = /*__RUBRIC_DATA__*/ {} /*__END__*/;
  const REMEDIATION_DATA = /*__REMEDIATION_DATA__*/ {} /*__END__*/;
</script>
```

- **REPORT_DATA**: Contents of `ReadinessReportEnvelope` (repoUrl, branch, commitHash, apps, report with all 81 criterion evaluations)
- **RUBRIC_DATA**: Contents of `criteria_scope.json` (scope, level, skippable, description per criterion)
- **REMEDIATION_DATA**: Map of `criterion_id → markdown template string` (loaded from 81 `.md` files)

Empty `{}` defaults allow the template to open in a browser during development. Python replaces content between marker comments with `json.dumps()` output.

## Dashboard Layout

Single-page app with fixed sidebar nav and scrollable main content. Six sections:

### 1. Summary Header
- Repo name, branch, short commit hash, rubric version
- Hero metric: pass rate as large percentage + circular progress ring
- Level badge (1-5) with color coding
- Three stat cards: Passed / Failed / Skipped counts

### 2. Level Breakdown
- Chart.js horizontal bar chart showing pass rate per level (1-5)
- Each bar labeled "Level N: X/Y passed (Z%)"
- Green-to-red color gradient

### 3. Scope Breakdown
- Two side-by-side cards: Repository Scope vs Application Scope
- Each shows pass rate, pass/fail/skip counts
- Application scope card lists discovered apps with languages

### 4. Criterion List (filterable/sortable table)
- Columns: status icon, criterion ID, level, scope, score (num/denom), rationale (truncated)
- Filters: by status (pass/fail/skip), by level (1-5), by scope (repo/app)
- Sort: by level, status, name
- Clicking a row opens the remediation panel

### 5. Actions Priority View
- Failed criteria only, sorted by priority (level asc, ratio asc)
- Card layout with criterion name, level badge, score, "Fix This" button
- "Fix This" opens the remediation panel

### 6. Remediation Panel (Hero Feature)
- Right-side drawer or inline expansion
- Shows: criterion name, score, level, scope, full rubric description, rationale, per-app evidence
- Styled code block with the full assembled LLM prompt
- "Copy to Clipboard" button with visual feedback

Sidebar nav has anchor links + mini status summary.

## Remediation Prompt Structure

Each `.md` file contains only the **static, criterion-specific** content:
- Human-readable signal name
- Criterion-specific fix guidance (3-10 concrete action bullet points)
- Criterion-specific exploration steps
- Criterion-specific verification steps

The **dynamic wrapper** is assembled by JS at render time:

```
# [Readiness Fix] {signal_name}
Fix the failing signal: {signal_name} ([{numerator}/{denominator}])

<system-reminder>
You are fixing an Agent Readiness signal...

## Failing Signal
**Signal**: {signal_name}
**Score**: [{numerator}/{denominator}]
**Description**: {rubric_description}
**Why it failed**: {rationale}

## Original Signal Evaluation Criteria
{rubric_description_full}

## Criterion-Specific Fix Guidance
{CONTENT FROM .md FILE}

## Your Task
1. Explore the repository...
2. {criterion-specific exploration steps from .md}
3. Make substantive improvements...
4. {criterion-specific verification steps from .md}
5. Keep changes focused
6. Open a PULL REQUEST and return the PR URL

## Quality Standards
{standard quality standards block}
</system-reminder>
```

**Prompts target agentic coding tools** — assume file access, command execution, git/gh capabilities.

## Remediation Template Authoring

All 81 files authored with genuine, useful fix guidance — no stubs. Depth scales with level:

- **Level 1** (6 criteria): Most detailed, step-by-step guidance
- **Level 2** (22 criteria): Solid, actionable with specific tool/config recommendations
- **Level 3** (24 criteria): Good guidance, may be more exploratory
- **Level 4-5** (29 criteria): Adequate, points LLM in right direction

## Frontend Tech

- **Tailwind CSS** via CDN play script
- **Chart.js** via CDN for level breakdown chart
- **Vanilla JS** — no framework. Dashboard is read-only with filtering/sorting/clipboard
- Responsive: desktop primary, degrades on tablet (sidebar collapses)
- Dark sidebar, light main content, professional information-dense design

Client-side modules (all inline):
- `computeStats()` — derives pass rate, level, counts, breakdowns
- `renderSummary()` — header section
- `renderCharts()` — Chart.js level breakdown
- `renderCriteriaTable()` — filterable table with event listeners
- `renderActions()` — priority action cards
- `renderRemediation()` — assembles prompt from template + dynamic data
- `copyToClipboard()` — clipboard with visual feedback

## Pipeline Integration

### Changes to `artifacts.py`
- New `write_html_dashboard(envelope, rubric, out_dir)` function
- Called from existing `write_artifacts()` flow
- Reads template via `importlib.resources` or relative `pathlib`
- Injects three JSON blobs via string replacement
- Writes `readiness-dashboard.html` to `out_dir`
- Adds path to CLI stdout JSON under `artifacts`

### Changes to `rubric.py`
- New `load_remediation_templates(version) -> dict[str, str]`
- Reads all `.md` files from `rubric/droid/{version}/remediation/`
- Validates 1:1 mapping with `criteria_order.txt` (no missing, no orphans)
- Raises on mismatch (same strictness as existing rubric validation)

### Runner changes
- Pass rubric object through to artifact generation (minimal wiring)

### No changes to
- `runner.py` evaluation logic
- `models.py`
- `registry.py`
- Existing 3 artifacts (format and behavior unchanged)

## Testing Strategy

- **`test_remediation_coverage.py`**: All 81 `.md` files exist, map 1:1 to rubric criteria
- **`test_artifacts.py`**: Extend to verify `readiness-dashboard.html` is written, contains expected data markers, valid HTML structure
- **`test_rubric.py`**: Extend to test `load_remediation_templates()` loads correctly, raises on missing files
- No browser/Selenium testing — validate through data contract

## Output

Pipeline produces 4 artifacts:
1. `readiness-report.json` (unchanged)
2. `readiness-report.md` (unchanged)
3. `readiness-actions.json` (unchanged)
4. `readiness-dashboard.html` (new)
