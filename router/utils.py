import json
from typing import Any, Dict, List, Optional, Tuple
from contextlib import asynccontextmanager
from fastapi import HTTPException
from common.message_utils import extract_text_content

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
        if "content" in mm:
            raw_content = mm.get("content")
            if raw_content is None:
                mm["content"] = ""
            else:
                # Normalize multimodal/list content to plain text to protect downstream `.strip()` calls
                mm["content"] = extract_text_content(raw_content)
        out.append(mm)
    return out

@asynccontextmanager
async def log_time(operation_name: str, level: int = 20):  # 20 is logging.INFO
    import time
    import logging
    logger = logging.getLogger("router.perf")
    t0 = time.time()
    try:
        yield
    finally:
        duration = time.time() - t0
        logger.log(level, f"PERF: {operation_name} completed in {duration:.4f}s")

def parse_model_string(model: str, default_prefix: str = "ollama") -> Tuple[str, str]:
    if not isinstance(model, str) or not model.strip():
        raise HTTPException(status_code=400, detail="model must be a non-empty string")
    s = model.strip()
    if ":" in s:
        prefix, rest = s.split(":", 1)
        return prefix.strip(), rest.strip()
    return default_prefix, s
