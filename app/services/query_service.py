import logging
import re
import time

from app.config import settings
from app.generation.llm_client import complete
from app.generation.prompts import SYSTEM_PROMPT, build_user_prompt
from app.ingestion.embedder import embed_query
from app.models import Citation, QueryRequest, QueryResponse
from app.retrieval.vector_store import get_client, search

logger = logging.getLogger(__name__)

TOP_K = 5
CITATION_PATTERN = re.compile(r"\[(\d+)\]")


class QueryService:
    def __init__(self) -> None:
        self.client = get_client()

    def answer(self, request: QueryRequest) -> QueryResponse:
        start = time.perf_counter()

        points = search(self.client, embed_query(request.question), top_k=TOP_K)
        passages = [p.payload or {} for p in points]

        text, usage = complete(
            SYSTEM_PROMPT, build_user_prompt(request.question, passages)
        )

        citations = self._extract_citations(text, passages)
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        logger.info(
            "query_handled",
            extra={
                "extra_fields": {
                    "model": settings.llm_model,
                    "question": request.question,
                    "retrieved_chunks": [p.get("chunk_id") for p in passages],
                    "cited_chunks": [c.chunk_id for c in citations],
                    "total_tokens": usage.get("total_tokens"),
                    "cost_usd": usage.get("cost", 0.0),
                    "latency_ms": elapsed_ms,
                    "refused": "INSUFFICIENT_CONTEXT" in text,
                }
            },
        )

        return QueryResponse(
            answer=text, citations=citations, latency_ms=elapsed_ms
        )

    def _extract_citations(
        self, text: str, passages: list[dict]
    ) -> list[Citation]:
        seen: set[int] = set()
        citations: list[Citation] = []
        for match in CITATION_PATTERN.finditer(text):
            idx = int(match.group(1))
            if idx in seen or not (1 <= idx <= len(passages)):
                continue
            seen.add(idx)
            p = passages[idx - 1]
            citations.append(
                Citation(
                    chunk_id=p.get("chunk_id", ""),
                    source_file=p.get("source_file", ""),
                    section_title=p.get("section_title"),
                )
            )
        return citations