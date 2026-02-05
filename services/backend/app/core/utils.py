def extract_code_block(text: str) -> str:
    if "```" not in text:
        return text.strip()

    parts = text.split("```")
    if len(parts) < 2:
        return text.strip()

    code = parts[1]
    lines = code.splitlines()
    if lines and lines[0].strip().lower().startswith("mermaid"):
        lines = lines[1:]

    return "\n".join(lines).strip()
