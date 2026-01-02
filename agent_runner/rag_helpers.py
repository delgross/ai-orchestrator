import logging
import json
import base64
import time
import asyncio
import io
import re
from typing import Any, Dict
from pathlib import Path
from agent_runner.registry import ServiceRegistry

logger = logging.getLogger("agent_runner.rag_helpers")

# --- NON-BLOCKING I/O WRAPPERS ---
async def aio_read_text(file_path: Path) -> str:
    return await asyncio.to_thread(file_path.read_text, encoding="utf-8", errors="replace")

async def aio_read_bytes(file_path: Path) -> bytes:
    return await asyncio.to_thread(file_path.read_bytes)

async def aio_rename(src: Path, dest: Path):
    await asyncio.to_thread(src.rename, dest)

async def aio_write_text(file_path: Path, content: str):
    await asyncio.to_thread(file_path.write_text, content, encoding="utf-8")

# --- EXTRACTION HELPERS ---

def extract_filename_meta(file_path: Path) -> Dict[str, Any]:
    """Parse [Key=Value] tags from filename."""
    filename_meta = {}
    clean_name = file_path.stem
    tags = re.findall(r'\[(\w+)=([^\]]+)\]', clean_name)
    for key, val in tags:
        filename_meta[key.lower()] = val
    return filename_meta

