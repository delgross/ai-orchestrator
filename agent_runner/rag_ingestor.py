import os
import time
import logging
import json
import hashlib
from pathlib import Path
from typing import Optional
import httpx
import asyncio
import datetime
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    class FileSystemEventHandler: pass # Dummy

from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer
from common.notifications import notify_info, notify_error, notify_health
from agent_runner.service_registry import ServiceRegistry
from agent_runner.rag_helpers import _process_locally, _ingest_content, aio_read_bytes, aio_rename

logger = logging.getLogger("agent_runner.rag_ingestor")

# Directory Configuration
# Directory Configuration
INGEST_DIR = Path(os.getenv("RAG_INGEST_DIR", "/Users/bee/Sync/Antigravity/ai/agent_fs_root/ingest")).resolve()
# [SAFETY PATCH] Structural Isolation: Storage folders are now SIBLINGS of ingest, not children.
# This prevents the Watchdog (which watches ingest/) from seeing output files.
FS_ROOT = INGEST_DIR.parent 
BRAIN_DIR = Path(os.getenv("BRAIN_DIR", "/Users/bee/Brain/Permanent_Memory")).resolve()

DEFERRED_DIR = FS_ROOT / "deferred"
PROCESSED_BASE_DIR = FS_ROOT / "processed"
REVIEW_DIR = FS_ROOT / "review"

DUPLICATES_DIR = FS_ROOT / "duplicates"
REJECTED_DIR = FS_ROOT / "rejected"

for d in [INGEST_DIR, DEFERRED_DIR, PROCESSED_BASE_DIR, REVIEW_DIR, DUPLICATES_DIR, REJECTED_DIR, BRAIN_DIR]:
    d.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = ('.txt', '.md', '.pdf', '.docx', '.csv', '.png', '.jpg', '.jpeg', '.mp3', '.m4a', '.mp4', '.json')
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
    if not HAS_WATCHDOG:
        logger.warning("Watchdog not installed. Real-time RAG updates disabled (falling back to periodic).")
        return None

    try:
        loop = asyncio.get_running_loop()
        event_handler = RAGFileEventHandler(rag_base_url, state, loop)
        observer = Observer()
        observer.schedule(event_handler, str(INGEST_DIR), recursive=False)
        # [SOVEREIGNTY UPDATE] Brain Directory is now handled by System Ingestor only.
        # observer.schedule(event_handler, str(BRAIN_DIR), recursive=True) 
        observer.start()
        logger.info(f"RAG WATCHDOG: Started observer on {INGEST_DIR}")
        return observer
    except Exception as e:
        logger.error(f"Failed to start RAG Watchdog: {e}")
        return None

import hashlib
import json

async def get_file_hash(path: Path) -> str:
    """
    Calculate SHA-256 hash of a file asynchronously.
    Uses asyncio.to_thread for CPU-bound work.
    """
    def _calculate_hash(p: Path) -> str:
        sha256_hash = hashlib.sha256()
        with open(p, "rb") as f:
            # Read in chunks to handle large files efficiently
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    return await asyncio.to_thread(_calculate_hash, path)

