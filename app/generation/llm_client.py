import logging

import httpx

from app.config import settings
from app.errors import GenerationError

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def complete(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.0,
    max_tokens: int = 800,
) -> tuple[str, dict]:
    """Returns (text, usage). Raises GenerationError on failure."""
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {settings.openrouter_api_key}"}

    try:
        response = httpx.post(
            OPENROUTER_URL, json=payload, headers=headers, timeout=60.0
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(
            "llm request failed: %s | body=%s",
            exc.response.status_code,
            exc.response.text[:500],
        )
        raise GenerationError(f"{exc.response.status_code}: {exc.response.text[:200]}") from exc
    except httpx.HTTPError as exc:
        logger.error("llm request failed: %s", exc)
        raise GenerationError(str(exc)) from exc

    body = response.json()
    text = body["choices"][0]["message"]["content"]
    usage = body.get("usage", {})
    return text, usage