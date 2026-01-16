"""
Logging setup utilities for consistent logging configuration across services.
"""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional



import threading
import queue
import time
import requests
import json
import traceback

# DB Log Configuration
SURREAL_URL = os.getenv("SURREAL_URL", "http://localhost:8000")
SURREAL_NS = os.getenv("SURREAL_NS", "orchestrator")
SURREAL_DB = os.getenv("SURREAL_DB", "memory") # Logs go to memory DB for diagnostic analysis

class DBLogHandler(logging.Handler):
    """
    A non-blocking log handler that queues records and pushes them to SurrealDB in a background thread.
    Specifically designed for 'The Diagnostician' to analyze system errors.
    """
    def __init__(self, service_name: str, enabled_levels=None):
        super().__init__()
        self.service_name = service_name
        self.queue = queue.Queue(maxsize=1000)
        self.enabled_levels = enabled_levels or ["ERROR", "CRITICAL", "WARNING"] # Default to collecting issues
        
        # Start Worker
        self._stop_event = threading.Event()
        self.worker = threading.Thread(target=self._worker_loop, daemon=True, name=f"DBLogWorker-{service_name}")
        self.worker.start()

    def emit(self, record):
        try:
            # Filter noise
            if record.levelname not in self.enabled_levels:
                return
            
            # Format Exception trace if present
            trace = ""
            if record.exc_info:
                trace = "".join(traceback.format_exception(*record.exc_info))
                
            entry = {
                "timestamp": record.created, # Unix float
                "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
                "service": self.service_name,
                "level": record.levelname,
                "message": record.getMessage(),
                "file": record.filename,
                "line": record.lineno,
                "trace": trace
            }
            try:
                self.queue.put_nowait(entry)
            except queue.Full:
                # Drop log if queue full to prevent application blocking
                pass 
        except Exception:
            self.handleError(record)

    def _worker_loop(self):
        # Configure Session for Keep-Alive
        session = requests.Session()
        session.auth = (os.getenv("SURREAL_USER", "root"), os.getenv("SURREAL_PASS", "root"))
        session.headers.update({
            "Accept": "application/json", 
            "NS": SURREAL_NS, 
            "DB": SURREAL_DB
        })
        url = f"{SURREAL_URL.rstrip('/')}/sql"
        
        batch = []
        last_flush = time.time()
        
        while not self._stop_event.is_set():
            try:
                # Accumulate for 1 second or until batch size 10
                try:
                    record = self.queue.get(timeout=1.0)
                    batch.append(record)
                except queue.Empty:
                    pass
                
                now = time.time()
                if (batch and now - last_flush > 1.0) or (len(batch) >= 10):
                    self._flush_batch(session, url, batch)
                    batch = []
                    last_flush = now
                    
            except Exception:
                # Failsafe: Don't kill the logger thread
                pass

        # Final Flush
        if batch:
            self._flush_batch(session, url, batch)

    def _flush_batch(self, session, url, batch):
        if not batch: return
        try:
            # Construct Bulk Insert
            # INSERT INTO diagnostic_log [...]
            vals = []
            for r in batch:
                vals.append(r)
            
            # SurrealDB INSERT expects variable JSON
            # "INSERT INTO diagnostic_log $data"
            # Explicitly use Namespace to avoid header issues
            queries = f"USE NS {SURREAL_NS}; USE DB {SURREAL_DB}; INSERT INTO diagnostic_log {json.dumps(vals)};"
            
            resp = session.post(url, data=queries, timeout=5.0)
            if resp.status_code >= 400:
                # Fallback to stderr if DB fails
                # sys.stderr.write(f"DB Log Fail: {resp.status_code} {resp.text}\n")
                pass
        except Exception:
            pass

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    log_level: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger with file, console, AND DB handlers.
    """
    # ... (Path Logic Redundant with above but simpler to just overwrite function body)
    # Re-implementing path logic for cohesion
    
    if log_dir is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    if log_file is None:
        log_file = os.path.join(log_dir, f"{name}.log")
    elif not os.path.isabs(log_file):
        log_file = os.path.join(log_dir, log_file)
    
    logger = logging.getLogger(name)
    if logger.handlers:
        logger.handlers.clear()

    # 1. File Handler
    fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(fh)
    
    # 2. Console Handler
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(ch)
    
    # 3. DB Handler (The Diagnostician Hook)
    # We push WARNING+ logs to the database for analysis
    db_h = DBLogHandler(name, enabled_levels=["WARNING", "ERROR", "CRITICAL"])
    logger.addHandler(db_h)
    
    # Noise Reduction
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    log_level_map = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL}
    logger.setLevel(log_level_map.get(log_level, logging.INFO))
    logger.propagate = False
    
    return logger














