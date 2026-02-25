from __future__ import annotations

from agent_readiness.rubric import load_frozen_rubric


def test_rubric_loader_returns_81_unique_criteria() -> None:
    rubric = load_frozen_rubric("v0.62.1")
    assert len(rubric.criteria_order) == 81
    assert len(set(rubric.criteria_order)) == 81


def test_rubric_has_definition_for_every_criterion() -> None:
    rubric = load_frozen_rubric("v0.62.1")
    assert set(rubric.criteria_order) == set(rubric.definitions)


def test_load_remediation_templates_returns_dict_of_strings() -> None:
    from agent_readiness.rubric import load_remediation_templates

    templates = load_remediation_templates("v0.62.1")
    assert isinstance(templates, dict)
    assert all(isinstance(v, str) for v in templates.values())
    assert all(isinstance(k, str) for k in templates.keys())
    assert len(templates) > 0


def test_load_remediation_templates_keys_are_subset_of_rubric() -> None:
    from agent_readiness.rubric import load_frozen_rubric, load_remediation_templates

    rubric = load_frozen_rubric("v0.62.1")
    templates = load_remediation_templates("v0.62.1")
    assert set(templates.keys()).issubset(set(rubric.criteria_order))


def test_load_remediation_templates_raises_on_bad_version() -> None:
    import pytest
    from agent_readiness.rubric import load_remediation_templates

    with pytest.raises((FileNotFoundError, ValueError)):
        load_remediation_templates("v99.99.99")
