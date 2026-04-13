#!/usr/bin/env python3
"""Apply human reviewer ranks to a biz-planning evaluation dataset."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


DATASET_HEADER = [
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

REVIEW_HEADER = [
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
        description="Convert a completed review TSV into a service_value_eval dataset."
    )
    parser.add_argument("--dataset", required=True, help="Original biz-planning TSV.")
    parser.add_argument("--review", required=True, help="Completed reviewer TSV.")
    parser.add_argument("--output", required=True, help="Output gold-label TSV.")
    return parser.parse_args()


def read_tsv(path: Path, expected_header: list[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != expected_header:
            raise SystemExit(f"error: header mismatch: {path}")
        rows = list(reader)
    if not rows:
        raise SystemExit(f"error: file has no rows: {path}")
    return rows


def validate_and_index_review(rows: list[dict[str, str]]) -> dict[tuple[str, str], str]:
    review_index: dict[tuple[str, str], str] = {}
    ranks_by_case: dict[str, list[int]] = defaultdict(list)

    for row in rows:
        key = (row["case_id"], row["item_id"])
        if key in review_index:
            raise SystemExit(f"error: duplicate review row: {key}")
        rank_value = row["reviewer_rank"]
        if not rank_value.isdigit():
            raise SystemExit(f"error: reviewer_rank must be a positive integer: {key}")
        rank = int(rank_value)
        if rank < 1:
            raise SystemExit(f"error: reviewer_rank must be >= 1: {key}")
        review_index[key] = str(rank)
        ranks_by_case[row["case_id"]].append(rank)

    for case_id, ranks in ranks_by_case.items():
        expected = list(range(1, len(ranks) + 1))
        if sorted(ranks) != expected:
            raise SystemExit(
                f"error: reviewer ranks for {case_id} must be contiguous 1..{len(ranks)}"
            )

    return review_index


def apply_labels(dataset_rows: list[dict[str, str]], review_index: dict[tuple[str, str], str]) -> list[dict[str, str]]:
    dataset_keys = {(row["case_id"], row["item_id"]) for row in dataset_rows}
    review_keys = set(review_index)
    if dataset_keys != review_keys:
        missing = sorted(dataset_keys - review_keys)[:3]
        extra = sorted(review_keys - dataset_keys)[:3]
        raise SystemExit(f"error: dataset/review case-item set mismatch missing={missing} extra={extra}")

    output: list[dict[str, str]] = []
    for row in dataset_rows:
        copy = dict(row)
        copy["expected_rank"] = review_index[(row["case_id"], row["item_id"])]
        output.append(copy)
    return output


def write_dataset(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=DATASET_HEADER,
            delimiter="\t",
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    args = parse_args()
    dataset_rows = read_tsv(Path(args.dataset), DATASET_HEADER)
    review_rows = read_tsv(Path(args.review), REVIEW_HEADER)
    review_index = validate_and_index_review(review_rows)
    output_rows = apply_labels(dataset_rows, review_index)
    write_dataset(output_rows, Path(args.output))
    case_count = len({row["case_id"] for row in output_rows})
    print(f"wrote={args.output} rows={len(output_rows)} cases={case_count}")


if __name__ == "__main__":
    main()
