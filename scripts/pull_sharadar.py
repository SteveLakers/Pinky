#!/usr/bin/env python3
"""CLI: download all Sharadar bulk tables (full history) → data/sharadar/*.parquet.

Usage:
  python scripts/pull_sharadar.py [table ...]
"""

import sys

from pinky.sharadar import pull_all

if __name__ == "__main__":
    pull_all(sys.argv[1:] or None)
