from typing import Any, Dict, List


def normalize_pipeline_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    cleaned: Dict[str, Any] = {}

    for key in ("participants", "elements", "flows"):
        items = payload.get(key)
        if isinstance(items, list):
            cleaned[key] = _clean_items(items)

    for key, value in payload.items():
        if key in {"participants", "elements", "flows", "processing_time_ms"}:
            continue
        cleaned[key] = value

    return cleaned


def _clean_items(items: List[Any]) -> List[Any]:
    cleaned_items: List[Any] = []

    for item in items:
        if not isinstance(item, dict):
            cleaned_items.append(item)
            continue

        cleaned_item: Dict[str, Any] = {}
        for key, value in item.items():
            if isinstance(value, str):
                value = _clean_text(value)

            if key == "name" and value == "":
                continue

            cleaned_item[key] = value

        cleaned_items.append(cleaned_item)

    return cleaned_items


def _clean_text(value: str) -> str:
    return " ".join(value.split())
