
import asyncio
import sys
import os
import logging

# Setup Path
sys.path.append(os.getcwd())

# Mock Env to match config
os.environ["SURREAL_URL"] = "http://localhost:8000"
# Auth token from config.yaml
os.environ["ROUTER_AUTH_TOKEN"] = "9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic" 

logging.basicConfig(level=logging.INFO)

async def run_repro():
    print("Importing RAGServer...")
    try:
        from rag_server import RAGServer
        server = RAGServer()
        print("Initialized RAGServer. calling search...")
        
        # Mocking State because RAGServer loads AgentState which might be heavy/fail
        # Actually RAGServer line 89: self.state = AgentState()
        # If AgentState fails to load, that would blow up __init__.
        # But server is running (PID 4135), so __init__ worked?
        
        res = await server.search("torture test", "default", 5)
        print(f"Search Result: {res}")
        
    except Exception as e:
        print("CRASH DETECTED:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_repro())
