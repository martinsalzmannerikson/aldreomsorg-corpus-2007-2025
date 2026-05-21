from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_helpers import append_audit_log, ensure_dirs, read_json, repo_path, write_csv


SCHEMA = "analysis/00_protocol/section_coding_schema.json"
INPUT_DIR = "analysis/03_outputs/section_coding_json"
REPORT = "analysis/04_quality_checks/json_validation_report.csv"


def resolve_ref(schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        return {}
    node: Any = schema
    for part in ref[2:].split("/"):
        node = node.get(part, {})
    return node if isinstance(node, dict) else {}


def expected_type_name(expected: Any) -> str:
    if isinstance(expected, list):
        return "|".join(expected)
    return str(expected)


def type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def validate_node(
    value: Any,
    node_schema: dict[str, Any],
    root_schema: dict[str, Any],
    path: str,
    errors: list[dict[str, str]],
) -> None:
    if "$ref" in node_schema:
        node_schema = resolve_ref(root_schema, str(node_schema["$ref"]))

    expected_type = node_schema.get("type")
    if expected_type:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(type_matches(value, item) for item in expected_types):
            errors.append(
                {
                    "json_path": path,
                    "error_type": "invalid_type",
                    "message": f"expected {expected_type_name(expected_type)}, got {type(value).__name__}",
                }
            )
            return

    if "enum" in node_schema and value not in node_schema["enum"]:
        errors.append(
            {
                "json_path": path,
                "error_type": "invalid_enum",
                "message": f"value {value!r} not in {node_schema['enum']}",
            }
        )

    if isinstance(value, dict):
        for required in node_schema.get("required", []):
            if required not in value:
                errors.append(
                    {
                        "json_path": f"{path}.{required}",
                        "error_type": "missing_required",
                        "message": "required field is missing",
                    }
                )
        for key, prop_schema in node_schema.get("properties", {}).items():
            if key in value:
                validate_node(value[key], prop_schema, root_schema, f"{path}.{key}", errors)

    if isinstance(value, list) and "items" in node_schema:
        item_schema = node_schema["items"]
        for idx, item in enumerate(value):
            validate_node(item, item_schema, root_schema, f"{path}[{idx}]", errors)


def validate_file(path: Path, schema: dict[str, Any]) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        return [
            {
                "json_path": "$",
                "error_type": "invalid_json",
                "message": f"{exc.msg} at line {exc.lineno}, column {exc.colno}",
            }
        ]

    errors: list[dict[str, str]] = []
    validate_node(payload, schema, schema, "$", errors)
    return errors


def run_validation() -> int:
    ensure_dirs([INPUT_DIR, "analysis/04_quality_checks"])
    schema = read_json(SCHEMA)
    json_files = sorted(repo_path(INPUT_DIR).glob("*.json"))
    rows: list[dict[str, str]] = []
    error_count = 0

    if not json_files:
        rows.append(
            {
                "file_path": "",
                "status": "no_files",
                "json_path": "",
                "error_type": "",
                "message": "No JSON coding files found. This is acceptable before coding starts.",
            }
        )

    for json_file in json_files:
        errors = validate_file(json_file, schema)
        if errors:
            error_count += len(errors)
            for error in errors:
                rows.append(
                    {
                        "file_path": json_file.relative_to(repo_path(".")).as_posix(),
                        "status": "invalid",
                        **error,
                    }
                )
        else:
            rows.append(
                {
                    "file_path": json_file.relative_to(repo_path(".")).as_posix(),
                    "status": "valid",
                    "json_path": "",
                    "error_type": "",
                    "message": "",
                }
            )

    write_csv(REPORT, rows, ["file_path", "status", "json_path", "error_type", "message"])
    append_audit_log(
        step="validate_section_coding_json",
        input_files=[SCHEMA, INPUT_DIR],
        output_files=[REPORT],
        notes=f"json_files={len(json_files)}; errors={error_count}",
    )
    return 1 if error_count else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate section coding JSON files.")
    parser.parse_args()
    raise SystemExit(run_validation())


if __name__ == "__main__":
    main()
