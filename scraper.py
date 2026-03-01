#!/usr/bin/env python3
"""
Akkermansia muciniphila & Probiotic Paper Scraper
Automated scraper for downloading research papers from academic databases
"""

import os
import csv
import json
import time
import random
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SEARCH_TERMS = [
    "Akkermansia muciniphila",
    "Akkermansia probiotic",
    "Akkermansia muciniphila health",
    "Akkermansia muciniphila disease",
    "Akkermansia gut microbiota",
    "muciniphila therapeutic",
    "next generation probiotic Akkermansia"
]

OPEN_ACCESS_SOURCES = [
    "PMC",
    "Frontiers",
    "Springer Open",
    "Wiley Open Access",
    "Oxford Open",
    "PLOS"
]


def load_existing_papers(csv_file):
    """Load existing papers from CSV"""
    existing = set()
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row.get('URL', '').strip())
    logger.info(f"Loaded {len(existing)} existing papers")
    return existing


def get_pubmed_papers(term, max_results=10):
    """Get papers from PubMed using E-utilities API"""
    papers = []
    try:
        import urllib.request
        import urllib.parse

        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': f'{term} AND (free full text[filter] OR open access[filter])',
            'retmax': max_results,
            'retmode': 'json',
            'sort': 'relevance'
        }
        url = f"{base_url}?{urllib.parse.urlencode(params)}"

        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
            ids = data.get('esearchresult', {}).get('idlist', [])

        if ids:
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={','.join(ids)}&retmode=json"
            with urllib.request.urlopen(fetch_url, timeout=30) as response:
                summary_data = json.loads(response.read().decode())
                for uid, info in summary_data.get('result', {}).items():
                    if uid == 'uids':
                        continue
                    authors_list = []
                    for author in info.get('authors', []):
                        if isinstance(author, dict):
                            authors_list.append(author.get('name', ''))
                        elif isinstance(author, str):
                            authors_list.append(author)
                    papers.append({
                        'title': info.get('title', ''),
                        'authors': ', '.join(authors_list)[:100],
                        'year': info.get('pubdate', '')[:4],
                        'date': info.get('pubdate', ''),
                        'journal': info.get('source', ''),
                        'doi': info.get('elocationid', '').replace('doi: ', ''),
                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                        'pubmed': uid,
                        'source': 'PubMed'
                    })
    except Exception as e:
        logger.warning(f"PubMed API error: {e}")

    return papers


def check_pdf_available(url, source):
    """Check if PDF is available for download"""
    pdf_url = ""

    if 'pubmed' in url and 'pmc' not in url:
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode()
                if 'PMC' in html:
                    import re
                    pmc_match = re.search(r'PMC\d+', html)
                    if pmc_match:
                        pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_match.group()}/pdf/"
        except:
            pass
    elif 'frontiersin.org' in url:
        pdf_url = url.replace('/articles/', '/journals/') + '/pdf'
    elif 'springer.com' in url:
        pdf_url = url.replace('/article/', '/content/pdf/') + '.pdf'

    return pdf_url


def download_pdf(paper_info, pdf_url, pdf_dir):
    """Download PDF"""
    try:
        import urllib.request

        safe_title = paper_info['title'][:50].replace('/', '_').replace(':', '').replace(' ', '_')
        pdf_num = len([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]) + 1
        filename = f"{pdf_num:02d}_{safe_title}.pdf"
        filepath = os.path.join(pdf_dir, filename)

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(pdf_url, headers=headers)

        with urllib.request.urlopen(req, timeout=60) as response:
            content = response.read()
            with open(filepath, 'wb') as f:
                f.write(content)

            size = len(content) / (1024 * 1024)
            if size > 0.1:
                logger.info(f"Downloaded: {filename} ({size:.1f} MB)")
                return filename
            else:
                os.remove(filepath)
                return None

    except Exception as e:
        logger.warning(f"PDF download failed: {e}")
        return None


def add_paper_to_csv(paper, csv_file):
    """Add paper to CSV"""
    file_exists = os.path.exists(csv_file)

    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['Title', 'Authors', 'Year', 'Date', 'Journal', 'DOI', 'URL', 'PubMed', 'Source', 'Abstract']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'Title': paper.get('title', ''),
            'Authors': paper.get('authors', ''),
            'Year': paper.get('year', ''),
            'Date': paper.get('date', ''),
            'Journal': paper.get('journal', ''),
            'DOI': paper.get('doi', ''),
            'URL': paper.get('url', ''),
            'PubMed': paper.get('pubmed', ''),
            'Source': paper.get('source', ''),
            'Abstract': paper.get('abstract', '')[:500]
        })


def save_status(new_papers_count, pdfs_downloaded, log_file):
    """Save run status"""
    status = {
        'last_run': datetime.now().isoformat(),
        'papers_found': new_papers_count,
        'pdfs_downloaded': pdfs_downloaded
    }
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)


def main():
    """Main function"""
    logger.info("=" * 50)
    logger.info("Starting paper scraper...")
    logger.info("=" * 50)

    # Configuration
    workspace = "/workspace/project"
    pdf_dir = f"{workspace}/pdfs"
    csv_file = f"{workspace}/papers.csv"
    log_file = f"{workspace}/status.json"

    os.makedirs(pdf_dir, exist_ok=True)

    existing = load_existing_papers(csv_file)

    all_papers = []
    pdfs_downloaded = 0

    for term in SEARCH_TERMS[:4]:
        logger.info(f"Searching: {term}")

        papers = get_pubmed_papers(term, max_results=5)
        for p in papers:
            if p['url'] not in existing and len(all_papers) < 20:
                all_papers.append(p)

        time.sleep(random.uniform(1, 3))

    seen = set()
    unique_papers = []
    for p in all_papers:
        if p['url'] not in seen:
            seen.add(p['url'])
            unique_papers.append(p)

    logger.info(f"Found {len(unique_papers)} new papers")

    for paper in unique_papers[:20]:
        try:
            add_paper_to_csv(paper, csv_file)
            logger.info(f"Added paper: {paper['title'][:50]}...")

            pdf_url = check_pdf_available(paper['url'], paper['source'])
            if pdf_url:
                filename = download_pdf(paper, pdf_url, pdf_dir)
                if filename:
                    pdfs_downloaded += 1

            time.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            logger.error(f"Failed to process paper: {e}")

    save_status(len(unique_papers), pdfs_downloaded, log_file)

    logger.info("=" * 50)
    logger.info(f"Complete! Added {len(unique_papers)} papers, downloaded {pdfs_downloaded} PDFs")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
