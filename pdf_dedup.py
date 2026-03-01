#!/usr/bin/env python3
"""
PDF Deduplicator - Removes duplicate PDFs based on content hash
"""

import os
import sys
import hashlib
from pathlib import Path
from collections import defaultdict


class PDFDeduplicator:
    """Finds and removes duplicate PDFs"""

    def __init__(self, directory: str):
        self.directory = directory

    def find_duplicates(self):
        """Find duplicate PDFs by content hash"""
        hash_to_files = defaultdict(list)

        pdf_files = list(Path(self.directory).glob('*.pdf'))

        print(f"Hashing {len(pdf_files)} files...")

        for pdf_file in pdf_files:
            file_hash = self._hash_file(pdf_file)
            hash_to_files[file_hash].append(pdf_file)

        # Find duplicates
        duplicates = {h: files for h, files in hash_to_files.items()
                     if len(files) > 1}

        return duplicates

    def remove_duplicates(self, keep_first: bool = True):
        """Remove duplicate files, keeping only one"""
        duplicates = self.find_duplicates()

        if not duplicates:
            print("No duplicates found.")
            return

        print(f"\nFound {len(duplicates)} sets of duplicates:\n")

        total_removed = 0

        for file_hash, files in duplicates.items():
            print(f"Duplicate group (hash: {file_hash[:8]}...):")
            for i, f in enumerate(files):
                if i == 0 and keep_first:
                    print(f"  KEEP: {f.name}")
                else:
                    print(f"  REMOVE: {f.name}")
                    f.unlink()
                    total_removed += 1

        print(f"\nRemoved {total_removed} duplicate files.")

    def _hash_file(self, filepath: Path) -> str:
        """Calculate SHA256 hash of file"""
        hasher = hashlib.sha256()

        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)

        return hasher.hexdigest()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = './papers'

    dedup = PDFDeduplicator(directory)
    dedup.remove_duplicates()
