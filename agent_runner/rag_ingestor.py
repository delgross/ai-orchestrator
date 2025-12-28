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
SUPPORTED_EXTENSIONS = ('.txt', '.md', '.pdf', '.docx', '.csv', '.png', '.jpg', '.jpeg')

from common.state import AgentState

async def rag_ingestion_task(rag_base_url: str, state: AgentState):
    """
    Background task to automatically ingest files and extract atomic facts.
    """
    http_client = await state.get_http_client()
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
            
            # 1. Advanced Structural Parsing (Layout-Aware)
            content = ""
            ext = file_path.suffix.lower()
            
            if ext in ('.txt', '.md'):
                content = file_path.read_text(encoding="utf-8", errors="replace")
            elif ext == '.csv':
                # Convert CSV to Markdown Table to preserve structural relationships
                import csv
                try:
                    with open(file_path, newline='') as csvfile:
                        reader = csv.reader(csvfile)
                        lines = list(reader)
                        if lines:
                            headers = lines[0]
                            content = "| " + " | ".join(headers) + " |\n"
                            content += "| " + " | ".join(["---"] * len(headers)) + " |\n"
                            for row in lines[1:]:
                                content += "| " + " | ".join([str(c) for c in row]) + " |\n"
                    logger.info(f"STRUCTURAL PARSE: Converted {file_path.name} to Markdown table")
                except Exception as e:
                    logger.warning(f"CSV parse failed, using raw: {e}")
                    content = file_path.read_text(encoding="utf-8", errors="replace")
            elif ext in ('.png', '.jpg', '.jpeg'):
                # MULTIMODAL PARSING (Vision-to-Text)
                logger.info(f"MULTIMODAL: Analyzing image {file_path.name}...")
                import base64
                img_data = base64.b64encode(file_path.read_bytes()).decode('utf-8')
                
                vision_payload = {
                    "model": "openai:gpt-4o", # Direct high-end vision call
                    "messages": [
                        {"role": "user", "content": [
                            {"type": "text", "text": "Describe this image in extreme detail for a knowledge base. If it's a document/diagram/label, transcribe all text and describe relationships. Focus on technical accuracy."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}}
                        ]}
                    ]
                }
                try:
                    v_url = f"{state.gateway_base}/v1/chat/completions"
                    v_res = await http_client.post(v_url, json=vision_payload, timeout=60.0)
                    v_res.raise_for_status()
                    content = v_res.json()["choices"][0]["message"]["content"]
                    logger.info(f"MULTIMODAL SUCCESS: Transcribed {len(content)} chars from {file_path.name}")
                except Exception as e:
                    logger.error(f"Vision analysis failed for {file_path.name}: {e}")
                    continue
            else:
                # For PDF/DOCX, we'd need more complex parsing
                logger.warning(f"Complex file format {file_path.suffix} not yet fully supported for OCR. Skipping.")
                continue

            # 2. THE DIGITAL LIBRARIAN (Autonomous Classification)
            # Before we ingest, we ask the LLM to categorize the file
            kb_id = "default"
            authority = 0.7
            try:
                lib_prompt = (
                    f"You are Dr. Ed's Personal Knowledge Manager. Categorize this new entry for his library.\n"
                    f"Filename: {file_path.name}\n"
                    f"Content Snippet: {content[:1000]}\n\n"
                    "Step 1: Identify the main theme of this piece of Dr. Ed's knowledge.\n"
                    "Step 2: If it matches an existing domain, use it: [farm-noc, osu-med, farm-beekeeping, farm-agronomy, farm-woodworking, farm-inventory].\n"
                    "Step 3: If it is a NEW distinct area of his interests or expertise, propose a new descriptive kb_id (e.g., 'homesteading', 'legal-archives').\n"
                    "Step 4: Assign Authority (1.0 for Professional/Peer-Reviewed, 0.7 for Casual/Secondary sources).\n"
                    "Step 5: Determine Chunking Strategy:\n"
                    "   - TECHNICAL/CODE: window_size: 800, overlap: 100\n"
                    "   - NARRATIVE/NOVELS: window_size: 2000, overlap: 500\n"
                    "   - GENERAL/MAGAZINES: window_size: 1000, overlap: 200\n"
                    "Step 6: Volatility Detection: Is this a 'Status' doc that expires (NOC logs, health reports) or 'Static' knowledge (Novels, Manuals)?\n\n"
                    "Return ONLY JSON: {'kb_id': '...', 'authority': 0.0, 'window_size': 1000, 'overlap': 200, 'is_volatile': true/false, 'theme_detected': '...'}"
                )
                
                url = f"{state.gateway_base}/v1/chat/completions"
                lib_payload = {
                    "model": state.task_model,
                    "messages": [{"role": "user", "content": lib_prompt}],
                    "response_format": {"type": "json_object"}
                }
                
                lib_resp = await http_client.post(url, json=lib_payload, timeout=30.0)
                if lib_resp.status_code == 200:
                    lib_data = json.loads(lib_resp.json()["choices"][0]["message"]["content"])
                    kb_id = lib_data.get("kb_id", "default")
                    authority = lib_data.get("authority", 0.7)
                    window_size = lib_data.get("window_size", 1000)
                    overlap = lib_data.get("overlap", 200)
                    is_volatile = lib_data.get("is_volatile", False)
                    logger.info(f"LIBRARIAN: Classified {file_path.name} as {kb_id} (Volatility: {is_volatile})")
            except Exception as e:
                logger.warning(f"Librarian failed to classify {file_path.name}, using defaults: {e}")

            # 3. Send to RAG backend
            payload = {
                "filename": file_path.name,
                "content": content,
                "kb_id": kb_id,
                "metadata": {
                    "source": "auto_ingest",
                    "ingested_at": time.time(),
                    "path": str(file_path),
                    "authority": authority,
                    "is_volatile": is_volatile
                },
                "window_size": window_size,
                "overlap": overlap
            }
            
            try:
                resp = await http_client.post(f"{rag_base_url}/ingest", json=payload, timeout=60.0)
                resp.raise_for_status()
                logger.info(f"RAG server ingested {file_path.name} into {kb_id}")
            except Exception as e:
                logger.error(f"Failed to send {file_path.name} to RAG backend: {e}")
                continue

            # 3. AUTOMATED FACT EXTRACTION (Cross-Layer Automation)
            # We summarize the file into key atomic facts for the 'Project Memory'
            try:
                from agent_runner.tools.mcp import tool_mcp_proxy
                
                # Assign authority based on file type for the memory confidence
                authority = 0.7
                ext = file_path.suffix.lower()
                if ext in ['.pdf', '.docx']: authority = 0.9
                elif ext in ['.csv', '.conf']: authority = 0.8
                
                extraction_prompt = (
                    f"Analyze this file: {file_path.name}\n\nContent:\n{content[:3000]}\n\n"
                    "Extract the 5 most important structural facts (locations, equipment, status, relationships). "
                    "Format each as: 'Entity | Relation | Target'. "
                    "Example: 'Barn_1 | contains | Tractor_A'\n"
                    "Return ONLY a JSON list of objects: {'facts': [{'e': '...', 'r': '...', 't': '...'}]}"
                )
                
                url = f"{state.gateway_base}/v1/chat/completions"
                payload = {
                    "model": state.task_model,
                    "messages": [{"role": "user", "content": extraction_prompt}],
                    "response_format": {"type": "json_object"}
                }
                
                v_resp = await http_client.post(url, json=payload, timeout=60.0)
                if v_resp.status_code == 200:
                    f_data = v_resp.json()
                    import json
                    extracted = json.loads(f_data["choices"][0]["message"]["content"]).get("facts", [])
                    
                    for f in extracted:
                        # Store in the 'Diary' (Project Memory) with Source Authority as Confidence
                        await tool_mcp_proxy(state, "project-memory", "store_fact", {
                            "entity": f.get("e"),
                            "relation": f.get("r"),
                            "target": f.get("t"),
                            "context": f"Auto-extracted from {file_path.name}",
                            "confidence": authority 
                        })
                    logger.info(f"AUTO-FACTS: Extracted {len(extracted)} facts from {file_path.name}")
            except Exception as e:
                logger.warning(f"Fact extraction failed for {file_path.name}: {e}")

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










