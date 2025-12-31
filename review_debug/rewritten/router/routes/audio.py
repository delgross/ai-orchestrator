import json
import logging
from fastapi import APIRouter, Request, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from router.config import state
from router.utils import join_url
from router.providers import provider_headers, retry_policy
from router.middleware import require_auth

router = APIRouter(tags=["audio"])
logger = logging.getLogger("router.audio")

@router.post("/v1/audio/transcriptions")
async def audio_transcriptions(request: Request):
    """Proxy audio transcriptions to OpenAI provider."""
    require_auth(request)
    
    # 1. Identify OpenAI Provider
    prov = state.providers.get("openai")
    if not prov:
        # Try finding one
        for p_name, p in state.providers.items():
            if "openai.com" in p.base_url:
                prov = p
                break
    
    if not prov:
        raise HTTPException(status_code=503, detail="No OpenAI provider configured for audio")
        
    url = join_url(prov.base_url, "/audio/transcriptions")
    
    try:
        form = await request.form()
        
        # httpx needs a specific files/data structure
        files = []
        data = {}
        
        for field_name, value in form.items():
            if isinstance(value, UploadFile):
                # It's a file
                content = await value.read()
                files.append((field_name, (value.filename, content, value.content_type)))
            else:
                # It's a form field
                data[field_name] = value
                
        # 3. Call Upstream with Retry
        @retry_policy
        async def fetch_audio():
            r = await state.client.post(url, headers=provider_headers(prov), data=data, files=files, timeout=60.0)
            if r.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate Limit")
            if r.status_code >= 400:
                raise HTTPException(status_code=r.status_code, detail=r.text)
            return r

        r = await fetch_audio()
        body = r.content
        
        return JSONResponse(json.loads(body), status_code=r.status_code)
            
    except Exception as e:
        logger.error(f"Audio transcription failed: {e}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))
