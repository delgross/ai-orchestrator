"""
Lightweight response quality evaluation for chat completions.
Adds simple, fast checks without modifying content.
"""
from typing import Dict, Any, List, Optional


def _extract_content(completion: Dict[str, Any]) -> str:
    # Handles both direct OpenAI-style and nested "result"
    choices = completion.get("choices")
    if not choices and isinstance(completion.get("result"), dict):
        choices = completion["result"].get("choices")

    if choices and isinstance(choices, list) and choices:
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            return content
    return ""


def evaluate_completion(completion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a dict with quality metadata and warnings.
    Does not mutate the original completion.
    """
    warnings: List[str] = []
    content = _extract_content(completion)

    if not completion.get("choices") and not (completion.get("result") or {}).get("choices"):
        warnings.append("missing_choices")

    if not content.strip():
        warnings.append("empty_content")

    finish_reason: Optional[str] = None
    choices = completion.get("choices")
    if choices and choices:
        finish_reason = choices[0].get("finish_reason")
    elif isinstance(completion.get("result"), dict):
        r_choices = completion["result"].get("choices")
        if r_choices:
            finish_reason = r_choices[0].get("finish_reason")

    if finish_reason is None:
        warnings.append("missing_finish_reason")

    return {
        "has_choices": "missing_choices" not in warnings,
        "has_content": "empty_content" not in warnings,
        "content_length": len(content),
        "finish_reason": finish_reason,
        "warnings": warnings,
    }