class IngestionHistory:
    """
    Database-backed registry of ingested file hashes to prevent duplication.
    Uses SurrealDB as the source of truth instead of a local JSON file.
    """
    def __init__(self, memory_server: MemoryServer) -> None:
        self.memory = memory_server
        self._cache: Optional[set] = None  # Optional in-memory cache for fast lookups

    async def _ensure_connected(self) -> None:
        """Ensure database connection is established."""
        await self.memory.ensure_connected()

    async def is_duplicate(self, file_hash: str) -> bool:
        """
        Check if a file hash exists in the database.
        
        Args:
            file_hash: SHA256 hash of the file
            
        Returns:
            True if the file has been ingested before, False otherwise
        """
        await self._ensure_connected()
        
        try:
            query = f"SELECT file_hash FROM ingestion_history WHERE file_hash = '{file_hash}' LIMIT 1;"
            from agent_runner.db_utils import run_query_with_memory
            result = await run_query_with_memory(self.memory, query)
            
            if result and len(result) > 0:
                return True
            return False
        except Exception as e:
            logger.warning(f"Failed to check ingestion history for {file_hash[:8]}: {e}")
            return False  # Fail open - allow ingestion if check fails

    async def mark_seen(self, file_hash: str, kb_id: str = "default", file_path: Optional[str] = None, file_size: Optional[int] = None) -> None:
        """
        Record a file ingestion in the database.
        
        Args:
            file_hash: SHA256 hash of the file
            kb_id: Knowledge base ID where the file was ingested
            file_path: Optional path to the file
            file_size: Optional size of the file in bytes
        """
        await self._ensure_connected()
        
        try:
            # SurrealDB: Use UPSERT with record ID based on file_hash (unique index)
            # This automatically handles duplicates - if exists, updates; if not, creates
            record_id = f"ingestion_history:{file_hash}"
            
            # Escape single quotes in strings for SurrealDB
            safe_path = file_path.replace("'", "''") if file_path else None
            safe_kb = kb_id.replace("'", "''") if kb_id else "default"
            
            # Build content object
            content_parts = [
                f"file_hash: '{file_hash}'",
                f"kb_id: '{safe_kb}'",
                f"ingested_at: time::now()"
            ]
            
            if safe_path:
                content_parts.append(f"file_path: '{safe_path}'")
            if file_size is not None:
                content_parts.append(f"file_size: {file_size}")
            
            content_str = ", ".join(content_parts)
            
            # UPSERT automatically handles duplicates
            query = f"UPSERT {record_id} SET {content_str};"
            
            await run_query_with_memory(self.memory, query)
            
            # Invalidate cache if it exists
            self._cache = None
        except Exception as e:
            logger.warning(f"Failed to record ingestion history for {file_hash[:8]}: {e}")
            # Don't raise - ingestion can continue even if history recording fails

# Global singleton (lazy init)
_history_manager = None

from agent_runner.service_registry import ServiceRegistry

