import json
import logging
import asyncio
import hashlib
import fcntl
import os
import time
import difflib
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Any as AnyType

logger = logging.getLogger("agent_runner.feedback")

FEEDBACK_FILE = "maitre_d_feedback.json"
MAX_RECORDS = 10000  # Prevent unlimited growth
DEDUP_CACHE_SIZE = 1000  # Cache for fast deduplication
FUZZY_WEIGHT = 0.4       # Weight for fuzzy similarity
RECENCY_HALF_LIFE_DAYS = 3  # Recency decay window

def _resolve_root(state: Optional[AnyType] = None, path_override: Optional[Path] = None) -> Path:
    """Resolve base directory for feedback storage."""
    if path_override:
        return path_override
    if state and getattr(state, "agent_fs_root", None):
        return Path(state.agent_fs_root)
    # fallback to current working dir
    return Path.cwd()

def get_feedback_path(state: Optional[AnyType] = None, path_override: Optional[Path] = None) -> Path:
    """
    Resolve feedback file path, preferring state.agent_fs_root when available.
    Allows tests to override path via path_override.
    """
    root = _resolve_root(state, path_override)
    return root / "agent_data" / FEEDBACK_FILE

async def record_tool_success(query: str, server_name: str, *, state: Optional[AnyType] = None, path_override: Optional[Path] = None):
    """
    Record a successful tool usage for a given query.
    This effectively "teaches" the system that this server is good for this type of query.
    """
    if not query or not server_name:
        return

    # Skip Core servers (we don't need to learn them, they are always there)
    if server_name in ["project-memory", "location", "thinking", "system-control"]:
        return

    # Normalize query (lowercase, strip whitespace)
    normalized_query = query.lower().strip()
    if len(normalized_query) < 3:  # Skip very short queries
        return

    path = get_feedback_path(state, path_override)
    data = []

    # Load existing data
    if path.exists():
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load existing feedback data: {e}")
            data = []

    # Enforce size limits - keep only recent records
    if len(data) >= MAX_RECORDS:
        # Keep most recent 80% to maintain learning while preventing unbounded growth
        data = data[-int(MAX_RECORDS * 0.8):]
        logger.debug(f"Trimmed feedback data to {len(data)} records")

    # Create record with better structure
    record = {
        "query": normalized_query,
        "server": server_name,
        "timestamp": time.time(),  # Wall clock for cross-process comparability
        "query_hash": hashlib.md5(normalized_query.encode()).hexdigest()[:8]  # For faster comparison
    }

    # Efficient deduplication using set for O(1) lookups
    existing_hashes = {r.get("query_hash", "") + r.get("server", "") for r in data}

    record_hash = record["query_hash"] + record["server"]
    if record_hash not in existing_hashes:
        data.append(record)

        # Validate data persistence with file locking
        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            # Use file locking to prevent concurrent access corruption
            with open(path, "w") as f:
                # Acquire exclusive lock (blocks until available)
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=None)  # Compact JSON for better performance
                    f.flush()  # Ensure data is written to disk
                    os.fsync(f.fileno())  # Force write to disk (not just cache)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Release lock

            # Verify write succeeded
            if path.exists() and path.stat().st_size > 0:
                logger.info(f"Maître d' Learning: '{normalized_query[:30]}...' → {server_name} ({len(data)} total)")
            else:
                logger.error("Feedback write verification failed - file not created or empty")

        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
    else:
        logger.debug(f"Skipped duplicate feedback: {normalized_query[:30]}... → {server_name}")

async def get_suggested_servers(query: str, max_suggestions: int = 5, *, state: Optional[AnyType] = None, path_override: Optional[Path] = None) -> List[str]:
    """
    Retrieve servers that have been successful for similar queries in the past.
    Uses hybrid scoring: keyword overlap + fuzzy similarity + recency weighting.
    """
    path = get_feedback_path(state, path_override)
    if not path.exists():
        return []

    try:
        with open(path, "r") as f:
            data = json.load(f)

        if not data:
            return []

        # Normalize input query
        normalized_query = query.lower().strip()
        query_words = set(normalized_query.split())
        # Require at least minimal signal (2+ words) to avoid noisy matches
        if len(query_words) < 2:
            return []

        counts = {}
        current_time = time.time()
        half_life_secs = RECENCY_HALF_LIFE_DAYS * 86400

        for record in data:
            rec_q = record.get("query", "").lower()
            rec_srv = record.get("server")
            rec_time = record.get("timestamp", 0)

            if not rec_q or not rec_srv:
                continue

            # Skip core servers (they're always available)
            if rec_srv in ["project-memory", "location", "thinking", "system-control"]:
                continue

            rec_words = set(rec_q.split())

            # Keyword overlap
            overlap = len(query_words.intersection(rec_words))

            # Fuzzy similarity (SequenceMatcher ratio)
            fuzzy_sim = difflib.SequenceMatcher(None, normalized_query, rec_q).ratio()

            # Skip if nothing matches
            if overlap == 0 and fuzzy_sim < 0.2:
                continue

            # Recency weighting (exponential decay)
            time_diff = max(0.0, current_time - rec_time)
            recency_weight = 0.5 ** (time_diff / half_life_secs) if half_life_secs > 0 else 1.0

            # Coverage score
            coverage = overlap / max(1, len(query_words))

            # Hybrid score: keyword + fuzzy (weighted) times recency
            hybrid = (overlap + coverage + FUZZY_WEIGHT * fuzzy_sim) * recency_weight

            counts[rec_srv] = counts.get(rec_srv, 0.0) + hybrid

        # Return sorted by score, limit results
        if counts:
            sorted_srvs = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            result = [server for server, score in sorted_srvs[:max_suggestions]]
            logger.debug(f"Maître d' suggestions for '{normalized_query[:30]}...': {result}")
            return result

        return []

    except Exception as e:
        logger.error(f"Failed to retrieve maître d' suggestions: {e}")
        return []
