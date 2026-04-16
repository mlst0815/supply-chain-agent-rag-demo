from __future__ import annotations

import unittest

from scm_copilot.agent import SupplyChainCopilot


class SmokeTest(unittest.TestCase):
    def test_agent_returns_actions_and_docs(self) -> None:
        copilot = SupplyChainCopilot()
        result = copilot.run("华东仓SKU-C缺货导致订单延迟，给出建议和证据")

        self.assertTrue(result["actions"])
        self.assertTrue(result["retrieved_docs"])
        self.assertIn("stockout", result["focus_areas"])


if __name__ == "__main__":
    unittest.main()

