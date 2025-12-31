import time
import logging
from typing import Any, Dict
from fastapi import HTTPException
from router.config import state, RAG_BASE, RAG_QUERY_PATH, PREFIX_RAG, OBJ_CHAT_COMPLETION, ROLE_ASSISTANT
from router.utils import join_url

logger = logging.getLogger("router.rag")

async def call_rag(model: str, body: Dict[str, Any]) -> Dict[str, Any]:
    url = join_url(RAG_BASE, RAG_QUERY_PATH)
    payload = {
        "model": model,
        "messages": body.get("messages", []),
    }
    if not state.circuit_breakers.is_allowed("rag"):
        raise HTTPException(status_code=503, detail="RAG service is currently disabled via circuit breaker")

    try:
        r = await state.client.post(url, json=payload, headers={"Content-Type": "application/json"})
        if r.status_code >= 400:
            state.circuit_breakers.record_failure("rag")
            logger.error(f"RAG backend error: {r.status_code}")
            raise HTTPException(status_code=r.status_code, detail=r.text)
        
        state.circuit_breakers.record_success("rag")
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"answer": r.text}
    except Exception as e:
        state.circuit_breakers.record_failure("rag")
        logger.error(f"RAG call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    content = data.get("answer") if isinstance(data, dict) else ""
    
    return {
        "id": f"rag-{int(time.time())}",
        "object": OBJ_CHAT_COMPLETION,
        "created": int(time.time()),
        "model": f"{PREFIX_RAG}:{model}",
        "choices": [
            {"index": 0, "message": {"role": ROLE_ASSISTANT, "content": content}, "finish_reason": "stop"}
        ],
        "rag_context": data.get("context") if isinstance(data, dict) else None,
    }
