# Pipeline Readme

This folder contains a reproducible technical pipeline for AI-assisted document analysis of the curated corpus.

The pipeline does not modify source data under `data/corpus_2026/`. It creates batches, validation reports, merged matrices, keyword trend files, and chunk retrieval memos under `analysis/`.

## Analysis Unit

The primary analysis unit is `data/corpus_2026/metadata/curated_sections.csv`.

`data/corpus_2026/texts/curated_chunks_jsonl/curated_chunks.jsonl` is used only for text-near search, quote candidates, and checks of deviant or uncertain cases.

## Scripts

`scripts/build_section_batches.py` reads `curated_sections.csv` and writes JSONL batch files to `analysis/03_outputs/section_batches/`. Each batch item contains section metadata, the path to the section text, and a 500-character preview if the text file exists. It also writes `batch_index.csv`.

`scripts/retrieve_chunks_for_section.py` retrieves all chunks for one `curated_section_id` and writes them to `analysis/03_outputs/memos/`. Optional keywords annotate the retrieved chunks with hit counts.

`scripts/validate_section_coding_json.py` validates JSON coding files in `analysis/03_outputs/section_coding_json/` against `analysis/00_protocol/section_coding_schema.json`. It reports invalid JSON, missing required fields, invalid types, and invalid enum values. The script exits with non-zero status when validation errors are found.

`scripts/merge_section_coding_outputs.py` reads validated JSON coding files and writes a long coding matrix and a wide section matrix to `analysis/03_outputs/section_coding_csv/`.

`scripts/keyword_trends.py` counts predefined keyword groups in curated section texts and writes summaries by year and by period. The period grouping is an assumption for descriptive orientation only: `2007-2010`, `2011-2014`, `2015-2018`, `2019-2022`, and `2023-2025`.

`scripts/audit_helpers.py` contains shared helpers for SHA256, local timestamps, CSV/JSONL reading, audit logging, and a simple check that source corpus files match the audit-start inventory.

## How To Run

From the repository root:

```bash
python scripts/build_section_batches.py --batch-size 10
python scripts/retrieve_chunks_for_section.py --section-id CUR2025_S010 --keywords kontinuitet samordning trygghet
python scripts/validate_section_coding_json.py
python scripts/merge_section_coding_outputs.py
python scripts/keyword_trends.py
```

Every script appends a row to `analysis/04_quality_checks/audit_log.csv`.

## Output Files

Batch files:

- `analysis/03_outputs/section_batches/section_batch_*.jsonl`
- `analysis/03_outputs/section_batches/batch_index.csv`

Chunk retrieval memos:

- `analysis/03_outputs/memos/chunks_<curated_section_id>.jsonl`

Validation and quality checks:

- `analysis/04_quality_checks/json_validation_report.csv`
- `analysis/04_quality_checks/audit_log.csv`

Coding matrices:

- `analysis/03_outputs/section_coding_csv/coding_matrix_long.csv`
- `analysis/03_outputs/section_coding_csv/coding_matrix_wide.csv`

Keyword summaries:

- `analysis/03_outputs/section_coding_csv/keyword_trends_by_year.csv`
- `analysis/03_outputs/section_coding_csv/keyword_trends_by_period.csv`

## Manual Review Required

All AI-assisted coding JSON files must be reviewed by human researchers before they are treated as analysis results. Quote candidates must be checked against the curated section text and, where needed, the original PDF. The corpus does not include original PDFs and therefore cannot replace final source control.

ChatGPT output is preliminary analytic support, not a final scientific result. Human adjudication is required because the corpus includes PDF extraction artefacts, heuristic sectioning, possible encoding issues, and interpretive uncertainty.
