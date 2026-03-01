#!/usr/bin/env python3
"""
PDF Downloader - Advanced PDF downloader for academic papers
Supports multiple sources: PubMed, PMC, Frontiers, Springer, Nature, BMC, etc.
"""

import os
import re
import csv
import time
import hashlib
import requests
from urllib.parse import urljoin, urlparse
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFDownloader:
    """Advanced PDF downloader with multi-source support"""

    # Known PDF URL patterns for different publishers
    PDF_PATTERNS = {
        'pubmed': [
            r'https://pubmed\.ncbi\.nlm\.nih\.gov/\d+/',
            r'https://www\.ncbi\.nlm\..nih\.gov/pmc/articles/PMC\d+/',
        ],
        'frontiers': [
            r'https://www\.frontiersin\.org/articles/\d+/\d+/full',
            r'https://www\.frontiersin\.org/articles/.*/pdf',
        ],
        'springer': [
            r'https://link\.springer\.com/article/\d+',
            r'https://link\.springer\.com/content/pdf/.*\.pdf',
        ],
        'nature': [
            r'https://www\.nature\.com/articles/',
            r'https://www\.nature\.com/articles/.*\.pdf',
        ],
        'bmc': [
            r'https://bmcmicrobiol\.biomedcentral\.com/articles/',
            r'https://bmcmicrobiol\.biomedcentral\.com/.*/.*\.pdf',
        ],
        'elsevier': [
            r'https://www\.sciencedirect\.com/science/article/',
        ],
        'wiley': [
            r'https://onlinelibrary\.wiley\.com/doi/',
            r'https://onlinelibrary\.wiley\.com/doi/pdfdirect/',
        ],
        'pmc': [
            r'https://www\.ncbi\.nlm\.nih\.gov/pmc/articles/PMC\d+/pdf/',
        ],
    }

    # PDF download endpoints
    PDF_ENDPOINTS = {
        'frontiers': '/articles/{article_id}/pdf',
        'springer': '/content/pdf/{article_id}.pdf',
        'nature': '/articles/{article_id}/.pdf',
        'bmc': '/{article_id}/.pdf',
    }

    def __init__(self, timeout=30, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def load_papers_from_csv(self, csv_path):
        """Load paper data from CSV file"""
        papers = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                papers.append({
                    'title': row.get('title', ''),
                    'doi': row.get('doi', ''),
                    'pmid': row.get('pmid', ''),
                    'pmc': row.get('pmc', ''),
                    'url': row.get('url', ''),
                    'journal': row.get('journal', ''),
                    'year': row.get('year', ''),
                })
        return papers

    def scrape_pubmed_recent(self, keywords, max_results=20):
        """Scrape recent papers from PubMed (simplified)"""
        # This is a placeholder - in production, use Bio.Entrez from Biopython
        logger.info(f"Searching PubMed for: {keywords}")
        logger.info(f"Note: For production use, install Biopython and use Entrez API")

        # Return sample data for demonstration
        return []

    def find_pdf_url(self, paper_url):
        """Find PDF URL from paper page"""
        pdf_url = None

        # Direct PMC link
        if 'pmc' in paper_url.lower() and '/pdf' not in paper_url:
            pdf_url = paper_url.rstrip('/') + '/pdf/'

        # Direct PDF link
        elif paper_url.lower().endswith('.pdf'):
            pdf_url = paper_url

        # Try Frontiers
        elif 'frontiers' in paper_url.lower():
            pdf_url = paper_url.rstrip('/') + '/pdf'

        # Try Springer
        elif 'springer' in paper_url.lower():
            parsed = urlparse(paper_url)
            article_id = parsed.path.split('/')[-1]
            pdf_url = f"https://link.springer.com/content/pdf/{article_id}.pdf"

        # Try Nature
        elif 'nature' in paper_url.lower():
            parsed = urlparse(paper_url)
            article_id = parsed.path.split('/')[-1]
            pdf_url = f"https://www.nature.com/articles/{article_id}.pdf"

        # Try BMC
        elif 'bmc' in paper_url.lower():
            parsed = urlparse(paper_url)
            parts = parsed.path.strip('/').split('/')
            article_id = parts[-1] if parts else ''
            pdf_url = f"https://bmcmicrobiol.biomedcentral.com/{article_id}.pdf"

        return pdf_url

    def download_pdf(self, url, output_path, filename=None):
        """Download a single PDF file"""
        if not url:
            return False, "No URL provided"

        try:
            # If no filename provided, extract from URL
            if not filename:
                parsed = urlparse(url)
                filename = os.path.basename(parsed.path)
                if not filename.endswith('.pdf'):
                    filename += '.pdf'

            # Clean filename
            filename = self._clean_filename(filename)
            filepath = os.path.join(output_path, filename)

            # Check if already exists
            if os.path.exists(filepath):
                logger.info(f"File already exists: {filename}")
                return True, filepath

            # Download with retries
            for attempt in range(self.max_retries):
                try:
                    response = self.session.get(url, timeout=self.timeout, stream=True)
                    response.raise_for_status()

                    # Save file
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    # Verify download
                    if os.path.getsize(filepath) > 1000:  # At least 1KB
                        logger.info(f"Downloaded: {filename}")
                        return True, filepath
                    else:
                        os.remove(filepath)
                        logger.warning(f"File too small, deleted: {filename}")

                except requests.exceptions.RequestException as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)

            return False, "Download failed after retries"

        except Exception as e:
            return False, str(e)

    def download_from_doi(self, doi, output_path):
        """Download PDF using DOI"""
        # Try multiple sources
        sources = [
            # Unpaywall API
            f"https://api.unpaywall.org/v2/{doi}?email=example@example.com",
        ]

        try:
            response = self.session.get(sources[0], timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('best_oa_location'):
                    pdf_url = data['best_oa_location'].get('url_for_pdf')
                    if pdf_url:
                        return self.download_pdf(pdf_url, output_path)

            return False, "No open access PDF found"

        except Exception as e:
            return False, str(e)

    def download_all(self, papers, output_dir):
        """Download all papers"""
        os.makedirs(output_dir, exist_ok=True)

        success_count = 0
        for i, paper in enumerate(papers):
            logger.info(f"Processing {i+1}/{len(papers)}: {paper.get('title', 'Unknown')[:50]}...")

            # Try different sources
            pdf_url = None

            # 1. Try direct URL
            if paper.get('url'):
                pdf_url = self.find_pdf_url(paper['url'])

            # 2. Try PMC
            if not pdf_url and paper.get('pmc'):
                pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{paper['pmc']}/pdf/"

            # 3. Try DOI
            if not pdf_url and paper.get('doi'):
                result, path = self.download_from_doi(paper['doi'], output_dir)
                if result:
                    success_count += 1
                    continue

            # Download if URL found
            if pdf_url:
                result, message = self.download_pdf(pdf_url, output_dir)
                if result:
                    success_count += 1

            time.sleep(1)  # Rate limiting

        return success_count

    def _clean_filename(self, filename):
        """Clean filename to remove invalid characters"""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        return filename


if __name__ == "__main__":
    # Test
    downloader = PDFDownloader()
    print("PDF Downloader initialized")
    print("Supported sources:", list(downloader.PDF_PATTERNS.keys()))
