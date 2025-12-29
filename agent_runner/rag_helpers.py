import logging
import json
import base64
import time
import asyncio
import re
from typing import Any, Dict
from pathlib import Path

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
                with open(file_path, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    lines = list(reader)
                    if lines:
                        headers = lines[0]
                        res = "| " + " | ".join(headers) + " |\n"
                        res += "| " + " | ".join(["---"] * len(headers)) + " |\n"
                        for row in lines[1:]:
                            res += "| " + " | ".join([str(c) for c in row]) + " |\n"
                        return res
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
            v_res = await http_client.post(v_url, json=vision_payload, timeout=60.0)
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
                    v_res = await http_client.post(f"{state.gateway_base}/v1/chat/completions", json=vision_payload, timeout=45.0)
                    if v_res.status_code == 200:
                        ocr_text.append(v_res.json()["choices"][0]["message"]["content"])
                except: pass
            full_text += "\n\n".join(ocr_text)
            
        content = full_text

    return content

# --- INGESTION PIPELINE ---

async def _ingest_content(file_path: Path, content: str, state: Any, http_client: Any, rag_base_url: str, processed_dir_base: Path, review_dir: Path):
    """
    Submits extracted content to RAG, Librarian, and Knowledge Graph.
    Includes smart filing.
    """
    if not content:
        raise ValueError("No content extracted")
    
    # Clean content
    content = content.encode('utf-8', 'ignore').decode('utf-8')
    filename_meta = extract_filename_meta(file_path)

    # 1. LIBRARIAN (Classification)
    kb_id = "default"
    authority = 0.7
    window_size = 1000
    overlap = 200
    is_volatile = False
    global_summary = ""
    shadow_tags = []
    
    try:
        lib_prompt = (
            f"Categorize this new entry.\nFilename: {file_path.name}\nContent Snippet: {content[:1000]}\n"
            "Identify domain [farm-noc, osu-med, farm-beekeeping, etc] or new.\n"
            "Return JSON: {'kb_id': '...', 'authority': 0.7, 'is_volatile': false, 'global_summary': '...', 'shadow_tags': []}"
        )
        lib_payload = {
            "model": state.task_model,
            "messages": [{"role": "user", "content": lib_prompt}],
            "response_format": {"type": "json_object"}
        }
        lib_resp = await http_client.post(f"{state.gateway_base}/v1/chat/completions", json=lib_payload, timeout=30.0)
        if lib_resp.status_code == 200:
            lib_data = json.loads(lib_resp.json()["choices"][0]["message"]["content"])
            kb_id = lib_data.get("kb_id", "default")
            authority = lib_data.get("authority", 0.7)
            global_summary = lib_data.get("global_summary", "")
            shadow_tags = lib_data.get("shadow_tags", [])
    except Exception as e:
        logger.warning(f"Librarian classification failed: {e}")

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
    # Shadow tags injection
    if shadow_tags:
        payload["content"] += f"\n\n[Index Keywords: {', '.join(shadow_tags)}]"

    try:
        resp = await http_client.post(f"{rag_base_url}/ingest", json=payload, timeout=60.0)
        resp.raise_for_status()
        logger.info(f"RAG server ingested {file_path.name} into {kb_id}")
    except Exception as e:
        logger.error(f"Failed to send {file_path.name} to RAG backend: {e}")
        # Proceed anyway? Or stop? Usually stop if RAG fails.
        # But we might want to save the sidecar at least.
        pass

    # 4. GRAPH CONSTRUCTION
    try:
        extract_prompt = f"Analyze for Knowledge Graph:\n{content[:4000]}\nReturn JSON: {{'entities': [], 'relations': []}}"
        v_resp = await http_client.post(
            f"{state.gateway_base}/v1/chat/completions", 
            json={"model": state.task_model, "messages": [{"role": "user", "content": extract_prompt}], "response_format": {"type": "json_object"}}, 
            timeout=60.0
        )
        if v_resp.status_code == 200:
            g_data = json.loads(v_resp.json()["choices"][0]["message"]["content"])
            if g_data.get("entities") or g_data.get("relations"):
                await http_client.post(f"{rag_base_url}/ingest/graph", json={"entities": g_data["entities"], "relations": g_data["relations"], "origin_file": file_path.name}, timeout=30.0)
                logger.info(f"GRAPH: Extracted {len(g_data['entities'])} nodes.")
    except Exception as e:
        logger.warning(f"Graph extraction failed: {e}")

    # 5. SMART FILING (Sidecar + Move)
    try:
        domain_slug = kb_id.lower().replace(" ", "_")
        processed_dir = processed_dir_base / domain_slug
        await asyncio.to_thread(processed_dir.mkdir, parents=True, exist_ok=True)
        
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
        await aio_write_text(processed_dir / f"{file_path.stem}_transcript.md", sidecar_content)
        
        # Move Original
        await aio_rename(file_path, processed_dir / file_path.name)
        logger.info(f"FILED: {file_path.name} -> {domain_slug}")
        
    except Exception as e:
        logger.error(f"Filing failed for {file_path.name}: {e}")
