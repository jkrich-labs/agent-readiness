"""Verify every rubric criterion has a corresponding remediation template."""
from agent_readiness.rubric import load_frozen_rubric, load_remediation_templates


def test_remediation_templates_cover_all_81_criteria() -> None:
    rubric = load_frozen_rubric("v0.62.1")
    templates = load_remediation_templates("v0.62.1")
    rubric_ids = set(rubric.criteria_order)
    template_ids = set(templates.keys())

    missing = rubric_ids - template_ids
    orphans = template_ids - rubric_ids

    assert not missing, f"Missing remediation templates: {sorted(missing)}"
    assert not orphans, f"Orphan remediation templates (no matching criterion): {sorted(orphans)}"
    assert len(templates) == 81


def test_remediation_templates_have_signal_name() -> None:
    """Each template must have a signal_name in its YAML frontmatter."""
    templates = load_remediation_templates("v0.62.1")
    for criterion_id, content in templates.items():
        assert "signal_name:" in content, (
            f"Remediation template {criterion_id}.md missing signal_name in frontmatter"
        )


def test_remediation_templates_have_fix_guidance() -> None:
    """Each template must include criterion-specific fix guidance."""
    templates = load_remediation_templates("v0.62.1")
    for criterion_id, content in templates.items():
        assert "## Criterion-Specific Fix Guidance" in content, (
            f"Remediation template {criterion_id}.md missing fix guidance section"
        )
