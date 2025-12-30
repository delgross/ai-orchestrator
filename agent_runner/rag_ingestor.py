import os
import time
import logging
from pathlib import Path
import httpx
import asyncio
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from agent_runner.state import AgentState
from common.notifications import notify_info, notify_error, notify_health
from agent_runner.rag_helpers import _process_locally, _ingest_content, aio_read_bytes, aio_rename

logger = logging.getLogger("agent_runner.rag_ingestor")

# Directory Configuration
INGEST_DIR = Path(os.getenv("RAG_INGEST_DIR", "/Users/bee/Sync/Antigravity/ai/agent_fs_root/ingest")).resolve()
DEFERRED_DIR = INGEST_DIR / "deferred"
PROCESSED_BASE_DIR = INGEST_DIR / "processed"
REVIEW_DIR = INGEST_DIR / "review"

for d in [INGEST_DIR, DEFERRED_DIR, PROCESSED_BASE_DIR, REVIEW_DIR]:
    d.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = ('.txt', '.md', '.pdf', '.docx', '.csv', '.png', '.jpg', '.jpeg', '.mp3', '.m4a', '.mp4')
NIGHT_SHIFT_START = int(os.getenv("NIGHT_SHIFT_START", "1"))
NIGHT_SHIFT_END = int(os.getenv("NIGHT_SHIFT_END", "6"))

# State tracking for smart logging
_last_connection_ok = True
_ingestion_lock = asyncio.Lock()

