# Quotes Scraper

A clean, production-style static web scraper that extracts **quotes, authors, and tags** from [quotes.toscrape.com](https://quotes.toscrape.com) — handling pagination, retries, logging, and dual-format export.

---

## Problem It Solves

Manually collecting quotes for NLP datasets, sentiment analysis, or content apps is tedious. This scraper automates the full extraction across all paginated pages and delivers a clean, structured dataset in both CSV and JSON.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| `requests` | HTTP requests with retry logic |
| `BeautifulSoup` | HTML parsing |
| `pandas` | DataFrame + CSV export |
| `logging` | File + console structured logs |

---

## Folder Structure

```
project1-quotes-scraper/
├── scraper/
│   └── scraper.py       # Main scraping logic
├── data/
│   ├── quotes.csv       # Output dataset
│   └── quotes.json      # Output dataset (JSON)
├── logs/
│   └── scraper.log      # Runtime logs
├── requirements.txt
└── README.md
```

---

## Setup & Run

```bash
# 1. Clone / enter the project
cd "01. quotesScrapper"

# 2. Create and activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate
# (For Mac/Linux use: source venv/bin/activate)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the scraper
python scraper/scraper.py
```

---

## Example Output (`quotes.csv`)

| quote | author | author_url | tags |
|---|---|---|---|
| The world as we have created it... | Albert Einstein | /author/Albert-Einstein | change, deep-thoughts |
| It is our choices, Harry... | J.K. Rowling | /author/J-K-Rowling | abilities, choices |
| There are only two ways to live... | Albert Einstein | /author/Albert-Einstein | inspirational, life |

---

## Configuration

Inside `scraper.py`, adjust these constants:

```python
MAX_RETRIES   = 3    # retry failed requests
RETRY_DELAY   = 2    # seconds between retries
REQUEST_DELAY = 1    # polite crawl delay between pages
```

Pass `max_pages=5` to `scrape_all_quotes()` to limit pages during testing.

---

## Future Improvements

- Add proxy rotation for large-scale runs
- Scrape individual author bio pages for richer data
