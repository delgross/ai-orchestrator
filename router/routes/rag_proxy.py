from fastapi import APIRouter, Response
from router.config import state, RAG_BASE
import logging

router = APIRouter()
logger = logging.getLogger("router.rag_proxy")

@router.get("/rag/health")
async def rag_health():
    """Proxy health check to RAG server."""
    try:
        target = f"{RAG_BASE}/health"
        r = await state.client.get(target, timeout=2.0)
        return Response(content=r.content, status_code=r.status_code, media_type=r.headers.get("content-type"))
    except Exception as e:
        logger.error(f"RAG health proxy failed: {e}")
        return Response(content='{"status":"offline"}', status_code=503, media_type="application/json")
