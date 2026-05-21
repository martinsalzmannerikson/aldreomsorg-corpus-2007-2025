# Dataset Card

## Dataset name

Vard och omsorg for aldre: corpus 2007-2025

## Purpose

The dataset supports scientific document analysis of how Swedish care and services for older adults are described, measured, problematized, and governed over time.

## Source material

Annual reports from 2007-2025 located locally under `D:\Data` at the time of corpus construction. The series includes:

- 2007-2015: `Oppna jamforelser` reports.
- 2016-2025: Socialstyrelsen annual status reports, `Lagesrapport`.

## Dataset structure

The recommended analysis layer is:

- `metadata/curated_sections.csv`
- `texts/curated_sections/`
- `metadata/curated_chunks.csv`
- `texts/curated_chunks_jsonl/curated_chunks.jsonl`

Additional automatically generated metadata and text layers are included for auditability and alternative analyses.

## Unit of analysis

Primary unit: curated semantic section.

Secondary units:

- report
- page
- automatically extracted heading section
- chunk

## Construction method

The corpus was built in `D:\Data\2026`.

For 2007-2024, existing split-section titles were used as a semantic section map. The final text, however, was extracted from the original full annual reports so that page references remain tied to the original PDFs.

For 2025, top-level table-of-contents sections were manually encoded from the report structure and extracted from the full report.

## Known limitations

- PDF text extraction is imperfect.
- Some older reports have encoding artefacts in front matter.
- Sectioning is reproducible but partly heuristic.
- Harmonized themes are starting metadata, not final qualitative codes.
- The data includes extracted text from published reports, so copyright and reuse conditions should be reviewed before public release.

## Recommended quality checks before publication

- Verify whether the GitHub repository should be private or public.
- Review copyright/reuse permissions for extracted report text.
- Spot-check page references against original PDFs.
- Decide whether to include all extracted fulltext layers or only the curated layer.

## Suggested use

Suitable for:

- qualitative document analysis
- thematic coding
- discourse-oriented analysis
- longitudinal policy analysis
- LLM-assisted retrieval and summarization

Not intended as:

- official reproduction of the source reports
- replacement for the original PDFs
- validated statistical register data

