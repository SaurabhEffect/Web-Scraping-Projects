import json
import logging
import os
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)


REQUIRED_FIELDS = ["title", "price_gbp", "rating", "availability"]

def validate_record(record: dict) -> tuple[bool, str]:
    for field in REQUIRED_FIELDS:
        if field not in record or record[field] is None:
            return False, f"Missing required field: {field}"

    if not isinstance(record["title"], str) or len(record["title"].strip()) == 0:
        return False, "Empty title"

    if not isinstance(record["price_gbp"], (int, float)) or record["price_gbp"] < 0:
        return False, f"Invalid price: {record['price_gbp']}"

    if not isinstance(record["rating"], int) or record["rating"] not in range(0, 6):
        return False, f"Invalid rating: {record['rating']}"

    return True, ""


def clean_books(raw_data: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    logger.info(f"Starting cleaning pipeline with {len(raw_data)} raw records")

    df = pd.DataFrame(raw_data)

    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    valid_mask = []
    reasons = []
    for _, row in df.iterrows():
        ok, reason = validate_record(row.to_dict())
        valid_mask.append(ok)
        reasons.append(reason)

    df["_valid"]  = valid_mask
    df["_reason"] = reasons

    rejected_df = df[~df["_valid"]].copy()
    rejected_df = rejected_df.drop(columns=["_valid"])
    rejected_df.rename(columns={"_reason": "rejection_reason"}, inplace=True)

    clean_df = df[df["_valid"]].copy()
    clean_df.drop(columns=["_valid", "_reason"], inplace=True)
    logger.info(f"Validation: {len(clean_df)} valid | {len(rejected_df)} rejected")

    before = len(clean_df)
    clean_df.drop_duplicates(subset=["title", "price_gbp"], inplace=True)
    logger.info(f"Deduplication removed {before - len(clean_df)} rows")

    clean_df["availability"] = clean_df["availability"].apply(
        lambda v: "In stock" if "In stock" in str(v) else "Out of stock"
    )

    clean_df["price_gbp"] = pd.to_numeric(clean_df["price_gbp"], errors="coerce").round(2)
    clean_df["rating"]    = clean_df["rating"].astype(int)

    def price_tier(p: float) -> str:
        if p < 15:  return "Budget"
        if p < 35:  return "Mid-range"
        return "Premium"

    clean_df["price_tier"] = clean_df["price_gbp"].apply(price_tier)

    clean_df.sort_values(["rating", "price_gbp"], ascending=[False, True], inplace=True)
    clean_df.reset_index(drop=True, inplace=True)

    logger.info(f"Cleaning complete. Final clean records: {len(clean_df)}")
    return clean_df, rejected_df


def load_raw(raw_path: str) -> list[dict]:
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw data file not found: {raw_path}")

    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Loaded {len(data)} raw records from {raw_path}")
    return data
