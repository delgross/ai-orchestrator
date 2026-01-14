import json
import os
import re
import logging
from agent_runner.db_utils import run_query
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
        # Database is source of truth - sync from DB on init
        # Local JSON is just a performance cache for Tier 2 lookups
        self._load_memory()

    async def initialize(self):
        """Initialize Sentinel by syncing from database (source of truth)."""
        try:
            await self._sync_from_db()
        except Exception as e:
            logger.warning(f"Sentinel DB sync failed on init, using local cache: {e}")
            # Fallback to local cache if DB unavailable
            self._load_memory()

    def _load_memory(self):
        """Load learned patterns from local cache file (fallback only)."""
        if self.lexicon_path.exists():
            try:
                with open(self.lexicon_path, "r") as f:
                    self._memory_cache = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load Sentinel memory from cache: {e}")
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
                "max_tokens": 100,
                "options": {"num_ctx": 32768} # [USER] Expanded Context to 32k
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
        Database is the authoritative source - JSON file is just a performance cache.
        
        NOTE: Cache invalidation framework available in agent_runner/cache_helpers.py
        Future: Integrate with CacheInvalidator for automatic TTL and DB timestamp validation.
        """
        try:
            if not hasattr(self.state, "memory") or not self.state.memory:
                logger.warning("Memory server not available for Sentinel sync")
                return
            
            # Fetch all enabled rules from database
            query = "SELECT * FROM sentinel_rules WHERE enabled = true;"
            rows = await run_query(self.state, query)
            
            if rows:
                # Rebuild cache structure from database
                new_cache = {"approved": [], "blocked": []}
                for r in rows:
                    # Map database fields to cache structure
                    pattern = r.get("pattern", "")
                    action = r.get("action", "allow")  # "allow" or "block"
                    reason = r.get("name", "Database rule")  # Use name as reason
                    
                    entry = {
                        "pattern": pattern,
                        "allowed": (action.lower() == "allow"),
                        "reason": reason,
                        "source": "database"
                    }
                    
                    target = "approved" if entry["allowed"] else "blocked"
                    new_cache[target].append(entry)
                
                self._memory_cache = new_cache
                self._save_memory()  # Update local cache file for fast Tier 2 lookups
                logger.info(f"Sentinel synced {len(rows)} rules from database (source of truth)")
            else:
                logger.debug("No Sentinel rules found in database")
                    
        except Exception as e:
            logger.warning(f"Sentinel DB sync failed (using local cache): {e}", exc_info=True)

    async def learn_pattern(self, pattern: str, allowed: bool, reason: str):
        """
        Learn a new pattern: Write to Database (Primary) then update local cache.
        Database is source of truth - JSON file is just a performance cache.
        """
        if not hasattr(self.state, "memory") or not self.state.memory:
            logger.error("Memory server not available for Sentinel learn_pattern")
            return
        
        try:
            # 1. Write to Database (Source of Truth)
            rule_name = f"pattern_{hash(pattern) % 10000}"  # Generate unique name
            action = "allow" if allowed else "block"
            
            query = """
            UPSERT type::thing('sentinel_rules', $name)
            SET name = $name,
                pattern = $pattern,
                action = $action,
                enabled = true;
            """
            
            await run_query(self.state, query, {
                "name": rule_name,
                "pattern": pattern,
                "action": action
            })
            
            logger.info(f"Sentinel rule written to database: {pattern} -> {action}")
            
            # 2. Update local cache for immediate use (Tier 2 lookups)
            target = "approved" if allowed else "blocked"
            entry = {
                "pattern": pattern,
                "allowed": allowed,
                "reason": reason,
                "source": "database"
            }
            self._memory_cache[target].append(entry)
            self._save_memory()  # Persist cache for fast lookups
            
            logger.info(f"Sentinel LEARNED: {target.upper()} -> {pattern}")
            
        except Exception as e:
            logger.error(f"Sentinel learn_pattern failed: {e}", exc_info=True)
            # Fallback: at least update local cache
            target = "approved" if allowed else "blocked"
            entry = {
                "pattern": pattern,
                "allowed": allowed,
                "reason": reason,
                "source": "local_fallback"
            }
            self._memory_cache[target].append(entry)
            self._save_memory()
