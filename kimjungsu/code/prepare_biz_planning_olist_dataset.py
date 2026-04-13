#!/usr/bin/env python3
"""Prepare a biz-planning TSV from Olist public real logs.

This uses anonymized real marketing funnel and e-commerce order logs. The
result still uses deterministic silver labels because the public data does not
contain a human "planning team first review item" label.
"""

from __future__ import annotations

import argparse
import calendar
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
        description="Convert Olist real public logs to biz-planning silver-label TSV."
    )
    parser.add_argument(
        "--olist-dir",
        required=True,
        help="Directory containing Olist marketing funnel and e-commerce CSV files.",
    )
    parser.add_argument("--output", required=True, help="Output TSV path.")
    parser.add_argument("--items-per-case", type=int, default=4)
    parser.add_argument("--max-cases", type=int, default=12)
    parser.add_argument("--min-items-per-case", type=int, default=4)
    return parser.parse_args()


def require_file(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"error: missing required file: {path}")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def parse_float(value: str | None, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def parse_datetime(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\t", " ")).strip()


def bucket(value: float, sorted_values: list[float], scale: int) -> int:
    if not sorted_values:
        return 1
    rank = bisect_right(sorted_values, value)
    return max(1, min(scale, math.ceil((rank / len(sorted_values)) * scale)))


def month_end_hours(timestamp: dt.datetime) -> int:
    last_day = calendar.monthrange(timestamp.year, timestamp.month)[1]
    end = dt.datetime(timestamp.year, timestamp.month, last_day, 23, 59, 59)
    hours = math.ceil((end - timestamp).total_seconds() / 3600)
    return max(12, min(720, hours))


def load_order_reviews(path: Path) -> dict[str, float]:
    scores: dict[str, list[float]] = defaultdict(list)
    for row in read_csv(path):
        order_id = row.get("order_id", "")
        score = parse_float(row.get("review_score"))
        if order_id:
            scores[order_id].append(score)
    return {order_id: sum(values) / len(values) for order_id, values in scores.items()}


def load_order_payments(path: Path) -> dict[str, dict[str, float | int]]:
    payments: dict[str, dict[str, float | int | set[str]]] = defaultdict(
        lambda: {"value": 0.0, "max_installments": 0, "types": set()}
    )
    for row in read_csv(path):
        order_id = row.get("order_id", "")
        if not order_id:
            continue
        record = payments[order_id]
        record["value"] = float(record["value"]) + parse_float(row.get("payment_value"))
        record["max_installments"] = max(int(record["max_installments"]), int(parse_float(row.get("payment_installments"))))
        cast_types = record["types"]
        assert isinstance(cast_types, set)
        if row.get("payment_type"):
            cast_types.add(row["payment_type"])

    output: dict[str, dict[str, float | int]] = {}
    for order_id, record in payments.items():
        cast_types = record["types"]
        assert isinstance(cast_types, set)
        output[order_id] = {
            "value": float(record["value"]),
            "max_installments": int(record["max_installments"]),
            "type_count": len(cast_types),
        }
    return output


def build_seller_months(olist_dir: Path) -> list[dict[str, object]]:
    paths = {
        "closed": olist_dir / "olist_closed_deals_dataset.csv",
        "mql": olist_dir / "olist_marketing_qualified_leads_dataset.csv",
        "orders": olist_dir / "olist_orders_dataset.csv",
        "items": olist_dir / "olist_order_items_dataset.csv",
        "payments": olist_dir / "olist_order_payments_dataset.csv",
        "reviews": olist_dir / "olist_order_reviews_dataset.csv",
        "sellers": olist_dir / "olist_sellers_dataset.csv",
    }
    for path in paths.values():
        require_file(path)

    mqls = {row["mql_id"]: row for row in read_csv(paths["mql"]) if row.get("mql_id")}
    closed = {row["seller_id"]: row for row in read_csv(paths["closed"]) if row.get("seller_id")}
    orders = {row["order_id"]: row for row in read_csv(paths["orders"]) if row.get("order_id")}
    sellers = {row["seller_id"]: row for row in read_csv(paths["sellers"]) if row.get("seller_id")}
    reviews = load_order_reviews(paths["reviews"])
    payments = load_order_payments(paths["payments"])

    seller_months: dict[tuple[str, str], dict[str, object]] = {}
    skipped_items = 0

    for item in read_csv(paths["items"]):
        seller_id = item.get("seller_id", "")
        if seller_id not in closed:
            continue

        order = orders.get(item.get("order_id", ""))
        if not order:
            skipped_items += 1
            continue

        purchase_ts = parse_datetime(order.get("order_purchase_timestamp"))
        if purchase_ts is None:
            skipped_items += 1
            continue

        month = purchase_ts.strftime("%Y-%m")
        key = (seller_id, month)
        record = seller_months.setdefault(
            key,
            {
                "seller_id": seller_id,
                "month": month,
                "orders": set(),
                "products": set(),
                "revenue": 0.0,
                "freight": 0.0,
                "late_orders": 0,
                "review_scores": [],
                "payment_installments": 0,
                "payment_type_count": 0,
                "first_purchase_ts": purchase_ts,
            },
        )

        cast_orders = record["orders"]
        cast_products = record["products"]
        cast_scores = record["review_scores"]
        assert isinstance(cast_orders, set)
        assert isinstance(cast_products, set)
        assert isinstance(cast_scores, list)

        order_id = item["order_id"]
        cast_orders.add(order_id)
        cast_products.add(item.get("product_id", ""))
        record["revenue"] = float(record["revenue"]) + parse_float(item.get("price"))
        record["freight"] = float(record["freight"]) + parse_float(item.get("freight_value"))
        record["first_purchase_ts"] = min(record["first_purchase_ts"], purchase_ts)  # type: ignore[arg-type]

        estimated_delivery = parse_datetime(order.get("order_estimated_delivery_date"))
        delivered = parse_datetime(order.get("order_delivered_customer_date"))
        if estimated_delivery and delivered and delivered > estimated_delivery:
            record["late_orders"] = int(record["late_orders"]) + 1

        if order_id in reviews:
            cast_scores.append(reviews[order_id])

        payment = payments.get(order_id)
        if payment:
            record["payment_installments"] = max(
                int(record["payment_installments"]),
                int(payment["max_installments"]),
            )
            record["payment_type_count"] = max(
                int(record["payment_type_count"]),
                int(payment["type_count"]),
            )

    rows: list[dict[str, object]] = []
    for (_, _), record in seller_months.items():
        seller_id = str(record["seller_id"])
        deal = closed[seller_id]
        mql = mqls.get(deal.get("mql_id", ""), {})
        seller = sellers.get(seller_id, {})

        orders_set = record["orders"]
        products_set = record["products"]
        review_scores = record["review_scores"]
        assert isinstance(orders_set, set)
        assert isinstance(products_set, set)
        assert isinstance(review_scores, list)

        rows.append(
            {
                "seller_id": seller_id,
                "month": str(record["month"]),
                "business_segment": deal.get("business_segment") or "unknown",
                "origin": mql.get("origin") or "unknown",
                "business_type": deal.get("business_type") or "unknown",
                "seller_state": seller.get("seller_state") or "unknown",
                "declared_monthly_revenue": parse_float(deal.get("declared_monthly_revenue")),
                "declared_catalog_size": parse_float(deal.get("declared_product_catalog_size")),
                "revenue": float(record["revenue"]),
                "freight": float(record["freight"]),
                "order_count": len(orders_set),
                "product_count": len(products_set),
                "late_order_count": int(record["late_orders"]),
                "avg_review_score": sum(review_scores) / len(review_scores) if review_scores else 5.0,
                "payment_installments": int(record["payment_installments"]),
                "payment_type_count": int(record["payment_type_count"]),
                "first_purchase_ts": record["first_purchase_ts"],
            }
        )

    print(
        f"closed_deals={len(closed)} mqls={len(mqls)} seller_months={len(rows)} skipped_items={skipped_items}",
        file=sys.stderr,
    )
    return rows


def build_tsv_rows(seller_months: list[dict[str, object]], items_per_case: int, max_cases: int, min_items_per_case: int) -> list[dict[str, object]]:
    revenues = sorted(float(row["revenue"]) for row in seller_months)
    order_counts = sorted(float(row["order_count"]) for row in seller_months)

    segment_month_revenues: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in seller_months:
        segment_month_revenues[(str(row["month"]), str(row["business_segment"]))].append(float(row["revenue"]))

    forecast_gap_raw_by_key: dict[tuple[str, str], float] = {}
    for row in seller_months:
        segment_values = sorted(segment_month_revenues[(str(row["month"]), str(row["business_segment"]))])
        segment_median = segment_values[len(segment_values) // 2] if segment_values else 1.0
        plan_value = float(row["declared_monthly_revenue"]) or segment_median or 1.0
        key = (str(row["seller_id"]), str(row["month"]))
        forecast_gap_raw_by_key[key] = abs(float(row["revenue"]) - plan_value) / max(plan_value, 1.0) * 100.0
    forecast_gap_values = sorted(forecast_gap_raw_by_key.values())

    candidates: list[dict[str, object]] = []
    for row in seller_months:
        case_id = f"{row['month']}_{normalize(str(row['business_segment'])) or 'unknown'}"
        forecast_gap_key = (str(row["seller_id"]), str(row["month"]))
        forecast_gap_pct = bucket(forecast_gap_raw_by_key[forecast_gap_key], forecast_gap_values, 10)

        review_risk = 1 if float(row["avg_review_score"]) < 4.0 else 0
        late_risk = 1 if int(row["late_order_count"]) > 0 else 0
        catalog_risk = 1 if float(row["declared_catalog_size"]) >= 100 else 0
        dependency = 1 + review_risk + late_risk + catalog_risk
        dependency += 1 if int(row["payment_installments"]) >= 6 else 0
        dependency += 1 if int(row["product_count"]) >= 4 else 0
        cross_team_dependency = max(1, min(5, dependency))

        revenue_impact = bucket(float(row["revenue"]), revenues, 5)
        order_impact = bucket(float(row["order_count"]), order_counts, 5)
        exec_visibility = int(revenue_impact >= 5 or order_impact >= 5 or row["business_type"] == "manufacturer")

        first_purchase_ts = row["first_purchase_ts"]
        assert isinstance(first_purchase_ts, dt.datetime)
        board_deadline_hours = month_end_hours(first_purchase_ts)

        deadline_component = 40 if board_deadline_hours <= 72 else 20 if board_deadline_hours <= 168 else 0
        silver_score = (
            revenue_impact * 25
            + forecast_gap_pct * 6
            + cross_team_dependency * 12
            + exec_visibility * 20
            + review_risk * 15
            + late_risk * 15
            + deadline_component
        )

        title = clean_text(
            f"{row['business_segment']} seller {str(row['seller_id'])[:8]} "
            f"{row['month']} revenue {float(row['revenue']):.2f} origin {row['origin']} state {row['seller_state']}"
        )

        candidates.append(
            {
                "case_id": case_id,
                "item_id": f"{row['seller_id']}_{row['month']}",
                "title": title,
                "forecast_gap_pct": forecast_gap_pct,
                "board_deadline_hours": board_deadline_hours,
                "cross_team_dependency": cross_team_dependency,
                "exec_visibility": exec_visibility,
                "revenue_impact": revenue_impact,
                "silver_score": silver_score,
                "revenue": float(row["revenue"]),
            }
        )

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in candidates:
        grouped[str(row["case_id"])].append(row)

    emitted: list[dict[str, object]] = []
    for case_id, rows in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        if len(rows) < min_items_per_case:
            continue
        ranked = sorted(
            rows,
            key=lambda row: (-float(row["silver_score"]), -float(row["revenue"]), str(row["item_id"])),
        )
        for rank, row in enumerate(ranked[:items_per_case], start=1):
            copy = dict(row)
            copy["expected_rank"] = rank
            emitted.append(copy)
        if len({row["case_id"] for row in emitted}) >= max_cases:
            break

    if not emitted:
        raise SystemExit("error: no rows emitted; relax min/max case settings")
    return emitted


def write_tsv(rows: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=TSV_HEADER,
            delimiter="\t",
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"wrote={output} rows={len(rows)} cases={len({row['case_id'] for row in rows})}", file=sys.stderr)


def main() -> None:
    args = parse_args()
    if args.items_per_case < 1 or args.max_cases < 1 or args.min_items_per_case < 1:
        raise SystemExit("error: item/case limits must be >= 1")

    seller_months = build_seller_months(Path(args.olist_dir))
    rows = build_tsv_rows(seller_months, args.items_per_case, args.max_cases, args.min_items_per_case)
    write_tsv(rows, Path(args.output))


if __name__ == "__main__":
    main()
