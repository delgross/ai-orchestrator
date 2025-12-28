import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
import httpx

logger = logging.getLogger("agent_runner.rag_ingestor")

# Directory to watch for new files to ingest
INGEST_DIR = Path(os.getenv("RAG_INGEST_DIR", "/Users/bee/Sync/Antigravity/ai/agent_fs_root/ingest")).resolve()
INGEST_DIR.mkdir(parents=True, exist_ok=True)

# Extension whitelist
SUPPORTED_EXTENSIONS = ('.txt', '.md', '.pdf', '.docx', '.csv', '.png', '.jpg', '.jpeg')

from agent_runner.state import AgentState
from common.notifications import notify_info, notify_error, notify_health

async def rag_ingestion_task(rag_base_url: str, state: AgentState):
    """
    Background task to automatically ingest files and extract atomic facts.
    Includes a built-in circuit breaker for system stability.
    """
    http_client = await state.get_http_client()
    
    # CIRCUIT BREAKER: Check RAG health before starting batch
    try:
        health = await http_client.get(f"{rag_base_url}/health", timeout=5.0)
        if health.status_code != 200:
            logger.warning("RAG Ingestor: Circuit Breaker TRIPPED (Server unhealthy). Skipping batch.")
            notify_health("RAG Ingestor Suspended", "Circuit breaker tripped: RAG server is report unhealthy.", source="RAG Ingestor")
            return
    except Exception as e:
        logger.warning(f"RAG Ingestor: Circuit Breaker TRIPPED (Connection failed: {e}). Skipping batch.")
        notify_health("RAG Ingestor Offline", f"RAG server connection failed: {e}", source="RAG Ingestor")
        return
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
            
            # 0. FILENAME METADATA EXTRACTION (The Tag-Extract Workflow)
            # Parse [Key=Value] tags from filename
            import re
            filename_meta = {}
            clean_name = file_path.stem
            
            # Match patterns like [Source=Starlink] or [Type=Official]
            tags = re.findall(r'\[(\w+)=([^\]]+)\]', clean_name)
            for key, val in tags:
                filename_meta[key.lower()] = val
            
            # Remove tags from the user-facing filename for cleaner titles
            if tags:
                clean_name = re.sub(r'\[.*?\]', '', clean_name).strip()
                clean_name = re.sub(r'\s+', ' ', clean_name) # Fix double spaces
                logger.info(f"METADATA: Extracted {filename_meta} from filename. Clean title: '{clean_name}'")

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
            elif ext == '.pdf':
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    text = []
                    for i, page in enumerate(reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text.append(f"[Page {i+1}]\n{page_text}")
                    
                    full_text = "\n\n".join(text)
                    if not full_text.strip():
                        logger.warning(f"PDF {file_path.name} appears to be scanned/empty (no text layer). Skipping for now.")
                        continue
                        
                    content = full_text
                    logger.info(f"PDF PARSE: Extracted {len(content)} chars from {file_path.name}")
                except Exception as e:
                    logger.warning(f"PDF parse failed for {file_path.name}: {e}")
                    continue

            # 2. THE DIGITAL LIBRARIAN (Autonomous Classification)
            # Before we ingest, we ask the LLM to categorize the file
            kb_id = "default"
            authority = 0.7
            window_size = 1000
            overlap = 200
            is_volatile = False
            global_summary = ""
            shadow_tags = []
            
            try:
                lib_prompt = (
                    f"You are Dr. Ed's Personal Knowledge Manager. Categorize this new entry for his library.\n"
                    f"Filename: {file_path.name}\n"
                    f"Content Snippet: {content[:1000]}\n\n"
                    "Step 1: Identify the main theme of this piece of Dr. Ed's knowledge.\n"
                    "Step 2: If it matches an existing domain, use it: [farm-noc, osu-med, farm-beekeeping, farm-agronomy, farm-woodworking, farm-inventory].\n"
                    "Step 3: If it is a NEW distinct area of his interests or expertise, propose a new descriptive kb_id (e.g., 'homesteading', 'legal-archives').\n"
                    "Step 4: Assign Authority (1.0 for Professional/Peer-Reviewed, 0.7 for Casual/Secondary sources).\n"
                    "Step 5: Determine Chunking Strategy [TECHNICAL (800/100), NARRATIVE (2000/500), GENERAL (1000/200)].\n"
                    "Step 6: Volatility Detection: Is this 'Status' (expires) or 'Static' (permanent)?\n"
                    "Step 7: GLOBAL CONTEXT: Produce a 1-sentence executive summary of the document purpose.\n"
                    "Step 8: ENTITY ALIGNMENT: Map synonyms (e.g., 'Starlink', 'Omada', 'The Router') to a canonical name.\n"
                    "Step 9: SHADOW TAGS: Generate 15-20 semantic keywords (synonyms, related concepts, model numbers) to improve fuzzy search.\n\n"
                    "Return ONLY JSON: {'kb_id': '...', 'authority': 0.0, 'window_size': 1000, 'overlap': 200, 'is_volatile': true/false, 'global_summary': '...', 'canonical_entities': {...}, 'shadow_tags': ['tag1', 'tag2']}"
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
                    global_summary = lib_data.get("global_summary", "")
                    shadow_tags = lib_data.get("shadow_tags", [])
                    
                    # Notify on new domain discovery
                    if kb_id != "default" and kb_id not in ["farm-noc", "osu-med", "farm-beekeeping", "farm-agronomy", "farm-woodworking", "farm-inventory"]:
                        notify_info("New Knowledge Domain Discovery", f"The Librarian has created a new domain: {kb_id} based on {file_path.name}", source="Digital Librarian")
                    
                    logger.info(f"LIBRARIAN: Classified {file_path.name} (Volatility: {is_volatile}, Summary: {global_summary[:50]}...)")
            except Exception as e:
                logger.warning(f"Librarian failed to classify {file_path.name}: {e}")
                global_summary = ""

            # 2.5 DEDUPLICATION CHECK
            try:
                # Query RAG to see if this exact filename already exists
                check_url = f"{rag_base_url}/query"
                check_payload = {"query": f"filename:{file_path.name}", "kb_id": kb_id, "limit": 1}
                c_resp = await http_client.post(check_url, json=check_payload, timeout=10.0)
                if c_resp.status_code == 200 and c_resp.json().get("chunks_ingested", 0) > 0:
                    # Note: /query returns chunks, we check if filename is in results
                    # But for now, let's just log and proceed or skip if exact match
                    logger.info(f"DEDUPLICATION: File {file_path.name} may already be in {kb_id}. Proceeding with update.")
            except: pass

            # 3. Send to RAG backend
            payload = {
                "filename": file_path.name,
                "content": content,
                "kb_id": kb_id,
                "metadata": {
                    "source": filename_meta.get("source", "auto_ingest"),
                    "ingested_at": time.time(),
                    "path": str(file_path),
                    "authority": authority,
                    "is_volatile": is_volatile,
                    "global_summary": global_summary,
                    "shadow_tags": shadow_tags,
                    **filename_meta
                },
                "window_size": window_size,
                "overlap": overlap,
                "prepend_text": f"[DOCUMENT SUMMARY: {global_summary}] " if global_summary else ""
            }
            
            # Inject Shadow Tags into the content stream invisibly (at the end of the last chunk via RAG server logic if we wanted, 
            # but simpler to just append to the content here so it gets chunked in)
            if shadow_tags:
                # We append them to the content so they are part of the vector embedding
                # We label them as 'Keywords' so the AI reading the chunk knows what they are
                payload["content"] += f"\n\n[Index Keywords: {', '.join(shadow_tags)}]"
            
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
            
            # 3b. CREATE SIDECAR TRANSCRIPTION (The Archive Strategy)
            # We save the text content to a .md file so the user has the 'Truth' on disk
            try:
                sidecar_name = f"{file_path.stem}_transcript.md"
                sidecar_path = processed_dir / sidecar_name
                
                # Format Metadata as YAML Frontmatter
                yaml_block = "---\n"
                yaml_block += f"kb_id: {kb_id}\n"
                yaml_block += f"authority: {authority}\n"
                yaml_block += f"ingested_at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                for k, v in filename_meta.items():
                    yaml_block += f"{k}: {v}\n"
                if shadow_tags:
                    yaml_block += f"keywords: [{', '.join(shadow_tags)}]\n"
                yaml_block += "---\n"
                
                sidecar_content = (
                    f"{yaml_block}\n"
                    f"# Transcription of {clean_name}\n\n"
                    f"**Summary:** {global_summary}\n"
                    "---\n\n"
                    f"{content}"
                )
                
                sidecar_path.write_text(sidecar_content, encoding="utf-8")
                logger.info(f"SIDECAR: Created transcript at {sidecar_name}")
                
            except Exception as e:
                logger.error(f"Failed to create sidecar for {file_path.name}: {e}")

            # Move original file
            file_path.rename(processed_dir / file_path.name)
            
            logger.info(f"Successfully ingested {file_path.name}")
            
            # Be nice to the system - small pause between files even if idle
            import asyncio
            await asyncio.sleep(1.0)

        except Exception as e:
            logger.error(f"Error ingesting {file_path.name}: {e}")
            notify_error("Ingestion Failure", f"Failed to ingest {file_path.name}: {e}", source="RAG Ingestor")

    if len(files) > 1:
        notify_info("Knowledge Ingestion Complete", f"Successfully filed {len(files)} new entries into the library.", source="RAG Ingestor")










