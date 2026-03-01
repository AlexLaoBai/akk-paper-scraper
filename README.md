# AKK Paper Scraper

Academic paper scraping tool for arXiv and preprint servers.

## Features

- Search and scrape papers from arXiv
- Download PDFs with retry logic
- Check PDF validity
- Deduplicate downloads

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Search and download papers
python akk_scraper.py --keyword "machine learning" --max-results 10

# Check downloaded PDFs
python pdf_checker.py ./papers

# Remove duplicates
python pdf_dedup.py ./papers
```

## License

MIT License
