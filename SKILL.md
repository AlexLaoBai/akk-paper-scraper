# AKK Paper Scraper Skill

<<<<<<< HEAD
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
=======
**Skill ID**: akk-paper-scraper

**Description**: Automated scraper for downloading and managing Akkermansia muciniphila research papers from academic databases.

**Category**: Scientific Research / Literature Mining

## Trigger Phrases

- "抓取AKK论文" / "scrape AKK papers"
- "下载Akkermansia论文" / "download Akkermansia papers"
- "AKK文献下载" / "AKK paper download"
- "学术论文批量下载" / "batch paper download"

## Features

1. **Multi-source PDF Download**
   - PubMed/PMC (Open Access)
   - Frontiers
   - Springer
   - Nature
   - BMC
   - Elsevier
   - Wiley

2. **PDF Integrity Check**
   - Validates PDF structure
   - Detects corrupted files
   - Identifies scanned documents

3. **PDF Verification & Deduplication**
   - MD5 hash-based deduplication
   - Automatic duplicate removal
   - Content validation

4. **Batch Processing**
   - CSV-based batch download
   - Configurable max results

## Usage

### Basic Commands

```bash
# Scrape and download papers
python3 akk_scraper.py --scrape

# Check PDF integrity
python3 akk_scraper.py --check

# Verify and deduplicate
python3 akk_scraper.py --verify

# Run all operations
python3 akk_scraper.py --all
```

### Options

- `--scrape, -s`: Scrape and download papers
- `--check, -c`: Check PDF integrity
- `--verify, -v`: Verify and deduplicate PDFs
- `--all, -a`: Run all operations
- `--max, -m`: Maximum papers to download (default: 20)
- `--csv, -f`: CSV file with paper data
- `--output, -o`: Output directory for PDFs
- `--directory, -d`: PDF directory for check/verify

### Examples

```bash
# Download 50 papers
python3 akk_scraper.py --scrape --max 50

# Check PDFs in custom directory
python3 akk_scraper.py --check --directory /path/to/pdfs

# Use CSV file for batch download
python3 akk_scraper.py --scrape --csv papers.csv --output my_pdfs
```

## CSV Format

CSV file should contain the following columns:

```csv
title,doi,pmid,pmc,url,journal,year
"Paper Title",10.1234/example,12345678,PMC1234567,https://...,"Nature",2024
```

## Dependencies

- Python 3.7+
- requests
- pypdf (optional, for advanced validation)

## Notes

- For PubMed API access, consider installing Biopython
- Some papers may require institutional access
- Respect copyright and terms of service
>>>>>>> 96c9d6291e883ad518ddb326d32528ccd798a49f
