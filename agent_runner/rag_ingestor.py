import os
import time
import logging
from pathlib import Path

logger = logging.getLogger("agent_runner.rag_ingestor")

# Directory to watch for new files to ingest
INGEST_DIR = Path(os.getenv("RAG_INGEST_DIR", "/Users/bee/Sync/Antigravity/ai/agent_fs_root/ingest")).resolve()
DEFERRED_DIR = INGEST_DIR / "deferred"
PROCESSED_BASE_DIR = INGEST_DIR / "processed"
REVIEW_DIR = INGEST_DIR / "review"

for d in [INGEST_DIR, DEFERRED_DIR, PROCESSED_BASE_DIR, REVIEW_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Extension whitelist
SUPPORTED_EXTENSIONS = ('.txt', '.md', '.pdf', '.docx', '.csv', '.png', '.jpg', '.jpeg', '.mp3', '.m4a', '.mp4')

# Night Shift Configuration
NIGHT_SHIFT_START = 1 # 1 AM
NIGHT_SHIFT_END = 6   # 6 AM

import httpx
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from agent_runner.state import AgentState
from common.notifications import notify_info, notify_error, notify_health

# State tracking for smart logging (suppress repetitive errors)
_last_connection_ok = True
# Lock to prevent concurrent ingestion runs triggered by rapid file events
_ingestion_lock = asyncio.Lock()

class RAGFileEventHandler(FileSystemEventHandler):
    """Bridges synchronous file system events to the async ingestion task."""
    def __init__(self, rag_base_url, state, loop):
        self.rag_base_url = rag_base_url
        self.state = state
        self.loop = loop

    def _trigger_ingest(self):
        # Fire and forget - the task handles its own locking
        asyncio.run_coroutine_threadsafe(
            rag_ingestion_task(self.rag_base_url, self.state), 
            self.loop
        )

    def on_created(self, event):
        if not event.is_directory and not event.src_path.endswith('.tmp'):
            logger.info(f"WATCHDOG: Detected new file: {Path(event.src_path).name}")
            self._trigger_ingest()

    def on_moved(self, event):
        if not event.is_directory and not event.dest_path.endswith('.tmp'):
             logger.info(f"WATCHDOG: Detected moved file: {Path(event.dest_path).name}")
             self._trigger_ingest()

def start_rag_watcher(rag_base_url: str, state: AgentState):
    """Starts the Watchdog observer."""
    try:
        loop = asyncio.get_running_loop()
        event_handler = RAGFileEventHandler(rag_base_url, state, loop)
        observer = Observer()
        observer.schedule(event_handler, str(INGEST_DIR), recursive=False)
        observer.start()
        logger.info(f"RAG WATCHDOG: Started observer on {INGEST_DIR}")
        return observer
    except Exception as e:
        logger.error(f"Failed to start RAG Watchdog: {e}")
        return None

async def rag_ingestion_task(rag_base_url: str, state: AgentState):
    """
    Background task to automatically ingest files and extract atomic facts.
    Includes a built-in circuit breaker for system stability.
    """
    # Prevent overlapping runs from multiple events
    if _ingestion_lock.locked():
        # Optional: just return if locked, or wait. 
        # Typically for "run now" we might want to wait, but "debounce" is also fine.
        # Let's wait to ensure we process the file that just arrived.
        pass

    async with _ingestion_lock:
        http_client = await state.get_http_client()
        
        # CIRCUIT BREAKER: Check RAG health before starting batch
    global _last_connection_ok
    try:
        if not state.internet_available:
             if _last_connection_ok:
                 logger.warning("RAG Ingestor: Internet unavailable. Pausing ingestion.")
                 _last_connection_ok = False
             return

        health = await http_client.get(f"{rag_base_url}/health", timeout=5.0)
        
        if health.status_code != 200:
            if _last_connection_ok:
                logger.warning(f"RAG Ingestor: Server returned unhealthy status ({health.status_code}). Pausing ingestion.")
                notify_health("RAG Ingestor Suspended", f"Server status: {health.status_code}", source="RAG Ingestor")
                _last_connection_ok = False
            return
            
        # If we reach here, we are back online
        if not _last_connection_ok:
            logger.info("RAG Ingestor: Connection restored. Resuming operations.")
            notify_info("RAG Ingestor Restored", "Connection to RAG server re-established.", source="RAG Ingestor")
            _last_connection_ok = True
            
    except (httpx.ConnectError, httpx.TimeoutException, ConnectionRefusedError) as e:
        # Expected offline states - Silent handling unless state changed
        if _last_connection_ok:
            logger.warning(f"RAG Ingestor: Connection failed ({type(e).__name__}). Pausing ingestion.")
            _last_connection_ok = False
        return
    except Exception as e:
        # Unexpected crashes - Always log
        logger.error(f"RAG Ingestor: Unexpected Circuit Breaker Error: {e}", exc_info=True)
        notify_health("RAG Ingestor Error", f"Unexpected error: {e}", source="RAG Ingestor")
        return
        
    if not INGEST_DIR.exists():
        return

    # --- NIGHT SHIFT LOGIC ---
    import datetime
    current_hour = datetime.datetime.now().hour
    is_night = (NIGHT_SHIFT_START <= current_hour < NIGHT_SHIFT_END) # Night shift logic
    
    trigger_file = INGEST_DIR / ".trigger_now"
    force_run = trigger_file.exists()

    if force_run:
        logger.warning("⚡ TURBO MODE: Forced ingestion triggered by user!")
        try:
            trigger_file.unlink()
        except Exception as e:
            logger.error(f"Failed to unlink .trigger_now file: {e}")

    # --- PROJECT AUTO-DISCOVERY (Feature 4) ---
    root_dir = Path(__file__).parent.parent
    project_knowledge = root_dir / ".agent" / "knowledge"
    if project_knowledge.exists() and project_knowledge.is_dir():
        project_name = root_dir.name.lower().replace(" ", "-")
        kb_id = f"project-{project_name}"
        logger.info(f"PROJECT DISCOVERY: Syncing {project_knowledge} to KB '{kb_id}'...")
        
        pk_files = [p for p in project_knowledge.glob("**/*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
        for pkf in pk_files:
            try:
                # We don't move these, we just read and ingest if they are "new"
                # (Simple heuristic: if it was modified in the last 15 minutes)
                if time.time() - pkf.stat().st_mtime < 900: 
                    logger.info(f"Ingesting project doc: {pkf.name}")
                    with open(pkf, "rb") as f_data:
                        files = {"file": (pkf.name, f_data.read())}
                        await http_client.post(f"{rag_base_url}/ingest?kb_id={kb_id}", files=files)
            except Exception as e:
                logger.error(f"Failed to ingest project doc {pkf.name}: {e}")

    # Files to process in this run
    batch_files = []

    # 1. Check Inbox (Automatic Assessment)
    inbox_files = [p for p in INGEST_DIR.glob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
    
    for f in inbox_files:
        # Determine strict "Heaviness"
        is_heavy = False
        ext = f.suffix.lower()
        size_mb = f.stat().st_size / (1024 * 1024)
        
        if ext in ['.mp3', '.m4a', '.mp4']:
            is_heavy = True # Audio/Video is always heavy
        elif size_mb > 10: 
            is_heavy = True # Large files > 10MB
        elif ext == '.pdf' and size_mb > 2:
            # Quick check for large PDFs (proxy for page count without opening)
            is_heavy = True
            
        if is_heavy and not (is_night or force_run):
            logger.info(f"NIGHT SHIFT: Deferring heavy file {f.name} ({size_mb:.1f}MB) to off-hours.")
            try:
                f.rename(DEFERRED_DIR / f.name)
            except Exception as e:
                logger.error(f"Failed to defer file {f.name}: {e}")
        else:
            batch_files.append(f)

    # 2. If Night Shift, also pull from Deferred
    if (is_night or force_run):
        deferred_files = [p for p in DEFERRED_DIR.glob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
        if deferred_files:
            logger.info(f"NIGHT SHIFT: Processing {len(deferred_files)} deferred items.")
            batch_files.extend(deferred_files)

    if not batch_files:
        return

    logger.info(f"Found {len(batch_files)} files for RAG ingestion")

    for file_path in batch_files:
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
                
                content = ""
                try:
                    # CLOUD OFFLOAD STRATEGY: Only for Night Shift or Forced Runs
                    from agent_runner.modal_tasks import cloud_process_image, has_modal
                    
                    # Policy: Use Cloud GPU only if it's Night Shift or a Forced Run (Turbo)
                    # Otherwise, use local/gateway vision API which is cheaper/faster for single images
                    use_cloud = (is_night or force_run) and has_modal
                    
                    if use_cloud:
                        logger.info(f"CLOUD GPU: Offloading Image {file_path.name} to Modal (Night/Force Rule)...")
                        try:
                            raw_result = cloud_process_image.remote(file_path.read_bytes())
                            
                            # Parse Structured Output
                            import json
                            data = json.loads(raw_result)
                            content = data.get("description", "")
                            
                            # Merge strict metadata
                            if "objects" in data: filename_meta["objects"] = data["objects"]
                            if "animals" in data: filename_meta["animals"] = data["animals"]
                            if "plants" in data: filename_meta["plants"] = data["plants"]
                            if "people" in data: filename_meta["people"] = data["people"]
                            if "camera_data" in data: filename_meta["camera_data"] = data["camera_data"]
                            
                            logger.info(f"CLOUD SUCCESS: Received structured analysis. Objects: {len(data.get('objects', []))}")
                        except Exception as cloud_err:
                            logger.error(f"Modal Cloud processing failed: {cloud_err}")
                            logger.warning(f"STRICT QUALITY: Aborting {file_path.name} to preserve quality. Re-deferring.")
                            if file_path.parent != DEFERRED_DIR:
                                try: file_path.rename(DEFERRED_DIR / file_path.name)
                                except: pass
                            continue # Skip local fallback
                    else:
                         # Fall through to Local Vision if not Night/Force or Modal missing
                         raise ImportError("Modal skipped by policy (Daytime/Local Pref)")
                        
                except Exception as cloud_err:
                    # LOCAL FALLBACK (Standard Vision Model)
                    # This runs for daytime images OR if Modal fails
                    try:
                        import base64
                        with open(file_path, "rb") as image_file:
                             img_b64 = base64.b64encode(image_file.read()).decode('utf-8')
                        
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
                        v_res = await http_client.post(v_url, json=vision_payload, timeout=60.0)
                        if v_res.status_code == 200:
                            content = v_res.json()["choices"][0]["message"]["content"]
                            logger.info(f"LOCAL VISION: Analyzed {file_path.name}")
                        else:
                            raise Exception(f"Vision API returned {v_res.status_code}")
                            
                    except Exception as e:
                        logger.error(f"Local Image analysis failed: {e}")
                        # Defer logic remains
                        if is_night or force_run:
                            if file_path.parent != DEFERRED_DIR:
                                try: file_path.rename(DEFERRED_DIR / file_path.name)
                                except: pass
                        continue

            elif ext in ('.mp3', '.m4a', '.mp4'):
                # ... (Audio logic unchanged) ...
                # AUDIO TRANSCRIPTION (Whisper via Router)
                logger.info(f"AUDIO: Transcribing {file_path.name}...")
                try:
                    # We must read bytes to send via httpx inside this async loop
                    # Note: For very large files, streaming upload would be better, but httpx+files supports file objects
                    # We'll rely on the night shift to handle the latency
                    with open(file_path, "rb") as audio_file:
                        # Construct multipart payload
                        files = {"file": (file_path.name, audio_file, "application/octet-stream")}
                        data = {"model": "whisper-1"}
                        
                        tx_url = f"{state.gateway_base}/v1/audio/transcriptions"
                        # Long timeout for audio
                        tx_resp = await http_client.post(tx_url, files=files, data=data, timeout=600.0)
                        
                        if tx_resp.status_code == 200:
                            content = tx_resp.json().get("text", "")
                            logger.info(f"AUDIO SUCCESS: Transcribed {len(content)} chars from {file_path.name}")
                        else:
                            raise Exception(f"Gateway returned {tx_resp.status_code}: {tx_resp.text}")
                            
                except Exception as e:
                    logger.error(f"Audio transcription failed for {file_path.name}: {e}")
                    # Defer for next night shift
                    if is_night or force_run:
                        logger.info(f"ECONOMY GUARD: Deferring audio {file_path.name} for next available window.")
                        if file_path.parent != DEFERRED_DIR:
                            try: file_path.rename(DEFERRED_DIR / file_path.name)
                            except: pass
                    continue

            elif ext == '.pdf':
                try:
                    # CLOUD OFFLOAD STRATEGY: Use Modal H100/CPU if available
                    from agent_runner.modal_tasks import cloud_process_pdf, has_modal
                    
                    # Policy: Heavy PDF processing (Modal) is reserved for Night Shift or Turbo Mode
                    use_cloud = (is_night or force_run) and has_modal

                    if use_cloud:
                        logger.info(f"CLOUD GPU: Offloading PDF {file_path.name} to Modal (Night/Force Rule)...")
                        # Run remote function
                        try:
                            content = cloud_process_pdf.remote(file_path.read_bytes(), file_path.name)
                            logger.info(f"CLOUD SUCCESS: Received {len(content)} chars from Modal.")
                        except Exception as cloud_err:
                            logger.error(f"Modal Cloud processing failed: {cloud_err}")
                            logger.warning(f"STRICT QUALITY: Aborting {file_path.name} to preserve quality. Re-deferring.")
                            if file_path.parent != DEFERRED_DIR:
                                try: file_path.rename(DEFERRED_DIR / file_path.name)
                                except: pass
                            continue # Skip local fallback
                    else:
                        raise ImportError("Modal skipped by policy (Daytime/Local Pref)")

                except Exception:
                    # FALLBACK: Local PyPDF
                    # logic continues...
                    # FALLBACK: Local PyPDF
                    logger.info(f"Processing PDF locally (Fallback): {file_path.name}")
                    import pypdf
                    import base64
                    reader: Any = pypdf.PdfReader(file_path)
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
                    
                    full_text = "\n\n".join(text)
                    
                    # If text content is low but we have images, trigger OCR
                    if len(full_text) < 500 and scanned_images:
                        logger.warning(f"PDF {file_path.name} appears to be scanned ({len(scanned_images)} images). Triggering Full Vision OCR...")
                        
                        ocr_text = []
                        total_images = len(scanned_images)
                        network_issues = False
                        
                        for idx, (page_num, img) in enumerate(scanned_images):
                            logger.info(f"OCR: Processing Page {page_num}/{total_images}...")
                            try:
                                img_b64 = base64.b64encode(img.data).decode('utf-8')
                                vision_payload = {
                                    "model": state.vision_model,
                                    "messages": [
                                        {"role": "user", "content": [
                                            {"type": "text", "text": f"Transcribe this scanned document page (Page {page_num})."},
                                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                                        ]}
                                    ]
                                }
                                v_url = f"{state.gateway_base}/v1/chat/completions"
                                v_res = await http_client.post(v_url, json=vision_payload, timeout=45.0)
                                if v_res.status_code == 200:
                                    desc = v_res.json()["choices"][0]["message"]["content"]
                                    ocr_text.append(f"[Page {page_num} - VISION OCR]\n{desc}")
                                else:
                                    network_issues = True
                            except Exception:
                                network_issues = True
                        
                        full_text += "\n\n".join(ocr_text)

                    content = full_text
                    logger.info(f"PDF PARSE: Extracted {len(content)} chars.")
                
            else: # Handle unsupported extensions
                logger.warning(f"Unknown file extension: {ext}. Moving to REVIEW.")
                logger.warning(f"Unknown file extension: {ext}. Moving to REVIEW.")
                notify_info(f"Unknown File Type: {file_path.name}", f"Extension {ext} not supported. Moved to review folder.")
                file_path.rename(REVIEW_DIR / file_path.name)
                continue

            # SANITIZATION: Remove surrogates and non-printable chars that crash JSON/UTF-8
            if content:
                content = content.encode('utf-8', 'ignore').decode('utf-8')

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
            if shadow_tags and isinstance(payload["content"], str):
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

            # 3. KNOWLEDGE GRAPH CONSTRUCTION (GraphRAG)
            # We extract Entities and Relations to build the visual brain.
            try:
                extraction_prompt = (
                    f"Analyze this file: {file_path.name} for the Knowledge Graph.\n\nContent:\n{content[:4000]}\n\n"
                    "Task: Identify core ENTITIES (Systems, Objects, Concepts, People) and RELATIONSHIPS.\n"
                    "Focus specifically on:\n"
                    "1. Dependencies & Prerequisites (A requires B, A depends on B)\n"
                    "2. Maintenance & Actionable Requirements (A needs Service, A needs Update)\n"
                    "3. Temporal Events (A happened on Date, A is scheduled for Date)\n"
                    "4. Structural Links (A contains B, A is part of B)\n\n"
                    "Return JSON: {'entities': [{'name': '...', 'type': '...', 'description': '...'}], 'relations': [{'source': '...', 'target': '...', 'relation': '...', 'description': '...'}]}"
                )
                
                url = f"{state.gateway_base}/v1/chat/completions"
                payload = {
                    "model": state.task_model,
                    "messages": [{"role": "user", "content": extraction_prompt}],
                    "response_format": {"type": "json_object"}
                }
                
                v_resp = await http_client.post(url, json=payload, timeout=60.0)
                if v_resp.status_code == 200:
                    # Clean response
                    res_content = v_resp.json()["choices"][0]["message"]["content"]
                    import json
                    graph_data = json.loads(res_content)
                    
                    # Ensure minimal valid structure
                    entities = graph_data.get("entities", [])
                    relations = graph_data.get("relations", [])
                    
                    if entities or relations:
                        graph_payload = {
                            "entities": entities,
                            "relations": relations,
                            "origin_file": file_path.name
                        }
                        
                        g_resp = await http_client.post(f"{rag_base_url}/ingest/graph", json=graph_payload, timeout=30.0)
                        if g_resp.status_code == 200:
                            logger.info(f"GRAPH INGEST: Added {len(entities)} nodes and {len(relations)} edges from {file_path.name}")
                        else:
                            logger.warning(f"Graph ingest failed: {g_resp.text}")
            except Exception as e:
                logger.warning(f"Graph extraction failed for {file_path.name}: {e}")

            # 4. SMART FILING (The Digital Librarian's Shelf)
            # Create a specific folder for this domain
            domain_slug = kb_id.lower().replace(" ", "_")
            processed_dir = PROCESSED_BASE_DIR / domain_slug
            processed_dir.mkdir(parents=True, exist_ok=True)
            
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
                logger.info(f"SIDECAR: Created transcript at {sidecar_path.name}")
                
            except Exception as e:
                logger.error(f"Failed to create sidecar for {file_path.name}: {e}")

            # Move original file to the smart folder
            try:
                 file_path.rename(processed_dir / file_path.name)
            except Exception as e:
                logger.error(f"Failed to move {file_path.name} to processed dir: {e}")
            
            logger.info(f"Successfully ingested {file_path.name} into {domain_slug}")
            
            # Be nice to the system - small pause between files even if idle
            import asyncio
            await asyncio.sleep(1.0)

        except Exception as e:
            logger.error(f"Error ingesting {file_path.name}: {e}")
            # ECONOMY GUARD: If it's a heavy file or night shift, defer instead of review
            if is_night or force_run:
                logger.warning(f"INGESTION DELAYED: {file_path.name} moved back to deferred for next retry.")
                try: 
                    if file_path.parent != DEFERRED_DIR:
                        file_path.rename(DEFERRED_DIR / file_path.name)
                except: pass
            else:
                notify_error("Ingestion Failure", f"Failed to ingest {file_path.name}: {e}. Moved to review.", source="RAG Ingestor")
                try:
                    file_path.rename(REVIEW_DIR / file_path.name)
                except: pass

    if len(batch_files) > 1:
        notify_info("Knowledge Ingestion Complete", f"Successfully filed {len(batch_files)} new entries into the library.", source="RAG Ingestor")










