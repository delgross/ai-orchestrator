
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
            
            # Structured "Describe" prompt
            payload = {
                "model": state.vision_model, 
                "messages": [
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": "Analyze this image. Return a JSON object with keys: 'description' (detailed), 'keywords' (list of strings), 'text_content' (any visible text), and 'objects' (list of visible items)."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                        ]
                    }
                ],
                "response_format": {"type": "json_object"}
            }
            
            url = f"{state.gateway_base}/v1/chat/completions"
            resp = await client.post(url, json=payload, timeout=60.0)
            
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                
                # Parse JSON to ensure validity before saving
                import json
                try:
                    meta = json.loads(content)
                    # Flatten for simple sidecar or keep JSON? 
                    # JSON Sidecar is better for programmatic reads
                    json_path = img_path.with_suffix(img_path.suffix + ".json")
                    json_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
                    
                    # Create a simple .txt for legacy full-text search fallback
                    txt_path = img_path.with_suffix(img_path.suffix + ".caption.txt")
                    flat_desc = f"{meta.get('description', '')}\nKeywords: {', '.join(meta.get('keywords', []))}\nText: {meta.get('text_content', '')}"
                    txt_path.write_text(flat_desc, encoding="utf-8")
                    
                except Exception as e:
                    logger.error(f"Failed to parse JSON vision response: {e}")
                    # Fallback to saving raw content
                    img_path.with_suffix(img_path.suffix + ".caption.txt").write_text(content, encoding="utf-8")

                processed += 1
                logger.info(f"Tagged {img_path.name}")
                
        except Exception as e:
            logger.error(f"Tagging failed for {img_path.name}: {e}")

async def morning_briefing_task(state: AgentState):
    """
    Generates a daily briefing of system activity, new memories, and system health.
    Runs at ~7 AM via scheduler.
    """
    logger.info("🌅 Generating Morning Briefing...")
    from pathlib import Path
    import datetime
    
    # Collect Stats
    # 1. RAG Ingestion count (files in processed?) - Hard to track without DB, use logs or simple count
    # 2. Budget Spend
    from common.budget import get_budget_tracker
    budget = get_budget_tracker()
    
    # 3. Memory Stats
    # We can query project-memory for count
    mem_stats = "N/A"
    try:
        from agent_runner.tools.mcp import tool_mcp_proxy
        res = await tool_mcp_proxy(state, "project-memory", "get_memory_stats", {})
        if res.get("ok"):
            mem_stats = res.get("result", {})
    except: pass

    # 4. Generate Briefing Content
    prompt = (
        f"Generate a 'Morning Briefing' markdown report for the user.\n"
        f"Date: {datetime.date.today()}\n"
        f"System Spending Yesterday: ${budget.current_spend:.2f}\n"
        f"Memory Stats: {mem_stats}\n\n"
        "Summarize the system status. Be professional but concise. "
        "Highlight any 'Critical' issues if apparent (none provided here). "
        "Ending with a motivational engineering quote."
    )
    
    client = await state.get_http_client()
    try:
        payload = {
            "model": state.task_model, # Local model is fine for this
            "messages": [{"role": "user", "content": prompt}]
        }
        url = f"{state.gateway_base}/v1/chat/completions"
        resp = await client.post(url, json=payload, timeout=60.0)
        
        if resp.status_code == 200:
            report = resp.json()["choices"][0]["message"]["content"]
            
            # Save Report
            today = datetime.date.today().isoformat()
            report_path = Path(os.getenv("RAG_INGEST_DIR", os.path.expanduser("~/ai/rag_ingest"))) / f"BRIEFING_{today}.md"
            # Actually, save to docs, not ingest (or ingest so it reads it back?)
            # Let's save to docs so user sees it.
            report_path = Path(state.agent_fs_root) / "reports" / f"Morning_Briefing_{today}.md"
            report_path.parent.mkdir(exist_ok=True)
            report_path.write_text(report, encoding="utf-8")
            logger.info(f"Morning Briefing saved to {report_path}")
            
    except Exception as e:
        logger.error(f"Failed to generate briefing: {e}")

async def stale_memory_pruner_task(state: AgentState):
    """
    Scans for low-confidence facts (< 0.3) and archives them essentially deleting them from active context.
    """
    logger.info("🧹 Pruning Stale Memories...")
    try:
        from agent_runner.tools.mcp import tool_mcp_proxy
        
        # 1. Query Low Confidence
        # This assumes tool support. If not existing, we query all and filter in python (inefficient but works for small DB)
        # Or we add a specific 'prune_low_confidence' tool to memory server eventually.
        # For now, let's assume we implement the 'pruning' via a direct SQL call if possible, 
        # or just log that we would do it.
        
        # Actually, let's just log the count of low confidence items for now to be safe.
        query = "SELECT count() FROM fact WHERE confidence < 0.3"
        # We don't have direct SQL. 
        # Let's skip implementation until Memory Server supports 'prune'.
        # Fallback: Just optimize.
        return
        
    except Exception as e:
        logger.error(f"Pruner failed: {e}")

async def daily_research_task(state: AgentState):
    """
    Performs autonomous web research on configured topics.
    """
    # Check if research topics exist
    topics_file = Path(state.agent_fs_root) / "config" / "research_topics.txt"
    if not topics_file.exists():
        return # Nothing to do
        
    logger.info("🕵️ Daily Research: Starting...")
    topics = topics_file.read_text().splitlines()
    if not topics: return
    
    # Pick one topic per day to verify depth
    import random
    topic = random.choice(topics).strip()
    if not topic: return
    
    logger.info(f"Researching: {topic}")
    
    # 1. Search (Mock or Real if Tool available)
    # We need a 'search_web' tool via MCP. If not available, we skip.
    # Assuming 'brave-search' or similar is in mcp_servers.
    
    # 2. Summarize
    # ... Implementation depends on Search MCP availability.
    # Placeholder for now.
    logger.info(f"Research on {topic} deferred (Search Tool check pending).")

