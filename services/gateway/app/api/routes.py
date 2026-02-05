import json
from typing import Dict

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.clients.llm_client import call_llm
from app.clients.pipeline_client import call_pipeline
from app.core.config import settings
from app.core.utils import extract_code_block
from app.schemas import (
    DiagramToTextResponse,
    ErrorResponse,
    TextToDiagramRequest,
    TextToDiagramResponse,
)

router = APIRouter()


@router.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@router.post(
    "/api/v1/diagram-to-text",
    response_model=DiagramToTextResponse,
    responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
    summary="Convert diagram image to text",
)
async def diagram_to_text(image: UploadFile = File(...)) -> DiagramToTextResponse:
    pipeline_payload = await call_pipeline(image)
    prompt_payload = json.dumps(pipeline_payload, ensure_ascii=False)
    # Replace only the explicit placeholder to avoid KeyError from other braces in the template.
    prompt = settings.prompt_bpmn_to_text.replace("{payload}", prompt_payload)
    description = await call_llm(prompt)
    return DiagramToTextResponse(description=description, pipeline=pipeline_payload)


@router.post(
    "/api/v1/text-to-diagram",
    response_model=TextToDiagramResponse,
    responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
    summary="Convert text to Mermaid",
)
async def text_to_diagram(payload: TextToDiagramRequest) -> TextToDiagramResponse:
    description = payload.description.strip()
    if not description:
        raise HTTPException(status_code=400, detail="Description is required.")

    prompt = settings.prompt_text_to_mermaid.replace("{description}", description)
    diagram_code = await call_llm(prompt)
    diagram_code = extract_code_block(diagram_code)
    return TextToDiagramResponse(diagramCode=diagram_code)
