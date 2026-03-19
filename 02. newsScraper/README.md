# Hacker News Scraper

A multi-page news scraper that extracts **tech headlines, scores, authors, and comment counts** from [Hacker News](https://news.ycombinator.com). Ideal for trend analysis, dataset building, or monitoring tech topics over time.

---

## Problem It Solves

Tech professionals and researchers need structured snapshots of what the developer community is discussing. This lightweight scraper produces daily CSV/JSON datasets from HN's front page with zero API rate limits, keeping the core script extremely minimal and focused strictly on reliable execution.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| `requests` | HTTP with retry logic |
| `BeautifulSoup` | HTML parsing of HN rows |
| `pandas` | Data cleaning, type casting, sorted export |
| `logging` | Structured log files + console output |

---

## Folder Structure

```
project2-news-scraper/
├── scraper/
│   └── news_scraper.py     # Core scraper script (minified, comment-free)
├── data/
│   ├── hn_news_YYYY-MM-DD.csv
│   └── hn_news_YYYY-MM-DD.json
├── logs/
│   └── news_scraper.log
├── requirements.txt
└── README.md
```

---

## Setup & Run

```bash
# 1. Clone / enter the project
cd "02. newsScraper"

# 2. Create and activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate
# (For Mac/Linux use: source venv/bin/activate)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the scraper
python scraper/news_scraper.py
```

---

## Example Output

| rank | title | domain | score | author | comment_count |
|---|---|---|---|---|---|
| 4 | Show HN: I built a Rust-based terminal RSS reader | github.com | 487 | thrxwaway | 143 |
| 12 | The quiet death of open-source funding | lwn.net | 321 | pgpg | 89 |
| 7 | Ask HN: What's your stack in 2025? | news.ycombinator.com | 210 | throwaway99 | 256 |

---

## Configuration

The script scrapes `max_pages=3` internally within the `__main__` block. To scrape more pages, update `max_pages` inside `scrape_hn_news()`.

---

## Future Improvements

- Add asynchronous fetching to speed up multi-page scraping
- Filter stories by minimum score threshold
