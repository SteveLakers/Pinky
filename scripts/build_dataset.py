#!/usr/bin/env python3
"""CLI: join features + labels into data/dataset/train_dataset.parquet."""

from pinky.dataset import build_train_dataset, save_dataset

if __name__ == "__main__":
    ds = build_train_dataset()
    path = save_dataset(ds)
    print(f"Wrote {path}")
