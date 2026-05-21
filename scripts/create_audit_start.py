from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Europe/Stockholm")
CREATED_AT = datetime.now(TZ).isoformat(timespec="seconds")
REPOSITORY = "martinsalzmannerikson/aldreomsorg-corpus-2007-2025"
ACTOR = "Codex"
TOOL_OR_MODEL = "Codex 5.5"

SOURCE_FILES = [
    "README.md",
    "DATASET_CARD.md",
    "data/corpus_2026/README.md",
    "data/corpus_2026/manifest.json",
    "data/corpus_2026/metadata/curated_sections.csv",
    "data/corpus_2026/texts/curated_chunks_jsonl/curated_chunks.jsonl",
    "data/corpus_2026/metadata/curated_chunks.csv",
    "data/corpus_2026/metadata/curated_theme_summary.csv",
]


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dirs() -> None:
    for rel in [
        "analysis/00_protocol",
        "analysis/01_inputs",
        "analysis/02_prompts",
        "analysis/03_outputs",
        "analysis/04_quality_checks",
        "analysis/05_manuscript_support",
        "scripts",
    ]:
        (ROOT / rel).mkdir(parents=True, exist_ok=True)


def file_records() -> list[dict[str, str]]:
    records = []
    for rel in SOURCE_FILES:
        path = ROOT / rel
        exists = path.exists()
        records.append(
            {
                "file_path": rel,
                "file_role": role_for(rel),
                "file_size_bytes": str(path.stat().st_size) if exists else "MISSING",
                "sha256": sha256(path) if exists else "MISSING",
                "notes": "present" if exists else "missing",
            }
        )
    return records


def role_for(rel: str) -> str:
    if rel == "README.md":
        return "repository_overview"
    if rel == "DATASET_CARD.md":
        return "dataset_documentation"
    if rel.endswith("manifest.json"):
        return "machine_readable_manifest"
    if rel.endswith("curated_sections.csv"):
        return "primary_analysis_unit_metadata"
    if rel.endswith("curated_chunks.jsonl"):
        return "text_near_search_and_citation_support"
    if rel.endswith("curated_chunks.csv"):
        return "chunk_metadata"
    if rel.endswith("curated_theme_summary.csv"):
        return "theme_summary_metadata"
    if rel.endswith("data/corpus_2026/README.md"):
        return "corpus_documentation"
    return "source_file"


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_docs_summary() -> dict[str, object]:
    manifest_path = ROOT / "data/corpus_2026/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    curated = manifest.get("curated_layer", {})
    return {
        "purpose": (
            "The dataset supports qualitative and computational document analysis "
            "of Swedish annual reports on care and services for older adults, 2007-2025."
        ),
        "primary_unit": curated.get("recommended_primary_analysis_unit", "curated_section"),
        "curated_sections": curated.get("curated_sections"),
        "curated_chunks": curated.get("curated_chunks"),
        "limitations": [
            "PDF extraction is imperfect.",
            "Sectioning is reproducible but partly heuristic.",
            "Some older reports may contain encoding artefacts in extracted text.",
            "Original PDF reports are not included in the repository.",
            "Copyright and reuse conditions should be reviewed before relying on redistribution.",
        ],
    }


def profile_curated_sections() -> tuple[list[dict[str, object]], str]:
    path = ROOT / "data/corpus_2026/metadata/curated_sections.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    columns = list(rows[0].keys()) if rows else []
    years = [int(r["year"]) for r in rows if r.get("year")]
    themes = sorted({r.get("theme", "") for r in rows if r.get("theme")})
    total_words = sum(int(r.get("word_count") or 0) for r in rows)
    per_year = Counter(years)
    profile_rows = [
        {"metric": "row_count", "value": len(rows)},
        {"metric": "columns", "value": "|".join(columns)},
        {"metric": "unique_years", "value": len(set(years))},
        {"metric": "unique_themes", "value": len(themes)},
        {"metric": "min_year", "value": min(years) if years else ""},
        {"metric": "max_year", "value": max(years) if years else ""},
        {"metric": "total_word_count", "value": total_words},
    ]
    for year in sorted(per_year):
        profile_rows.append({"metric": f"sections_in_{year}", "value": per_year[year]})
    md = [
        "# Curated Sections Profile",
        "",
        f"Created: {CREATED_AT}",
        "",
        f"- Rows: {len(rows)}",
        f"- Columns: {', '.join(columns)}",
        f"- Unique years: {len(set(years))}",
        f"- Year range: {min(years)}-{max(years)}" if years else "- Year range: missing",
        f"- Unique themes: {len(themes)}",
        f"- Total word_count: {total_words}",
        "",
        "## Sections Per Year",
        "",
    ]
    md.extend(f"- {year}: {per_year[year]}" for year in sorted(per_year))
    return profile_rows, "\n".join(md) + "\n"


