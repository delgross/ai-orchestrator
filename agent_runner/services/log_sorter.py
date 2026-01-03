
import asyncio
import logging
import os
import time
import httpx
from typing import List, Dict, Any
from common.lexicon import LexiconRegistry

logger = logging.getLogger("agent_runner.services.log_sorter")

class LogSorterService:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        self.interval = 5.0 # Seconds
        self.registry = LexiconRegistry(
            config_dir=os.path.join(os.getcwd(), "config", "lexicons")
        )
        # Database configs
        self.surreal_url = config.get("surreal", {}).get("url", "http://localhost:8000")
        self.surreal_ns = os.getenv("SURREAL_NS", "orchestrator")
        self.surreal_db = os.getenv("SURREAL_DB", "memory")
        self.surreal_auth = (os.getenv("SURREAL_USER", "root"), os.getenv("SURREAL_PASS", "root"))
        
        # Resilience State (Phase 3.5)
        self._seen_hashes = {}
        self._llm_semaphore = asyncio.Semaphore(2)
        self._cb_open = False
        self._cb_failures = 0
        self._cb_last_failure = 0.0
        print(f"DEBUG_SORTER: Init complete. URL={self.surreal_url}")

    async def start(self):
        """Start the background sorting loop."""
        print("DEBUG_SORTER: Start called.")
        if self.running:
            return
        self.running = True
        logger.info("LogSorter Service started.")
        asyncio.create_task(self._loop())

    async def stop(self):
        self.running = False
        logger.info("LogSorter Service stopping...")

    async def _loop(self):
        while self.running:
            try:
                await self._process_batch()
            except Exception as e:
                logger.error(f"Error in LogSorter loop: {e}", exc_info=True)
            
            await asyncio.sleep(self.interval)

    async def _process_batch(self):
        # 1. Fetch unhandled logs
        # Embed USE statement to ensure correct namespace
        query = f"USE NS {self.surreal_ns}; USE DB {self.surreal_db}; SELECT * FROM diagnostic_log WHERE handled IS NONE ORDER BY timestamp ASC LIMIT 50;"
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Accept": "application/json", 
                "Content-Type": "text/plain"
            }
            
            try:
                resp = await client.post(
                    f"{self.surreal_url}/sql",
                    content=query, 
                    auth=self.surreal_auth,
                    headers=headers,
                    timeout=5.0
                )
                if resp.status_code != 200: return
                data = resp.json()
                
                # Surreal returns one result object per statement. 
                # We sent 3 statements (USE, USE, SELECT).
                # We expect the 3rd result (index 2) to contain our logs.
                # Use flexible logic to find 'diagnostic_log' results or just take the last one.
                
                results = []
                # Find the result that has 'result' list
                for item in data:
                    if item.get("status") == "OK" and isinstance(item.get("result"), list):
                        # This works for SELECT. USE returns null or string?
                         res_list = item.get("result", [])
                         if res_list:
                             results = res_list
                             break
                
                if not results: return
            except Exception as e:
                logger.error(f"Fetch failed: {e}")
                return

            # 2. Process logs
            updates = []
            
            # Stream File
            stream_path = os.path.join(os.getcwd(), "logs", "live_stream.md")
            os.makedirs(os.path.dirname(stream_path), exist_ok=True)
            
            with open(stream_path, "a") as sf:
                for log_entry in results:
                    log_id = log_entry["id"]
                    msg = log_entry.get("message", "")
                    service = log_entry.get("service", "unknown")
                    timestamp = log_entry.get("timestamp", "")
                    
                    # Classify
                    result = self.registry.classify(service, msg)
                    
                    if result.label != "NOISE":
                        # --- FAST LANE (Known Signal) ---
                        # 1. Output to Stream
                        sf.write(f"{timestamp} {result.formatted_message}\n")
                        
                        # 2. Mark handled
                        updates.append(f"UPDATE {log_id} SET handled = true, classification = '{result.label}', severity = '{result.severity}', needs_review = false;")
                        
                        # 3. Trigger Context Snapshot if CRITICAL (Future Phase)
                        if result.severity == "CRITICAL":
                            asyncio.create_task(self._capture_context(log_id))
                            
                    else:
                        # --- SLOW LANE (Unknown / Noise) ---
                        # 1. Output to Stream (Visual Feedback for Unknowns)
                        sf.write(f"{timestamp} [UNKNOWN] {msg}\n")

                        # 2. Mark for Review
                        updates.append(f"UPDATE {log_id} SET handled = true, classification = 'UNKNOWN', needs_review = true;")
                        
                        # 3. Trigger Async Analysis (Throttle logic needed here, for now just fire)
                        # We only analyze unique unknowns to save cost.
                        asyncio.create_task(self._analyze_unknown(log_id, msg))

            # 3. Execute DB Updates
            if updates:
                # Prepend USE statement
                batch_query = f"USE NS {self.surreal_ns}; USE DB {self.surreal_db};\n" + "\n".join(updates)
                try:
                    await client.post(
                        f"{self.surreal_url}/sql",
                        content=batch_query,
                        auth=self.surreal_auth,
                        headers=headers, # Reuse headers (Content-Type: text/plain)
                        timeout=5.0
                    )
                except Exception as e:
                    logger.error(f"Failed to update log status: {e}")

    async def _capture_context(self, log_id: str):
        """Placeholder for Snapshot Logic"""
        pass

    async def _analyze_unknown(self, log_id: str, msg: str):
        """Async LLM Analysis for Unknowns (Resilient & Local Only)"""
        import hashlib
        
        # 0. Deduplication (Phase 3.5)
        msg_hash = hashlib.md5(msg.encode()).hexdigest()
        curr_time = time.time()
        
        # Clean old cache
        self._seen_hashes = {h: t for h, t in self._seen_hashes.items() if curr_time - t < 600}
        
        if msg_hash in self._seen_hashes:
            logger.debug(f"Skipping duplicate analysis for {log_id}")
            return
        self._seen_hashes[msg_hash] = curr_time

        # 1. Circuit Breaker Check (Phase 3.5)
        if self._cb_open:
            if curr_time - self._cb_last_failure > 60.0:
                logger.info("Circuit Breaker Half-Open: Retrying LLM...")
                self._cb_open = False
                self._cb_failures = 0
            else:
                logger.warning(f"Circuit Breaker OPEN. Skipping analysis for {log_id}.")
                return

        # 2. Concurrency Limit (Phase 3.5)
        if self._llm_semaphore.locked():
             logger.warning("LLM Busy (Concurrency Limit Reached). Dropping analysis.")
             return

        async with self._llm_semaphore:
            # 3. Privacy / "Never Remote" Enforcement (Phase 3.6)
            # We bypass the Gateway entirely to ensure NO billing risk.
            target_url = "http://localhost:11434/v1/chat/completions" 
            
            # Use local model only (Prefer Env/DB < Config < Default)
            env_model = os.getenv("FALLBACK_MODEL")
            cfg_model = self.config.get("agent_runner", {}).get("fallback", {}).get("model")
            
            # Default to Mistral (7B) if nothing else is set, instead of 70B
            model = env_model or cfg_model or "ollama:mistral:latest"
            
            if model.startswith("ollama:"): model = model.replace("ollama:", "")
            
            prompt = (
                f"You are the System Diagnostician.\n"
                f"A new anomaly occurred in the system.\n"
                f"Log Message: {msg}\n\n"
                f"Task: Explain the potential cause and suggest 1 command to fix or verify it. "
                f"Be extremely concise (max 20 words)."
            )
            
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": prompt}],
                "stream": False
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(target_url, json=payload, timeout=45.0)
                    
                    if resp.status_code == 200:
                        analysis = resp.json()['choices'][0]['message']['content'].strip()
                        
                        # Append to Stream
                        stream_path = os.path.join(os.getcwd(), "logs", "live_stream.md")
                        with open(stream_path, "a") as sf:
                            sf.write(f"\n    ↳ 🧠 [AI Insight] {analysis}\n\n")
                            
                        logger.info(f"Analyzed Anomaly: {log_id} via Local Ollama")
                        # Reset Circuit Breaker on Success
                        self._cb_failures = 0
                        
                    else:
                        logger.warning(f"Local LLM Failed: {resp.status_code} {resp.text}")
                        self._cb_failures += 1
                        
            except Exception as e:
                logger.error(f"Local LLM Connection Error: {e}")
                self._cb_failures += 1
                self._cb_last_failure = curr_time
            
            # Trip Circuit Breaker?
            if self._cb_failures >= 5:
                self._cb_open = True
                self._cb_last_failure = time.time()
                logger.critical("Circuit Breaker TRIPPED. Pausing LLM analysis for 60s.")

