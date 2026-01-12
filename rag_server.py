import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("rag_server")

# Import MemoryServer from existing codebase
try:
    from agent_runner.memory_server import MemoryServer
except ImportError:
    # If running from root, ensure python path is set or handle imports
    import sys
    sys.path.append(os.getcwd())
    from agent_runner.memory_server import MemoryServer

# Configuration
PORT = int(os.getenv("RAG_PORT", 5555))
HOST = "0.0.0.0"

# Initialize FastAPI
app = FastAPI(title="Antigravity RAG Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
memory_server: Optional[MemoryServer] = None

@app.on_event("startup")
async def startup_event():
    global memory_server
    logger.info("Initializing RAG Service...")
    
    # Initialize MemoryServer (wrapper for SurrealDB)
    # We pass None for state as we want a standalone connection or minimal state
    # MemoryServer reads env vars for connection specifics
    memory_server = MemoryServer(state=None) 
    
    try:
        await memory_server.initialize()
        logger.info("RAG Service Initialized Successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MemoryServer: {e}")
        # We don't exit here to allow /health to report failure
        # In a strict environment, we might panic.

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down RAG Service...")
    # Add cleanup if needed

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not memory_server:
        return {"status": "starting"}
    
    try:
        status = await memory_server.health_check()
        return status
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/rag/query")
async def query_rag(
    model: str = Body(..., embed=True),
    messages: List[Dict[str, Any]] = Body(..., embed=True)
):
    """
    Execute a RAG retrieval based on chat history.
    This reconstructs the query from messages and fetches relevant chunks.
    """
    if not memory_server or not memory_server.initialized:
        raise HTTPException(status_code=503, detail="RAG Service not ready (DB disconnected)")

    try:
        # Extract query from last user message
        query_text = ""
        if messages:
             for m in reversed(messages):
                 if m.get("role") == "user":
                     query_text = m.get("content", "")
                     break
        
        if not query_text:
            return {"answer": "", "context": []}

        # Use memory_server to search
        # Note: MemoryServer needs a specific search method. 
        # Looking at memory_server.py, we might use `execute_query` for vector search
        # or if it has a `search` or `retrieve` method.
        # Since strict RAG methods might be missing in the base class, we'll implement a basic search here
        # or use execute_query directly if we know the schema.
        
        # NOTE: For now, we return a simple placeholder if specific retrieval logic 
        # isn't exposed in the base MemoryServer class yet.
        # Ideally, MemoryServer should have `search_chunks(query)`.
        # Let's inspect memory_server.py again or implement a raw query.
        
        # Basic Vector Search Implementation using SurrealQL
        # 1. Get Embedding for query (using memory_server.get_embedding)
        embedding = await memory_server.get_embedding(query_text)
        
        # 2. Search Chunks
        # Ensure embedding is valid format
        if not embedding or len(embedding) == 0:
             return {"answer": "Error generating embedding", "context": []}

        sql = """
        SELECT file_path, content, 
               vector::similarity::euclidean(embedding, $query_vec) AS score
        FROM chunk 
        WHERE embedding <|4|> $query_vec 
        ORDER BY score DESC 
        LIMIT 5;
        """
        
        results = await memory_server.execute_query(sql, {"query_vec": embedding})
        
        context_str = ""
        context_items = []
        
        if results:
            for res in results:
                c = res.get("content", "")
                s = res.get("score", 0)
                context_str += f"- {c}\n"
                context_items.append({"content": c, "score": s})
        
        # We perform retrieval-only here. Generation happens in the Router/Agent.
        # The Router expects {"answer": ..., "context": ...}
        # If the Router wants the RAG service to GENERATE the answer, we need an LLM here.
        # But typically RAG service provides CONTEXT.
        # Let's verify what router/rag.py expects.
        # It expects "answer" or "rag_context".
        
        return {
            "answer": "Retrieved context for query.", # RAG service acted as retrieval
            "context": context_items,
            "rag_context": context_str # Compatible with router
        }

    except Exception as e:
        logger.error(f"RAG Query Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
