from __future__ import annotations

import argparse
from pathlib import Path

from audit_helpers import (
    append_audit_log,
    data_check_note,
    ensure_dirs,
    read_csv,
    repo_path,
    write_csv,
    write_jsonl,
)


INPUT = "data/corpus_2026/metadata/curated_sections.csv"
OUTPUT_DIR = "analysis/03_outputs/section_batches"
INDEX = "analysis/03_outputs/section_batches/batch_index.csv"


def as_int(value: str) -> int | str:
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def preview_text(text_path: str, chars: int = 500) -> tuple[bool, str]:
    if not text_path:
        return False, ""
    target = repo_path(text_path)
    if not target.exists():
        return False, ""
    text = target.read_text(encoding="utf-8", errors="replace")
    return True, text[:chars]


def batch_rows(rows: list[dict[str, str]], batch_size: int) -> list[list[dict[str, str]]]:
    return [rows[i : i + batch_size] for i in range(0, len(rows), batch_size)]


def build(batch_size: int) -> list[str]:
    ensure_dirs([OUTPUT_DIR])
    out_dir = repo_path(OUTPUT_DIR)
    for old_batch in out_dir.glob("section_batch_*.jsonl"):
        old_batch.unlink()

    rows = read_csv(INPUT)
    index_rows: list[dict[str, str]] = []
    output_files: list[str] = []

    for idx, batch in enumerate(batch_rows(rows, batch_size), 1):
        batch_id = f"batch_{idx:03d}"
        batch_file = f"{OUTPUT_DIR}/section_{batch_id}.jsonl"
        section_payloads = []
        for row in batch:
            exists, preview = preview_text(row.get("text_path", ""))
            section_payloads.append(
                {
                    "batch_id": batch_id,
                    "curated_section_id": row.get("curated_section_id", ""),
                    "year": as_int(row.get("year", "")),
                    "section_index": as_int(row.get("section_index", "")),
                    "title": row.get("title", ""),
                    "theme_from_dataset": row.get("theme", ""),
                    "source_type": row.get("source_type", ""),
                    "source_text_path": row.get("text_path", ""),
                    "text_file_exists": exists,
                    "text_preview_500": preview,
                    "original_report_file": row.get("original_report_file", ""),
                    "original_start_pdf_page": as_int(row.get("original_start_pdf_page", "")),
                    "original_end_pdf_page": as_int(row.get("original_end_pdf_page", "")),
                    "word_count": as_int(row.get("word_count", "")),
                }
            )
        write_jsonl(batch_file, section_payloads)
        output_files.append(batch_file)
        index_rows.append(
            {
                "batch_id": batch_id,
                "batch_file": batch_file,
                "row_count": str(len(batch)),
                "first_curated_section_id": batch[0].get("curated_section_id", ""),
                "last_curated_section_id": batch[-1].get("curated_section_id", ""),
                "years": "|".join(sorted({row.get("year", "") for row in batch})),
                "themes": "|".join(sorted({row.get("theme", "") for row in batch})),
            }
        )

    write_csv(
        INDEX,
        index_rows,
        [
            "batch_id",
            "batch_file",
            "row_count",
            "first_curated_section_id",
            "last_curated_section_id",
            "years",
            "themes",
        ],
    )
    output_files.append(INDEX)

    append_audit_log(
        step="build_section_batches",
        input_files=[INPUT],
        output_files=output_files,
        notes=f"batch_size={batch_size}; batches={len(index_rows)}; {data_check_note()}",
    )
    return output_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Build JSONL batches from curated_sections.csv.")
    parser.add_argument("--batch-size", type=int, default=10)
    args = parser.parse_args()
    if args.batch_size < 1:
        raise SystemExit("--batch-size must be at least 1")
    files = build(args.batch_size)
    print(f"Wrote {len(files)} output files to {Path(OUTPUT_DIR).as_posix()}")


if __name__ == "__main__":
    main()
