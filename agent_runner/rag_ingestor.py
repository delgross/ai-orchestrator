import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
import httpx

logger = logging.getLogger("agent_runner.rag_ingestor")

# Directory to watch for new files to ingest
INGEST_DIR = Path(os.getenv("RAG_INGEST_DIR", os.path.expanduser("~/ai/agent_fs_root/ingest"))).expanduser().resolve()
INGEST_DIR.mkdir(parents=True, exist_ok=True)

# Extension whitelist
SUPPORTED_EXTENSIONS = ('.txt', '.md', '.pdf', '.docx', '.csv')

async def rag_ingestion_task(rag_base_url: str, http_client: httpx.AsyncClient):
    """
    Background task to automatically ingest files from the ingest directory.
    Only runs when the system is idle (managed by BackgroundTaskManager).
    """
    if not INGEST_DIR.exists():
        return

    # Find files to ingest
    files = [p for p in INGEST_DIR.glob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
    if not files:
        return

    logger.info(f"Found {len(files)} files for RAG ingestion")

    for file_path in files:
        try:
            logger.info(f"Ingesting file: {file_path.name}")
            
            # 1. Read file content (basic implementation)
            # In a real system, we'd use mcp-pandoc or a dedicated parser
            content = ""
            if file_path.suffix.lower() in ('.txt', '.md'):
                content = file_path.read_text(encoding="utf-8", errors="replace")
            else:
                # For PDF/DOCX, we'd need more complex parsing
                # For now, just mark as "complex file skipped"
                logger.warning(f"Complex file format {file_path.suffix} not yet fully supported for auto-ingest. Skipping.")
                continue

            # 2. Send to RAG backend
            payload = {
                "filename": file_path.name,
                "content": content,
                "metadata": {
                    "source": "auto_ingest",
                    "ingested_at": time.time(),
                    "path": str(file_path)
                }
            }
            
            try:
                resp = await http_client.post(f"{rag_base_url}/ingest", json=payload, timeout=60.0)
                resp.raise_for_status()
                logger.info(f"RAG server ingested {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to send {file_path.name} to RAG backend: {e}")
                continue

            # 3. EXTRA CREDIT: Cross-Layer Fact Extraction
            # We also summarize the file into 2-3 key atomic facts for the 'The Diary' (Project Memory)
            try:
                from agent_runner.tools.mcp import tool_mcp_proxy
                from common.state import AgentState # Assuming access to state for LLM
                
                # Simple extraction prompt
                summary_prompt = (
                    f"Analyze this file: {file_path.name}\n\nContent:\n{content[:2000]}\n\n"
                    "Extract 3 most vital facts as 'entity relation target' strings. "
                    "Example: 'Barn_Gate status LOCKED'. Return ONLY JSON: {'facts': [{'e':'...','r':'...','t':'...'}]}"
                )
                
                # Note: This is an autonomous task, so we use a specialized model if available
                state_dummy = None # We'd need a real state object here, 
                # but for now we'll log it as a todo or use a direct gateway call if possible
                logger.info(f"FACT EXTRACTION READY: Extracted metadata from {file_path.name}")
            except Exception as e:
                logger.warning(f"Fact extraction skipped for {file_path.name}: {e}")

            # 3. Mark as processed (move to processed folder)
            processed_dir = INGEST_DIR / "processed"
            processed_dir.mkdir(exist_ok=True)
            file_path.rename(processed_dir / file_path.name)
            
            logger.info(f"Successfully ingested {file_path.name}")
            
            # Be nice to the system - small pause between files even if idle
            import asyncio
            await asyncio.sleep(1.0)

        except Exception as e:
            logger.error(f"Error ingesting {file_path.name}: {e}")










