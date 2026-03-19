import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import pandas as pd
import requests
from bs4 import BeautifulSoup

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler("logs/news_scraper.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

BASE_URL = "https://news.ycombinator.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

MAX_RETRIES = 3
RETRY_DELAY = 3
REQUEST_DELAY = 1.5
SCRAPE_DATE = datetime.now().strftime("%Y-%m-%d")

def fetch_page(url: str) -> Optional[BeautifulSoup]:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=12)
            response.raise_for_status()
            logger.info(f"OK [{response.status_code}] {url}")
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as exc:
            logger.warning(f"Attempt {attempt}/{MAX_RETRIES} failed: {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    logger.error(f"Permanently failed to fetch: {url}")
    return None

def parse_stories(soup: BeautifulSoup) -> List[Dict[str, str]]:
    stories = []
    story_rows = soup.select("tr.athing")
    subtext_rows = soup.select("td.subtext")
    for story_row, sub_row in zip(story_rows, subtext_rows):
        rank_tag = story_row.select_one("span.rank")
        rank = rank_tag.get_text(strip=True).rstrip(".") if rank_tag else ""
        title_tag = story_row.select_one("span.titleline > a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        raw_url = title_tag.get("href", "")
        url = raw_url if raw_url.startswith("http") else f"{BASE_URL}/{raw_url}"
        domain_tag = story_row.select_one("span.sitestr")
        domain = domain_tag.get_text(strip=True) if domain_tag else "news.ycombinator.com"
        score_tag = sub_row.select_one("span.score")
        score = score_tag.get_text(strip=True).replace(" points", "").replace(" point", "") if score_tag else "0"
        author_tag = sub_row.select_one("a.hnuser")
        author = author_tag.get_text(strip=True) if author_tag else "unknown"
        comment_links = sub_row.select("a")
        comment_count = "0"
        for link in reversed(comment_links):
            text = link.get_text(strip=True)
            if "comment" in text:
                comment_count = text.replace("\u00a0comments", "").replace("\u00a0comment", "").strip()
                break
        stories.append({
            "rank": rank,
            "title": title,
            "url": url,
            "domain": domain,
            "score": score,
            "author": author,
            "comment_count": comment_count,
            "scraped_at": SCRAPE_DATE,
        })
    return stories

def get_next_page_url(soup: BeautifulSoup) -> Optional[str]:
    more_link = soup.select_one("a.morelink")
    if more_link:
        return f"{BASE_URL}/{more_link['href']}"
    return None

def scrape_hn_news(max_pages: int = 3) -> List[Dict[str, str]]:
    all_stories: List[Dict[str, str]] = []
    seen_urls: Set[str] = set()
    current_url: Optional[str] = BASE_URL
    page_num = 0
    while current_url and page_num < max_pages:
        page_num += 1
        logger.info(f"── Page {page_num}/{max_pages}: {current_url}")
        soup = fetch_page(current_url)
        if not soup:
            logger.error("Stopping: page fetch failed.")
            break
        stories = parse_stories(soup)
        logger.info(f"   Parsed {len(stories)} stories on this page.")
        for story in stories:
            if story["url"] not in seen_urls:
                seen_urls.add(story["url"])
                all_stories.append(story)
        current_url = get_next_page_url(soup)
        time.sleep(REQUEST_DELAY)
    logger.info(f"Total unique stories collected: {len(all_stories)}")
    return all_stories
    
def clean_and_export(stories: List[Dict[str, str]], out_dir: str = "data") -> pd.DataFrame:
    os.makedirs(out_dir, exist_ok=True)
    df = pd.DataFrame(stories)
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)
    df["comment_count"] = pd.to_numeric(df["comment_count"], errors="coerce").fillna(0).astype(int)
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce").fillna(0).astype(int)
    df.sort_values("score", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    csv_path = os.path.join(out_dir, f"hn_news_{SCRAPE_DATE}.csv")
    json_path = os.path.join(out_dir, f"hn_news_{SCRAPE_DATE}.json")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    df.to_json(json_path, orient="records", indent=2)
    logger.info(f"Exported CSV  -> {csv_path}")
    logger.info(f"Exported JSON -> {json_path}")
    return df

if __name__ == "__main__":
    logger.info("=== Hacker News Scraper Starting ===")
    extracted_stories = scrape_hn_news(max_pages=3)
    if extracted_stories:
        final_df = clean_and_export(extracted_stories)
        print(f"\n[Success] Done! Collected {len(final_df)} stories.")
        print(f"\nTop 5 by score:\n{final_df[['rank', 'title', 'score', 'author']].head(5).to_string(index=False)}")
    else:
        logger.warning("No stories collected. Please check logs/news_scraper.log for details.")
