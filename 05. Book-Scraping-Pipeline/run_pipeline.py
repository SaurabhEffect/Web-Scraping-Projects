import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pipeline.scraper  import scrape_books
from pipeline.cleaner  import load_raw, clean_books
from pipeline.exporter import export_clean, export_rejected, print_pipeline_report

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

RAW_CHECKPOINT = "data/raw/books_raw.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Books.toscrape.com — Full Scraping Pipeline"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limit pages scraped (default: all 50 pages).",
    )
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Skip scraping and re-run clean/export on existing raw checkpoint.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logger.info("=" * 55)
    logger.info("  PIPELINE START")
    logger.info("=" * 55)

    if args.skip_scrape:
        logger.info("Stage 1: SCRAPE - SKIPPED (--skip-scrape flag set)")
        raw_data = load_raw(RAW_CHECKPOINT)
    else:
        logger.info("Stage 1: SCRAPE - Starting")
        raw_data = scrape_books(
            max_pages=args.max_pages,
            raw_dir="data/raw",
        )
        if not raw_data:
            logger.error("Scraping returned no data. Aborting pipeline.")
            sys.exit(1)
        logger.info(f"Stage 1: SCRAPE - Complete ({len(raw_data)} raw records)")

    logger.info("Stage 2: CLEAN - Starting")
    clean_df, rejected_df = clean_books(raw_data)
    logger.info(
        f"Stage 2: CLEAN - Complete "
        f"({len(clean_df)} clean | {len(rejected_df)} rejected)"
    )

    logger.info("Stage 3: EXPORT - Starting")
    output_paths = export_clean(clean_df, out_dir="data/clean")
    export_rejected(rejected_df,         out_dir="data/clean")
    logger.info("Stage 3: EXPORT - Complete")

    print_pipeline_report(
        raw_count=len(raw_data),
        clean_df=clean_df,
        rejected_df=rejected_df,
        output_paths=output_paths,
    )

    logger.info("Pipeline finished successfully.")


if __name__ == "__main__":
    main()
