from __future__ import annotations

import argparse
from pathlib import Path

from scm_copilot.agent import SupplyChainCopilot
from scm_copilot.reporting import export_artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Supply chain Agent + RAG demo for internship portfolio."
    )
    parser.add_argument(
        "--question",
        default="华东仓SKU-C连续缺货并导致订单延迟，请给我一份处理建议和证据",
        help="Business question for the copilot.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of retrieved knowledge base documents.",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip Markdown/JSON/chart export.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    copilot = SupplyChainCopilot()
    result = copilot.run(args.question, top_k=args.top_k)

    print("=== Supply Chain Agent RAG Demo ===")
    print(f"Question: {result['question']}")
    print(f"Focus Areas: {', '.join(result['focus_areas'])}")
    print()
    print("Summary:")
    print(result["summary"])
    print()
    print("Key Actions:")
    for index, action in enumerate(result["actions"], start=1):
        print(f"{index}. {action}")
    print()
    print("Evidence:")
    for item in result["evidence"]:
        print(f"- {item}")
    print()
    print("Retrieved Docs:")
    for doc in result["retrieved_docs"]:
        print(f"- {doc['title']} (score={doc['score']})")

    if not args.no_report:
        artifacts = export_artifacts(
            result=result,
            orders=copilot.orders,
            inventory=copilot.inventory,
        )
        print()
        print("Artifacts:")
        for label, path in artifacts.items():
            if isinstance(path, list):
                for value in path:
                    print(f"- {label}: {Path(value)}")
            else:
                print(f"- {label}: {Path(path)}")


if __name__ == "__main__":
    main()

