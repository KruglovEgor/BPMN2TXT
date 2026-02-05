from typing import Any, Dict

from pydantic import BaseModel


class TextToDiagramRequest(BaseModel):
    description: str


class DiagramToTextResponse(BaseModel):
    description: str
    pipeline: Dict[str, Any]


class TextToDiagramResponse(BaseModel):
    diagramCode: str


class ErrorResponse(BaseModel):
    error: str
