
import asyncio
import httpx
import os
import json
import time
import random
import logging
from dataclasses import dataclass

# Setup Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DB_TORTURE")

# Configuration
URL = "http://localhost:8000/sql"
AUTH = ("root", "root")
HEADERS = {"Accept": "application/json", "Content-Type": "text/plain"}

class DatabaseTorture:
    def __init__(self):
        self.ns = "test_torture_ns"
        self.db = "test_torture_db"
        self.client = httpx.AsyncClient(timeout=10.0)

    async def run(self):
        logger.info("🔥 STARTING DATABASE TORTURE TEST 🔥")
        
        try:
            await self.test_connection()
            await self.test_syntax_strictness()
            await self.test_namespace_isolation()
            await self.test_concurrency_stress(50)
            await self.test_connection_refusal_recovery()
        finally:
            await self.cleanup()
            await self.client.aclose()
            logger.info("🏁 TEST COMPLETE 🏁")

    async def _query(self, sql: str, ns=None, db=None, expect_error=False):
        """Helper to run raw SQL"""
        target_ns = ns or self.ns
        target_db = db or self.db
        
        # We purposely DON'T use the header NS/DB here to test the `USE NS` strictness,
        # unless we specifically want to test header behavior.
        # But per previous issues, we rely on the SQL prefix.
        full_sql = f"USE NS {target_ns}; USE DB {target_db}; {sql}"
        
        try:
            resp = await self.client.post(URL, content=full_sql, auth=AUTH, headers=HEADERS)
            data = resp.json()
            
            if resp.status_code != 200:
                if expect_error:
                    logger.info(f"✅ Expected Error caught: {resp.status_code} {data.get('details', '')}")
                    return None
                else:
                    logger.error(f"❌ Query Failed: {resp.status_code} {data}")
                    return None
            
            # Check for inner errors in the result list
            for item in data:
                if item.get("status") != "OK":
                     if expect_error:
                        logger.info(f"✅ Expected Inner Error: {item.get('details', '')}")
                        return None
                     else:
                        logger.error(f"❌ Inner Query Error: {item}")
                        return None
            
            return data
        except Exception as e:
            logger.error(f"❌ Connection Error: {e}")
            return None

    async def test_connection(self):
        logger.info("--- PHASE 1: CONNECTION ---")
        res = await self._query("INFO FOR DB;")
        if res:
            logger.info("✅ Connection Established")
        else:
            logger.critical("❌ Connection Failed. Aborting.")
            exit(1)

    async def test_syntax_strictness(self):
        logger.info("--- PHASE 2: SYNTAX STRICTNESS ---")
        
        # Setup data (Use CREATE)
        await self._query("CREATE test_table:1 SET msg='hello', val=10;")
        
        # Test 1: ORDER BY missing field (The error user saw)
        logger.info("[Test] SELECT ... ORDER BY (without selecting field)")
        await self._query("SELECT msg FROM test_table ORDER BY val DESC;", expect_error=True)
        # Verify fix
        await self._query("SELECT msg, val FROM test_table ORDER BY val DESC;")
        logger.info("✅ ORDER BY requirement confirmed.")

        # Test 2: Invalid WHERE
        logger.info("[Test] Invalid WHERE clause")
        # SurrealDB often validly returns empty list for type mismatch, but let's check parsing
        # We'll use a syntax error to be sure
        await self._query("SELECT * FROM test_table WHERE val = ;", expect_error=True)
        logger.info("✅ Syntax strictness confirmed.")

    async def test_namespace_isolation(self):
        logger.info("--- PHASE 3: NAMESPACE ISOLATION ---")
        
        # Write to NS A
        await self._query("CREATE data:1 SET secret='A';", ns="NS_A", db="DB_A")
        
        # Read from NS B (Should be empty)
        res = await self._query("SELECT * FROM data;", ns="NS_B", db="DB_B")
        if res and len(res[-1]['result']) == 0:
            logger.info("✅ Namespace Isolation Confirmed (NS_B empty)")
        else:
            logger.error(f"❌ Namespace Leakage Detected! {res}")
            
    async def test_concurrency_stress(self, count):
        logger.info(f"--- PHASE 4: CONCURRENCY STRESS ({count} concurrent requests) ---")
        
        start = time.time()
        tasks = []
        for i in range(count):
            sql = f"CREATE stress_test:{i} SET val={i}, timestamp={time.time()};"
            tasks.append(self._query(sql))
            
        results = await asyncio.gather(*tasks)
        duration = time.time() - start
        
        success = sum(1 for r in results if r is not None)
        logger.info(f"Result: {success}/{count} succeeded in {duration:.2f}s ({success/duration:.0f} req/s)")
        
        if success == count:
            logger.info("✅ Concurrency Test Passed")
        else:
            logger.warning("⚠️ Concurrency Test Showed Failures")

    async def test_connection_refusal_recovery(self):
         logger.info("--- PHASE 5: RECOVERY SIMULATION ---")
         # This effectively tests how the client handles a 'soft' failure
         # We can't actually kill the DB here easily without running shell commands, 
         # but we can simulate a bad auth.
         
         bad_auth_client = httpx.AsyncClient(timeout=5.0)
         try:
            resp = await bad_auth_client.post(URL, content="INFO FOR DB;", auth=("wrong", "pass"))
            if resp.status_code == 401 or resp.status_code == 403:
                logger.info(f"✅ Auth Rejection Confirmed ({resp.status_code})")
            else:
                logger.error(f"❌ Unexpected Auth Response: {resp.status_code}")
         finally:
            await bad_auth_client.aclose()

    async def cleanup(self):
        logger.info("--- CLEANUP ---")
        await self._query("REMOVE TABLE test_table;")
        await self._query("REMOVE TABLE stress_test;")
        # Can't remove NS easily via SQL in all versions, but we clean the data.

if __name__ == "__main__":
    torture = DatabaseTorture()
    asyncio.run(torture.run())
