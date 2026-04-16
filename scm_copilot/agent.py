from __future__ import annotations

from dataclasses import asdict

from .analytics import AnalyticsSummary, build_dashboard, generate_focus_evidence
from .data_loader import load_inventory, load_orders
from .llm import maybe_generate_with_openai
from .retriever import load_knowledge_base, retrieve_documents


FOCUS_KEYWORDS = {
    "stockout": ["缺货", "库存", "补货", "安全库存", "stockout", "inventory", "shortage"],
    "delay": ["延迟", "晚到", "发货", "履约", "交付", "delay", "late", "otd"],
    "supplier": ["供应商", "交期", "lead time", "supplier", "采购"],
    "kpi": ["kpi", "分析", "summary", "dashboard", "汇报", "service level", "准时"],
}


class SupplyChainCopilot:
    def __init__(self) -> None:
        self.orders = load_orders()
        self.inventory = load_inventory()
        self.knowledge_base = load_knowledge_base()

    def detect_focus_areas(self, question: str) -> list[str]:
        query = question.lower()
        scores: dict[str, int] = {}

        for focus, keywords in FOCUS_KEYWORDS.items():
            scores[focus] = sum(keyword.lower() in query for keyword in keywords)

        selected = [focus for focus, score in sorted(scores.items(), key=lambda item: item[1], reverse=True) if score > 0]
        return selected[:2] or ["kpi"]

    def _compose_actions(self, focus_areas: list[str], dashboard: AnalyticsSummary) -> list[str]:
        actions: list[str] = []

        if "stockout" in focus_areas:
            critical = dashboard.critical_skus[0]
            actions.append(
                f"针对 {critical['warehouse']} 的 {critical['sku']} 立即触发加急补货，并将低优先级订单转移到有余量仓库。"
            )
            actions.append("把安全库存阈值从静态规则调整为滚动 4 周需求驱动，并建立缺货预警。")

        if "delay" in focus_areas:
            actions.append("对 East 区域建立 24 小时履约异常看板，按订单老化时间触发人工升级。")
            actions.append("将延迟原因拆分到仓内作业、承运商、供应商三个责任域，避免异常被统一归类。")

        if "supplier" in focus_areas:
            actions.append(f"把 {dashboard.worst_supplier} 纳入周度供应商交期复盘，并绑定 ASN 到货偏差指标。")

        if "kpi" in focus_areas or not actions:
            actions.append("把服务水平、OTD、缺货率、供应商 lead time 风险沉淀为周报模板。")

        return actions[:4]

    def _compose_prompt(
        self,
        question: str,
        focus_areas: list[str],
        retrieved_docs: list[dict[str, object]],
        evidence: list[str],
    ) -> str:
        joined_docs = "\n".join(
            f"- {doc['title']}: {doc['summary']}" for doc in retrieved_docs
        )
        joined_evidence = "\n".join(f"- {item}" for item in evidence)
        return (
            f"Question:\n{question}\n\n"
            f"Focus Areas: {', '.join(focus_areas)}\n\n"
            f"Evidence:\n{joined_evidence}\n\n"
            f"Retrieved Docs:\n{joined_docs}\n\n"
            "Please write a concise supply chain action summary in Chinese."
        )

    def _compose_local_summary(
        self,
        question: str,
        focus_areas: list[str],
        dashboard: AnalyticsSummary,
        retrieved_docs: list[dict[str, object]],
    ) -> str:
        top_doc_titles = "、".join(doc["title"] for doc in retrieved_docs[:2])
        critical = dashboard.critical_skus[0]
        if "stockout" in focus_areas:
            focus_text = (
                f"{critical['warehouse']} 的 {critical['sku']} 缺货风险"
                f"以及 {dashboard.worst_supplier} 的交期波动"
            )
        else:
            focus_text = f"{dashboard.worst_region} 区域的履约波动与 {dashboard.worst_supplier} 的交期风险"
        return (
            f"针对问题“{question}”，当前最值得优先处理的是 {focus_text}。"
            f"整体服务水平为 {dashboard.service_level:.1%}，"
            f"准时交付率为 {dashboard.on_time_rate:.1%}。结合知识库文档 {top_doc_titles}，"
            f"建议先做缺货止血，再做交期归因和 KPI 常态化跟踪。"
        )

    def run(self, question: str, top_k: int = 3) -> dict[str, object]:
        focus_areas = self.detect_focus_areas(question)
        dashboard = build_dashboard(self.orders, self.inventory)
        retrieved_docs = retrieve_documents(
            query=f"{question} {' '.join(focus_areas)}",
            documents=self.knowledge_base,
            top_k=top_k,
        )
        evidence = generate_focus_evidence(focus_areas, dashboard, self.orders, self.inventory)
        actions = self._compose_actions(focus_areas, dashboard)

        prompt = self._compose_prompt(question, focus_areas, retrieved_docs, evidence)
        llm_summary = maybe_generate_with_openai(prompt)

        return {
            "question": question,
            "focus_areas": focus_areas,
            "summary": llm_summary or self._compose_local_summary(question, focus_areas, dashboard, retrieved_docs),
            "actions": actions,
            "evidence": evidence,
            "retrieved_docs": retrieved_docs,
            "dashboard": asdict(dashboard),
        }
