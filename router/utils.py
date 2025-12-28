import json
import time
from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException
from common.error_utils import get_error_message as _get_error_message

def parse_default_headers(env_str: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    env_str = env_str.strip()
    if not env_str:
        return out
    for part in env_str.split(","):
        part = part.strip()
        if not part or ":" not in part:
            continue
        k, v = part.split(":", 1)
        out[k.strip()] = v.strip()
    return out

def merge_headers(*dicts: Optional[Dict[str, str]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for d in dicts:
        if d:
            out.update(d)
    return out

def join_url(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")

def sse_line(obj: Any) -> bytes:
    return (f"data: {json.dumps(obj, ensure_ascii=False)}\n\n").encode("utf-8")

def estimate_token_count(text: str) -> int:
    """Conservative estimate: ~1.2 tokens per character."""
    return int(len(text) * 1.2)

def sanitize_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for m in messages:
        mm = dict(m)
        if "content" in mm and mm["content"] is None:
            mm["content"] = ""
        out.append(mm)
    return out

def parse_model_string(model: str, default_prefix: str = "ollama") -> Tuple[str, str]:
    if not isinstance(model, str) or not model.strip():
        raise HTTPException(status_code=400, detail="model must be a non-empty string")
    s = model.strip()
    if ":" in s:
        prefix, rest = s.split(":", 1)
        return prefix.strip(), rest.strip()
    return default_prefix, s