async def rag_ingestion_task(rag_base_url: Optional[str] = None, state: Optional[AgentState] = None) -> None:
    logger.debug("rag_ingestion_task entered")
    # 0. SETUP & ARGUMENT RECONCILIATION
    if rag_base_url is None:
        rag_base_url = os.getenv("RAG_BASE_URL", "http://127.0.0.1:5555")
        
    if state is None:
        # PURE PATTERN: Fetch from Registry
        try:
            state = ServiceRegistry.get_state()
        except RuntimeError:
            logger.warning("Skipping RAG Ingestion: AgentState not initialized in Registry.")
            return

    if getattr(state, "shutdown_event", None) and state.shutdown_event.is_set():
        return

    if _ingestion_lock.locked():
        return

    async with _ingestion_lock:
        # 0.5 NETWORK CHECK (Topography Aware)
        # Only require internet if the RAG server is REMOTE.
        is_local_rag = "127.0.0.1" in rag_base_url or "localhost" in rag_base_url
        if not is_local_rag and not state.internet_available:
            logger.warning("Skipping RAG Ingestion: Remote Server requires Internet.")
            return

        http_client = await state.get_http_client()
        
        # 1. HEALTH CHECK
        global _last_connection_ok
        pause_file = INGEST_DIR / ".paused"
        if pause_file.exists():
            logger.warning(f"Ingestion paused. Remove {pause_file.name} to resume.")
            return

        # 0.5 HEALTH CHECK
        global _last_connection_ok
        try:
            # if not state.internet_available: return # Removed: Local RAG shouldn't require internet
            health = await http_client.get(f"{rag_base_url}/health", timeout=5.0)
            if health.status_code != 200:
                logger.warning(f"RAG Health Check Failed: {health.status_code} from {rag_base_url}")
                if _last_connection_ok:
                    logger.warning(f"RAG Server unhealthy ({health.status_code})")
                    _last_connection_ok = False
                return
            if not _last_connection_ok:
                logger.info("RAG Connection Restored")
                _last_connection_ok = True
        except Exception as e:
            logger.warning(f"RAG Health Check Error: {e}")
            return

        # 1. BATCH PREPARATION
        # Use simple os.listdir via thread to avoid blocking if directory is huge (unlikely but safe)
        inbox_files = [p for p in INGEST_DIR.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
        brain_files = [p for p in BRAIN_DIR.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
        # Filter brain files: Only ingest if modified recently? Or trust history hash?
        # Trust hash (standard logic).
        inbox_files.extend(brain_files)
        
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
            except Exception as e:
                logger.debug(f"Error during file processing: {e}")

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
        
        # Init History Manager if needed (now uses DB)
        global _history_manager
        if _history_manager is None:
            from agent_runner.memory_server import MemoryServer
            memory = MemoryServer(state)
            await memory.ensure_connected()
            _history_manager = IngestionHistory(memory)

        for file_path in light_batch:
            try:
                is_brain_file = str(BRAIN_DIR) in str(file_path.resolve())

                # [DEDUPLICATION CHECK]
                f_hash = await get_file_hash(file_path)
                if await _history_manager.is_duplicate(f_hash):
                    if is_brain_file:
                        # Brain file duplicate = No Op (Already ingested, don't move, don't delete)
                        continue 
                        
                    reason = f"Duplicate Detected: {file_path.name} (Hash: {f_hash[:8]})"
                    logger.warning(f"AUTO-DISPOSE: {reason}. Moving to duplicates/.")
                    # [PHASE 15] Trash Bin Logic: Move to duplicates and continue
                    try:
                        await aio_rename(file_path, DUPLICATES_DIR / file_path.name)
                    except Exception as e:
                        logger.debug(f"Error during file processing: {e}")
                    continue # Skip to next file
                
                logger.info(f"TRACK A (Light): Processing {file_path.name} locally...")
                content = await _process_locally(file_path, state, http_client)
                
                # Check for Quality Exception and move to processed directory
                try:
                    target_processed_dir = PROCESSED_BASE_DIR
                    if is_brain_file:
                        target_processed_dir = None # READ-ONLY MODE

                    await _ingest_content(file_path, content, state, http_client, rag_base_url, target_processed_dir, REVIEW_DIR)
                    # Mark as seen ONLY after successful ingestion
                    file_size = file_path.stat().st_size if file_path.exists() else None
                    await _history_manager.mark_seen(f_hash, kb_id="default", file_path=str(file_path), file_size=file_size)
                    
                except ValueError as ve:
                    # Quality Check Failed (raised by rag_helpers)
                    if "Quality Check Failed" in str(ve):
                        reason = f"Quality Check Failed: {file_path.name} - {str(ve)}"
                        logger.warning(reason)
                        
                        if is_brain_file:
                             continue # Do not move brain files to rejected

                        # [RECURSION GUARD]
                        if "RECURSION" in str(ve):
                            logger.warning(f"RECURSION GUARD: Detected previously processed file. Moving to review/.")
                            try: 
                                await aio_rename(file_path, REVIEW_DIR / file_path.name)
                            except Exception as e:
                                logger.warning(f"Failed to move {file_path} to review: {e}")
                            continue
                        # [PHASE 15] Trash Bin Logic: Move to rejected and continue
                        try: 
                            await aio_rename(file_path, REJECTED_DIR / file_path.name)
                        except Exception as e:
                            logger.warning(f"Failed to move {file_path} to rejected: {e}")
                        continue # Skip to next file
                    else:
                        raise ve


                     
            except Exception as e:
                logger.error(f"Failed local processing for {file_path.name}: {e}")
                # Move to Review
                try: 
                    await aio_rename(file_path, REVIEW_DIR / file_path.name)
                except Exception as rename_e:
                    logger.warning(f"Failed to move {file_path} to review after error: {rename_e}")

        # 4. PROCESSING - TRACK B: HEAVY FILES (Manual/Deferred)
        for file_path in heavy_batch:
            # Simple Triage: Heavy files always go to deferred (Waiting for manual action or future cloud worker)
            if file_path.parent != DEFERRED_DIR:
                logger.info(f"TRACK B (Heavy): Deferring {file_path.name} (Too large for local)")
                try: 
                    await aio_rename(file_path, DEFERRED_DIR / file_path.name)
                except Exception as e:
                    logger.warning(f"Failed to move {file_path} to deferred: {e}")
        
        # 5. NIGHTLY GARDENER (The Truth Judge)
        # Runs once per night to verify facts.
        if is_night_window:
            garden_marker = INGEST_DIR / ".last_garden_run"
            should_garden = True
            
            if garden_marker.exists():
                # Check if ran in last 20 hours
                if time.time() - garden_marker.stat().st_mtime < 72000:
                    should_garden = False
            
            if should_garden:
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


