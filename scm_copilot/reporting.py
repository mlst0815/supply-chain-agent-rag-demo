from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .config import OUTPUT_DIR


def _plot_on_time_by_region(orders: pd.DataFrame, path: Path) -> None:
    summary = (
        orders.groupby("region")["on_time"]
        .mean()
        .mul(100)
        .sort_values(ascending=True)
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(summary.index, summary.values, color=["#d97706", "#f59e0b", "#10b981", "#2563eb"])
    ax.set_title("On-time Delivery by Region")
    ax.set_ylabel("OTD %")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _plot_inventory_risk(inventory: pd.DataFrame, path: Path) -> None:
    risk = inventory.copy()
    risk["coverage_ratio"] = risk["on_hand"] / risk["safety_stock"]
    risk = risk.sort_values("coverage_ratio").head(6)
    labels = [f"{row.warehouse}-{row.sku}" for row in risk.itertuples()]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(labels, risk["coverage_ratio"], color="#dc2626")
    ax.axvline(1.0, color="#111827", linestyle="--", linewidth=1)
    ax.set_title("Inventory Coverage Risk")
    ax.set_xlabel("On-hand / Safety Stock")
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def export_artifacts(
    result: dict[str, object],
    orders: pd.DataFrame,
    inventory: pd.DataFrame,
    output_dir: Path | None = None,
) -> dict[str, object]:
    destination = output_dir or OUTPUT_DIR
    destination.mkdir(parents=True, exist_ok=True)

    chart_on_time = destination / "on_time_by_region.png"
    chart_inventory = destination / "inventory_risk.png"
    report_path = destination / "demo_report.md"
    json_path = destination / "demo_result.json"

    _plot_on_time_by_region(orders, chart_on_time)
    _plot_inventory_risk(inventory, chart_inventory)

    report_lines = [
        "# Supply Chain Agent RAG Demo Report",
        "",
        f"## Question",
        result["question"],
        "",
        "## Summary",
        result["summary"],
        "",
        "## Focus Areas",
        ", ".join(result["focus_areas"]),
        "",
        "## Recommended Actions",
    ]
    report_lines.extend(f"{index}. {action}" for index, action in enumerate(result["actions"], start=1))
    report_lines.extend(["", "## Evidence"])
    report_lines.extend(f"- {item}" for item in result["evidence"])
    report_lines.extend(["", "## Retrieved Docs"])
    report_lines.extend(
        f"- {doc['title']} | score={doc['score']} | {doc['summary']}"
        for doc in result["retrieved_docs"]
    )
    report_lines.extend(
        [
            "",
            "## Generated Files",
            f"- {report_path.name}",
            f"- {json_path.name}",
            f"- {chart_on_time.name}",
            f"- {chart_inventory.name}",
        ]
    )

    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "markdown_report": str(report_path),
        "json_result": str(json_path),
        "charts": [str(chart_on_time), str(chart_inventory)],
    }

