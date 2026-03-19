# Books Scraping Pipeline

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Data](https://img.shields.io/badge/Data-ETL-orange)

A modular, production-style end-to-end data pipeline that scrapes all books from [books.toscrape.com](https://books.toscrape.com), cleans the raw data, validates every record, removes duplicates, enriches with derived fields, and exports a clean production-ready dataset.

---

## Overview

Real-world web scraping isn't just about fetching HTML markup. It requires a robust pipeline architecture containing raw data checkpoints, strict validation, deduplication, type enforcement, and well-structured exports. This repository delivers an end-to-end Extract, Transform, Load (ETL) pipeline mimicking professional environment architectures.

---

## Technologies Used

| Tool | Purpose |
|---|---|
| `requests` & `BeautifulSoup` | Multi-page scraping, rate limiting, and HTML parsing |
| `pandas` | Data cleaning, validation, deduplication, and type-casting |
| `json` | Raw checkpoint persistence |
| `logging` | Systematic stage-by-stage structured logs |
| `argparse` | CLI flags for configurable pipeline executions |

---

## Folder Structure

```
.
├── pipeline/
│   ├── __init__.py
│   ├── scraper.py       # Stage 1: Extractor with pagination & checkpointing
│   ├── cleaner.py       # Stage 2: Transformer for validation & deduplication
│   └── exporter.py      # Stage 3: Loader for CSV/JSON exports & reporting
├── data/
│   ├── raw/
│   │   └── books_raw.json          
│   └── clean/
│       ├── books_clean_*.csv       
│       ├── books_clean_*.json
│       └── books_rejected_*.csv    
├── run_pipeline.py      # Main CLI entry point
├── requirements.txt     # Python dependencies
└── README.md
```

---

## Getting Started

### Prerequisites

Ensure you have Python 3.10+ installed on your local machine.

### Installation

1. Clone the repository and navigate into the project directory:
   ```bash
   git clone https://github.com/yourusername/book-scraping-pipeline.git
   cd book-scraping-pipeline
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Execution

Execute the full pipeline across all 50 pages (~1000 books):
```bash
python run_pipeline.py
```

Quick test run (e.g., first 5 pages only):
```bash
python run_pipeline.py --max-pages 5
```

Skip the scraping phase and re-clean an existing raw checkpoint:
```bash
python run_pipeline.py --skip-scrape
```

---

## Pipeline Architecture

The pipeline follows a strict separation of concerns over three stages:

1. **Stage 1 (Scraper):** Crawls the target catalogue asynchronously with exponential backoff and error retries. Checkpoints the results to a raw JSON file.
2. **Stage 2 (Cleaner):** Validates all required fields, removes exact duplicate hits, enforces appropriate native data types, and computes derived fields like `price_tier`.
3. **Stage 3 (Exporter):** Splits the valid from invalid records and generates the final structured dataset into multiple formats for downstream analytics.

---

## Output Example

```
==========================================================
  SCRAPING PIPELINE - RUN REPORT
==========================================================
  Raw records scraped    :  1,000
  Clean records exported :    998
  Rejected records       :      2
  Dedup rate             :    0.2%

  Availability
    In stock             :    872
    Out of stock         :    126

  Pricing
    Average price (£)    :    35.07
    Budget  (<£15)       :    348
    Mid-range (£15-£35)  :    315
    Premium (>£35)       :    335

  Average rating         :     2.99 / 5

  Output files
    CSV    -> data/clean/books_clean_20240601_143022.csv
    JSON   -> data/clean/books_clean_20240601_143022.json
==========================================================
```

---
