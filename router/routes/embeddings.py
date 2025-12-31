import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from common.constants import PREFIX_OLLAMA
from router.config import state, OLLAMA_BASE, MAX_REQUEST_BODY_BYTES
from router.utils import join_url, parse_model_string
from router.providers import provider_headers
from router.middleware import require_auth

router = APIRouter(tags=["embeddings"])
logger = logging.getLogger("router.embeddings")

@router.post("/v1/embeddings")
async def embeddings(request: Request):
    require_auth(request)
    
    # Check body size
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Request body too large")

    body = await request.json()
    model = body.get("model", "")
    logger.debug(f"ROUTER Received Model: {model}")
    prefix, model_id = parse_model_string(model, default_prefix="")
    
    # 0. Default / Fallback Handling
    if not prefix or model == "default":
        logger.info(f"Using default embedding model '{state.default_embedding_model}' for request '{model}'")
        model = state.default_embedding_model
        prefix, model_id = parse_model_string(model)
        logger.debug(f"Parsed Prefix: {prefix}, ID: {model_id}")
    
    # Update body to use the stripped model ID
    body["model"] = model_id

    # 1. Ollama 
    if prefix == PREFIX_OLLAMA or not prefix:
        url = join_url(OLLAMA_BASE, "/v1/embeddings")
        try:
            r = await state.client.post(url, json=body)
            if r.status_code >= 400:
                raise HTTPException(status_code=r.status_code, detail=r.text)
            return JSONResponse(r.json())
        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    # 2. Providers
    prov = state.providers.get(prefix)
    if prov:
        if not state.circuit_breakers.is_allowed(prefix):
            raise HTTPException(status_code=503, detail=f"Provider '{prefix}' is currently disabled")

        url = join_url(prov.base_url, prov.embeddings_path)
        try:
            r = await state.client.post(url, headers=provider_headers(prov), json=body)
            if r.status_code >= 400:
                state.circuit_breakers.record_failure(prefix)
                raise HTTPException(status_code=r.status_code, detail=r.text)
            state.circuit_breakers.record_success(prefix)
            return JSONResponse(r.json())
        except Exception as e:
            state.circuit_breakers.record_failure(prefix)
            logger.error(f"Provider {prefix} embedding failed: {e}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))
            
    raise HTTPException(status_code=404, detail=f"Provider not found for embedding model: {model}")
