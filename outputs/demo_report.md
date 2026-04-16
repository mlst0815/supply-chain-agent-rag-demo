# Supply Chain Agent RAG Demo Report

## Question
华东仓SKU-C连续缺货并导致订单延迟，请给我一份处理建议和证据

## Summary
针对问题“华东仓SKU-C连续缺货并导致订单延迟，请给我一份处理建议和证据”，当前最值得优先处理的是 WH-East 的 SKU-C 缺货风险以及 DeltaFlex 的交期波动。整体服务水平为 88.7%，准时交付率为 50.0%。结合知识库文档 Delay Management SOP、Inventory Stockout Recovery SOP，建议先做缺货止血，再做交期归因和 KPI 常态化跟踪。

## Focus Areas
stockout, delay

## Recommended Actions
1. 针对 WH-East 的 SKU-C 立即触发加急补货，并将低优先级订单转移到有余量仓库。
2. 把安全库存阈值从静态规则调整为滚动 4 周需求驱动，并建立缺货预警。
3. 对 East 区域建立 24 小时履约异常看板，按订单老化时间触发人工升级。
4. 将延迟原因拆分到仓内作业、承运商、供应商三个责任域，避免异常被统一归类。

## Evidence
- 整体服务水平为 88.7%，准时交付率为 50.0%。
- 当前平均延迟时长为 14.9 小时，最弱区域为 North。
- 延迟风险最高的供应商为 DeltaFlex。
- 库存最危险组合是 WH-East / SKU-C，现货 35，安全库存 90，覆盖率 0.39。
- 由缺货引发的延迟订单共有 6 单。
- East 区域平均延迟 14.3 小时，明显高于其他区域。

## Retrieved Docs
- Delay Management SOP | score=8 | 用于处理履约晚到、仓内积压与运输异常的标准流程。
- Inventory Stockout Recovery SOP | score=8 | 用于处理高风险 SKU 缺货、补货不足与安全库存失效问题。
- Weekly KPI Review Template | score=3 | 用于周会汇报的供应链核心 KPI 模板。

## Generated Files
- demo_report.md
- demo_result.json
- on_time_by_region.png
- inventory_risk.png