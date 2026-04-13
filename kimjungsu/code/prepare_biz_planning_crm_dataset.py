#!/usr/bin/env python3
"""Prepare a biz-planning service_value_eval TSV from Maven CRM data.

The public CRM dataset does not contain board deadlines, cross-team dependency,
or human gold labels. This script creates a deterministic silver-label dataset
from observable proxies so the harness can be tested against a larger,
pipeline-shaped source before real company logs are available.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import math
import re
import sys
from bisect import bisect_right
from collections import defaultdict
from pathlib import Path


TSV_HEADER = [
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Maven CRM Sales Opportunities CSVs to biz-planning TSV."
    )
    parser.add_argument(
        "--crm-dir",
        required=True,
        help="Directory containing sales_pipeline.csv, accounts.csv, products.csv, and sales_teams.csv.",
    )
    parser.add_argument("--output", required=True, help="Output TSV path.")
    parser.add_argument(
        "--items-per-case",
        type=int,
        default=4,
        help="Maximum ranked opportunities to keep per quarter/region case.",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=8,
        help="Maximum quarter/region cases to emit after filtering.",
    )
    parser.add_argument(
        "--min-items-per-case",
        type=int,
        default=3,
        help="Minimum opportunities required before a case is emitted.",
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def require_file(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"error: missing required file: {path}")


def parse_float(value: str | None, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def parse_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\t", " ")).strip()


def bucket(value: float, values: list[float], scale: int) -> int:
    if not values:
        return 1
    rank = bisect_right(values, value)
    return max(1, min(scale, math.ceil((rank / len(values)) * scale)))


def percentile(values: list[float], ratio: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = min(len(sorted_values) - 1, max(0, math.ceil(len(sorted_values) * ratio) - 1))
    return sorted_values[index]


def quarter_start(value: dt.date) -> dt.date:
    quarter_month = ((value.month - 1) // 3) * 3 + 1
    return dt.date(value.year, quarter_month, 1)


def quarter_label(value: dt.date) -> str:
    quarter = ((value.month - 1) // 3) + 1
    return f"{value.year}Q{quarter}"


def load_lookup(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows if row.get(key)}


def build_candidates(crm_dir: Path) -> list[dict[str, object]]:
    pipeline_path = crm_dir / "sales_pipeline.csv"
    accounts_path = crm_dir / "accounts.csv"
    products_path = crm_dir / "products.csv"
    teams_path = crm_dir / "sales_teams.csv"

    for path in [pipeline_path, accounts_path, products_path, teams_path]:
        require_file(path)

    accounts = load_lookup(read_csv(accounts_path), "account")
    teams = load_lookup(read_csv(teams_path), "sales_agent")
    products = {normalize_key(row["product"]): row for row in read_csv(products_path) if row.get("product")}

    raw_candidates: list[dict[str, object]] = []
    skipped = 0

    for row in read_csv(pipeline_path):
        close_date = parse_date(row.get("close_date"))
        close_value = parse_float(row.get("close_value"))
        if close_date is None or close_value is None:
            skipped += 1
            continue

        account = accounts.get(row.get("account", ""), {})
        team = teams.get(row.get("sales_agent", ""), {})
        product = products.get(normalize_key(row.get("product", "")), {})

        product_price = parse_float(product.get("sales_price"), close_value) or close_value
        account_revenue = parse_float(account.get("revenue"), 0.0) or 0.0
        account_employees = parse_float(account.get("employees"), 0.0) or 0.0
        raw_gap = abs(close_value - product_price) / max(product_price, 1.0) * 100.0

        raw_candidates.append(
            {
                "opportunity_id": row["opportunity_id"],
                "account": row.get("account", ""),
                "product": row.get("product", ""),
                "deal_stage": row.get("deal_stage", ""),
                "close_date": close_date,
                "close_value": close_value,
                "account_revenue": account_revenue,
                "account_employees": account_employees,
                "regional_office": team.get("regional_office", "unknown") or "unknown",
                "manager": team.get("manager", "unknown") or "unknown",
                "raw_gap": raw_gap,
            }
        )

    if not raw_candidates:
        raise SystemExit(f"error: no usable closed opportunities found in {pipeline_path}")

    close_values = sorted(float(row["close_value"]) for row in raw_candidates)
    account_revenues = sorted(float(row["account_revenue"]) for row in raw_candidates)
    employee_counts = sorted(float(row["account_employees"]) for row in raw_candidates)
    gaps = sorted(float(row["raw_gap"]) for row in raw_candidates)

    high_value = percentile(close_values, 0.80)
    high_account_revenue = percentile(account_revenues, 0.80)
    high_employee_count = percentile(employee_counts, 0.75)

    candidates: list[dict[str, object]] = []
    for row in raw_candidates:
        close_date = row["close_date"]
        assert isinstance(close_date, dt.date)
        close_value = float(row["close_value"])

        forecast_gap_pct = bucket(float(row["raw_gap"]), gaps, 10)
        revenue_impact = bucket(close_value, close_values, 5)

        deadline_days = max(0, (close_date - quarter_start(close_date)).days)
        board_deadline_hours = max(12, min(720, deadline_days * 24))

        stage = str(row["deal_stage"])
        dependency = {"Won": 3, "Lost": 1, "Engaging": 4, "Prospecting": 2}.get(stage, 2)
        if float(row["account_employees"]) >= high_employee_count:
            dependency += 1
        if "Plus" in str(row["product"]) or str(row["product"]).startswith("GTK"):
            dependency += 1
        cross_team_dependency = max(1, min(5, dependency))

        exec_visibility = int(
            close_value >= high_value
            or float(row["account_revenue"]) >= high_account_revenue
            or str(row["product"]).startswith("GTK")
        )

        deadline_score = 40 if board_deadline_hours <= 24 else 25 if board_deadline_hours <= 72 else 10 if board_deadline_hours <= 168 else 0
        stage_score = {"Won": 30, "Lost": -10, "Engaging": 15, "Prospecting": 5}.get(stage, 0)
        silver_score = (
            stage_score
            + (revenue_impact * 25)
            + (exec_visibility * 20)
            + (cross_team_dependency * 12)
            + deadline_score
            + (forecast_gap_pct * 4)
        )

        regional_office = clean_text(str(row["regional_office"]))
        case_id = f"{quarter_label(close_date)}_{normalize_key(regional_office) or 'unknown'}"
        title = clean_text(f"{row['account']} {row['product']} {stage} via {regional_office}")

        candidates.append(
            {
                "case_id": case_id,
                "item_id": row["opportunity_id"],
                "title": title,
                "forecast_gap_pct": forecast_gap_pct,
                "board_deadline_hours": board_deadline_hours,
                "cross_team_dependency": cross_team_dependency,
                "exec_visibility": exec_visibility,
                "revenue_impact": revenue_impact,
                "silver_score": silver_score,
                "close_value": close_value,
            }
        )

    print(
        f"source_rows={len(raw_candidates) + skipped} usable_closed_rows={len(raw_candidates)} skipped_open_rows={skipped}",
        file=sys.stderr,
    )
    return candidates


def emit_tsv(candidates: list[dict[str, object]], output_path: Path, items_per_case: int, max_cases: int, min_items_per_case: int) -> None:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in candidates:
        grouped[str(row["case_id"])].append(row)

    emitted: list[dict[str, object]] = []
    for case_id in sorted(grouped):
        ranked = sorted(
            grouped[case_id],
            key=lambda row: (-float(row["silver_score"]), -float(row["close_value"]), str(row["item_id"])),
        )
        if len(ranked) < min_items_per_case:
            continue
        for rank, row in enumerate(ranked[:items_per_case], start=1):
            row = dict(row)
            row["expected_rank"] = rank
            emitted.append(row)
        if len({str(row["case_id"]) for row in emitted}) >= max_cases:
            break

    if not emitted:
        raise SystemExit("error: no cases emitted; relax max/min case settings")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=TSV_HEADER,
            delimiter="\t",
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in emitted:
            writer.writerow(row)

    print(
        f"wrote={output_path} rows={len(emitted)} cases={len({row['case_id'] for row in emitted})}",
        file=sys.stderr,
    )


def main() -> None:
    args = parse_args()
    if args.items_per_case < 1:
        raise SystemExit("error: --items-per-case must be >= 1")
    if args.max_cases < 1:
        raise SystemExit("error: --max-cases must be >= 1")
    if args.min_items_per_case < 1:
        raise SystemExit("error: --min-items-per-case must be >= 1")

    candidates = build_candidates(Path(args.crm_dir))
    emit_tsv(
        candidates,
        Path(args.output),
        items_per_case=args.items_per_case,
        max_cases=args.max_cases,
        min_items_per_case=args.min_items_per_case,
    )


if __name__ == "__main__":
    main()
