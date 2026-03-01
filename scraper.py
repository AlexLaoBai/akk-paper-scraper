#!/usr/bin/env python3
"""
Akkermansia muciniphila & Probiotic Paper Scraper
每天自动抓取20篇论文并更新数据库
"""

import os
import csv
import json
import time
import random
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/project/logs/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
WORKSPACE = "/workspace/project"
PDF_DIR = f"{WORKSPACE}/pdfs"
CSV_FILE = f"{WORKSPACE}/Akkermansia_muciniphila_papers_database.csv"
HTML_FILE = f"{WORKSPACE}/Akkermansia_database_with_pdfs.html"
LOG_FILE = f"{WORKSPACE}/scraper_status.json"

# 搜索关键词
SEARCH_TERMS = [
    "Akkermansia muciniphila",
    "Akkermansia probiotic",
    "Akkermansia muciniphila health",
    "Akkermansia muciniphila disease",
    "Akkermansia gut microbiota",
    "muciniphila therapeutic",
    "next generation probiotic Akkermansia"
]

# Open Access 数据源
OPEN_ACCESS_SOURCES = [
    "PMC",
    "Frontiers",
    "Springer Open",
    "Wiley Open Access",
    "Oxford Open",
    "PLOS"
]

def load_existing_papers():
    """加载已存在的论文"""
    existing = set()
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row.get('URL', '').strip())
    logger.info(f"已加载 {len(existing)} 篇已有论文")
    return existing

def get_pubmed_papers(term, max_results=10):
    """从 PubMed 获取论文 (使用 E-utilities API)"""
    papers = []
    try:
        import urllib.request
        import urllib.parse

        # 使用 PubMed E-utilities
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

        # 获取详情
        if ids:
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={','.join(ids)}&retmode=json"
            with urllib.request.urlopen(fetch_url, timeout=30) as response:
                summary_data = json.loads(response.read().decode())
                for uid, info in summary_data.get('result', {}).items():
                    if uid == 'uids':
                        continue
                    # 处理作者列表
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
        logger.warning(f"PubMed API 错误: {e}")

    return papers

def get_frontiers_papers(term, max_results=5):
    """从 Frontiers 获取 Open Access 论文"""
    papers = []
    try:
        import urllib.request
        import urllib.parse
        import re

        # 使用网页搜索 - Frontiers 搜索页面
        search_url = f"https://www.frontiersin.org/search?term={urllib.parse.quote(term)}&type=article"

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = urllib.request.Request(search_url, headers=headers)

        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='ignore')

            # 解析搜索结果 (简化版)
            # 实际生产环境可能需要更复杂的解析
            # 这里返回空列表，让主要依赖 PubMed
            pass

    except Exception as e:
        logger.warning(f"Frontiers 搜索错误: {e}")

    return papers

def get_springer_papers(term, max_results=5):
    """从 Springer 获取 Open Access 论文"""
    papers = []
    try:
        import urllib.request
        import urllib.parse

        # Springer Open 搜索
        search_url = f"https://api.springernature.com/meta/v1/search?query={urllib.parse.quote(term)}&p=5&openaccess=true"

        headers = {
            'User-Agent': 'Mozilla/5.0',
            'X-API-Key': ''  # 可能需要 API key
        }

        # 使用网页搜索替代
        search_url = f"https://link.springer.com/search?query={urllib.parse.quote(term)}&facet=content-type%2FOpen%20Access"
        # 这里简化处理，实际需要爬虫
    except Exception as e:
        logger.warning(f"Springer 搜索错误: {e}")

    return papers

def check_pdf_available(url, source):
    """检查是否有可下载的 PDF"""
    pdf_url = ""

    if 'pubmed' in url and 'pmc' not in url:
        # PubMed 可能链接到 PMC
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

def download_pdf(paper_info, pdf_url):
    """下载 PDF"""
    try:
        import urllib.request

        # 生成文件名
        safe_title = paper_info['title'][:50].replace('/', '_').replace(':', '').replace(' ', '_')
        pdf_num = len([f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]) + 1
        filename = f"{pdf_num:02d}_{safe_title}.pdf"
        filepath = os.path.join(PDF_DIR, filename)

        # 下载
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(pdf_url, headers=headers)

        with urllib.request.urlopen(req, timeout=60) as response:
            content = response.read()
            with open(filepath, 'wb') as f:
                f.write(content)

            # 检查文件大小
            size = len(content) / (1024 * 1024)
            if size > 0.1:  # 至少 100KB
                logger.info(f"下载成功: {filename} ({size:.1f} MB)")
                return filename
            else:
                os.remove(filepath)
                return None

    except Exception as e:
        logger.warning(f"PDF 下载失败: {e}")
        return None

def add_paper_to_csv(paper):
    """添加论文到 CSV"""
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
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

def update_html():
    """更新 HTML 数据库页面"""
    # 读取现有 HTML 并更新论文列表部分
    # 这里简化处理，实际需要解析和更新 HTML
    pass

def save_status(new_papers_count, pdfs_downloaded):
    """保存运行状态"""
    status = {
        'last_run': datetime.now().isoformat(),
        'papers_found': new_papers_count,
        'pdfs_downloaded': pdfs_downloaded
    }
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("开始抓取论文...")
    logger.info("=" * 50)

    # 确保 PDF 目录存在
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(f"{WORKSPACE}/logs", exist_ok=True)

    # 加载已有论文
    existing = load_existing_papers()

    all_papers = []
    pdfs_downloaded = 0

    # 从不同来源获取论文
    for term in SEARCH_TERMS[:4]:  # 限制搜索次数
        logger.info(f"搜索: {term}")

        # PubMed
        papers = get_pubmed_papers(term, max_results=5)
        for p in papers:
            if p['url'] not in existing and len(all_papers) < 20:
                all_papers.append(p)

        # Frontiers
        papers = get_frontiers_papers(term, max_results=3)
        for p in papers:
            if p['url'] not in existing and len(all_papers) < 20:
                all_papers.append(p)

        time.sleep(random.uniform(1, 3))  # 避免请求过快

    # 去重
    seen = set()
    unique_papers = []
    for p in all_papers:
        if p['url'] not in seen:
            seen.add(p['url'])
            unique_papers.append(p)

    logger.info(f"找到 {len(unique_papers)} 篇新论文")

    # 处理论文
    for paper in unique_papers[:20]:
        try:
            # 添加到 CSV
            add_paper_to_csv(paper)
            logger.info(f"添加论文: {paper['title'][:50]}...")

            # 尝试下载 PDF
            pdf_url = check_pdf_available(paper['url'], paper['source'])
            if pdf_url:
                filename = download_pdf(paper, pdf_url)
                if filename:
                    pdfs_downloaded += 1

            time.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            logger.error(f"处理论文失败: {e}")

    # 保存状态
    save_status(len(unique_papers), pdfs_downloaded)

    logger.info("=" * 50)
    logger.info(f"完成! 新增 {len(unique_papers)} 篇论文, 下载 {pdfs_downloaded} 个 PDF")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
