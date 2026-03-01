#!/usr/bin/env python3
"""
AKK Paper Scraper - Main entry point
Downloads academic papers from arXiv based on keywords
"""

import argparse
import os
import sys
from scraper import ArxivScraper
from pdf_downloader import PDFDownloader
from pdf_checker import PDFChecker


def main():
    parser = argparse.ArgumentParser(description='AKK Paper Scraper')
    parser.add_argument('--keyword', '-k', type=str, required=True,
                        help='Search keyword for papers')
    parser.add_argument('--max-results', '-n', type=int, default=10,
                        help='Maximum number of papers to download')
    parser.add_argument('--output-dir', '-o', type=str, default='./papers',
                        help='Output directory for papers')
    parser.add_argument('--check-only', action='store_true',
                        help='Only check existing PDFs, do not download')

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    if args.check_only:
        print(f"Checking PDFs in {args.output_dir}...")
        checker = PDFChecker(args.output_dir)
        checker.check_all()
        return

    # Scrape paper metadata
    print(f"Searching for papers matching: {args.keyword}")
    scraper = ArxivScraper()

    papers = scraper.search(args.keyword, max_results=args.max_results)
    print(f"Found {len(papers)} papers")

    if not papers:
        print("No papers found.")
        return

    # Download PDFs
    print(f"Downloading to {args.output_dir}...")
    downloader = PDFDownloader(args.output_dir)

    for paper in papers:
        success = downloader.download(paper)
        status = "✓" if success else "✗"
        print(f"{status} {paper['title'][:50]}...")

    print("\nDownload complete!")


if __name__ == '__main__':
    main()
