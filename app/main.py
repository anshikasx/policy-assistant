import logging
import truststore

truststore.inject_into_ssl()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import settings
from app.errors import AppError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.exception_handler(AppError)
def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    logging.warning("app error: %s", exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "detail": str(exc) or None},
    )