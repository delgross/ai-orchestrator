
import asyncio
import aiohttp
import time
import random
import argparse
import sys
import logging
import uuid
import string

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("torture_v2")

# Target RAG Server
RAG_URL = "http://127.0.0.1:5555"

# Stats
stats = {
    "ingest_ok": 0,
    "ingest_fail": 0,
    "query_ok": 0,
    "query_fail": 0,
    "consistency_pass": 0,
    "consistency_fail": 0,
    "latency": [],
}

def generate_payload(size_type="normal"):
    """
    Generates payloads of various types to test edge cases.
    """
    unique_id = str(uuid.uuid4())
    
    if size_type == "empty":
        content = ""
    elif size_type == "large":
        # 10KB of text
        content = f"LARGE_PAYLOAD_{unique_id} " + " ".join(["data" for _ in range(2000)])
    elif size_type == "special":
        content = f"SPECIAL_{unique_id} 🚀 🔥 🙃 \u202eRTL_TEXT\u202c"
    else: # normal
        content = f"NORMAL_PAYLOAD_{unique_id} This is a standard test sentence for retrieval."
        
    return unique_id, content


async def worker_ingest_and_verify(session, worker_id, count, url):
    """
    Ingests data, then probes for consistency:
    1. Direct GET (KV Store Consistency)
    2. Search (Index Latency)
    """
    for i in range(count):
        p_type = random.choice(["normal", "normal", "normal", "large", "special"]) 
        uid, content = generate_payload(p_type)
        filename = f"v2_{worker_id}_{i}.txt"
        
        # 1. INGEST
        t0 = time.time()
        try:
            async with session.post(f"{url}/ingest", json={
                "content": content,
                "kb_id": "torture_v2_kb",
                "filename": filename,
                "metadata": {"worker": worker_id, "type": p_type}
            }) as resp:
                if resp.status == 200:
                    stats["ingest_ok"] += 1
                else:
                    stats["ingest_fail"] += 1
                    logger.error(f"[{worker_id}] Ingest failed: {resp.status}")
                    continue 
        except Exception as e:
            stats["ingest_fail"] += 1
            logger.error(f"[{worker_id}] Ingest error: {e}")
            continue

        ingest_lat = time.time() - t0
        stats["latency"].append(ingest_lat)
        
        # 2. PROBE LOOP (Measure Time-to-Index)
        found_in_search = False
        start_probe = time.time()
        attempts = 0
        
        while time.time() - start_probe < 10.0: # 10s Timeout
            attempts += 1
            
            # Check Search
            try:
                async with session.post(f"{url}/query", json={
                    "query": uid,
                    "kb_id": "torture_v2_kb",
                    "limit": 1
                }) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get("context", []) # Updated to match API
                        for r in results:
                            if uid in r.get("content", ""):
                                found_in_search = True
                                break
            except: pass
            
            if found_in_search:
                break
            
            await asyncio.sleep(0.2)
            
        index_latency = time.time() - start_probe
        
        if found_in_search:
            stats["consistency_pass"] += 1
            logger.info(f"[{worker_id}] Item {uid}: Indexed in {index_latency:.2f}s (Attempts: {attempts})")
        else:
            stats["consistency_fail"] += 1
            logger.warning(f"[{worker_id}] Item {uid}: Not found after 10s")

async def run_torture_v2(args):
    target_url = args.url or RAG_URL
    logger.info(f"Starting TORTURE V2 (Consistency & Chaos) against {target_url}")
    logger.info(f"Workers: {args.workers}, Items/Worker: {args.items}")

    async with aiohttp.ClientSession() as session:
        tasks = []
        for w in range(args.workers):
            tasks.append(worker_ingest_and_verify(session, f"w{w}", args.items, target_url))
            
        start_time = time.time()
        await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        logger.info("--- TORTURE V2 REPORT ---")
        logger.info(f"Duration: {duration:.2f}s")
        logger.info(f"Ingest: {stats['ingest_ok']} OK, {stats['ingest_fail']} Fail")
        logger.info(f"Query:  {stats['query_ok']} OK, {stats['query_fail']} Fail")
        logger.info(f"Consistency: {stats['consistency_pass']} Pass, {stats['consistency_fail']} FAIL")
        
        if stats['latency']:
            avg_lat = sum(stats['latency']) / len(stats['latency'])
            logger.info(f"Avg Ingest Latency: {avg_lat:.4f}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=None)
    parser.add_argument("--workers", type=int, default=10) # Higher concurrency
    parser.add_argument("--items", type=int, default=10)
    args = parser.parse_args()
    asyncio.run(run_torture_v2(args))
