
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
        self.surreal_user = self.surreal_auth[0]
        self.surreal_pass = self.surreal_auth[1]
        
        # Resilience State (Phase 3.5)
        self._seen_hashes = {}
        self._llm_semaphore = asyncio.Semaphore(2)
        self._llm_queue = asyncio.Queue(maxsize=100) # [FIX] Added missing queue
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
        # [BACKPRESSURE] Stop fetching if local queue is busy
        # User requested cap to avoid 62k backlog situations turning into error floods.
        if self._llm_queue.qsize() > 50:
            # Queue is half full (max 100). Let it drain.
            return

        # [LOAD SHEDDING] Immediate Destruction Mode
        shedding_load = self._llm_queue.qsize() > 1000
        
        # 1. Fetch unhandled logs
        # Embed USE statement to ensure correct namespace
        query = f"USE NS {self.surreal_ns}; USE DB {self.surreal_db}; SELECT * FROM diagnostic_log WHERE handled IS NONE ORDER BY timestamp ASC LIMIT 50;"
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.surreal_url}/sql", 
                    content=query, 
                    auth=(self.surreal_user, self.surreal_pass),
                    headers={"Accept": "application/json"}
                )
                
                if resp.status_code != 200:
                    logger.error(f"Failed to fetch logs: {resp.text}")
                    return

                data = resp.json()
                # Surreal returns array of results. Last one is SELECT.
                if not data or not isinstance(data, list):
                    return
                
                # Find the result that has 'result' list
                results = []
                for item in data:
                    if item.get("status") == "OK" and isinstance(item.get("result"), list):
                         res_list = item.get("result", [])
                         if res_list:
                             results = res_list
                             break
                
                if not results: return

                updates = []
                # Stream File
                stream_path = os.path.join(os.getcwd(), "logs", "live_stream.md")
                os.makedirs(os.path.dirname(stream_path), exist_ok=True)
                
                # Ensure we have a valid output file for stream
                sf = open(stream_path, "a")

                ids_to_shred = [] # For Immediate Destruction

                for log_entry in results:
                    log_id = log_entry["id"]
                    msg = log_entry.get("message", "")
                    service = log_entry.get("service", "unknown")
                    timestamp = log_entry.get("timestamp", "")
                    
                    if not log_id: continue

                    if shedding_load:
                        # [LOAD SHEDDING] Bitbucket (Immediate Destruction)
                        # We collect IDs to DELETE them in one go.
                        ids_to_shred.append(log_id)
                        continue

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
                        # QUEUE LLM ANALYSIS instead of firing async task
                        try:
                            self._llm_queue.put_nowait((log_id, msg, timestamp))
                        except asyncio.QueueFull:
                            # If even the queue is full (persistent overload), we drop.
                            logger.warning(f"LogSorter Queue Full. Dropping analysis for {log_id}")

                sf.close()
                
                # Execute Destruction Batch
                if ids_to_shred:
                    # Construct DELETE query
                    # DELETE FROM diagnostic_log WHERE id IN ['diagnostic_log:1', 'diagnostic_log:2']
                    # SurrealDB IDs need to be properly formatted/quoted if complex, but default output usually works.
                    # Safest is update handled=true (archive) but user wants destruction.
                    id_list = ", ".join([f"{uid}" for uid in ids_to_shred]) # IDs come as strings with colons usually
                    delete_query = f"USE NS {self.surreal_ns}; USE DB {self.surreal_db}; DELETE {id_list};"
                    
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            f"{self.surreal_url}/sql", 
                            content=delete_query, 
                            auth=(self.surreal_user, self.surreal_pass),
                             headers={"Accept": "application/json"}
                        )
                    logger.warning(f"[LOAD SHEDDING] Vaporized {len(ids_to_shred)} logs due to overload.")

                # Execute Update Batch
                if updates:
                    update_query = f"USE NS {self.surreal_ns}; USE DB {self.surreal_db}; " + " ".join(updates)
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            f"{self.surreal_url}/sql", 
                            content=update_query, 
                            auth=(self.surreal_user, self.surreal_pass),
                            headers={"Accept": "application/json"}
                        )

        except Exception as e:
            logger.error(f"Failed processing LogSorter batch: {e}")
            # The original code had `return []` here, but it's not needed as this is a void method.
            # Keeping it as a void method.
                

    async def _perform_llm_analysis(self, log_id: str, msg: str):
        """Performs LLM analysis for unknown logs, with resilience."""
        import hashlib
        
        # 0. Deduplication
        msg_hash = hashlib.md5(msg.encode()).hexdigest()
        curr_time = time.time()
        
        # Clean old cache
        self._seen_hashes = {h: t for h, t in self._seen_hashes.items() if curr_time - t < 600}
        
        if msg_hash in self._seen_hashes:
            logger.debug(f"Skipping duplicate analysis for {log_id}")
            return
        self._seen_hashes[msg_hash] = curr_time

        # 1. Circuit Breaker Check
        if self._cb_open:
            if curr_time - self._cb_last_failure > 60.0:
                logger.info("Circuit Breaker Half-Open: Retrying LLM...")
                self._cb_open = False
                self._cb_failures = 0
            else:
                logger.warning(f"Circuit Breaker OPEN. Skipping analysis for {log_id}.")
                return

        # 2. Privacy / "Never Remote" Enforcement
        # We bypass the Gateway entirely to ensure NO billing risk.
        target_url = "http://localhost:11434/v1/chat/completions" 
        
        # DYNAMIC CONFIG LOOKUP:
        model = "llama3.1:latest" # Default
        
        if self.state:
            # Map 'Diagnostician' role to 'healer_model' as per Dashboard convention
            model = getattr(self.state, "healer_model", None) or getattr(self.state, "fallback_model", "llama3.1:latest")
        else:
            # Fallback to static config if state not injected (tests)
            env_model = os.getenv("FALLBACK_MODEL")
            cfg_model = self.config.get("agent_runner", {}).get("fallback", {}).get("model")
            model = env_model or cfg_model or "llama3.1:latest"

        if model.startswith("ollama:"): model = model.replace("ollama:", "")
        
        # Use a simpler prompt structure that Llama 3.1 tends to respect better via API
        # Explicitly telling it NOT to solve math seems to backfire (negative prompting issues).
        # Instead, we give it a persona and a single direct command.
        prompt = (
            f"Analyze this error log:\n{msg}\n\n"
            f"1. OPTIMIZED EXPLANATION (10 words): "
        )
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a serious system administrator. You output only technical analysis."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.0,
                "top_p": 0.9
            }
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
            self._cb_last_failure = time.time()
            logger.critical("Circuit Breaker TRIPPED. Pausing LLM analysis for 60s.")
