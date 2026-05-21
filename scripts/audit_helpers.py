from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Europe/Stockholm")
AUDIT_LOG = ROOT / "analysis/04_quality_checks/audit_log.csv"
INVENTORY = ROOT / "analysis/01_inputs/input_file_inventory.csv"
AUDIT_COLUMNS = [
    "timestamp",
    "step",
    "actor",
    "tool_or_model",
    "input_files",
    "output_files",
    "prompt_file",
    "notes",
]


def timestamp() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def repo_path(path: str | Path) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path
    return ROOT / path


def rel_path(path: str | Path) -> str:
    path = Path(path)
    if not path.is_absolute():
        return path.as_posix()
    return path.relative_to(ROOT).as_posix()


def sha256(path: str | Path) -> str:
    target = repo_path(path)
    h = hashlib.sha256()
    with target.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dirs(paths: Iterable[str | Path]) -> None:
    for path in paths:
        repo_path(path).mkdir(parents=True, exist_ok=True)


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with repo_path(path).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: str | Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    target = repo_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def read_json(path: str | Path) -> Any:
    with repo_path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with repo_path(path).open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            record["_line_number"] = line_number
            records.append(record)
    return records


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> int:
    target = repo_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with target.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def append_audit_log(
    *,
    step: str,
    input_files: Iterable[str | Path],
    output_files: Iterable[str | Path],
    prompt_file: str = "",
    notes: str = "",
    actor: str = "Codex",
    tool_or_model: str = "Codex 5.5",
) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    exists = AUDIT_LOG.exists()
    with AUDIT_LOG.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=AUDIT_COLUMNS)
        if not exists:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp": timestamp(),
                "step": step,
                "actor": actor,
                "tool_or_model": tool_or_model,
                "input_files": "|".join(rel_path(path) for path in input_files),
                "output_files": "|".join(rel_path(path) for path in output_files),
                "prompt_file": prompt_file,
                "notes": notes,
            }
        )


def check_files_against_inventory(
    inventory_path: str | Path = INVENTORY,
    only_prefix: str = "data/corpus_2026/",
) -> list[str]:
    inventory = repo_path(inventory_path)
    if not inventory.exists():
        return [f"inventory_missing:{rel_path(inventory)}"]

    discrepancies: list[str] = []
    for row in read_csv(inventory):
        file_path = row.get("file_path", "")
        expected = row.get("sha256", "")
        if only_prefix and not file_path.startswith(only_prefix):
            continue
        target = repo_path(file_path)
        if not target.exists():
            discrepancies.append(f"missing:{file_path}")
            continue
        actual = sha256(target)
        if expected and expected != "MISSING" and actual != expected:
            discrepancies.append(f"sha256_changed:{file_path}")
    return discrepancies


def data_check_note() -> str:
    discrepancies = check_files_against_inventory()
    if not discrepancies:
        return "source_data_check=ok"
    return "source_data_check=" + ";".join(discrepancies)
