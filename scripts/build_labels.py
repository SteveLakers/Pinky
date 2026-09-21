#!/usr/bin/env python3
"""CLI: build labels vs SPY from data/raw/ into data/labels/."""

from pinky.labels import build_universe_labels, save_labels

if __name__ == "__main__":
    panel = build_universe_labels()
    path = save_labels(panel)
    print(f"Wrote {path}")
