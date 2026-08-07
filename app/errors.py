class AppError(Exception):
    """Base for errors we raise deliberately."""

    status_code = 500
    message = "Internal error"


class RetrievalError(AppError):
    status_code = 503
    message = "Retrieval backend unavailable"


class GenerationError(AppError):
    status_code = 503
    message = "Language model unavailable"