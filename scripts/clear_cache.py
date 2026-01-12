#!/usr/bin/env python3
"""
Cache Clearing Utility

Clears Python bytecode cache to prevent stale code issues.
Run this before starting services or when debugging cache-related problems.

Usage:
    python scripts/clear_cache.py [--dry-run] [--verbose]
"""

import os
import sys
import shutil
import glob
import argparse
from pathlib import Path

def clear_python_cache(dry_run=False, verbose=False):
    """Clear all Python bytecode cache files and directories."""
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)

    cache_dirs = []
    pyc_files = []

    # Find all __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == '__pycache__':
                cache_dir = Path(root) / d
                cache_dirs.append(cache_dir)

    # Find all .pyc and .pyo files
    pyc_files = list(Path('.').rglob('*.pyc')) + list(Path('.').rglob('*.pyo'))

    print(f"Found {len(cache_dirs)} cache directories and {len(pyc_files)} bytecode files")

    if dry_run:
        print("\nDRY RUN - Would remove:")
        for cache_dir in cache_dirs:
            print(f"  Directory: {cache_dir}")
        for pyc_file in pyc_files:
            print(f"  File: {pyc_file}")
        return

    # Remove cache directories
    removed_dirs = 0
    for cache_dir in cache_dirs:
        try:
            shutil.rmtree(cache_dir)
            removed_dirs += 1
            if verbose:
                print(f"Removed directory: {cache_dir}")
        except Exception as e:
            print(f"Failed to remove {cache_dir}: {e}")

    # Remove .pyc/.pyo files
    removed_files = 0
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
            removed_files += 1
            if verbose:
                print(f"Removed file: {pyc_file}")
        except Exception as e:
            print(f"Failed to remove {pyc_file}: {e}")

    print(f"\n✅ Successfully cleared {removed_dirs} cache directories and {removed_files} bytecode files")

def main():
    parser = argparse.ArgumentParser(description="Clear Python bytecode cache")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be removed without actually removing")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")

    args = parser.parse_args()
    clear_python_cache(dry_run=args.dry_run, verbose=args.verbose)

if __name__ == '__main__':
    main()