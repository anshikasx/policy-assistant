from functools import lru_cache

from fastapi import APIRouter, Depends

from app.config import settings
from app.models import QueryRequest, QueryResponse
from app.services.query_service import QueryService

router = APIRouter()


@lru_cache
def get_query_service() -> QueryService:
    return QueryService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


@router.post("/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    service: QueryService = Depends(get_query_service),
) -> QueryResponse:
    return service.answer(request)