"""
Quotes Scrapper
-----------------
Scrapes quotes, authors and tags from https://quotes.toscrape.com
Handles pagination, retries and exports to CSV and JSON.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging
import time
import os
from typing import Optional

# Logging setup
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler("logs/scraper.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL   = "https://quotes.toscrape.com"
HEADERS    = {"User-Agent": "Mozilla/5.0 (compatible; QuotesScraper/1.0)"}
MAX_RETRIES = 3
RETRY_DELAY = 2
REQUEST_DELAY = 1

# Core helpers
def fetch_page(url: str, retries: int = MAX_RETRIES) -> Optional[BeautifulSoup]:
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            logger.info(f"Fetched: {url} [HTTP {response.status_code}]")
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error on attempt {attempt}/{retries}: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error on attempt {attempt}/{retries}: {e}")
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt}/{retries} for {url}")
        if attempt < retries:
            logger.info(f"Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
    logger.error(f"Failed to fetch {url} after {retries} attempts.")
    return None

def parse_quotes(soup: BeautifulSoup) -> list[dict]:
    quotes = []
    quote_blocks = soup.select("div.quote")

    for block in quote_blocks:
        text_tag   = block.select_one("span.text")
        author_tag = block.select_one("small.author")
        author_link = block.select_one("span a")
        tag_tags   = block.select("a.tag")

        if not text_tag or not author_tag:
            continue

        quotes.append({
            "quote":      text_tag.get_text(strip=True).strip("\u201c\u201d"),
            "author":     author_tag.get_text(strip=True),
            "author_url": BASE_URL + author_link["href"] if author_link else "",
            "tags":       ", ".join(t.get_text(strip=True) for t in tag_tags),
        })
    return quotes

def get_next_page(soup: BeautifulSoup) -> Optional[str]:
    next_btn = soup.select_one("li.next a")
    if next_btn:
        return BASE_URL + next_btn["href"]
    return None

def scrape_all_quotes(max_pages: Optional[int] = None) -> list[dict]:
    all_quotes = []
    current_url = BASE_URL
    page_num = 0

    while current_url:
        page_num += 1
        if max_pages and page_num > max_pages:
            logger.info(f"Reached max_pages limit ({max_pages}). Stopping.")
            break
        logger.info(f"── Scraping page {page_num}: {current_url}")
        soup = fetch_page(current_url)
        if soup is None:
            logger.error("Skipping page due to fetch failure.")
            break
        page_quotes = parse_quotes(soup)
        logger.info(f"   Found {len(page_quotes)} quotes on page {page_num}")
        all_quotes.extend(page_quotes)
        current_url = get_next_page(soup)
        time.sleep(REQUEST_DELAY)
    logger.info(f"Scraping complete. Total quotes collected: {len(all_quotes)}")
    return all_quotes

# Export helpers
def save_to_csv(data: list[dict], filepath: str) -> None:
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding="utf-8")
    logger.info(f"Saved {len(df)} records → {filepath}")

def save_to_json(data: list[dict], filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(data)} records → {filepath}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    logger.info("=== Quotes Scraper Starting ===")
    quotes = scrape_all_quotes()

    if quotes:
        save_to_csv(quotes,  "data/quotes.csv")
        save_to_json(quotes, "data/quotes.json")
        print(f"\nDone! Scraped {len(quotes)} quotes.")
        print("   Output: data/quotes.csv  |  data/quotes.json")
    else:
        logger.warning("No data collected. Check logs for details.")
