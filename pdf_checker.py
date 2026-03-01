#!/usr/bin/env python3
"""
PDF Checker - Validates PDF files
"""

import os
import sys
from pathlib import Path
from PyPDF2 import PdfReader


class PDFChecker:
    """Checks PDF files for validity"""

    def __init__(self, directory: str):
        self.directory = directory

    def check_all(self):
        """Check all PDFs in directory"""
        pdf_files = list(Path(self.directory).glob('*.pdf'))

        if not pdf_files:
            print("No PDF files found.")
            return

        print(f"Checking {len(pdf_files)} PDF files...\n")

        valid = 0
        invalid = 0

        for pdf_file in pdf_files:
            if self.check_pdf(pdf_file):
                valid += 1
                print(f"✓ {pdf_file.name}")
            else:
                invalid += 1
                print(f"✗ {pdf_file.name} - Invalid")

        print(f"\nResults: {valid} valid, {invalid} invalid")

    def check_pdf(self, filepath: Path) -> bool:
        """Check if a PDF is valid"""
        try:
            with open(filepath, 'rb') as f:
                reader = PdfReader(f)
                # Try to read first page
                if len(reader.pages) > 0:
                    _ = reader.pages[0]
                return True
        except Exception:
            return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = './papers'

    checker = PDFChecker(directory)
    checker.check_all()
