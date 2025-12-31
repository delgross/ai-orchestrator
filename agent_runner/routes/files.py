import logging
import os
import time
import glob
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, Form, HTTPException

from agent_runner.agent_runner import get_shared_state

router = APIRouter()
logger = logging.getLogger("agent_runner.files")

@router.post("/admin/upload")
async def upload_file_endpoint(
    file: UploadFile = File(None),
    content: str = Form(None),
    filename: str = Form(None)
):
    """
    Handle uploads from the dashboard (Paste-to-Upload).
    Accepts specific file uploads OR raw text content.
    Saves to WORKSPACE_ROOT/uploads/.
    """
    state = get_shared_state()
    try:
        import aiofiles
        
        # Ensure uploads dir exists
        raw_root = state.agent_fs_root
        if raw_root.startswith("~"):
            raw_root = os.path.expanduser(raw_root)
            
        upload_dir = Path(raw_root) / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        final_filename = ""
        file_path = None
        
        # Case 1: File Upload
        if file:
            timestamp = int(time.time())
            # Sanitize filename (basic)
            safe_name = "".join([c for c in file.filename if c.isalpha() or c.isdigit() or c in (' ','.','_','-')]).rstrip()
            final_filename = f"{timestamp}_{safe_name}"
            file_path = upload_dir / final_filename
            
            async with aiofiles.open(file_path, 'wb') as out_file:
                content_bytes = await file.read()
                await out_file.write(content_bytes)

        # Case 2: Raw Text (Pasted Content)
        elif content and filename:
            final_filename = filename
            file_path = upload_dir / final_filename
            async with aiofiles.open(file_path, 'w') as out_file:
                await out_file.write(content)
        
        else:
            return {"ok": False, "error": "No file or content provided"}

        logger.info(f"Saved upload: {file_path}")
        return {
            "ok": True, 
            "message": "Upload successful", 
            "filename": final_filename,
            "path": str(file_path),
            "size": file_path.stat().st_size
        }

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return {"ok": False, "error": str(e)}

@router.get("/admin/docs/list")
async def list_documentation_files():
    """List markdown files in the ai/docs directory."""
    docs_dir = os.path.expanduser("~/Sync/Antigravity/ai/docs")
    if not os.path.exists(docs_dir):
        try:
            os.makedirs(docs_dir, exist_ok=True)
            # Create a README
            with open(f"{docs_dir}/README.md", "w") as f:
                f.write("# Documentation\n\nDrop markdown files here to view them in the dashboard.")
        except: pass
        
    try:
        files = glob.glob(f"{docs_dir}/*.md")
        return {"ok": True, "files": [{"name": os.path.basename(f), "path": f} for f in files]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/admin/docs/read")
async def read_documentation_file(path: str):
    # Security check: must be in docs dir
    docs_dir = os.path.expanduser("~/Sync/Antigravity/ai/docs")
    abs_path = os.path.abspath(path)
    if not abs_path.startswith(docs_dir):
        return {"ok": False, "error": "Access denied"}
        
    try:
        with open(abs_path, 'r') as f:
            return {"ok": True, "content": f.read()}
    except Exception as e:
        return {"ok": False, "error": str(e)}
