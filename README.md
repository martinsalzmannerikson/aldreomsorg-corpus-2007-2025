# Vard och omsorg for aldre: corpus 2007-2025

This repository contains a curated research corpus built from Swedish annual reports on care and services for older adults, 2007-2025.

The corpus was prepared for qualitative and computational document analysis. It preserves links back to the original annual reports through year, section title, source file, and PDF page metadata.

## Contents

- `data/corpus_2026/metadata/curated_sections.csv`  
  Recommended primary analysis table. One row per curated semantic section.

- `data/corpus_2026/texts/curated_sections/`  
  Curated section text files, grouped by year.

- `data/corpus_2026/metadata/curated_chunks.csv`  
  Metadata for LLM/search chunks generated from curated sections.

- `data/corpus_2026/texts/curated_chunks_jsonl/curated_chunks.jsonl`  
  Chunk text with metadata in JSONL format.

- `data/corpus_2026/manifest.json`  
  Machine-readable corpus summary.

- `data/corpus_2026/README.md`  
  Detailed corpus construction notes.

The repository does not include the original PDF reports. It includes extracted text and metadata generated from local source files.

## Recommended analysis unit

Use `curated_sections.csv` as the primary unit for scientific document analysis. Use `curated_chunks.jsonl` for semantic search, summarization, and LLM-assisted coding.

The curated layer contains:

- 19 annual reports, 2007-2025
- 114 curated semantic sections
- 1,428 text chunks
- Original PDF page references where available

## Corpus design

The dataset has several levels:

1. `report`: one annual report.
2. `page`: extracted page text with PDF page numbers.
3. `section`: semantically meaningful analysis units.
4. `chunk`: LLM/search-friendly units derived from sections.

For 2007-2024, existing `Data_split` section titles were used as semantic anchors, while the actual text was extracted from the full original annual reports. For 2025, the report was split into top-level sections from its table of contents.

## Important rights note

The extracted text derives from reports published by Swedish public bodies. The original reports may still be protected by copyright. Treat this repository as a research dataset and check reuse rights before making it public or redistributing it beyond the research context.

## Suggested citation

See `CITATION.cff`.

