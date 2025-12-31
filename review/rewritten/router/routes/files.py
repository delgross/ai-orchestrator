import os
import uuid
import shutil
import time
import logging
from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

from common.unified_tracking import track_event, EventCategory, EventSeverity
from router.config import state, FS_ROOT
from router.middleware import require_auth

router = APIRouter(tags=["files"])
logger = logging.getLogger("router.files")

@router.post("/v1/files")
async def upload_file(request: Request, file: UploadFile = File(...), purpose: str = Form(...)):
    """Upload a file to the agent's sandbox (OpenAI Compatible)."""
    require_auth(request)
    
    upload_dir = os.path.join(FS_ROOT, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_id = f"file-{uuid.uuid4().hex[:12]}"
    # Sanitize filename
    orig_name = file.filename or "unknown"
    safe_name = "".join([c for c in orig_name if c.isalnum() or c in "._-"]).strip()
    stored_name = f"{file_id}_{safe_name}"
    stored_path = os.path.join(upload_dir, stored_name)
    
    try:
        with open(stored_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_size = os.path.getsize(stored_path)
        
        logger.info(f"📁 File uploaded: {file.filename} -> {stored_path} ({file_size} bytes)")
        track_event("file_uploaded", severity=EventSeverity.INFO, category=EventCategory.SYSTEM, 
                    message=f"File uploaded: {file.filename}", metadata={"file_id": file_id, "size": file_size})
        
        return {
            "id": file_id,
            "object": "file",
            "bytes": file_size,
            "created_at": int(time.time()),
            "filename": file.filename,
            "purpose": purpose,
            "status": "processed",
            "path": stored_path 
        }
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/v1/files")
async def list_files(request: Request):
    """List uploaded files."""
    require_auth(request)
    upload_dir = os.path.join(FS_ROOT, "uploads")
    if not os.path.exists(upload_dir):
        return {"object": "list", "data": []}
        
    data = []
    for f in os.listdir(upload_dir):
        if f.startswith("file-") and "_" in f:
            path = os.path.join(upload_dir, f)
            stat = os.stat(path)
            f_id, name = f.split("_", 1)
            data.append({
                "id": f_id,
                "object": "file",
                "bytes": stat.st_size,
                "created_at": int(stat.st_mtime),
                "filename": name,
                "purpose": "assistants",
                "status": "processed"
            })
            
    return {"object": "list", "data": data}

@router.get("/v1/files/{file_id}")
async def retrieve_file(file_id: str, request: Request):
    """Retrieve metadata for a file."""
    require_auth(request)
    upload_dir = os.path.join(FS_ROOT, "uploads")
    if not os.path.exists(upload_dir):
         raise HTTPException(status_code=404, detail="Upload directory not found")
         
    for f in os.listdir(upload_dir):
        if f.startswith(file_id):
            path = os.path.join(upload_dir, f)
            stat = os.stat(path)
            _, name = f.split("_", 1)
            return {
                "id": file_id,
                "object": "file",
                "bytes": stat.st_size,
                "created_at": int(stat.st_mtime),
                "filename": name,
                "purpose": "assistants",
                "status": "processed"
            }
    raise HTTPException(status_code=404, detail="File not found")

@router.get("/v1/files/{file_id}/content")
async def retrieve_file_content(file_id: str, request: Request):
    """Retrieve the actual content of a file."""
    require_auth(request)
    upload_dir = os.path.join(FS_ROOT, "uploads")
    if not os.path.exists(upload_dir):
         raise HTTPException(status_code=404, detail="Upload directory not found")
         
    for f in os.listdir(upload_dir):
        if f.startswith(file_id):
            return FileResponse(os.path.join(upload_dir, f))
    raise HTTPException(status_code=404, detail="File not found")