async def _process_locally(file_path: Path, state: Any, http_client: Any) -> str:
    """
    Processes a file locally using PyPDF (for PDFs) or Vision API (for Images).
    Non-blocking where possible.
    """
    content = ""
    ext = file_path.suffix.lower()
    
    if ext in ('.txt', '.md'):
        content = await aio_read_text(file_path)
        
    elif ext == '.csv':
        try:
            # CSV parsing uses 'open', so we run in thread
            def parse_csv():
                import csv
                import io
                
                # Check file encoding via crude heuristic? Defaults to utf-8 from open()
                try:
                    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                        # Sniff to find dialect?
                        sample = csvfile.read(1024)
                        csvfile.seek(0)
                        sniffer = csv.Sniffer()
                        try:
                            dialect = sniffer.sniff(sample)
                            has_header = sniffer.has_header(sample)
                        except:
                            dialect = 'excel'
                            has_header = True # Assume header
                        
                        reader = csv.reader(csvfile, dialect=dialect)
                        rows = list(reader)
                        
                        if not rows: return ""
                        
                        # Markdown Table Generator
                        # Ensure all rows have same column count as header
                        header = rows[0]
                        col_count = len(header)
                        
                        md_lines = []
                        # Header
                        md_lines.append("| " + " | ".join(str(h).replace("|", "&#124;").replace("\n", " ") for h in header) + " |")
                        # Separator
                        md_lines.append("| " + " | ".join(["---"] * col_count) + " |")
                        # Data
                        for row in rows[1:]:
                            # Pad row if short
                            row += [""] * (col_count - len(row))
                            # Truncate if long? Or just take first N? 
                            # Let's just zip to range
                            formatted_row = [str(c).replace("|", "&#124;").replace("\n", " ") for c in row[:col_count]]
                            md_lines.append("| " + " | ".join(formatted_row) + " |")
                            
                        return "\n".join(md_lines)
                except UnicodeDecodeError:
                    # Fallback to latin-1
                    pass
                return ""
            content = await asyncio.to_thread(parse_csv)
        except Exception as e:
            logger.warning(f"CSV parse failed, using raw: {e}")
            content = await aio_read_text(file_path)
            
    elif ext in ('.png', '.jpg', '.jpeg'):
        try:
            # We must read binary
            img_data = await aio_read_bytes(file_path)
            img_b64 = base64.b64encode(img_data).decode('utf-8')
            
            vision_payload = {
                "model": state.vision_model,
                "messages": [
                    {"role": "user", "content": [
                        {"type": "text", "text": "Describe this image in detail for a knowledge base. Include all visible text and objects."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]}
                ]
            }
            v_url = f"{state.gateway_base}/v1/chat/completions"
            v_res = await http_client.post(v_url, json=vision_payload, headers={"X-Skip-Refinement": "true"}, timeout=60.0)
            if v_res.status_code == 200:
                content = v_res.json()["choices"][0]["message"]["content"]
            else:
                raise Exception(f"Vision API returned {v_res.status_code}")
        except Exception as e:
            logger.error(f"Local Vision failed: {e}")
            raise e

    elif ext == '.pdf':
        def parse_pdf():
            import pypdf
            reader = pypdf.PdfReader(file_path)
            text = []
            scanned_images = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text and len(page_text.strip()) > 50:
                    text.append(f"[Page {i+1}]\n{page_text}")
                else:
                    if hasattr(page, "images") and page.images:
                        for img in page.images:
                            scanned_images.append((i+1, img))
            return "\n\n".join(text), scanned_images

        # Run CPU-bound task in thread
        full_text, scanned_images = await asyncio.to_thread(parse_pdf)
        
        # Scanned Doc Fallback (Vision logic requires async await, so we do it here outside the thread)
        if len(full_text) < 500 and scanned_images:
            logger.warning(f"PDF {file_path.name} appears to be scanned. Triggering Vision OCR...")
            ocr_text = []
            for idx, (page_num, img) in enumerate(scanned_images):
                if idx > 5: break 
                try:
                    img_b64 = base64.b64encode(img.data).decode('utf-8')
                    vision_payload = {
                        "model": state.vision_model,
                        "messages": [
                            {"role": "user", "content": [
                                {"type": "text", "text": f"Transcribe this page ({page_num})."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                            ]}
                        ]
                    }
                    v_res = await http_client.post(f"{state.gateway_base}/v1/chat/completions", json=vision_payload, headers={"X-Skip-Refinement": "true"}, timeout=45.0)
                    if v_res.status_code == 200:
                        ocr_text.append(v_res.json()["choices"][0]["message"]["content"])
                except: pass
            full_text += "\n\n".join(ocr_text)
            
        content = full_text

    return content

# --- INGESTION PIPELINE ---

# --- QUALITY CONTROL (The Sous Chef) ---
def _assess_local_quality(content: str, ext: str) -> dict:
    """
    Offline Heuristic Quality Check. 
    Returns {'score': float, 'is_noise': bool, 'reason': str}
    """
    if not content or not content.strip():
        return {'score': 0.0, 'is_noise': True, 'reason': "Empty Content"}
    
    val_len = len(content.strip())
    
    # 1. Length Check
    if val_len < 50:
         return {'score': 0.1, 'is_noise': True, 'reason': "Too Short (<50 chars)"}

    # 2. Log File / System Noise Detection
    # Heuristic: High density of timestamps AND log keywords
    import re
    timestamp_density = len(re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', content[:2000])) / (val_len / 100) if val_len > 0 else 0
    
    # Check for common log keywords to confirm it's a system log
    log_keywords = ["INFO", "DEBUG", "ERROR", "WARN", "CRITICAL", "TRACE"]
    has_log_keywords = any(k in content[:1000] for k in log_keywords)

    # Transcripts often have timestamps but no log levels.
    # Only flag if density is high AND keywords are present, OR density is extremely high (>2.0)
    if (timestamp_density > 0.5 and has_log_keywords) or (timestamp_density > 2.0):
         return {'score': 0.2, 'is_noise': True, 'reason': "System Log Detected"}

    return {'score': 0.6, 'is_noise': False, 'reason': "Baseline Acceptable"}

# --- INGESTION PIPELINE ---

async def _ingest_content(file_path: Path, content: str, state: Any, http_client: Any, rag_base_url: str, processed_dir_base: Path, review_dir: Path, cloud_metadata: dict = None):
    """
    Submits extracted content to RAG, Librarian, and Knowledge Graph.
    Includes smart filing and Local Quality Preprocessing ("The Sous Chef").
    """
    if not content:
        raise ValueError("No content extracted")
    
    # Clean content
    content = content.encode('utf-8', 'ignore').decode('utf-8')
    filename_meta = extract_filename_meta(file_path)
    
    # 0. THE SOUS CHEF (Local Quality Check)
    # We filter out obvious garbage before asking the Librarian or Cloud.
    quality_report = _assess_local_quality(content, file_path.suffix.lower())
    
    if quality_report['is_noise']:
        logger.warning(f"SOUS CHEF: Rejected {file_path.name} (Score: {quality_report['score']}, Reason: {quality_report['reason']})")
        # Raise exception to trigger Pause in ingestor
        raise ValueError(f"Quality Check Failed: {quality_report['reason']}")

    # 1. LIBRARIAN (Universal Content-Based Sorting)
    # We ignore the folder structure for routing/authority and rely 100% on the AI.
    
    kb_id = "default"
    authority = 0.5 # Default starting score
    is_volatile = False
    global_summary = ""
    shadow_tags = []
    
    # Capture source context just in case, but don't route by it
    try:
        # Calculate relative path from Ingest Root to preserve folder semantics
        # processed_dir_base is .../ingest/processed, so parent is .../ingest
        ingest_root = processed_dir_base.parent
        rel_folder = file_path.parent.relative_to(ingest_root)
        
        # Avoid tagging "." or system folders if they are the direct parent
        if str(rel_folder) != "." and file_path.parent.name not in ["ingest", "deferred", "review"]:
             shadow_tags.append(f"source_folder:{str(rel_folder)}")
    except Exception:
        # Fallback if path math fails
        if file_path.parent.name not in ["ingest", "deferred", "review"]:
            shadow_tags.append(f"source_folder:{file_path.parent.name}")

    try:
        lib_prompt = (
            f"Categorize this new entry.\nFilename: {file_path.name}\nContent Snippet: {content[:1000]}\n"
            "Identify domain [farm-noc, osu-med, farm-beekeeping, etc] or new.\n"
            "Return JSON ONLY: {'kb_id': '...', 'authority': 0.7, 'is_volatile': false, 'global_summary': '...', 'shadow_tags': []}"
        )
        lib_payload = {
            "model": state.task_model,
            "messages": [{"role": "user", "content": lib_prompt}],
            "response_format": {"type": "json_object"}
        }
        lib_resp = await http_client.post(f"{state.gateway_base}/v1/chat/completions", json=lib_payload, headers={"X-Skip-Refinement": "true"}, timeout=30.0)
        
        if lib_resp.status_code == 200:
            raw_content = lib_resp.json()["choices"][0]["message"]["content"]
            # Clean Markdown wrappers
            if "```json" in raw_content:
                raw_content = raw_content.split("```json")[1].split("```")[0]
            elif "```" in raw_content:
                raw_content = raw_content.split("```")[1].split("```")[0]
            
            lib_data = json.loads(raw_content.strip())
            kb_id = lib_data.get("kb_id", "default")
            authority = lib_data.get("authority", 0.7)
            global_summary = lib_data.get("global_summary", "")
            tags = lib_data.get("shadow_tags", [])
            if tags: shadow_tags.extend(tags)
            logger.info(f"LIBRARIAN: Assigned {file_path.name} to {kb_id} (Auth: {authority})")
        else:
             logger.warning(f"Librarian API failed: {lib_resp.status_code} {lib_resp.text}")

    except Exception as e:
        logger.warning(f"Librarian classification failed for {file_path.name}: {e}")

    # 2. DEDUPLICATION
    # (Skipped for brevity/latency - we trust RAG to handle updates usually, or we can add it back later)

    # 3. RAG INGEST
    payload = {
        "filename": file_path.name,
        "content": content,
        "kb_id": kb_id,
        "metadata": {
            "source": filename_meta.get("source", "auto_ingest"),
            "ingested_at": time.time(),
            "path": str(file_path),
            "authority": authority,
            "global_summary": global_summary,
            "shadow_tags": shadow_tags,
            **filename_meta
        },
        "prepend_text": f"[DOCUMENT SUMMARY: {global_summary}] " if global_summary else ""
    }
    
    # Merge Cloud Metadata (Creative Librarian)
    if cloud_metadata:
        payload["metadata"].update(cloud_metadata)
    # Shadow tags injection
    if shadow_tags:
        payload["content"] += f"\n\n[Index Keywords: {', '.join(shadow_tags)}]"

    rag_error = None
    try:
        resp = await http_client.post(f"{rag_base_url}/ingest", json=payload, timeout=60.0)
        resp.raise_for_status()
        logger.info(f"RAG server ingested {file_path.name} into {kb_id}")
    except Exception as e:
        logger.error(f"Failed to send {file_path.name} to RAG backend: {e}")
        rag_error = e # Defer raising so Graph Extraction can still happen

    # 4. GRAPH CONSTRUCTION (The Fusion Patch)
    facts_stored = 0
    try:
        # Check if Cloud H100 already did the work (Fast Track)
        if cloud_metadata and cloud_metadata.get("entities"):
            logger.info(f"GRAPH: Fast-tracking {len(cloud_metadata['entities'])} entities from H100.")
            memory_server = ServiceRegistry.get_memory_server()
            if memory_server:
                count = 0
                for entity in cloud_metadata["entities"]:
                    if isinstance(entity, str):
                        await memory_server.store_fact(entity, "mentioned_in", file_path.name, context="H100 Extraction")
                        count += 1
                logger.info(f"GRAPH: Stored {count} facts from H100.")
                facts_stored += count

        else:
            # Fallback: Local Extraction (Slower, less accurate)
            extract_prompt = (
                f"Analyze this text to extract Knowledge Graph Facts.\n"
                f"Text: {content[:4000]}\n"
                "Return JSON with a list of facts: {'facts': [{'entity': '...', 'relation': '...', 'target': '...'}]}"
            )
            v_resp = await http_client.post(
                f"{state.gateway_base}/v1/chat/completions", 
                json={"model": state.task_model, "messages": [{"role": "user", "content": extract_prompt}], "response_format": {"type": "json_object"}}, 
                headers={"X-Skip-Refinement": "true"},
                timeout=60.0
            )
            if v_resp.status_code == 200:
                raw_g = v_resp.json()["choices"][0]["message"]["content"]
                g_data = json.loads(raw_g)
                facts = g_data.get("facts", [])
                
                # Support legacy format just in case
                if not facts and g_data.get("entities"):
                     facts = [{"entity": e, "relation": "mentioned_in", "target": file_path.name} for e in g_data["entities"]]

                if facts:
                    memory_server = ServiceRegistry.get_memory_server()
                    if memory_server:
                        count = 0
                        for f in facts:
                            await memory_server.store_fact(
                                f.get("entity"), 
                                f.get("relation"), 
                                f.get("target"), 
                                context=f"Extracted from {file_path.name}"
                            )
                            count += 1
                        logger.info(f"GRAPH: Extracted and Stored {count} facts (Local).")
                        facts_stored += count
                    else:
                        logger.warning("GRAPH: MemoryServer not available in Registry.")
    except Exception as e:
        logger.warning(f"Graph extraction failed: {e}")

    # [RELIABILITY PATCH] Unrecoverable Content Fallback
    if facts_stored == 0:
        logger.info("GRAPH: Zero facts extracted (or extraction failed). Storing Raw Content Fallback.")
        memory_server = ServiceRegistry.get_memory_server()
        if memory_server:
            await memory_server.store_fact(
                entity=file_path.name, 
                relation="contains_text", 
                target=content[:100] + "..." if len(content) > 100 else content,
                context=content[:4000], # Embed up to 4k chars as context
                confidence=0.8
            )

    # 5. SMART FILING (Simple Flat Strategy)
    # User Request: "I like them the way they are", "Ignore directories".
    # Result: We do NOT reorganize into subfolders. We just move to 'processed/'.
    try:
        # We place everything in the root of the processed folder.
        # However, to avoid clutter collision if they used subfolders before, we just use the flattened name?
        # No, they said "ignore directories", so we assume they are dumping loose files.
        # We will just put them in PROCESSED_BASE_DIR directly.
        
        # But wait, processed_dir_base is generic. Let's make one "Completed" folder to start.
        # Actually, let's just use the KB_ID as metadata but NOT as a folder.
        
        target_dir = processed_dir_base
        # If we want to be slightly tidy, we can put them in "Library" or just root.
        # Let's use root `processed/` as requested. (Code requires target_dir to be a Path)
        
        # Sidecar
        sidecar_content = f"""---
kb_id: {kb_id}
authority: {authority}
ingested_at: {time.strftime('%Y-%m-%d %H:%M:%S')}
keywords: [{', '.join(shadow_tags)}]
---
# Transcription of {file_path.stem}
**Summary:** {global_summary}
---
{content}"""
        # Move Original with Collision Handling
        target_file = target_dir / file_path.name
        if target_file.exists():
            # Collision detected! e.g. "gas.pdf" already exists.
            # We rename the NEW file to "gas_{timestamp}.pdf" to preserve history.
            timestamp = int(time.time())
            new_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            target_file = target_dir / new_name
            # Update sidecar logic to match? The sidecar filename is derived from file_path.stem above.
            # We need to update the sidecar path too.
            sidecar_path = target_dir / f"{file_path.stem}_{timestamp}_transcript.md"
        else:
            sidecar_path = target_dir / f"{file_path.stem}_transcript.md"
            
        await aio_write_text(sidecar_path, sidecar_content)
        await aio_rename(file_path, target_file)
        logger.info(f"FILED: {file_path.name} -> {target_file.name}")
        
    except Exception as e:
        logger.error(f"Filing failed for {file_path.name}: {e}")

    # [RESILIENCE] Late raise of RAG backend error
    if rag_error:
        raise rag_error
