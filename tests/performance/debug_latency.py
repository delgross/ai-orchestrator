
import asyncio
import time
import httpx
import random
import logging
import json

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("latency_debug")

GATEWAY_URL = "http://127.0.0.1:5455" # Router/Gateway
SURREAL_SQL_URL = "http://127.0.0.1:8000/sql"
SURREAL_NS = "antigravity"
SURREAL_DB = "brain"
SURREAL_AUTH = ("root", "root")

SAMPLE_TEXT = "The quick brown fox jumps over the lazy dog."

async def test_embedding_latency():
    logger.info("--- TESTING EMBEDDING LATENCY (Ollama via Gateway) ---")
    async with httpx.AsyncClient() as client:
        # Warmup
        headers = {"Authorization": "Bearer 9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic"}
        await client.post(f"{GATEWAY_URL}/v1/embeddings", json={"input": "warmup", "model": "mxbai-embed-large"}, headers=headers)
        
        latencies = []
        for i in range(5):
            t0 = time.time()
            resp = await client.post(f"{GATEWAY_URL}/v1/embeddings", json={
                "input": SAMPLE_TEXT,
                "model": "mxbai-embed-large"
            }, headers=headers)
            dt = time.time() - t0
            if resp.status_code == 200:
                latencies.append(dt)
                logger.info(f"Embed #{i+1}: {dt:.4f}s")
            else:
                logger.error(f"Embed #{i+1} Failed: {resp.status_code} {resp.text}")
                
        avg = sum(latencies)/len(latencies) if latencies else 0
        logger.info(f"AVG EMBEDDING LATENCY: {avg:.4f}s")
        return latencies[0] if latencies else 0

async def test_surreal_indexing_latency():
    logger.info("\n--- TESTING SURREALDB INDEXING LATENCY ---")
    
    # Generate a dummy vector (1024 float32)
    dummy_vector = [random.random() for _ in range(1024)]
    
    async with httpx.AsyncClient() as client:
        latencies = []
        for i in range(5):
            unique_id = f"debug_bench_{i}"
            
            # SQL: Insert with Vector
            sql = f"""
            USE NS {SURREAL_NS} DB {SURREAL_DB};
            CREATE chunk SET 
                content = 'debug content {i}',
                embedding = $emb,
                kb_id = 'bench_kb',
                timestamp = time::now();
            """
            
            t0 = time.time()
            resp = await client.post(
                SURREAL_SQL_URL, 
                content=sql, 
                auth=SURREAL_AUTH,
                headers={"Accept": "application/json", "NS": SURREAL_NS, "DB": SURREAL_DB} 
                # Note: creating 'params' via string interpolation for simplicity in this bench logic
                # For strictly correct JSON handling we'd use LET, but here we just want to measure the INSERT overhead.
                # Actually proper protocol:
            )
            
            # RAGServer approach uses LET $emb = [...]
            # Let's mimic that to be fair
            payload = f"""
            USE NS {SURREAL_NS} DB {SURREAL_DB};
            LET $emb = {json.dumps(dummy_vector)};
            CREATE chunk SET content = 'bench {i}', embedding = $emb, kb_id = 'bench_kb';
            """
            
            t0 = time.time()
            resp = await client.post(SURREAL_SQL_URL, content=payload, auth=SURREAL_AUTH, headers={"Accept": "application/json"})
            dt = time.time() - t0
            
            if resp.status_code == 200:
                latencies.append(dt)
                logger.info(f"DB Insert #{i+1}: {dt:.4f}s")
            else:
                 logger.error(f"DB Insert #{i+1} Failed: {resp.status_code} {resp.text}")

        avg = sum(latencies)/len(latencies) if latencies else 0
        logger.info(f"AVG DB INSERT LATENCY: {avg:.4f}s")


async def test_search_consistency():
    logger.info("\n--- TESTING SEARCH CONSISTENCY (Read-After-Write) ---")
    
    # Generate a dummy vector
    dummy_vector = [random.random() for _ in range(1024)]
    unique_content = f"consistency_check_{time.time()}"
    
    async with httpx.AsyncClient() as client:
        # 1. INSERT
        t0 = time.time()
        # Note: We must include 'kb_id' and correct 'content' to match query params
        payload = f"""
        USE NS {SURREAL_NS} DB {SURREAL_DB};
        LET $emb = {json.dumps(dummy_vector)};
        CREATE chunk SET content = '{unique_content}', embedding = $emb, kb_id = 'bench_kb';
        """
        await client.post(SURREAL_SQL_URL, content=payload, auth=SURREAL_AUTH, headers={"Accept": "application/json"})
        write_time = time.time() - t0
        logger.info(f"Write Time: {write_time:.4f}s")
        
        # 2. SEARCH IMMEDIATELY
        # We use a query that mimics _run_keyword_search (CONTAINS) first, then Vector
        
        # Test A: Keyword Search (CONTAINS)
        start_probe = time.time()
        found = False
        attempts = 0
        while time.time() - start_probe < 5.0:
            attempts += 1
            sql = f"""
            USE NS {SURREAL_NS} DB {SURREAL_DB};
            SELECT * FROM chunk WHERE kb_id = 'bench_kb' AND content CONTAINS '{unique_content}';
            """
            resp = await client.post(SURREAL_SQL_URL, content=sql, auth=SURREAL_AUTH, headers={"Accept": "application/json"})
            data = resp.json()
            # Parse result
            if isinstance(data, list) and data:
                res = data[-1].get("result", [])
                if res:
                    found = True
                    break
            await asyncio.sleep(0.05) # 50ms polling
            
        latency = time.time() - start_probe
        if found:
            logger.info(f"KEYWORD SEARCH (CONTAINS): Found in {latency:.4f}s ({attempts} attempts)")
        else:
            logger.error(f"KEYWORD SEARCH (CONTAINS): Failed to find after 5s")

        # Test B: Vector Search
        # We search using the SAME vector. Distance should be 0.
        start_probe = time.time()
        found = False
        attempts = 0
        while time.time() - start_probe < 5.0:
            attempts += 1
            sql = f"""
            USE NS {SURREAL_NS} DB {SURREAL_DB};
            LET $target = {json.dumps(dummy_vector)};
            SELECT *, vector::distance::euclidean(embedding, $target) AS dist 
            FROM chunk 
            WHERE kb_id = 'bench_kb' 
            ORDER BY dist ASC LIMIT 1;
            """
            resp = await client.post(SURREAL_SQL_URL, content=sql, auth=SURREAL_AUTH, headers={"Accept": "application/json"})
            data = resp.json()
            if isinstance(data, list) and data:
                 last_res = data[-1]
                 res = last_res.get("result", [])
                 # logger.info(f"DEBUG VECTOR RES: {res}")
                 if res and isinstance(res, list) and len(res) > 0:
                     item = res[0]
                     if isinstance(item, dict) and item.get("content") == unique_content:
                         found = True
                         break
                     elif isinstance(item, str): 
                         # Edge case: sometimes selects return IDs?
                         logger.warning(f"Got string result: {item}")
            await asyncio.sleep(0.05)
            
        latency = time.time() - start_probe
        if found:
            logger.info(f"VECTOR SEARCH (HNSW): Found in {latency:.4f}s ({attempts} attempts)")
        else:
            logger.error(f"VECTOR SEARCH (HNSW): Failed to find after 5s")

if __name__ == "__main__":
    import asyncio
    async def main():
        await test_embedding_latency()
        await test_surreal_indexing_latency()
        await test_search_consistency()
    asyncio.run(main())
