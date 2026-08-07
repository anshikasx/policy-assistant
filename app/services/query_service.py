import logging
import time

from app.models import Citation, QueryRequest, QueryResponse

logger = logging.getLogger(__name__)


class QueryService:
    """Answers questions. Retrieval + generation arrive on day 5."""

    def answer(self, request: QueryRequest) -> QueryResponse:
        start = time.perf_counter()

        answer = f"Not implemented yet. You asked: {request.question}"
        citations: list[Citation] = []

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "query handled",
            extra={"question": request.question, "latency_ms": elapsed_ms},
        )
        return QueryResponse(
            answer=answer, citations=citations, latency_ms=elapsed_ms
        )