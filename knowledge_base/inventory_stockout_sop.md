title: Inventory Stockout Recovery SOP
keywords: 缺货, stockout, inventory, shortage, safety_stock, 补货, 安全库存, backorder
summary: 用于处理高风险 SKU 缺货、补货不足与安全库存失效问题。

当库存覆盖率小于 1.0 时，说明现货已经低于安全库存，需要优先进入缺货恢复流程。

推荐流程:

1. 识别 coverage ratio 最低的仓库和 SKU。
2. 如果存在跨仓库存不均衡，先做调拨而不是等待下一批采购。
3. 将低优先级订单延后，把现货优先分配给关键客户和高服务等级渠道。
4. 如果供应商 lead time 偏长，需要同步调整安全库存参数和补货节奏。

判断阈值:

- coverage ratio 小于 0.8 视为高危
- 缺货导致延迟订单大于 3 单，应启动专项复盘

