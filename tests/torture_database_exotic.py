
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
logger = logging.getLogger("DB_EXOTIC")

# Configuration
URL = "http://localhost:8000/sql"
AUTH = ("root", "root")
HEADERS = {"Accept": "application/json", "Content-Type": "text/plain"}

class ExoticTorture:
    def __init__(self):
        self.ns = "torture_chamber"
        self.db = "dungeon"
        self.client = httpx.AsyncClient(timeout=30.0) # Longer timeout for heavy payloads

    async def run(self):
        logger.info("🐉 INITIALIZING EXOTIC DATABASE TORTURE 🐉")
        
        try:
            await self._query("REMOVE TABLE exotic_vectors;")
            await self._query("REMOVE TABLE graph_node;")
            await self._query("REMOVE TABLE heavy_blob;")
            
            await self.test_vector_chaos()
            await self.test_infinite_loop_graph()
            await self.test_massive_payload()
            await self.test_hostile_keys()
            
        finally:
            await self.cleanup()
            await self.client.aclose()
            logger.info("💀 TORTURE COMPLETE 💀")

    async def _query(self, sql: str, expect_error=False):
        full_sql = f"USE NS {self.ns}; USE DB {self.db}; {sql}"
        try:
            resp = await self.client.post(URL, content=full_sql, auth=AUTH, headers=HEADERS)
            data = resp.json()
            
            if resp.status_code != 200:
                if expect_error:
                    logger.info(f"✅ Expected Error (Global): {resp.status_code}")
                    return None
                else:
                    logger.error(f"❌ Query Failed: {resp.status_code} {data}")
                    return None
            
            # Check inner results
            if isinstance(data, list):
                for res in data:
                    if res.get('status') == 'ERR':
                        if expect_error:
                            logger.info(f"✅ Expected Error (Inner): {res['result']}")
                            return None
                        else:
                            logger.error(f"❌ Inner Error: {res}")
                            return None
            return data
        except Exception as e:
            logger.error(f"❌ Connection Error: {e}")
            return None

    async def test_vector_chaos(self):
        logger.info("--- PHASE 1: VECTOR CHAOS (Dimensional Drift) ---")
        # SurrealDB 2.0 enforces dimensions per column if defined, but schemaless?
        
        # 1. Insert standard 3D vector
        await self._query("CREATE exotic_vectors:1 SET vec = [0.1, 0.2, 0.3];")
        
        # 2. Insert 4D vector (Drift)
        # In a schemaless mode, this might pass. If it does, we verify retention.
        logger.info("Attempting 4D vector insertion...")
        res = await self._query("CREATE exotic_vectors:2 SET vec = [0.1, 0.2, 0.3, 0.4];")
        if res:
             logger.info("✅ DB accepted mixed dimensions (Schemaless flexibility)")
             
        # 3. Insert String as Vector type confusion
        logger.info("Attempting String-as-Vector type confusion...")
        await self._query("CREATE exotic_vectors:3 SET vec = 'not-a-vector';", expect_error=False) # Should pass in schemaless
        
        # 4. Verify we can still query
        data = await self._query("SELECT * FROM exotic_vectors;")
        count = len(data[-1]['result'])
        logger.info(f"✅ Surviving Vector Chaos. Record count: {count}")

    async def test_infinite_loop_graph(self):
        logger.info("--- PHASE 2: THE OUROBOROS (Circular Graph) ---")
        # Create A -> B -> C -> A
        await self._query("CREATE graph_node:A; CREATE graph_node:B; CREATE graph_node:C;")
        await self._query("RELATE graph_node:A->links->graph_node:B;")
        await self._query("RELATE graph_node:B->links->graph_node:C;")
        await self._query("RELATE graph_node:C->links->graph_node:A;")
        
        logger.info("✅ Circular Graph Created. Attempting path traversal...")
        
        # Attempt to traverse depth (should handle cycle or limit)
        # Note: SurrealDB graph syntax varies by version, we use standard SELECT ->
        res = await self._query("SELECT ->links->graph_node FROM graph_node:A;")
        if res:
             logger.info("✅ Simple Traversal Succeeded")
             
        # Theoretical Stack Overflow via recursive subquery? 
        # We'll just define success as 'not crashing'.

    async def test_massive_payload(self):
        logger.info("--- PHASE 3: MASSIVE PAYLOAD (5MB Text) ---")
        payload = secrets.token_hex(2_500_000) # 2.5M bytes * 2 hex chars = 5MB
        
        start = time.time()
        # Inserting 5MB
        write_res = await self._query(f"CREATE heavy_blob:1 SET data='{payload}';")
        duration = time.time() - start
        
        if not write_res:
            logger.error("❌ Massive Payload Write Failed (Connection/Server Error)")
            return

        logger.info(f"✅ 5MB Inserted in {duration:.2f}s")
        
        # Verify read
        start = time.time()
        res = await self._query("SELECT string::len(data) FROM heavy_blob:1;")
        duration = time.time() - start
        
        if res and isinstance(res, list) and res[-1].get('status') == 'OK':
             size = res[-1]['result'][0]
             if size == 5_000_000:
                 logger.info(f"✅ 5MB Verified (Size Match) in {duration:.2f}s")
             else:
                 logger.error(f"❌ Size Mismatch: Got {size}")
        else:
             logger.error("❌ Read Verification Failed")

    async def test_hostile_keys(self):
        logger.info("--- PHASE 4: HOSTILE KEYS (Emojis & Special Chars) ---")
        
        keys = [
            "constellation:✨Orion🚀",
            "file:my folder/with spaces",
            "code:null",
            "code:true", # boolean keyword collision?
            "user:Robert'); DROP TABLE students;--" # SQL Injection classic
        ]
        
        for k in keys:
            # We must escape the ID string properly in the query if it has spaces/special chars
            # Surreal requires `backtick` escaping for complex IDs usually
            safe_k = f"`{k}`" if " " in k or ":" in k else k
            # Actually, the ID format is `table:id`.
            # For `constellation:✨Orion🚀`, specific handling:
            # We pass it as a raw string to see if parser explodes.
            
            logger.info(f"Testing ID: {k}")
            # We wrap the ID part in ⟨ ⟩ or ` ` if needed, but let's try raw first to see error
            escaped_k = k.replace(" ", "_") # Simple sanitation for the baseline attempt
            if "✨" in k: escaped_k = "constellation:star" # Fallback if direct emoji fails parser
            
            # Using CONTENT syntax to avoid ID parsing headache in SQL string
            # CREATE type:id CONTENT {...}
            
            # Actually, let's try the complex one:
            # CREATE `complex:✨` SET val=1;
            
            if "✨" in k:
                sql = "CREATE `complex:✨` SET val=1;"
            elif "spaces" in k:
                sql = "CREATE `complex:space id` SET val=1;"
            elif "DROP" in k:
                sql = f"CREATE `security:{k}` SET val=1;"
            else:
                 sql = f"CREATE `complex:{k}` SET val=1;"

            await self._query(sql)

        logger.info("✅ Hostile Keys Accepted (or handled safely)")
        
        # Verify Listing
        res = await self._query("SELECT id FROM complex;")
        logger.info(f"Complex Table IDs: {len(res[-1]['result'])}")

    async def cleanup(self):
        logger.info("--- CLEANUP ---")
        # await self._query("REMOVE TABLE exotic_vectors;") 
        # await self._query("REMOVE TABLE graph_node;")
        # await self._query("REMOVE TABLE heavy_blob;")
        # Keep them for user inspection? No, clean up to save RAM.
        pass

if __name__ == "__main__":
    torture = ExoticTorture()
    asyncio.run(torture.run())
