import json
from pathlib import Path


class TaskValidationError(Exception):
    """Raised when an Agent Task fails policy or schema validation."""


_SCHEMA = None


def _load_schema():
    global _SCHEMA
    if _SCHEMA is not None:
        return _SCHEMA

    schema_path = Path(__file__).resolve().parent.parent / "specs" / "technical.md"
    if not schema_path.exists():
        raise TaskValidationError(f"schema file not found at {schema_path}")

    text = schema_path.read_text(encoding="utf8")
    # Extract the first JSON code block
    import re

    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not m:
        raise TaskValidationError(
            "could not find JSON schema block in specs/technical.md"
        )

    try:
        _SCHEMA = json.loads(m.group(1))
    except Exception as e:
        raise TaskValidationError(f"failed to parse schema JSON: {e}")

    return _SCHEMA


def validate_agent_task(task: dict) -> bool:
    """Validate an Agent Task strictly against the canonical JSON Schema.

    Raises TaskValidationError when validation fails, with clear messages.
    Returns True when the task conforms to the schema.
    """
    if not isinstance(task, dict):
        raise TaskValidationError("task must be a dict")

    schema = _load_schema()

    try:
        import jsonschema
        from jsonschema import Draft7Validator
    except Exception:
        raise TaskValidationError(
            "jsonschema is required for strict validation; please install 'jsonschema' package"
        )

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(task), key=lambda e: e.path)
    if errors:
        # Build a clear, first-error focused message
        e = errors[0]
        path = "/".join([str(p) for p in e.path]) if e.path else "(root)"
        msg = f"Schema validation error: {e.message} at {path}"
        raise TaskValidationError(msg)

    return True
