# Corpus Snapshot Manifest

Created: 2026-05-21T14:18:51+02:00
Repository: martinsalzmannerikson/aldreomsorg-corpus-2007-2025
Branch: main
Commit SHA: `c14eca4d52b2fff035f34f48ec833b647a73609a`

## Source Files

| File | Size bytes | SHA256 | Notes |
|---|---:|---|---|
| `README.md` | 2333 | `d85826e54d789fadfc923438feac49929e91335c0cc91e04078e3185224edaca` | present |
| `DATASET_CARD.md` | 2416 | `7f4160b4c6a642f0cd8e66d3bd201976c411ecd95d81be72254c6d957900db52` | present |
| `data/corpus_2026/README.md` | 3200 | `fd7cae7f4bb0eaa6e10ae67488bb67d40a2b92c92be133603edd4c569846b7fd` | present |
| `data/corpus_2026/manifest.json` | 16058 | `2418eae365f4ae93ac4661d9c0c4fc8ee1fa63ac5bf4186584292f0ac67ded2c` | present |
| `data/corpus_2026/metadata/curated_sections.csv` | 34909 | `15c3100c3e684a5bc619e94b383c55d564870c6e301282ab0096d9c1dc93e28a` | present |
| `data/corpus_2026/texts/curated_chunks_jsonl/curated_chunks.jsonl` | 7417282 | `85919a3fe94b697e9256bc61ff58d4618aa2109909af0b0af2c00d23925139d9` | present |
| `data/corpus_2026/metadata/curated_chunks.csv` | 203075 | `29fe9ba3ae3186d90f02d27655f8502bad2a657ebe47810bfab385b6deb151e3` | present |
| `data/corpus_2026/metadata/curated_theme_summary.csv` | 522 | `29aa872940f26cb1e395a2fc7a795826910a73afe4995d41df21914ed09fa293` | present |

## Dataset Purpose

The dataset supports qualitative and computational document analysis of Swedish annual reports on care and services for older adults, 2007-2025.

## Analysis Unit

`curated_sections.csv` is the primary analysis unit. `curated_chunks.jsonl` is used for text-near search and citation support.

Manifest curated sections: 114.
Manifest curated chunks: 1428.

## Source-Control Caveat

Original PDF reports are not included in this repository. The corpus supports analysis and retrieval, but it cannot replace the original PDFs for final source checking.

## Known Limitations

- PDF extraction is imperfect.
- Sectioning is reproducible but partly heuristic.
- Some older reports may contain encoding artefacts in extracted text.
- Original PDF reports are not included in the repository.
- Copyright and reuse conditions should be reviewed before relying on redistribution.

## Assumptions

- Assumption: local system time in Europe/Stockholm is the appropriate audit timestamp.
- Assumption: repository-relative corpus files are the frozen analysis inputs for this audit start.

## AI Use Note

AI-generated text must not be used as a replacement for source checking against the corpus and, where needed, the original PDFs.
