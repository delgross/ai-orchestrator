import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("agent_runner.feedback")

FEEDBACK_FILE = "maitre_d_feedback.json"

def get_feedback_path() -> Path:
    # Assuming running from agent_runner or similar, adjusted for actual run path
    # Ideally should use state.data_dir, but for now relative to execution or fixed
    root = Path.cwd()
    return root / "agent_data" / FEEDBACK_FILE

async def record_tool_success(query: str, server_name: str):
    """
    Record a successful tool usage for a given query.
    This effectively "teaches" the system that this server is good for this type of query.
    """
    if not query or not server_name:
        return

    # Skip Core servers (we don't need to learn them, they are always there)
    if server_name in ["project-memory", "time", "weather", "thinking", "system-control"]:
        return

    path = get_feedback_path()
    data = []
    
    if path.exists():
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception:
            data = []

    # Simple append for now. 
    # In a real vector system, we would embed 'query' and store vector + server_name.
    record = {
        "query": query,
        "server": server_name,
        "timestamp": 0
    }
    
    # Avoid exact dupes
    if record not in data:
        data.append(record)
        
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Maître d' Learning: Associated '{query[:30]}...' with '{server_name}'")
    except Exception as e:
        logger.warning(f"Failed to record feedback: {e}")

async def get_suggested_servers(query: str) -> List[str]:
    """
    Retrieve servers that have been successful for similar queries in the past.
    (Currently simple keyword match, future: vector search)
    """
    path = get_feedback_path()
    if not path.exists():
        return []
        
    try:
        with open(path, "r") as f:
            data = json.load(f)
            
        # Naive keyword matching for V1
        # If words in stored query appear in current query
        query_words = set(query.lower().split())
        counts = {}
        
        for record in data:
            rec_q = record.get("query", "").lower()
            rec_srv = record.get("server")
            if not rec_q or not rec_srv: continue
            
            # Intersection score
            rec_words = set(rec_q.split())
            overlap = len(query_words.intersection(rec_words))
            
            if overlap > 0:
                counts[rec_srv] = counts.get(rec_srv, 0) + overlap
                
        # Return sorted by score
        sorted_srvs = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [s[0] for s in sorted_srvs]
        
    except Exception as e:
        logger.error(f"Failed to retrieve suggestions: {e}")
        return []
