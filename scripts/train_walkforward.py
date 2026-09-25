#!/usr/bin/env python3
"""CLI: walk-forward train + evaluate (default focus: 1y, v2 prep)."""

import sys

from pinky.train import DEFAULT_HORIZONS, run_all

if __name__ == "__main__":
    horizons = sys.argv[1:] or list(DEFAULT_HORIZONS)
    run_all(horizons=horizons)
