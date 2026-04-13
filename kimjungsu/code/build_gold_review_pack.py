#!/usr/bin/env python3
"""Build a blind reviewer pack for biz-planning gold labels."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


INPUT_HEADER = [
    "case_id",
    "item_id",
    "title",
    "forecast_gap_pct",
    "board_deadline_hours",
    "cross_team_dependency",
    "exec_visibility",
    "revenue_impact",
    "expected_rank",
]

OUTPUT_HEADER = [
    "case_id",
    "item_id",
    "title",
    "forecast_gap_pct",
    "board_deadline_hours",
    "cross_team_dependency",
    "exec_visibility",
    "revenue_impact",
    "reviewer_rank",
    "reviewer_rationale",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a blind review TSV from a biz-planning service_value_eval dataset."
    )
    parser.add_argument("--dataset", required=True, help="Input biz-planning TSV.")
    parser.add_argument("--output", required=True, help="Output review TSV.")
    return parser.parse_args()


def read_dataset(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != INPUT_HEADER:
            raise SystemExit(f"error: input header does not match biz-planning eval schema: {path}")
        rows = list(reader)
    if not rows:
        raise SystemExit(f"error: input dataset has no rows: {path}")
    return rows


def validate_rows(rows: list[dict[str, str]]) -> None:
    seen: set[tuple[str, str]] = set()
    cases: dict[str, int] = defaultdict(int)
    for row in rows:
        key = (row["case_id"], row["item_id"])
        if key in seen:
            raise SystemExit(f"error: duplicate case/item in input: {key}")
        seen.add(key)
        cases[row["case_id"]] += 1
    for case_id, count in cases.items():
        if count < 2:
            raise SystemExit(f"error: review case must have at least two items: {case_id}")


def write_review_pack(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=OUTPUT_HEADER,
            delimiter="\t",
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            out = {key: row[key] for key in OUTPUT_HEADER if key in row}
            out["reviewer_rank"] = ""
            out["reviewer_rationale"] = ""
            writer.writerow(out)


def main() -> None:
    args = parse_args()
    rows = read_dataset(Path(args.dataset))
    validate_rows(rows)
    write_review_pack(rows, Path(args.output))
    case_count = len({row["case_id"] for row in rows})
    print(f"wrote={args.output} rows={len(rows)} cases={case_count}")


if __name__ == "__main__":
    main()
