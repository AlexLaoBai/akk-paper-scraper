# AKK Paper Scraper Skill

A skill for scraping academic papers from arXiv and other preprint servers, with support for downloading PDFs, checking validity, and deduplication.

## Usage

Trigger phrases: "download papers", "scrape papers", "fetch academic papers", "download arxiv papers", "抓取论文"

This skill provides tools for:
- Searching and scraping papers from arXiv, arXiv mirror, and other academic sources
- Downloading PDFs with progress tracking
- Checking PDF validity and completeness
- Deduplicating downloaded papers

## Commands

### akk_scraper.py
Main entry point for the scraper. Usage:
```bash
python akk_scraper.py --keyword "machine learning" --max-results 10 --output-dir ./papers
```

### scraper.py
Core scraping functionality for arXiv.

### pdf_downloader.py
Downloads PDFs with retry logic and progress tracking.

### pdf_checker.py
Validates PDF files for completeness and readability.

### pdf_dedup.py
Detects and removes duplicate PDF files based on content hash.

## Requirements

See requirements.txt for dependencies.
