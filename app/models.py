from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    source_file: str
    section_title: str | None = None


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation] = []
    latency_ms: int = 0

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None