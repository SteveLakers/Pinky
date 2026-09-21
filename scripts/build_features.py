#!/usr/bin/env python3
"""CLI: build feature panel from data/raw/ into data/features/."""

from pinky.features import build_universe_features, save_features

if __name__ == "__main__":
    panel = build_universe_features()
    path = save_features(panel)
    print(f"Wrote {path}")
