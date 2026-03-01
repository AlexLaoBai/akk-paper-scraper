#!/usr/bin/env python3
"""
ArXiv Scraper - Fetches paper metadata from arXiv
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict


class ArxivScraper:
    """Scraper for arXiv papers"""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AKK-Paper-Scraper/1.0'
        })

    def search(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """Search for papers by keyword"""
        params = {
            'search_query': f'all:{keyword}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }

        response = self.session.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()

        return self._parse_feed(response.text)

    def _parse_feed(self, xml_content: str) -> List[Dict]:
        """Parse arXiv Atom feed"""
        papers = []

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            return papers

        namespace = {'atom': 'http://www.w3.org/2005/Atom'}

        for entry in root.findall('.//atom:entry', namespace):
            paper = {
                'id': entry.find('atom:id', namespace).text,
                'title': self._clean_text(entry.find('atom:title', namespace).text),
                'summary': self._clean_text(entry.find('atom:summary', namespace).text),
                'authors': [a.find('atom:name', namespace).text
                           for a in entry.findall('atom:author', namespace)],
                'published': entry.find('atom:published', namespace).text,
                'pdf_url': None,
                'arxiv_id': None
            }

            # Find PDF link
            for link in entry.findall('atom:link', namespace):
                if link.get('title') == 'pdf':
                    paper['pdf_url'] = link.get('href')
                    break

            # Extract arXiv ID
            if paper['id']:
                paper['arxiv_id'] = paper['id'].split('/')[-1]

            papers.append(paper)

        return papers

    def _clean_text(self, text: str) -> str:
        """Clean up text whitespace"""
        if not text:
            return ""
        return ' '.join(text.split())
