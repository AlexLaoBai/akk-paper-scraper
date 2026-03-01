#!/usr/bin/env python3
"""
AKK Paper Scraper - Main Entry Point
Automated scraper for Akkermansia muciniphila research papers
"""

import argparse
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_downloader import PDFDownloader
from pdf_checker import PDFChecker


def scrape_papers(args):
    """Scrape and download AKK papers from various sources"""
    print("=" * 60)
    print("AKK Paper Scraper - Downloading Papers")
    print("=" * 60)

    downloader = PDFDownloader()

    # If CSV provided, use it
    if args.csv:
        papers = downloader.load_papers_from_csv(args.csv)
        print(f"Loaded {len(papers)} papers from CSV")
    else:
        # Default: scrape recent papers
        papers = downloader.scrape_pubmed_recent(keywords="Akkermansia muciniphila", max_results=args.max)
        print(f"Found {len(papers)} papers from PubMed")

    # Download PDFs
    if args.output:
        output_dir = args.output
    else:
        output_dir = "pdfs"

    os.makedirs(output_dir, exist_ok=True)

    success = downloader.download_all(papers, output_dir)
    print(f"\nDownload complete: {success} papers downloaded")

    return success


def check_pdfs(args):
    """Check PDF integrity"""
    print("=" * 60)
    print("AKK Paper Scraper - Checking PDFs")
    print("=" * 60)

    pdf_dir = args.directory if args.directory else "pdfs"
    checker = PDFChecker(pdf_dir)

    results = checker.check_all()

    print(f"\nTotal PDFs: {results['total']}")
    print(f"Valid PDFs: {results['valid']}")
    print(f"Invalid PDFs: {results['invalid']}")

    if results['invalid'] > 0:
        print("\nInvalid files:")
        for file_info in results['files']:
            if not file_info['valid']:
                print(f"  - {file_info['name']}")
                print(f"    Error: {file_info['error']}")

    return results['invalid'] == 0


def verify_pdfs(args):
    """Verify PDFs: deduplication and content validation"""
    print("=" * 60)
    print("AKK Paper Scraper - Verifying PDFs")
    print("=" * 60)

    pdf_dir = args.directory if args.directory else "pdfs"
    checker = PDFChecker(pdf_dir)

    # Run verification
    results = checker.verify_and_deduplicate()

    print(f"\nTotal PDFs: {results['total']}")
    print(f"Unique PDFs: {results['unique']}")
    print(f"Duplicates removed: {results['duplicates']}")

    if results['invalid'] > 0:
        print(f"\nInvalid PDFs: {results['invalid']}")
        for file_info in results['files']:
            if not file_info['valid']:
                print(f"  - {file_info['name']}: {file_info['error']}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="AKK Paper Scraper - Automated paper downloader for Akkermansia muciniphila research"
    )

    # Add mutually exclusive group for actions
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        '--scrape', '-s',
        action='store_true',
        help='Scrape and download papers'
    )
    action_group.add_argument(
        '--check', '-c',
        action='store_true',
        help='Check PDF integrity'
    )
    action_group.add_argument(
        '--verify', '-v',
        action='store_true',
        help='Verify and deduplicate PDFs'
    )
    action_group.add_argument(
        '--all', '-a',
        action='store_true',
        help='Run all operations (scrape, check, verify)'
    )

    # Options
    parser.add_argument(
        '--max', '-m',
        type=int,
        default=20,
        help='Maximum papers to download (default: 20)'
    )
    parser.add_argument(
        '--csv', '-f',
        type=str,
        help='CSV file with paper data'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output directory for PDFs'
    )
    parser.add_argument(
        '--directory', '-d',
        type=str,
        help='PDF directory for check/verify operations'
    )

    args = parser.parse_args()

    # Run requested operations
    if args.all:
        scrape_papers(args)
        check_pdfs(args)
        verify_pdfs(args)
    elif args.scrape:
        scrape_papers(args)
    elif args.check:
        check_pdfs(args)
    elif args.verify:
        verify_pdfs(args)


if __name__ == "__main__":
    main()
