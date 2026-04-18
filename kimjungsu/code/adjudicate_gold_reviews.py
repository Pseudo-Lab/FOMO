#!/usr/bin/env python3
"""Combine multiple completed reviewer packs into an adjudication review."""

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

REVIEW_FEATURE_FIELDS = REVIEW_HEADER[:-2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a same-schema adjudication review from two or more completed "
            "blind review TSVs. Consensus cases are prefilled; disagreement cases "
            "keep reviewer_rank blank for final adjudication."
        )
    )
    parser.add_argument("--dataset", required=True, help="Original biz-planning TSV.")
    parser.add_argument(
        "--review",
        action="append",
        required=True,
        help="Completed review in reviewer_id=path form. Repeat for 2+ reviewers.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output adjudication review TSV using the same schema as a completed review.",
    )
    parser.add_argument(
        "--disagreements",
        help="Optional detailed TSV containing only disagreement cases.",
    )
    return parser.parse_args()


def parse_review_specs(specs: list[str]) -> list[tuple[str, Path]]:
    reviews: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for spec in specs:
        if "=" not in spec:
            raise SystemExit(f"error: --review must be reviewer_id=path: {spec}")
        reviewer_id, path = spec.split("=", 1)
        if not reviewer_id or not path:
            raise SystemExit(f"error: --review must be reviewer_id=path: {spec}")
        if reviewer_id in seen:
            raise SystemExit(f"error: duplicate reviewer id: {reviewer_id}")
        seen.add(reviewer_id)
        reviews.append((reviewer_id, Path(path)))
    if len(reviews) < 2:
        raise SystemExit("error: adjudication requires at least two reviewers")
    return reviews


