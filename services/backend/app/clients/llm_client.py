from typing import Any, Dict
import os

import httpx
from fastapi import HTTPException

from app.core.config import settings


async def call_llm(prompt: str) -> str:
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is empty.")

    headers = {"Content-Type": "application/json"}

    payload: Dict[str, Any] = {
        "model": settings.llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_tokens,
    }

    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        response = await client.post(f"{settings.llm_url}/v1/chat/completions", json=payload, headers=headers)

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"LLM error: {response.status_code}")

    data = response.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="LLM response format unexpected.") from exc

    return (content or "").strip()
