#!/usr/bin/env python3
"""
PDF Downloader - Downloads PDFs with retry logic
"""

import os
import time
import requests
from typing import Dict, Optional
from tqdm import tqdm


class PDFDownloader:
    """Downloads PDF files from URLs"""

    def __init__(self, output_dir: str, max_retries: int = 3):
        self.output_dir = output_dir
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AKK-Paper-Scraper/1.0'
        })

    def download(self, paper: Dict) -> bool:
        """Download PDF for a paper"""
        if not paper.get('pdf_url'):
            return False

        pdf_url = paper['pdf_url']
        filename = self._get_filename(paper)
        filepath = os.path.join(self.output_dir, filename)

        # Skip if already exists
        if os.path.exists(filepath):
            return True

        for attempt in range(self.max_retries):
            try:
                return self._download_file(pdf_url, filepath)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                print(f"Error downloading {filename}: {e}")
                return False

        return False

    def _download_file(self, url: str, filepath: str) -> bool:
        """Download a file with progress"""
        response = self.session.get(url, stream=True, timeout=60)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return True

    def _get_filename(self, paper: Dict) -> str:
        """Generate filename from paper metadata"""
        arxiv_id = paper.get('arxiv_id', 'unknown')
        title = paper.get('title', 'untitled')[:50]
        # Sanitize filename
        title = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in title)
        return f"{arxiv_id}_{title}.pdf"