def read_tsv(path: Path, expected_header: list[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != expected_header:
            raise SystemExit(f"error: header mismatch: {path}")
        rows = list(reader)
    if not rows:
        raise SystemExit(f"error: file has no rows: {path}")
    return rows


def index_dataset(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    dataset_index: dict[tuple[str, str], dict[str, str]] = {}
    cases: dict[str, int] = defaultdict(int)
    for row in rows:
        key = (row["case_id"], row["item_id"])
        if key in dataset_index:
            raise SystemExit(f"error: duplicate dataset row: {key}")
        dataset_index[key] = row
        cases[row["case_id"]] += 1
    for case_id, count in cases.items():
        if count < 2:
            raise SystemExit(f"error: review case must have at least two items: {case_id}")
    return dataset_index


def build_case_rows(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    cases: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        cases.setdefault(row["case_id"], []).append(row)
    return cases


def validate_and_index_review(
    rows: list[dict[str, str]],
    dataset_index: dict[tuple[str, str], dict[str, str]],
    reviewer_id: str,
) -> dict[tuple[str, str], dict[str, str]]:
    review_index: dict[tuple[str, str], dict[str, str]] = {}
    ranks_by_case: dict[str, list[int]] = defaultdict(list)

    for row in rows:
        key = (row["case_id"], row["item_id"])
        if key in review_index:
            raise SystemExit(f"error: duplicate review row for {reviewer_id}: {key}")
        if key not in dataset_index:
            raise SystemExit(f"error: review row not found in dataset for {reviewer_id}: {key}")
        for field in REVIEW_FEATURE_FIELDS:
            if row[field] != dataset_index[key][field]:
                raise SystemExit(
                    f"error: review feature mismatch for {reviewer_id} {key} field={field}"
                )
        rank_value = row["reviewer_rank"].strip()
        if not rank_value.isdigit():
            raise SystemExit(f"error: reviewer_rank must be a positive integer: {reviewer_id} {key}")
        rank = int(rank_value)
        if rank < 1:
            raise SystemExit(f"error: reviewer_rank must be >= 1: {reviewer_id} {key}")
        review_index[key] = {
            "rank": str(rank),
            "rationale": row["reviewer_rationale"].strip(),
        }
        ranks_by_case[row["case_id"]].append(rank)

    dataset_keys = set(dataset_index)
    review_keys = set(review_index)
    if dataset_keys != review_keys:
        missing = sorted(dataset_keys - review_keys)[:3]
        extra = sorted(review_keys - dataset_keys)[:3]
        raise SystemExit(
            f"error: dataset/review case-item set mismatch for {reviewer_id} "
            f"missing={missing} extra={extra}"
        )

    for case_id, ranks in ranks_by_case.items():
        expected = list(range(1, len(ranks) + 1))
        if sorted(ranks) != expected:
            raise SystemExit(
                f"error: reviewer ranks for {reviewer_id} {case_id} "
                f"must be contiguous 1..{len(ranks)}"
            )

    return review_index


def format_rate(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.00"
    return f"{numerator / denominator:.2f}"


def write_rows(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=header,
            delimiter="\t",
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def build_adjudication_rows(
    dataset_rows: list[dict[str, str]],
    reviewer_indexes: dict[str, dict[tuple[str, str], dict[str, str]]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, int]]:
    cases = build_case_rows(dataset_rows)
    reviewer_ids = list(reviewer_indexes)
    output_rows: list[dict[str, str]] = []
    disagreement_rows: list[dict[str, str]] = []
    consensus_cases = 0
    top1_consensus_cases = 0

    for case_id, rows in cases.items():
        keys = [(row["case_id"], row["item_id"]) for row in rows]
        first_reviewer = reviewer_ids[0]
        first_ranks = [reviewer_indexes[first_reviewer][key]["rank"] for key in keys]
        full_agreement = all(
            [reviewer_indexes[reviewer_id][key]["rank"] for key in keys] == first_ranks
            for reviewer_id in reviewer_ids[1:]
        )

        top1_items = set()
        for reviewer_id in reviewer_ids:
            rank_one_keys = [
                key for key in keys if reviewer_indexes[reviewer_id][key]["rank"] == "1"
            ]
            if len(rank_one_keys) != 1:
                raise SystemExit(f"error: reviewer {reviewer_id} has invalid top rank in {case_id}")
            top1_items.add(rank_one_keys[0])
        if len(top1_items) == 1:
            top1_consensus_cases += 1

        if full_agreement:
            consensus_cases += 1

        for row, key in zip(rows, keys, strict=True):
            adjudication_row = {field: row[field] for field in REVIEW_FEATURE_FIELDS}
            if full_agreement:
                adjudication_row["reviewer_rank"] = reviewer_indexes[first_reviewer][key]["rank"]
                adjudication_row["reviewer_rationale"] = (
                    f"consensus across {','.join(reviewer_ids)}"
                )
            else:
                rank_summary = "; ".join(
                    f"{reviewer_id}_rank={reviewer_indexes[reviewer_id][key]['rank']}"
                    for reviewer_id in reviewer_ids
                )
                adjudication_row["reviewer_rank"] = ""
                adjudication_row["reviewer_rationale"] = f"needs_adjudication; {rank_summary}"
                detail_row = dict(adjudication_row)
                for reviewer_id in reviewer_ids:
                    detail_row[f"{reviewer_id}_rank"] = reviewer_indexes[reviewer_id][key]["rank"]
                    detail_row[f"{reviewer_id}_rationale"] = reviewer_indexes[reviewer_id][key][
                        "rationale"
                    ]
                detail_row["adjudicated_rank"] = ""
                detail_row["adjudication_rationale"] = ""
                disagreement_rows.append(detail_row)
            output_rows.append(adjudication_row)

    stats = {
        "cases": len(cases),
        "rows": len(dataset_rows),
        "consensus_cases": consensus_cases,
        "top1_consensus_cases": top1_consensus_cases,
        "disagreement_cases": len(cases) - consensus_cases,
        "needs_adjudication_rows": len(disagreement_rows),
    }
    return output_rows, disagreement_rows, stats


def main() -> None:
    args = parse_args()
    review_specs = parse_review_specs(args.review)
    dataset_rows = read_tsv(Path(args.dataset), DATASET_HEADER)
    dataset_index = index_dataset(dataset_rows)

    reviewer_indexes: dict[str, dict[tuple[str, str], dict[str, str]]] = {}
    for reviewer_id, path in review_specs:
        review_rows = read_tsv(path, REVIEW_HEADER)
        reviewer_indexes[reviewer_id] = validate_and_index_review(
            review_rows, dataset_index, reviewer_id
        )

    adjudication_rows, disagreement_rows, stats = build_adjudication_rows(
        dataset_rows, reviewer_indexes
    )
    write_rows(Path(args.output), REVIEW_HEADER, adjudication_rows)

    if args.disagreements:
        reviewer_ids = list(reviewer_indexes)
        disagreement_header = (
            REVIEW_FEATURE_FIELDS
            + [f"{reviewer_id}_rank" for reviewer_id in reviewer_ids]
            + [f"{reviewer_id}_rationale" for reviewer_id in reviewer_ids]
            + ["adjudicated_rank", "adjudication_rationale"]
        )
        write_rows(Path(args.disagreements), disagreement_header, disagreement_rows)

    print(f"reviewers={len(reviewer_indexes)}")
    print(f"rows={stats['rows']}")
    print(f"cases={stats['cases']}")
    print(f"consensus_cases={stats['consensus_cases']}")
    print(f"disagreement_cases={stats['disagreement_cases']}")
    print(f"needs_adjudication_rows={stats['needs_adjudication_rows']}")
    print(
        "top1_agreement_rate="
        f"{format_rate(stats['top1_consensus_cases'], stats['cases'])}"
    )
    print(
        "full_rank_agreement_rate="
        f"{format_rate(stats['consensus_cases'], stats['cases'])}"
    )
    print(f"wrote_adjudication={args.output}")
    if args.disagreements:
        print(f"wrote_disagreements={args.disagreements}")


if __name__ == "__main__":
    main()
