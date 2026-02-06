import pytest


def make_task(**overrides):
    base = {
        "id": "task-1",
        "title": "Test Task",
        "task_type": "test",
        "inputs": {},
        "required_mcp_tools": ["payments:initiate"],
        # intentionally omit `budget_limit` and `spec_reference` by default
    }
    base.update(overrides)
    return base


def test_rejects_missing_budget_limit():
    """Orchestrator must reject tasks with no `budget_limit`."""
    task = make_task()
    task.pop("budget_limit", None)

    # import inside the test so the test fails first (TDD) when validator is absent
    from governor import validator

    with pytest.raises(Exception):
        validator.validate_agent_task(task)


def test_rejects_missing_spec_reference():
    """Orchestrator must reject tasks with no `spec_reference` linking to `specs/`."""
    task = make_task(budget_limit={"amount": 100, "currency": "USD", "scope": "task"})
    task.pop("spec_reference", None)

    from governor import validator

    with pytest.raises(Exception):
        validator.validate_agent_task(task)
