from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict

from audit_helpers import append_audit_log, data_check_note, ensure_dirs, read_csv, repo_path, write_csv


INPUT = "data/corpus_2026/metadata/curated_sections.csv"
BY_YEAR = "analysis/03_outputs/section_coding_csv/keyword_trends_by_year.csv"
BY_PERIOD = "analysis/03_outputs/section_coding_csv/keyword_trends_by_period.csv"

KEYWORD_GROUPS = {
    "delaktighet": ["delaktighet", "inflytande", "självbestämmande", "personcentrerad", "individanpassad"],
    "trygghet_sakerhet": ["trygghet", "säkerhet", "risk", "patientsäkerhet", "avvikelse"],
    "kontinuitet_samordning": ["kontinuitet", "samordning", "sammanhållen", "fast omsorgskontakt", "vårdkedja"],
    "anhoriga": ["anhörig", "närstående", "familj"],
    "personal_kompetens": ["personal", "kompetens", "bemanning", "utbildning", "undersköterska", "sjuksköterska"],
    "prevention_rehabilitering": ["förebyggande", "prevention", "rehabilitering", "funktionsförmåga"],
    "digitalisering": ["digitalisering", "välfärdsteknik", "e-hälsa", "teknik", "digital"],
    "jamlikhet": ["jämlik", "ojämlik", "tillgång", "minoritet", "utsatt"],
}


def period_for_year(year: int) -> str:
    if year <= 2010:
        return "2007-2010"
    if year <= 2014:
        return "2011-2014"
    if year <= 2018:
        return "2015-2018"
    if year <= 2022:
        return "2019-2022"
    return "2023-2025"


def count_terms(text: str, terms: list[str]) -> Counter[str]:
    lowered = text.lower()
    counts: Counter[str] = Counter()
    for term in terms:
        count = lowered.count(term.lower())
        if count:
            counts[term] = count
    return counts


def load_section_text(path: str) -> str:
    target = repo_path(path)
    if not target.exists():
        return ""
    return target.read_text(encoding="utf-8", errors="replace")


def run() -> tuple[int, int]:
    ensure_dirs(["analysis/03_outputs/section_coding_csv"])
    sections = read_csv(INPUT)
    years = sorted({int(row["year"]) for row in sections if row.get("year")})
    periods = ["2007-2010", "2011-2014", "2015-2018", "2019-2022", "2023-2025"]

    year_stats: dict[tuple[int, str], dict[str, object]] = {}
    period_stats: dict[tuple[str, str], dict[str, object]] = {}

    for year in years:
        for group in KEYWORD_GROUPS:
            year_stats[(year, group)] = {
                "total_hits": 0,
                "sections_with_hits": 0,
                "sections_total": 0,
                "term_hits": Counter(),
            }
    for period in periods:
        for group in KEYWORD_GROUPS:
            period_stats[(period, group)] = {
                "total_hits": 0,
                "sections_with_hits": 0,
                "sections_total": 0,
                "years": set(),
                "term_hits": Counter(),
            }

    missing_texts = 0
    for section in sections:
        year = int(section["year"])
        period = period_for_year(year)
        text = load_section_text(section.get("text_path", ""))
        if not text:
            missing_texts += 1
        for group, terms in KEYWORD_GROUPS.items():
            term_hits = count_terms(text, terms)
            total_hits = sum(term_hits.values())

            y = year_stats[(year, group)]
            y["sections_total"] = int(y["sections_total"]) + 1
            y["total_hits"] = int(y["total_hits"]) + total_hits
            y["term_hits"].update(term_hits)  # type: ignore[union-attr]
            if total_hits:
                y["sections_with_hits"] = int(y["sections_with_hits"]) + 1

            p = period_stats[(period, group)]
            p["sections_total"] = int(p["sections_total"]) + 1
            p["total_hits"] = int(p["total_hits"]) + total_hits
            p["term_hits"].update(term_hits)  # type: ignore[union-attr]
            p["years"].add(year)  # type: ignore[union-attr]
            if total_hits:
                p["sections_with_hits"] = int(p["sections_with_hits"]) + 1

    by_year_rows = []
    for (year, group), stats in sorted(year_stats.items()):
        term_hits = dict(sorted(stats["term_hits"].items()))  # type: ignore[union-attr]
        by_year_rows.append(
            {
                "year": year,
                "keyword_group": group,
                "total_hits": stats["total_hits"],
                "sections_with_hits": stats["sections_with_hits"],
                "sections_total": stats["sections_total"],
                "term_hits_json": json.dumps(term_hits, ensure_ascii=False, sort_keys=True),
            }
        )

    by_period_rows = []
    for (period, group), stats in sorted(period_stats.items()):
        term_hits = dict(sorted(stats["term_hits"].items()))  # type: ignore[union-attr]
        years_present = sorted(stats["years"])  # type: ignore[arg-type]
        by_period_rows.append(
            {
                "period": period,
                "keyword_group": group,
                "total_hits": stats["total_hits"],
                "sections_with_hits": stats["sections_with_hits"],
                "sections_total": stats["sections_total"],
                "years": "|".join(str(year) for year in years_present),
                "term_hits_json": json.dumps(term_hits, ensure_ascii=False, sort_keys=True),
            }
        )

    write_csv(
        BY_YEAR,
        by_year_rows,
        ["year", "keyword_group", "total_hits", "sections_with_hits", "sections_total", "term_hits_json"],
    )
    write_csv(
        BY_PERIOD,
        by_period_rows,
        ["period", "keyword_group", "total_hits", "sections_with_hits", "sections_total", "years", "term_hits_json"],
    )
    append_audit_log(
        step="keyword_trends",
        input_files=[INPUT],
        output_files=[BY_YEAR, BY_PERIOD],
        notes=f"keyword_groups={len(KEYWORD_GROUPS)}; missing_texts={missing_texts}; period_assumption=2007-2010|2011-2014|2015-2018|2019-2022|2023-2025; {data_check_note()}",
    )
    return len(by_year_rows), len(by_period_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Count predefined keyword groups in curated section texts.")
    parser.parse_args()
    year_rows, period_rows = run()
    print(f"Wrote {year_rows} year rows and {period_rows} period rows.")


if __name__ == "__main__":
    main()