class RAGFileEventHandler(FileSystemEventHandler):
    """Bridges synchronous file system events to the async ingestion task."""
    def __init__(self, rag_base_url, state, loop):
        self.rag_base_url = rag_base_url
        self.state = state
        self.loop = loop

    def _trigger_ingest(self):
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
    Simplified 2-Track Ingestion Task (Light/Local vs Heavy/Modal).
    """
    if _ingestion_lock.locked():
        return

    async with _ingestion_lock:
        http_client = await state.get_http_client()
        
        # 0. HEALTH CHECK
        global _last_connection_ok
        try:
            if not state.internet_available: return
            health = await http_client.get(f"{rag_base_url}/health", timeout=5.0)
            if health.status_code != 200:
                if _last_connection_ok:
                    logger.warning(f"RAG Server unhealthy ({health.status_code})")
                    _last_connection_ok = False
                return
            if not _last_connection_ok:
                logger.info("RAG Connection Restored")
                _last_connection_ok = True
        except Exception:
            return

        # 1. BATCH PREPARATION
        # Use simple os.listdir via thread to avoid blocking if directory is huge (unlikely but safe)
        inbox_files = [p for p in INGEST_DIR.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
        
        if not inbox_files: return # Fast exit

        light_batch = []
        heavy_batch = []
        
        try:
            from zoneinfo import ZoneInfo
            tz = ZoneInfo(os.getenv("AGENT_TIMEZONE", "America/New_York"))
            current_hour = datetime.datetime.now(tz).hour
        except ImportError:
            current_hour = datetime.datetime.now().hour

        # Robust Midnight Logic
        if NIGHT_SHIFT_START <= NIGHT_SHIFT_END:
            # Standard: 1 AM to 6 AM
            is_night = (NIGHT_SHIFT_START <= current_hour < NIGHT_SHIFT_END)
        else:
            # Wrap-around: 23 PM to 5 AM
            is_night = (current_hour >= NIGHT_SHIFT_START) or (current_hour < NIGHT_SHIFT_END)

        trigger_file = INGEST_DIR / ".trigger_now"
        force_run = trigger_file.exists()
        
        if force_run:
            logger.warning("Force Run Detected")
            try: await asyncio.to_thread(trigger_file.unlink)
            except: pass

        for f in inbox_files:
            f_size_mb = f.stat().st_size / (1024 * 1024)
            is_heavy = False
            if f.suffix.lower() in ['.mp3', '.m4a', '.mp4']: is_heavy = True
            elif f_size_mb > 10: is_heavy = True
            elif f.suffix.lower() == '.pdf' and f_size_mb > 2: is_heavy = True
                
            if is_heavy:
                heavy_batch.append(f)
            else:
                light_batch.append(f)

        # 2. NIGHT SHIFT PULL
        is_night_window = (is_night or force_run)
        if is_night_window:
            deferred_files = [p for p in DEFERRED_DIR.glob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
            if deferred_files:
                heavy_batch.extend(deferred_files)

        # 3. PROCESSING - TRACK A: LIGHT FILES (Local)
        for file_path in light_batch:
            try:
                logger.info(f"TRACK A (Light): Processing {file_path.name} locally...")
                content = await _process_locally(file_path, state, http_client)
                await _ingest_content(file_path, content, state, http_client, rag_base_url, PROCESSED_BASE_DIR, REVIEW_DIR)
            except Exception as e:
                logger.error(f"Failed local processing for {file_path.name}: {e}")
                # Move to Review
                try: await aio_rename(file_path, REVIEW_DIR / file_path.name)
                except: pass

        # 4. PROCESSING - TRACK B: HEAVY FILES (Modal)
        for file_path in heavy_batch:
            if not is_night_window:
                # Defer immediately (Day Time)
                if file_path.parent != DEFERRED_DIR:
                    logger.info(f"TRACK B (Heavy): Deferring {file_path.name}")
                    try: await aio_rename(file_path, DEFERRED_DIR / file_path.name)
                    except: pass
                continue

            # Night Time: Modal
            try:
                logger.info(f"TRACK B (Heavy): Offloading {file_path.name} to Modal")
                from agent_runner.modal_tasks import cloud_process_pdf, cloud_process_image, has_modal
                
                if not has_modal:
                    raise ImportError("Modal not available")
                    
                content = ""
                ext = file_path.suffix.lower()
                
                # Async read for upload
                file_bytes = await aio_read_bytes(file_path)

                if ext == '.pdf':
                     # Modal calls are currently synchronous, user might want to optimize this later
                     # For now run in thread to avoid blocking loop
                     content = await asyncio.to_thread(cloud_process_pdf.remote, file_bytes, file_path.name)
                
                elif ext in ('.png', '.jpg', '.jpeg'):
                    raw = await asyncio.to_thread(cloud_process_image.remote, file_bytes)
                    try:
                        import json
                        content = json.loads(raw).get("description", raw)
                    except: content = raw
                    
                # If we get here with content, finalize
                if content:
                    await _ingest_content(file_path, content, state, http_client, rag_base_url, PROCESSED_BASE_DIR, REVIEW_DIR)

            except Exception as e:
                logger.error(f"Modal failed for {file_path.name}: {e}. Keeping deferred.")
                # Ensure it stays in deferred
                if file_path.parent != DEFERRED_DIR:
                     try: await aio_rename(file_path, DEFERRED_DIR / file_path.name)
                     except: pass
        
        # 5. NIGHTLY GARDENER (The Truth Judge)
        # Runs once per night to verify facts.
        if is_night_window:
            garden_marker = INGEST_DIR / ".last_garden_run"
            should_garden = True
            
            if garden_marker.exists():
                # Check if ran in last 20 hours
                if time.time() - garden_marker.stat().st_mtime < 72000:
                    should_garden = False
            
            if should_garden and has_modal:
                logger.info("NIGHT SHIFT: Starting Gardener (Database Audit)...")
                try:
                    from agent_runner.modal_tasks import cloud_database_cleanup
                    
                    # In a real implementation, we would fetch recently added facts from RAG here.
                    # For now, we perform a 'Health Check' audit on a sample logic 
                    # to prove the H100 pipeline is active and ready.
                    sample_facts = '[{"fact": "System startup check", "context": "Nightly Automation"}]'
                    
                    # Fire and Forget (Async to avoiding blocking the loop too long, 
                    # but Modal tasks are fast enough to just await if needed, or run_in_executor)
                    # We'll run it in thread to be safe.
                    res = await asyncio.to_thread(cloud_database_cleanup.remote, sample_facts)
                    logger.info(f"GARDENER FINISHED: {res[:100]}...")
                    
                    # Touch marker
                    await asyncio.to_thread(garden_marker.touch)
                    
                except Exception as e:
                    logger.error(f"Gardener failed: {e}")