def profile_curated_chunks() -> tuple[list[dict[str, object]], str]:
    path = ROOT / "data/corpus_2026/texts/curated_chunks_jsonl/curated_chunks.jsonl"
    rows: list[dict[str, object]] = []
    errors = []
    empty_lines = 0
    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            if not line.strip():
                empty_lines += 1
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                errors.append(f"line {idx}: {exc}")
    keys = sorted({key for row in rows for key in row.keys()})
    section_ids = {str(r.get("curated_section_id")) for r in rows if r.get("curated_section_id")}
    per_year = Counter(int(r["year"]) for r in rows if r.get("year") is not None)
    profile_rows = [
        {"metric": "chunk_count", "value": len(rows)},
        {"metric": "keys", "value": "|".join(keys)},
        {"metric": "unique_curated_section_id", "value": len(section_ids)},
        {"metric": "empty_lines", "value": empty_lines},
        {"metric": "parsing_errors", "value": len(errors)},
    ]
    for year in sorted(per_year):
        profile_rows.append({"metric": f"chunks_in_{year}", "value": per_year[year]})
    md = [
        "# Curated Chunks Profile",
        "",
        f"Created: {CREATED_AT}",
        "",
        f"- Chunks: {len(rows)}",
        f"- Keys: {', '.join(keys)}",
        f"- Unique curated_section_id: {len(section_ids)}",
        f"- Empty lines: {empty_lines}",
        f"- Parsing errors: {len(errors)}",
        "",
        "## Chunks Per Year",
        "",
    ]
    md.extend(f"- {year}: {per_year[year]}" for year in sorted(per_year))
    if errors:
        md.extend(["", "## Parsing Errors", ""])
        md.extend(f"- {err}" for err in errors)
    return profile_rows, "\n".join(md) + "\n"


def write_snapshot(records: list[dict[str, str]]) -> None:
    branch = run_git(["branch", "--show-current"])
    commit = run_git(["rev-parse", "HEAD"])
    summary = read_docs_summary()
    lines = [
        "# Corpus Snapshot Manifest",
        "",
        f"Created: {CREATED_AT}",
        f"Repository: {REPOSITORY}",
        f"Branch: {branch}",
        f"Commit SHA: `{commit}`",
        "",
        "## Source Files",
        "",
        "| File | Size bytes | SHA256 | Notes |",
        "|---|---:|---|---|",
    ]
    for record in records:
        lines.append(
            f"| `{record['file_path']}` | {record['file_size_bytes']} | "
            f"`{record['sha256']}` | {record['notes']} |"
        )
    lines.extend(
        [
            "",
            "## Dataset Purpose",
            "",
            str(summary["purpose"]),
            "",
            "## Analysis Unit",
            "",
            "`curated_sections.csv` is the primary analysis unit. "
            "`curated_chunks.jsonl` is used for text-near search and citation support.",
            "",
            f"Manifest curated sections: {summary.get('curated_sections')}.",
            f"Manifest curated chunks: {summary.get('curated_chunks')}.",
            "",
            "## Source-Control Caveat",
            "",
            "Original PDF reports are not included in this repository. The corpus supports analysis "
            "and retrieval, but it cannot replace the original PDFs for final source checking.",
            "",
            "## Known Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in summary["limitations"])
    lines.extend(
        [
            "",
            "## Assumptions",
            "",
            "- Assumption: local system time in Europe/Stockholm is the appropriate audit timestamp.",
            "- Assumption: repository-relative corpus files are the frozen analysis inputs for this audit start.",
            "",
            "## AI Use Note",
            "",
            "AI-generated text must not be used as a replacement for source checking against the corpus "
            "and, where needed, the original PDFs.",
            "",
        ]
    )
    (ROOT / "analysis/00_protocol/corpus_snapshot_manifest.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def append_audit_log(records: list[dict[str, str]]) -> None:
    path = ROOT / "analysis/04_quality_checks/audit_log.csv"
    fieldnames = [
        "timestamp",
        "step",
        "actor",
        "tool_or_model",
        "input_files",
        "output_files",
        "prompt_file",
        "notes",
    ]
    row = {
        "timestamp": CREATED_AT,
        "step": "freeze_corpus_and_create_audit_start",
        "actor": ACTOR,
        "tool_or_model": TOOL_OR_MODEL,
        "input_files": "|".join(SOURCE_FILES),
        "output_files": "|".join(
            [
                "analysis/00_protocol/corpus_snapshot_manifest.md",
                "analysis/04_quality_checks/audit_log.csv",
                "analysis/01_inputs/input_file_inventory.csv",
                "analysis/01_inputs/curated_sections_profile.csv",
                "analysis/01_inputs/curated_sections_profile.md",
                "analysis/01_inputs/curated_chunks_profile.csv",
                "analysis/01_inputs/curated_chunks_profile.md",
            ]
        ),
        "prompt_file": "",
        "notes": (
            "Initial audit-start created. Missing source files: "
            + ", ".join(r["file_path"] for r in records if r["notes"] == "missing")
            if any(r["notes"] == "missing" for r in records)
            else "Initial audit-start created; all specified source files present."
        ),
    }
    write_header = not path.exists()
    with path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def main() -> None:
    ensure_dirs()
    records = file_records()
    write_csv(
        ROOT / "analysis/01_inputs/input_file_inventory.csv",
        records,
        ["file_path", "file_role", "file_size_bytes", "sha256", "notes"],
    )
    write_snapshot(records)
    section_profile, section_md = profile_curated_sections()
    write_csv(
        ROOT / "analysis/01_inputs/curated_sections_profile.csv",
        section_profile,
        ["metric", "value"],
    )
    (ROOT / "analysis/01_inputs/curated_sections_profile.md").write_text(
        section_md, encoding="utf-8"
    )
    chunk_profile, chunk_md = profile_curated_chunks()
    write_csv(
        ROOT / "analysis/01_inputs/curated_chunks_profile.csv",
        chunk_profile,
        ["metric", "value"],
    )
    (ROOT / "analysis/01_inputs/curated_chunks_profile.md").write_text(
        chunk_md, encoding="utf-8"
    )
    append_audit_log(records)
    print("Audit start created.")


if __name__ == "__main__":
    main()

