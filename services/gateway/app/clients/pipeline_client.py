from typing import Any, Dict

import httpx
from fastapi import HTTPException, UploadFile

from app.core.config import settings


async def call_pipeline(image: UploadFile) -> Dict[str, Any]:
    if image is None or not image.filename:
        raise HTTPException(status_code=400, detail="Image file is required.")

    files = {
        "image": (
            image.filename,
            await image.read(),
            image.content_type or "application/octet-stream",
        )
    }

    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        response = await client.post(f"{settings.pipeline_url}/api/v1/convert", files=files)

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Pipeline error: {response.status_code}")

    try:
        payload = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Pipeline returned non-JSON.") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=502, detail="Pipeline JSON must be an object.")

    return payload
