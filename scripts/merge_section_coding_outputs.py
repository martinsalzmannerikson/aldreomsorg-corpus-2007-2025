from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_helpers import append_audit_log, ensure_dirs, repo_path, write_csv


INPUT_DIR = "analysis/03_outputs/section_coding_json"
LONG_OUT = "analysis/03_outputs/section_coding_csv/coding_matrix_long.csv"
WIDE_OUT = "analysis/03_outputs/section_coding_csv/coding_matrix_wide.csv"

LONG_COLUMNS = [
    "curated_section_id",
    "year",
    "title",
    "theme_from_dataset",
    "prompt_version",
    "model",
    "coding_date",
    "human_review_status",
    "code",
    "salience",
    "code_justification",
    "textual_basis",
    "code_uncertainty",
    "problem_representations_json",
    "actor_positioning_json",
    "quality_flags_json",
    "needs_human_check",
    "possible_overinterpretation",
    "citation_needs_verification",
    "data_extraction_concern",
    "source_file",
]

WIDE_COLUMNS = [
    "curated_section_id",
    "year",
    "title",
    "theme_from_dataset",
    "prompt_version",
    "model",
    "coding_date",
    "human_review_status",
    "codes_high",
    "codes_medium",
    "codes_low",
    "all_codes",
    "problem_representations_json",
    "actor_positioning_json",
    "quality_flags_json",
    "needs_human_check",
    "possible_overinterpretation",
    "citation_needs_verification",
    "data_extraction_concern",
    "source_file",
]


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def read_coding_files() -> list[tuple[Path, dict[str, Any]]]:
    files = []
    for path in sorted(repo_path(INPUT_DIR).glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            files.append((path, json.load(f)))
    return files


def metadata(payload: dict[str, Any], source_file: Path) -> dict[str, Any]:
    coding_metadata = payload.get("coding_metadata", {}) or {}
    quality_flags = payload.get("quality_flags", {}) or {}
    return {
        "curated_section_id": payload.get("curated_section_id", ""),
        "year": payload.get("year", ""),
        "title": payload.get("title", ""),
        "theme_from_dataset": payload.get("theme_from_dataset", ""),
        "prompt_version": coding_metadata.get("prompt_version", ""),
        "model": coding_metadata.get("model", ""),
        "coding_date": coding_metadata.get("coding_date", ""),
        "human_review_status": coding_metadata.get("human_review_status", ""),
        "problem_representations_json": compact_json(payload.get("problem_representations", [])),
        "actor_positioning_json": compact_json(payload.get("actor_positioning", {})),
        "quality_flags_json": compact_json(quality_flags),
        "needs_human_check": quality_flags.get("needs_human_check", ""),
        "possible_overinterpretation": quality_flags.get("possible_overinterpretation", ""),
        "citation_needs_verification": quality_flags.get("citation_needs_verification", ""),
        "data_extraction_concern": quality_flags.get("data_extraction_concern", ""),
        "source_file": source_file.relative_to(repo_path(".")).as_posix(),
    }


def merge() -> tuple[int, int, int]:
    ensure_dirs([INPUT_DIR, "analysis/03_outputs/section_coding_csv"])
    coding_files = read_coding_files()
    long_rows: list[dict[str, Any]] = []
    wide_rows: list[dict[str, Any]] = []

    for source_file, payload in coding_files:
        base = metadata(payload, source_file)
        codes = payload.get("care_science_codes", []) or []

        if not codes:
            long_rows.append(
                {
                    **base,
                    "code": "",
                    "salience": "",
                    "code_justification": "",
                    "textual_basis": "",
                    "code_uncertainty": "",
                }
            )
        for code in codes:
            long_rows.append(
                {
                    **base,
                    "code": code.get("code", ""),
                    "salience": code.get("salience", ""),
                    "code_justification": code.get("justification", ""),
                    "textual_basis": code.get("textual_basis", ""),
                    "code_uncertainty": code.get("uncertainty", ""),
                }
            )

        codes_by_salience = {"high": [], "medium": [], "low": []}
        for code in codes:
            salience = code.get("salience", "")
            if salience in codes_by_salience:
                codes_by_salience[salience].append(code.get("code", ""))

        wide_rows.append(
            {
                **base,
                "codes_high": "|".join(codes_by_salience["high"]),
                "codes_medium": "|".join(codes_by_salience["medium"]),
                "codes_low": "|".join(codes_by_salience["low"]),
                "all_codes": "|".join(code.get("code", "") for code in codes),
            }
        )

    write_csv(LONG_OUT, long_rows, LONG_COLUMNS)
    write_csv(WIDE_OUT, wide_rows, WIDE_COLUMNS)
    append_audit_log(
        step="merge_section_coding_outputs",
        input_files=[INPUT_DIR],
        output_files=[LONG_OUT, WIDE_OUT],
        notes=f"json_files={len(coding_files)}; long_rows={len(long_rows)}; wide_rows={len(wide_rows)}",
    )
    return len(coding_files), len(long_rows), len(wide_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge section coding JSON files to CSV matrices.")
    parser.parse_args()
    files, long_rows, wide_rows = merge()
    print(f"Merged {files} JSON files into {long_rows} long rows and {wide_rows} wide rows.")


if __name__ == "__main__":
    main()
