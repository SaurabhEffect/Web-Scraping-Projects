import logging
import os
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def export_clean(df: pd.DataFrame, out_dir: str = "data/clean") -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)

    csv_path  = os.path.join(out_dir, f"books_clean_{RUN_TIMESTAMP}.csv")
    json_path = os.path.join(out_dir, f"books_clean_{RUN_TIMESTAMP}.json")

    df.to_csv(csv_path, index=False, encoding="utf-8")
    df.to_json(json_path, orient="records", indent=2)

    logger.info(f"Clean CSV  -> {csv_path}")
    logger.info(f"Clean JSON -> {json_path}")

    return {"csv": csv_path, "json": json_path}


def export_rejected(rejected_df: pd.DataFrame, out_dir: str = "data/clean") -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"books_rejected_{RUN_TIMESTAMP}.csv")

    if not rejected_df.empty:
        rejected_df.to_csv(path, index=False, encoding="utf-8")
        logger.info(f"Rejected records -> {path}  ({len(rejected_df)} rows)")
    else:
        logger.info("No rejected records - skipping rejected export.")

    return path


def print_pipeline_report(
    raw_count: int,
    clean_df: pd.DataFrame,
    rejected_df: pd.DataFrame,
    output_paths: dict[str, str],
) -> None:
    total_clean    = len(clean_df)
    total_rejected = len(rejected_df)
    in_stock       = (clean_df["availability"] == "In stock").sum()
    out_of_stock   = total_clean - in_stock

    avg_price   = clean_df["price_gbp"].mean()
    avg_rating  = clean_df["rating"].mean()

    tier_counts = clean_df["price_tier"].value_counts().to_dict()

    print("\n" + "=" * 58)
    print("  SCRAPING PIPELINE - RUN REPORT")
    print("=" * 58)
    print(f"  Raw records scraped    : {raw_count:>6,}")
    print(f"  Clean records exported : {total_clean:>6,}")
    print(f"  Rejected records       : {total_rejected:>6,}")
    print(f"  Dedup rate             : {((raw_count - total_clean) / max(raw_count,1) * 100):.1f}%")
    print()
    print(f"  Availability")
    print(f"    In stock             : {in_stock:>6,}")
    print(f"    Out of stock         : {out_of_stock:>6,}")
    print()
    print(f"  Pricing")
    print(f"    Average price (£)    : {avg_price:>8.2f}")
    print(f"    Budget  (<£15)       : {tier_counts.get('Budget', 0):>6,}")
    print(f"    Mid-range (£15–£35)  : {tier_counts.get('Mid-range', 0):>6,}")
    print(f"    Premium (>£35)       : {tier_counts.get('Premium', 0):>6,}")
    print()
    print(f"  Average rating         : {avg_rating:>8.2f} / 5")
    print()
    print(f"  Output files")
    for fmt, path in output_paths.items():
        print(f"    {fmt.upper():<6} -> {path}")
    print("=" * 58 + "\n")
