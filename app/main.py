import time

from fastapi import FastAPI

from app.config import settings
from app.models import QueryRequest, QueryResponse

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    start = time.perf_counter()
    answer = f"Not implemented yet. You asked: {request.question}"
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return QueryResponse(answer=answer, citations=[], latency_ms=elapsed_ms)