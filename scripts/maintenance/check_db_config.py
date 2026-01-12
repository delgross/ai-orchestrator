
import asyncio
from surrealdb import Surreal

async def check_db():
    async with Surreal("ws://127.0.0.1:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("agent", "memory")
        
        # Check current
        try:
            current = await db.query("SELECT * FROM config_state WHERE key='VISION_MODEL'")
            print(f"Current Config in DB: {current}")
        except Exception as e:
            print(f"Read Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
