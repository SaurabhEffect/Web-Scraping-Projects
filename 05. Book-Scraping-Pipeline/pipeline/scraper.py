import requests
from bs4 import BeautifulSoup
import json
import logging
import time
import os
from typing import Optional

logger = logging.getLogger(__name__)

BASE_URL    = "https://books.toscrape.com"
CATALOGUE   = BASE_URL + "/catalogue"
HEADERS     = {"User-Agent": "Mozilla/5.0 (compatible; BooksPipeline/1.0)"}
MAX_RETRIES = 3
RETRY_DELAY = 2
CRAWL_DELAY = 0.8

RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}


def fetch_page(url: str) -> Optional[BeautifulSoup]:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            r.raise_for_status()
            return BeautifulSoup(r.content, "html.parser")

        except requests.exceptions.RequestException as exc:
            logger.warning(f"Attempt {attempt}/{MAX_RETRIES} – {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)

    logger.error(f"Failed to fetch: {url}")
    return None


def parse_books(soup: BeautifulSoup) -> list[dict]:
    books = []
    for article in soup.select("article.product_pod"):
        title_tag = article.select_one("h3 > a")
        title = title_tag["title"] if title_tag else "Unknown"

        price_tag = article.select_one("p.price_color")
        price_str = price_tag.get_text(strip=True).replace("£", "").replace("Â", "").strip() if price_tag else "0"
        try:
            price = float(price_str)
        except ValueError:
            price = 0.0

        avail_tag = article.select_one("p.availability")
        availability = avail_tag.get_text(strip=True) if avail_tag else "Unknown"

        rating_tag = article.select_one("p.star-rating")
        rating_word = rating_tag["class"][1] if rating_tag and len(rating_tag["class"]) > 1 else "Zero"
        rating = RATING_MAP.get(rating_word, 0)

        link = title_tag["href"].replace("../", "") if title_tag else ""
        detail_url = f"{CATALOGUE}/{link}" if link else ""

        books.append({
            "title":        title,
            "price_gbp":    price,
            "rating":       rating,
            "availability": availability,
            "detail_url":   detail_url,
        })

    return books


def get_next_url(soup: BeautifulSoup, current_page_url: str) -> Optional[str]:
    next_btn = soup.select_one("li.next > a")
    if not next_btn:
        return None

    if "catalogue" in current_page_url:
        base = current_page_url.rsplit("/", 1)[0]
        return f"{base}/{next_btn['href']}"
    else:
        return f"{CATALOGUE}/{next_btn['href']}"


def scrape_books(max_pages: Optional[int] = None, raw_dir: str = "data/raw") -> list[dict]:
    os.makedirs(raw_dir, exist_ok=True)
    all_books: list[dict] = []
    current_url = f"{CATALOGUE}/page-1.html"
    page_num = 0

    while current_url:
        if max_pages and page_num >= max_pages:
            break

        page_num += 1
        logger.info(f"Scraping page {page_num}: {current_url}")
        soup = fetch_page(current_url)

        if soup is None:
            logger.error(f"Aborting at page {page_num}")
            break

        page_books = parse_books(soup)
        logger.info(f"  Extracted {len(page_books)} books")
        all_books.extend(page_books)

        current_url = get_next_url(soup, current_url)
        time.sleep(CRAWL_DELAY)

    raw_path = os.path.join(raw_dir, "books_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_books, f, indent=2)
    logger.info(f"Raw checkpoint saved: {raw_path}  ({len(all_books)} records)")

    return all_books
