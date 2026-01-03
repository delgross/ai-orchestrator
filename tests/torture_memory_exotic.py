
import asyncio
import httpx
import time
import random
import logging
import json
import secrets

# Setup Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MEM_TORTURE")

# RAG Server Configuration
URL_BASE = "http://localhost:5555"
ADD_TXT_URL = f"{URL_BASE}/ingest"
QUERY_URL = f"{URL_BASE}/query"
GRAPH_URL = f"{URL_BASE}/graph/snapshot"
AUTH = ("root", "root") # RAG Server might not use basic auth, but depends on middleware. usually internal.

class MemoryTorture:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0) # High timeout for heavy ops

    async def run(self):
        logger.info("🧠 INITIALIZING EXOTIC MEMORY TORTURE 🧠")
        
        try:
            # Verify Server Up
            try:
                await self.client.get(f"{URL_BASE}/health")
                logger.info("✅ RAG Server is UP")
            except Exception:
                logger.critical("❌ RAG Server DOWN. Aborting.")
                return

            await self.test_the_blob()
            await self.test_semantic_density()
            await self.test_supernode_stress()
            
        finally:
            await self.client.aclose()
            logger.info("💀 MEMORY TORTURE COMPLETE 💀")

    async def test_the_blob(self):
        logger.info("--- PHASE 1: THE BLOB (Chunking Stress) ---")
        # Generate 1MB of continuous non-spaced text (worst case for splitters that rely on spaces)
        # Using a repeating pattern to make it compressible but logically annoying
        base = "Supercalifragilisticexpialidocious" 
        blob = base * (30000) # ~1MB
        
        logger.info(f"Generated Blob of size: {len(blob)} bytes")
        
        start = time.time()
        payload = {
            "content": blob,
            "filename": "torture_blob.txt",
            "kb_id": "torture_kb"
        }
        
        try:
            resp = await self.client.post(ADD_TXT_URL, json=payload)
            duration = time.time() - start
            
            if resp.status_code == 200:
                logger.info(f"✅ The Blob Ingested in {duration:.2f}s")
            else:
                logger.error(f"❌ The Blob Rejected: {resp.status_code} {resp.text}")
        except httpx.ReadTimeout:
            logger.error("❌ The Blob Timed Out (>60s). Client-side chunking required.")
        except Exception as e:
            logger.error(f"❌ The Blob Failed: {e}")

    async def test_semantic_density(self):
        logger.info("--- PHASE 2: SEMANTIC DENSITY (Vector Discrimination) ---")
        # Ingest 50 facts that are VERY similar
        base_fact = "The quick brown fox jumps over the lazy dog."
        variations = []
        for i in range(50):
            # Change one word slightly
            variations.append(f"The quick brown fox jumps over the lazy dog version {i}.")
            
        logger.info(f"Ingesting {len(variations)} similar vectors...")
        start = time.time()
        for idx, var in enumerate(variations):
            payload = {
                "content": var,
                "filename": f"density_{idx}.txt",
                "kb_id": "torture_kb"
            }
            await self.client.post(ADD_TXT_URL, json=payload)
            
        duration = time.time() - start
        logger.info(f"✅ Ingested similar vectors in {duration:.2f}s")
        
        logger.info("Sleeping 5s for Vector Indexing...")
        await asyncio.sleep(5)
        
        # Query for specific one
        q = "The quick brown fox jumps over the lazy dog version 25."
        logger.info(f"Querying: '{q}'")
        
        resp = await self.client.post(QUERY_URL, json={"query": q, "kb_id": "torture_kb", "limit": 5})
        data = resp.json()
        
        if "results" in data and len(data["results"]) > 0:
            top_match = data["results"][0]["content"]
            logger.info(f"Top Match: {top_match}")
            if "version 25" in top_match:
                 logger.info("✅ Semantic Discrimination Successful")
            else:
                 logger.warning("⚠️ Semantic Discrimination Drifted (Top match wrong)")
        else:
             logger.error("❌ No results found")

    async def test_supernode_stress(self):
        logger.info("--- PHASE 3: SUPERNODE STRESS (Graph Limits) ---")
        # We need an endpoint that creates entities/relations.
        # Assuming RAG server extracts them, OR we can abuse `add_text` with strongly structured data 
        # that forces entity extraction if the LLM is smart, BUUUT we don't want to pay LLM costs.
        # Check if there is a direct graph endpoint? 
        # Current RAG Server might not have direct graph write API exposed publicly.
        
        # ALTERNATIVE: We use `torture_database_exotic.py` logic but aimed at RAG context...
        # Actually RAG server uses the DB. 
        # Let's try to query the graph endpoint for a massive dataset.
        
        logger.info("Querying Graph Endpoint for large result set...")
        start = time.time()
        resp = await self.client.get(f"{GRAPH_URL}?limit=1000")
        duration = time.time() - start
        
        if resp.status_code == 200:
            nodes = len(resp.json().get("nodes", []))
            lines = len(resp.json().get("links", []))
            logger.info(f"✅ Graph Retrieved in {duration:.2f}s (Nodes: {nodes}, Links: {lines})")
        else:
            logger.error(f"❌ Graph Query Failed: {resp.status_code}")

if __name__ == "__main__":
    torture = MemoryTorture()
    asyncio.run(torture.run())
