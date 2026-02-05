from dataclasses import dataclass
import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(filename=".env", usecwd=True))


@dataclass(frozen=True)
class Settings:
    pipeline_url: str = os.getenv("PIPELINE_URL", "http://pipeline:5000").rstrip("/")
    llm_url: str = os.getenv("LLM_URL", "http://llm-gpu:8001").rstrip("/")
    llm_model: str = os.getenv("LLM_MODEL", "local-model")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    http_timeout: float = float(os.getenv("HTTP_TIMEOUT", "60"))
    prompt_bpmn_to_text: str = os.getenv(
        "PROMPT_BPMN_TO_TEXT",
        "You are given BPMN extraction JSON. It may be noisy or incomplete. "
        "Write a concise, human-readable description of the process in plain text. "
        "Do not mention JSON.\n\nJSON:\n{payload}\n",
    )
    prompt_text_to_mermaid: str = os.getenv(
        "PROMPT_TEXT_TO_MERMAID",
        "Convert the following process description into Mermaid flowchart code. "
        "Return only Mermaid code, no fences or explanations.\n\nDescription:\n{description}\n",
    )


settings = Settings()
