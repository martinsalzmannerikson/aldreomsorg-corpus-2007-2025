# Corpus 2026: Vard och omsorg for aldre 2007-2025

Created: 2026-05-21T12:46:34
Source root: source (external original PDFs, not included)
Corpus root: source/2026
Extraction method: 2026-02-multilevel-toc-plus-heading-search

## Proposed corpus structure

This corpus is built for scientific document analysis and LLM-assisted work. It keeps full reports as source documents, pages as citation anchors, sections as the recommended coding units, and chunks as retrieval/LLM units.

Levels:

1. Report: one annual report as a complete source document.
2. Page: stable PDF page unit for traceability and citation.
3. Section: primary analysis unit, based on extracted TOC headings plus heading search from extraherade_rubriker.xlsx where available.
4. Chunk: approximately 850-word text unit inside a section, with metadata back to year, report, heading and page range.

## Files

- metadata/reports.csv: report-level metadata.
- metadata/pages.csv: page-level metadata, without full text.
- metadata/headings.csv: headings used to construct section anchors.
- metadata/sections.csv: primary analysis units and paths to section texts.
- metadata/chunks.csv: chunk metadata.
- metadata/theme_summary.csv: rough harmonized theme overview.
- metadata/legacy_data_split.csv: index of the older Data_split files for comparison/audit.
- texts/reports/: full extracted text per report.
- texts/pages_jsonl/: page text per report, one JSON object per line.
- texts/sections/: section text files grouped by year.
- texts/chunks_jsonl/chunks.jsonl: all chunks with text and metadata.
- manifest.json: machine-readable corpus summary.
- logs/extraction_warnings.txt: warnings and fallback decisions.

## Recommended use

Use metadata/sections.csv as the primary sampling and coding table. Use pages_jsonl for source checking. Use chunks.jsonl for semantic search, summarization and LLM-assisted coding. Keep the original PDFs in source as the audit trail.

## Important caveat

Sectioning is reproducible but still heuristic because PDF text extraction and table-of-contents layout vary across the series. This corpus therefore stores explicit PDF page references and keeps full text/page text alongside sections and chunks.

## Curated semantic layer (recommended)

The files below are the recommended primary layer for qualitative/scientific document analysis:

- metadata/curated_sections.csv: curated semantic sections.
- metadata/curated_chunks.csv: metadata for chunks generated from curated sections.
- metadata/curated_theme_summary.csv: theme overview for curated sections.
- texts/curated_sections/: text files for curated sections.
- texts/curated_chunks_jsonl/curated_chunks.jsonl: curated chunks with text.

Construction: for 2007-2024, the existing Data_split filenames are used as semantic section anchors, but the actual text is extracted from the full original annual reports so that original PDF page references are preserved. The 2025 report is split into top-level sections from its table of contents. The automatically extracted heading sections remain available as a secondary layer, but curated_sections.csv is the best starting point.
