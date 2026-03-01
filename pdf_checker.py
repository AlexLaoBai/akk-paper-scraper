#!/usr/bin/env python3
"""
PDF Checker - PDF integrity validation and deduplication tool
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False
    try:
        from PyPDF2 import PdfReader
        HAS_PYPDF = True
    except ImportError:
        HAS_PYPDF = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFChecker:
    """PDF integrity checker and deduplication tool"""

    def __init__(self, pdf_dir='pdfs'):
        self.pdf_dir = pdf_dir
        self.results = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'scanned': 0,
            'files': []
        }

    def calculate_md5(self, filepath):
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def check_pdf_integrity(self, filepath):
        """Check if PDF is valid and readable"""
        try:
            file_size = os.path.getsize(filepath)
            if file_size < 1000:
                return False, "File too small", file_size

            if HAS_PYPDF:
                reader = PdfReader(filepath)
                num_pages = len(reader.pages)

                is_scanned = False
                if num_pages <= 5:
                    text_length = 0
                    for i in range(min(num_pages, 3)):
                        page = reader.pages[i]
                        text = page.extract_text()
                        if text:
                            text_length += len(text.strip())

                    if text_length < 100:
                        is_scanned = True

                return True, f"{num_pages} pages", file_size, is_scanned
            else:
                with open(filepath, 'rb') as f:
                    header = f.read(5)
                    if header == b'%PDF-':
                        return True, "Valid PDF header", file_size, False
                    else:
                        return False, "Invalid PDF header", file_size, False

        except Exception as e:
            return False, str(e), 0, False

    def is_scanned_pdf(self, filepath):
        """Detect if PDF is a scanned image-only document"""
        if not HAS_PYPDF:
            return False

        try:
            reader = PdfReader(filepath)
            if len(reader.pages) == 0:
                return True

            first_page = reader.pages[0]
            text = first_page.extract_text()

            if not text or len(text.strip()) < 50:
                return True

            return False
        except Exception:
            return True

    def check_all(self):
        """Check all PDFs in directory"""
        if not os.path.exists(self.pdf_dir):
            logger.error(f"Directory not found: {self.pdf_dir}")
            return self.results

        pdf_files = [f for f in os.listdir(self.pdf_dir) if f.lower().endswith('.pdf')]

        self.results['total'] = len(pdf_files)
        self.results['valid'] = 0
        self.results['invalid'] = 0
        self.results['scanned'] = 0
        self.results['files'] = []

        for filename in pdf_files:
            filepath = os.path.join(self.pdf_dir, filename)

            if HAS_PYPDF:
                valid, message, size, is_scanned = self.check_pdf_integrity(filepath)

                file_info = {
                    'name': filename,
                    'valid': valid,
                    'message': message,
                    'size': size,
                    'scanned': is_scanned
                }

                if valid:
                    self.results['valid'] += 1
                    if is_scanned:
                        self.results['scanned'] += 1
                else:
                    self.results['invalid'] += 1
                    file_info['error'] = message
            else:
                try:
                    with open(filepath, 'rb') as f:
                        header = f.read(5)
                        if header == b'%PDF-':
                            self.results['valid'] += 1
                            file_info = {'name': filename, 'valid': True}
                        else:
                            self.results['invalid'] += 1
                            file_info = {'name': filename, 'valid': False, 'error': 'Invalid header'}
                except Exception as e:
                    self.results['invalid'] += 1
                    file_info = {'name': filename, 'valid': False, 'error': str(e)}

            self.results['files'].append(file_info)

        return self.results

    def verify_and_deduplicate(self):
        """Verify PDFs and remove duplicates based on MD5 hash"""
        results = self.check_all()

        hashes = {}
        duplicates = []

        for file_info in results['files']:
            if not file_info['valid']:
                continue

            filepath = os.path.join(self.pdf_dir, file_info['name'])
            file_hash = self.calculate_md5(filepath)

            if file_hash in hashes:
                duplicates.append({
                    'original': hashes[file_hash],
                    'duplicate': file_info['name']
                })
                os.remove(filepath)
                logger.info(f"Removed duplicate: {file_info['name']}")
            else:
                hashes[file_hash] = file_info['name']

        results['unique'] = len(hashes)
        results['duplicates'] = len(duplicates)
        results['duplicate_list'] = duplicates

        return results

    def generate_report(self, output_file=None):
        """Generate JSON report of check results"""
        results = self.check_all()

        report = {
            'timestamp': datetime.now().isoformat(),
            'directory': self.pdf_dir,
            'summary': {
                'total': results['total'],
                'valid': results['valid'],
                'invalid': results['invalid'],
                'scanned': results['scanned']
            },
            'files': results['files']
        }

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Report saved to: {output_file}")

        return report


if __name__ == "__main__":
    import sys

    pdf_dir = sys.argv[1] if len(sys.argv) > 1 else 'pdfs'

    checker = PDFChecker(pdf_dir)
    results = checker.check_all()

    print(f"\nPDF Check Results:")
    print(f"  Total: {results['total']}")
    print(f"  Valid: {results['valid']}")
    print(f"  Invalid: {results['invalid']}")
    print(f"  Scanned: {results['scanned']}")

    if results['invalid'] > 0:
        print("\nInvalid files:")
        for f in results['files']:
            if not f.get('valid', True):
                print(f"  - {f['name']}: {f.get('error', 'Unknown error')}")
