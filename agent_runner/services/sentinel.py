import json
import os
import re
import logging
import asyncio
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.services.sentinel")

class Sentinel:
    """
    The Sentinel is the Security Gatekeeper for Command Execution.
    It uses a 3-Tier Strategy to minimize latency while maximizing safety.
    
    Tier 1: Fast Whitelist (0ms) - Known safe binaries (ls, pwd, etc)
    Tier 2: Learned Memory (0ms) - Patterns previously approved by User/System
    Tier 3: LLM Evaluation (Slow) - Semantic analysis of novel/risky commands
    """
    
    TIER_1_BINARIES = {
        "ls", "pwd", "grep", "cat", "echo", "whoami", "date", "find", 
        "git status", "git log", "git diff", "uptime", "head", "tail",
        "wc", "sort", "uniq", "tree"
    }
    
    def __init__(self, state: AgentState):
        self.state = state
        self.lexicon_path = Path(state.agent_fs_root).parent / "config" / "lexicons" / "command_safety.json"
        self._memory_cache = {"approved": [], "blocked": []}
        self._load_memory()

    def _load_memory(self):
        """Load learned patterns from disk."""
        if self.lexicon_path.exists():
            try:
                with open(self.lexicon_path, "r") as f:
                    self._memory_cache = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load Sentinel memory: {e}")
        else:
            # Init empty
            self._save_memory()

    def _save_memory(self):
        """Persist learned patterns to disk."""
        try:
            self.lexicon_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.lexicon_path, "w") as f:
                json.dump(self._memory_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save Sentinel memory: {e}")

    async def evaluate(self, command: str) -> Tuple[bool, str]:
        """
        Evaluate a command string.
        Returns: (allowed: bool, reason: str)
        """
        cmd_stripped = command.strip()
        binary = cmd_stripped.split(" ")[0]
        
        # --- TIER 1: FAST WHITELIST ---
        if binary in self.TIER_1_BINARIES and ";" not in cmd_stripped and "|" not in cmd_stripped:
            # Simple single command matching allowed binary
            return True, "Tier 1: Safe Binary"
            
        # --- TIER 2: LEARNED MEMORY ---
        for entry in self._memory_cache.get("approved", []):
            try:
                if re.match(entry["pattern"], cmd_stripped):
                    return True, f"Tier 2: {entry['reason']}"
            except re.error:
                continue
                
        for entry in self._memory_cache.get("blocked", []):
            try:
                if re.match(entry["pattern"], cmd_stripped):
                    return False, f"Tier 2 BLOCKED: {entry['reason']}"
            except re.error:
                continue

        # --- TIER 3: LLM SENTINEL ---
        # If we fall through to here, we need help.
        logger.info(f"Sentinel checking novel command: {binary}...")
        return await self._llm_evaluate(cmd_stripped)

    async def _llm_evaluate(self, command: str) -> Tuple[bool, str]:
        """Ask the Router/Safety model to classify the command."""
        try:
            # Use Router model for speed if available, else Fallback
            model = self.state.router_model or "ollama:mistral"
            
            prompt = (
                "SYSTEM SAFETY & COMPETENCE AUDIT\n"
                f"User Context: The user 'Ed' is a developer. The workspace is '{self.state.agent_fs_root}'.\n"
                "Task: Audit this command for STUPIDITY or ACCIDENTAL DAMAGE.\n"
                "The user is NOT worried about malice, but about accidents (deleting wrong files, breaking git, infinite loops).\n"
                "SAFE = Standard dev commands (git add, python run, npm install, harmless reads).\n"
                "UNSAFE = \n"
                "  1. DESTRUCTIVE: rm -rf *, git reset --hard (without check), formatting disks.\n"
                "  2. STUPID: Commands that likely hang forever, delete the wrong directory, or act on root (/).\n"
                "  3. AppleScript: Allow if it looks like standard automation, block if it looks like it will spam the UI.\n\n"
                f"COMMAND: `{command}`\n\n"
                "Reply JSON only: {\"safe\": boolean, \"reason\": \"short explanation\"}"
            )
            
            client = await self.state.get_http_client()
            url = f"{self.state.gateway_base}/v1/chat/completions"
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "max_tokens": 100
            }
            
            resp = await client.post(url, json=payload, timeout=3.0) # Strict timeout
            
            if resp.status_code != 200:
                # Fail Closed if Audit Fails
                return False, f"Audit Error ({resp.status_code})"
                
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            
            # Simple parsing
            if '"safe": true' in content.lower() or "'safe': true" in content.lower():
                return True, "Tier 3: Audited Safe"
            else:
                reason = "Unknown Risk"
                if "reason" in content:
                    try:
                        obj = json.loads(content)
                        reason = obj.get("reason", reason)
                    except: pass
                return False, f"Tier 3 FLAGGED: {reason}"

        except Exception as e:
            logger.error(f"Sentinel LLM Check Failed: {e}")
            return False, "Sentinel Offline"

    async def _sync_from_db(self):
        """
        Pull latest rules from SurrealDB (Source of Truth) and update local cache.
        """
        try:
            # We use the generic tool_query_surreal pattern mentally, but implement directly here via HTTP
            # Table: sentinel_rules
            base_url = self.state.config.get("surreal", {}).get("url", "http://localhost:8000")
            ns = os.getenv("SURREAL_NS", "orchestrator")
            db = os.getenv("SURREAL_DB", "memory")
            auth = (os.getenv("SURREAL_USER", "root"), os.getenv("SURREAL_PASS", "root"))
            
            client = await self.state.get_http_client()
            
            # Fetch all rules
            query = f"USE NS {ns}; USE DB {db}; SELECT * FROM sentinel_rules;"
            url = f"{base_url}/sql"
            headers = {"Accept": "application/json", "ns": ns, "db": db}
            
            resp = await client.post(url, content=query, auth=auth, headers=headers, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                # Parse result... (Surreal returns list of results for each query statement)
                rows = []
                for res in data:
                    if res.get("status") == "OK" and isinstance(res.get("result"), list):
                        rows = res.get("result")
                        
                if rows:
                    # Rebuild cache structure
                    new_cache = {"approved": [], "blocked": []}
                    for r in rows:
                        target = "approved" if r.get("allowed") else "blocked"
                        new_cache[target].append(r)
                    
                    self._memory_cache = new_cache
                    self._save_memory() # Update local cache file
                    logger.info(f"Sentinel Synced {len(rows)} rules from DB.")
                    
        except Exception as e:
            logger.warning(f"Sentinel DB Sync Failed (Using Local Cache): {e}")

    async def learn_pattern(self, pattern: str, allowed: bool, reason: str):
        """Dual-Write: Persist to SurrealDB (Primary) and Local File (Cache)."""
        # 1. Update Local
        target = "approved" if allowed else "blocked"
        entry = {
            "pattern": pattern,
            "allowed": allowed,
            "reason": reason,
            "added_at": str(self.state.started_at),
            "source": "manual_override"
        }
        self._memory_cache[target].append(entry)
        self._save_memory()
        
        # 2. Write to DB
        try:
             base_url = self.state.config.get("surreal", {}).get("url", "http://localhost:8000")
             ns = os.getenv("SURREAL_NS", "orchestrator")
             db = os.getenv("SURREAL_DB", "memory")
             auth = (os.getenv("SURREAL_USER", "root"), os.getenv("SURREAL_PASS", "root"))
             
             # Create Record
             table = "sentinel_rules"
             query = f"USE NS {ns}; USE DB {db}; CREATE {table} CONTENT {json.dumps(entry)};"
             
             client = await self.state.get_http_client()
             url = f"{base_url}/sql"
             headers = {"Accept": "application/json", "ns": ns, "db": db}
             
             await client.post(url, content=query, auth=auth, headers=headers, timeout=5.0)
             logger.info(f"Sentinel DB Write Success: {pattern}")
             
        except Exception as e:
            logger.error(f"Sentinel DB Write Failed: {e}")
            
        logger.info(f"Sentinel LEARNED: {target.upper()} -> {pattern}")
