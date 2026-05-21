from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "corpus_2026"


def count_csv(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def count_jsonl(path: Path) -> int:
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def main() -> None:
    manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
    curated = manifest.get("curated_layer", {})

    checks = {
        "reports": count_csv(CORPUS / "metadata" / "reports.csv"),
        "curated_sections": count_csv(CORPUS / "metadata" / "curated_sections.csv"),
        "curated_chunks": count_jsonl(
            CORPUS / "texts" / "curated_chunks_jsonl" / "curated_chunks.jsonl"
        ),
    }

    print(json.dumps({"manifest_curated": curated, "observed": checks}, indent=2))


if __name__ == "__main__":
    main()

