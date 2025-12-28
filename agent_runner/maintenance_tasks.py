
import asyncio
import logging
import os
import glob
from pathlib import Path
from agent_runner.state import AgentState
from common.constants import OBJ_MODEL

logger = logging.getLogger("agent_runner.maintenance")

async def code_janitor_task(state: AgentState):
    """
    Weekly Code Janitor:
    - Scans Python files in the workspace.
    - Sends them to 'finalizer_model' (High-End) for review.
    - Generates a 'CODE_AUDIT.md' file with improvements.
    """
    logger.info("🧹 Code Janitor: Starting scan...")
    
    # 1. Identify Target Files
    # Limit to avoid scanning huge venv folders. Scan specific active dirs.
    target_dirs = ["agent_runner", "router", "common"]
    root = Path(os.getcwd()) / "ai"
    files_to_scan = []
    
    for d in target_dirs:
        p = root / d
        if p.exists():
            # Get .py files, ignore __init__
            files = list(p.glob("*.py"))
            files_to_scan.extend([f for f in files if "__init__" not in f.name])
            
    # Randomly select a few files per run to avoid blowing budget? 
    # Or scan all but only process modified ones?
    # Simple strategy: Scan 3 random files per run to keep it continuous and cheap.
    import random
    if not files_to_scan:
        logger.info("Code Janitor: No files found.")
        return
        
    # Pick 2 files
    selection = random.sample(files_to_scan, min(2, len(files_to_scan)))
    logger.info(f"Code Janitor: Reviewing {', '.join([f.name for f in selection])}")
    
    audit_notes = []
    
    client = await state.get_http_client()
    
    for file_path in selection:
        try:
            code = file_path.read_text("utf-8")
            if len(code) > 20000: continue # Skip huge files
            
            prompt = (
                f"Review the following Python code ({file_path.name}). "
                "Identify 1 critical bug or 1 meaningful refactor opportunity. "
                "Ignore style nitpicks. Focus on performance, security, or logic.\n"
                "Return valid Markdown bullet points.\n\n"
                f"```python\n{code}\n```"
            )
            
            payload = {
                "model": state.finalizer_model or "ollama:mistral:latest", # Use H100/GPT-4o
                "messages": [{"role": "user", "content": prompt}]
            }
            
            url = f"{state.gateway_base}/v1/chat/completions"
            resp = await client.post(url, json=payload, timeout=60.0)
            
            if resp.status_code == 200:
                review = resp.json()["choices"][0]["message"]["content"]
                audit_notes.append(f"### {file_path.name}\n{review}\n")
                
        except Exception as e:
            logger.error(f"Janitor failed on {file_path.name}: {e}")
            
    # Append to Audit Log
    if audit_notes:
        audit_file = root / "docs" / "JANITOR_AUDIT.md"
        audit_file.parent.mkdir(exist_ok=True)
        
        timestamp = asyncio.get_event_loop().time()
        with open(audit_file, "a") as f:
            f.write(f"\n## Scan {timestamp}\n")
            f.write("\n".join(audit_notes))
            
        logger.info(f"Code Janitor: Saved notes to {audit_file}")

async def auto_tagger_task(state: AgentState):
    """
    Image Captioning Agent:
    - Scans 'agent_fs_root/uploads' or RAG ingest dir.
    - Looks for images without a matching .caption.txt
    - Uses 'vision_model' to generate tags/captions.
    """
    logger.info("🏷️ Auto-Tagger: Scanning for untagged images...")
    
    # Target Directory (Ingest or Uploads?)
    # Let's assume Uploads for now, as that's where raw assets live before RAG
    # Or better: The RAG Ingest Dir
    ingest_dir = Path(os.getenv("RAG_INGEST_DIR", os.path.expanduser("~/ai/rag_ingest")))
    if not ingest_dir.exists(): return
    
    # Extended list of image extensions
    image_exts = {".jpg", ".jpeg", ".png", ".webp"}
    
    # Find images
    images = [p for p in ingest_dir.iterdir() if p.suffix.lower() in image_exts]
    
    processed = 0
    limit = 5 # Rate limit to avoid blowing budget in one run
    
    client = await state.get_http_client()
    
    for img_path in images:
        if processed >= limit: break
        
        caption_path = img_path.with_suffix(img_path.suffix + ".txt")
        if caption_path.exists(): continue # Already tagged
        
        logger.info(f"Tagging {img_path.name}...")
        
        try:
            import base64
            b64_img = base64.b64encode(img_path.read_bytes()).decode('utf-8')
            
            # Simple "Describe" prompt
            payload = {
                "model": state.vision_model, # High-End Vision
                "messages": [
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": "What is in this image? Provide search keywords and a brief description for a database."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                        ]
                    }
                ]
            }
            
            url = f"{state.gateway_base}/v1/chat/completions"
            resp = await client.post(url, json=payload, timeout=60.0)
            
            if resp.status_code == 200:
                caption = resp.json()["choices"][0]["message"]["content"]
                
                # Save sidecar
                caption_path.write_text(caption, encoding="utf-8")
                
                # TODO: Ideally verify if RAG index needs update, but RAG likely picks up text files automatically
                processed += 1
                logger.info(f"Tagged {img_path.name}")
                
        except Exception as e:
            logger.error(f"Tagging failed for {img_path.name}: {e}")

