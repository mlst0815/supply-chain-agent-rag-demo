from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .config import KB_DIR


TOKEN_PATTERN = re.compile(r"[a-z0-9_]+|[\u4e00-\u9fff]+", re.IGNORECASE)
META_KEYS = {"title", "keywords", "summary"}


@dataclass
class KnowledgeDocument:
    path: Path
    title: str
    keywords: list[str]
    summary: str
    content: str


def _extract_terms(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)]


def load_knowledge_base(kb_dir: Path | None = None) -> list[KnowledgeDocument]:
    documents: list[KnowledgeDocument] = []
    for path in sorted((kb_dir or KB_DIR).glob("*.md")):
        meta: dict[str, str] = {}
        body_lines: list[str] = []
        in_meta = True

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            if in_meta and ":" in raw_line:
                key, value = raw_line.split(":", 1)
                key = key.strip().lower()
                if key in META_KEYS:
                    meta[key] = value.strip()
                    continue
            in_meta = False
            body_lines.append(raw_line)

        documents.append(
            KnowledgeDocument(
                path=path,
                title=meta.get("title", path.stem),
                keywords=[item.strip().lower() for item in meta.get("keywords", "").split(",") if item.strip()],
                summary=meta.get("summary", ""),
                content="\n".join(body_lines).strip(),
            )
        )
    return documents


def retrieve_documents(
    query: str,
    documents: list[KnowledgeDocument],
    top_k: int = 3,
) -> list[dict[str, object]]:
    query_terms = _extract_terms(query)
    query_text = query.lower()
    scored: list[dict[str, object]] = []

    for doc in documents:
        keyword_hits = [keyword for keyword in doc.keywords if keyword in query_text]
        content_hits = [term for term in query_terms if term and term in doc.content.lower()]
        score = len(keyword_hits) * 3 + len(set(content_hits))
        scored.append(
            {
                "title": doc.title,
                "summary": doc.summary,
                "path": str(doc.path),
                "score": score,
                "matched_keywords": keyword_hits,
            }
        )

    ranked = sorted(scored, key=lambda item: item["score"], reverse=True)
    ranked = [item for item in ranked if item["score"] > 0] or ranked
    return ranked[:top_k]

