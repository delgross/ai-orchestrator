
import asyncio
import aiohttp
import time
import random
import argparse
import sys
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("torture_test")

# Target RAG Server
RAG_URL = "http://127.0.0.1:5555" # Default
# Configurable via args

# Test Data Generation
SAMPLE_WORDS = ["apple", "banana", "cherry", "omega", "alpha", "vector", "embedding", "neural", "synapse", "quantum", "flux", "capacitor", "blue", "red", "green", "code", "secret", "agent", "router", "protocol"]

def generate_sentence():
    return " ".join(random.choices(SAMPLE_WORDS, k=10))

# Metrics
stats = {
    "ingests_sent": 0,
    "ingests_ok": 0,
    "ingests_failed": 0,
    "queries_sent": 0,
    "queries_ok": 0,
    "queries_failed": 0,
    "total_latency": 0.0
}

async def torture_ingest(session, worker_id, count, url):
    for i in range(count):
        content = f"TORTURE_TEST_{worker_id}_{i}: {generate_sentence()}"
        payload = {
            "content": content,
            "kb_id": "torture_kb",
            "filename": f"torture_{worker_id}_{i}.txt",
            "metadata": {"source": "torture_script", "worker": worker_id}
        }
        
        t0 = time.time()
        try:
            stats["ingests_sent"] += 1
            async with session.post(f"{url}/ingest", json=payload) as resp:
                if resp.status == 200:
                    stats["ingests_ok"] += 1
                else:
                    stats["ingests_failed"] += 1
                    logger.error(f"Ingest {i} failed: {resp.status}")
        except Exception as e:
            stats["ingests_failed"] += 1
            logger.error(f"Ingest error: {e}")
        finally:
            dt = time.time() - t0
            stats["total_latency"] += dt
            
        if i % 10 == 0:
            logger.info(f"Worker {worker_id} ingested {i}/{count}")
            
async def torture_query(session, worker_id, count, url):
    for i in range(count):
        query_text = random.choice(SAMPLE_WORDS)
        payload = {
            "query": query_text,
            "kb_id": "torture_kb",
            "limit": 5
        }
        
        try:
            stats["queries_sent"] += 1
            async with session.post(f"{url}/query", json=payload) as resp:
                if resp.status == 200:
                    stats["queries_ok"] += 1
                else:
                    stats["queries_failed"] += 1
        except Exception as e:
            stats["queries_failed"] += 1
            logger.error(f"Query error: {e}")
            
        await asyncio.sleep(random.random() * 0.1) # Slight jitter

async def run_torture(args):
    target_url = args.url or RAG_URL
    logger.info(f"Starting TORTURE TEST against {target_url}")
    logger.info(f"Workers: {args.workers}, Items/Worker: {args.items}")
    
    async with aiohttp.ClientSession() as session:
        # Check health first
        try:
            async with session.get(f"{target_url}/health") as resp:
                if resp.status == 200:
                    logger.info("Target is HEALTHY")
                else:
                    logger.critical(f"Target is UNHEALTHY: {resp.status}")
                    if not args.force:
                        return
        except Exception as e:
            logger.critical(f"Cannot enable target: {e}")
            return

        tasks = []
        # Ingest Workers
        for w in range(args.workers):
            tasks.append(torture_ingest(session, f"ingest_{w}", args.items, target_url))
            
        # Query Workers (load items * 2)
        for w in range(args.workers):
            tasks.append(torture_query(session, f"query_{w}", args.items, target_url))
            
        start_time = time.time()
        await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        logger.info("--- TORTURE REPORT ---")
        logger.info(f"Duration: {duration:.2f}s")
        logger.info(f"Ingests: {stats['ingests_ok']}/{stats['ingests_sent']} (Errors: {stats['ingests_failed']})")
        logger.info(f"Queries: {stats['queries_ok']}/{stats['queries_sent']} (Errors: {stats['queries_failed']})")
        logger.info(f"Avg Latency (Ingest): {stats['total_latency']/max(1, stats['ingests_sent']):.4f}s")
        logger.info(f"Throughput: {(stats['ingests_ok'] + stats['queries_ok']) / duration:.2f} req/s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Memory System Torture Test")
    parser.add_argument("--url", default=None, help="RAG Server URL")
    parser.add_argument("--workers", type=int, default=5, help="Concurrent workers")
    parser.add_argument("--items", type=int, default=20, help="Items per worker")
    parser.add_argument("--force", action="store_true", help="Run even if health check fails")
    
    args = parser.parse_args()
    asyncio.run(run_torture(args))
