from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class AnalyticsSummary:
    service_level: float
    on_time_rate: float
    avg_delay_hours: float
    worst_region: str
    worst_supplier: str
    critical_skus: list[dict[str, object]]
    delayed_stockout_orders: int
    top_delay_reasons: list[dict[str, object]]


def _round(value: float) -> float:
    return round(float(value), 4)


def build_dashboard(orders: pd.DataFrame, inventory: pd.DataFrame) -> AnalyticsSummary:
    service_level = orders["shipped_qty"].sum() / orders["ordered_qty"].sum()
    on_time_rate = orders["on_time"].mean()

    delayed_orders = orders.loc[~orders["on_time"]]
    avg_delay_hours = delayed_orders["delayed_hours"].mean() if not delayed_orders.empty else 0.0

    region_table = (
        orders.groupby("region")
        .agg(on_time_rate=("on_time", "mean"), avg_delay_hours=("delayed_hours", "mean"))
        .sort_values(["on_time_rate", "avg_delay_hours"], ascending=[True, False])
    )
    worst_region = region_table.index[0]

    supplier_table = (
        orders.groupby("supplier")
        .agg(avg_delay_hours=("delayed_hours", "mean"), affected_orders=("order_id", "count"))
        .sort_values(["avg_delay_hours", "affected_orders"], ascending=[False, False])
    )
    worst_supplier = supplier_table.index[0]

    inventory = inventory.copy()
    inventory["coverage_ratio"] = inventory["on_hand"] / inventory["safety_stock"]
    critical_skus = (
        inventory.sort_values("coverage_ratio")
        .head(5)[["warehouse", "sku", "on_hand", "safety_stock", "lead_time_days", "coverage_ratio", "supplier"]]
        .to_dict(orient="records")
    )

    top_delay_reasons = (
        delayed_orders.groupby("exception_reason")
        .size()
        .sort_values(ascending=False)
        .head(3)
        .reset_index(name="orders")
        .to_dict(orient="records")
    )

    delayed_stockout_orders = int(
        delayed_orders["exception_reason"].str.contains("stockout", case=False, na=False).sum()
    )

    return AnalyticsSummary(
        service_level=_round(service_level),
        on_time_rate=_round(on_time_rate),
        avg_delay_hours=_round(avg_delay_hours),
        worst_region=worst_region,
        worst_supplier=worst_supplier,
        critical_skus=critical_skus,
        delayed_stockout_orders=delayed_stockout_orders,
        top_delay_reasons=top_delay_reasons,
    )


def generate_focus_evidence(
    focus_areas: list[str],
    dashboard: AnalyticsSummary,
    orders: pd.DataFrame,
    inventory: pd.DataFrame,
) -> list[str]:
    evidence: list[str] = [
        f"整体服务水平为 {dashboard.service_level:.1%}，准时交付率为 {dashboard.on_time_rate:.1%}。",
        f"当前平均延迟时长为 {dashboard.avg_delay_hours:.1f} 小时，最弱区域为 {dashboard.worst_region}。",
        f"延迟风险最高的供应商为 {dashboard.worst_supplier}。",
    ]

    if "stockout" in focus_areas:
        critical = dashboard.critical_skus[0]
        evidence.append(
            f"库存最危险组合是 {critical['warehouse']} / {critical['sku']}，现货 {critical['on_hand']}，"
            f"安全库存 {critical['safety_stock']}，覆盖率 {critical['coverage_ratio']:.2f}。"
        )
        evidence.append(f"由缺货引发的延迟订单共有 {dashboard.delayed_stockout_orders} 单。")

    if "delay" in focus_areas:
        east_delay = orders.loc[orders["region"] == "East", "delayed_hours"].mean()
        evidence.append(f"East 区域平均延迟 {east_delay:.1f} 小时，明显高于其他区域。")

    if "supplier" in focus_areas:
        long_lead = inventory.sort_values("lead_time_days", ascending=False).iloc[0]
        evidence.append(
            f"最长交期物料来自 {long_lead['supplier']}，SKU {long_lead['sku']}，lead time 为 {long_lead['lead_time_days']} 天。"
        )

    if "kpi" in focus_areas:
        delay_reason_summary = ", ".join(
            f"{item['exception_reason']}={item['orders']}" for item in dashboard.top_delay_reasons
        )
        evidence.append(
            f"主要异常原因分布为: {delay_reason_summary}。"
        )

    return evidence
