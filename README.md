# AKK Paper Scraper

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Automated scraper for downloading and managing **Akkermansia muciniphila** research papers from academic databases.

## Features

- **Multi-source PDF Download**: Supports PubMed/PMC, Frontiers, Springer, Nature, BMC, Elsevier, Wiley
- **PDF Integrity Check**: Validates PDF structure, detects corrupted files, identifies scanned documents
- **PDF Deduplication**: MD5 hash-based deduplication with automatic duplicate removal
- **Batch Processing**: CSV-based batch download with configurable parameters

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Scrape and download papers
python3 akk_scraper.py --scrape

# Check PDF integrity
python3 akk_scraper.py --check

# Verify and deduplicate
python3 akk_scraper.py --verify

# Run all operations
python3 akk_scraper.py --all

# Download 50 papers
python3 akk_scraper.py --scrape --max 50

# Use CSV file for batch download
python3 akk_scraper.py --scrape --csv papers.csv --output my_pdfs

# Check PDFs in custom directory
python3 akk_scraper.py --check --directory /path/to/pdfs
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--scrape` | `-s` | Scrape and download papers |
| `--check` | `-c` | Check PDF integrity |
| `--verify` | `-v` | Verify and deduplicate PDFs |
| `--all` | `-a` | Run all operations |
| `--max` | `-m` | Maximum papers to download (default: 20) |
| `--csv` | `-f` | CSV file with paper data |
| `--output` | `-o` | Output directory for PDFs |
| `--directory` | `-d` | PDF directory for check/verify |

## CSV Format

Create a CSV file with the following columns:

```csv
title,doi,pmid,pmc,url,journal,year
"Paper Title",10.1234/example,12345678,PMC1234567,https://...,"Nature",2024
```

## Module Usage

### PDF Downloader

```python
from pdf_downloader import PDFDownloader

downloader = PDFDownloader()

# Download from DOI
success, path = downloader.download_from_doi('10.1234/example', 'pdfs/')

# Download from URL
success, path = downloader.download_pdf('https://example.com/paper.pdf', 'pdfs/')
```

### PDF Checker

```python
from pdf_checker import PDFChecker

checker = PDFChecker('pdfs/')

# Check all PDFs
results = checker.check_all()
print(f"Valid: {results['valid']}, Invalid: {results['invalid']}")

# Verify and deduplicate
results = checker.verify_and_deduplicate()
print(f"Unique: {results['unique']}, Duplicates: {results['duplicates']}")
```

## Project Structure

```
akk-paper-scraper/
├── akk_scraper.py       # Main entry point
├── scraper.py           # PubMed/arXiv scraper
├── pdf_downloader.py    # PDF downloader with multi-source support
├── pdf_checker.py       # PDF integrity checker
├── pdf_dedup.py         # PDF deduplication utility
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── LICENSE              # MIT License
```

## Requirements

- Python 3.7+
- requests
- pypdf (optional, for advanced PDF validation)

## License

MIT License - see LICENSE file for details

## Disclaimer

This tool is for academic research purposes. Please respect copyright and terms of service of academic databases and publishers.
