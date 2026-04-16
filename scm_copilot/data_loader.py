from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import DATA_DIR


def load_orders(data_dir: Path | None = None) -> pd.DataFrame:
    path = (data_dir or DATA_DIR) / "orders.csv"
    orders = pd.read_csv(path, parse_dates=["order_date"])
    orders["on_time"] = orders["on_time"].astype(bool)
    return orders


def load_inventory(data_dir: Path | None = None) -> pd.DataFrame:
    path = (data_dir or DATA_DIR) / "inventory.csv"
    inventory = pd.read_csv(path, parse_dates=["snapshot_date"])
    return inventory

