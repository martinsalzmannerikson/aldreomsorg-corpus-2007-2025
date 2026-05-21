from __future__ import annotations

import argparse
from collections import Counter

from audit_helpers import append_audit_log, data_check_note, ensure_dirs, read_jsonl, write_jsonl


INPUT = "data/corpus_2026/texts/curated_chunks_jsonl/curated_chunks.jsonl"
OUTPUT_DIR = "analysis/03_outputs/memos"


def keyword_counts(text: str, keywords: list[str]) -> dict[str, int]:
    lowered = text.lower()
    counts: dict[str, int] = {}
    for keyword in keywords:
        counts[keyword] = lowered.count(keyword.lower())
    return {keyword: count for keyword, count in counts.items() if count > 0}


def retrieve(section_id: str, keywords: list[str]) -> str:
    ensure_dirs([OUTPUT_DIR])
    output = f"{OUTPUT_DIR}/chunks_{section_id}.jsonl"
    payload = []
    aggregate_counts: Counter[str] = Counter()

    for chunk in read_jsonl(INPUT):
        if chunk.get("curated_section_id") != section_id:
            continue
        chunk = dict(chunk)
        chunk.pop("_line_number", None)
        if keywords:
            matches = keyword_counts(str(chunk.get("text", "")), keywords)
            chunk["keyword_matches"] = matches
            chunk["keyword_match_count"] = sum(matches.values())
            aggregate_counts.update(matches)
        payload.append(chunk)

    write_jsonl(output, payload)
    notes = [
        f"section_id={section_id}",
        f"chunks={len(payload)}",
        data_check_note(),
    ]
    if keywords:
        notes.append("keywords=" + "|".join(keywords))
        notes.append("keyword_hits=" + "|".join(f"{k}:{v}" for k, v in sorted(aggregate_counts.items())))

    append_audit_log(
        step="retrieve_chunks_for_section",
        input_files=[INPUT],
        output_files=[output],
        notes="; ".join(notes),
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve chunks for a curated section.")
    parser.add_argument("--section-id", required=True)
    parser.add_argument("--keywords", nargs="*", default=[])
    args = parser.parse_args()
    output = retrieve(args.section_id, args.keywords)
    print(f"Wrote chunks to {output}")


if __name__ == "__main__":
    main()
