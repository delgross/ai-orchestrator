import os
import time
import logging
import uuid
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
import uvicorn
import sys

# Configuration
SURREAL_URL = os.getenv("SURREAL_URL", "http://localhost:8000")
SURREAL_USER = os.getenv("SURREAL_USER", "root")
SURREAL_PASS = os.getenv("SURREAL_PASS", "root")
SURREAL_NS = os.getenv("SURREAL_NS", "orchestrator")
SURREAL_DB = os.getenv("SURREAL_DB", "knowledge") # Separate DB for RAG
GATEWAY_BASE = os.getenv("GATEWAY_BASE", "http://127.0.0.1:5455")
ROUTER_AUTH_TOKEN = os.getenv("ROUTER_AUTH_TOKEN")
EMBED_MODEL = os.getenv("EMBED_MODEL", "ollama:mxbai-embed-large:latest")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s rag_server %(message)s")
logger = logging.getLogger("rag_server")

app = FastAPI(title="Antigravity RAG Server")

# MiddleWare for performance tracking
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log the request details
    if request.url.path not in ["/health"]:
        logger.info(f"API {request.method} {request.url.path} - Completed in {process_time:.4f}s")
    
    return response

class IngestRequest(BaseModel):
    content: str
    kb_id: str = "default"
    filename: Optional[str] = None
    metadata: Dict[str, Any] = {}

class QueryRequest(BaseModel):
    query: str
    kb_id: str = "default"
    limit: int = 5
    min_score: float = 0.0

class RAGServer:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth = (SURREAL_USER, SURREAL_PASS)
        self.headers = {
            "Accept": "application/json",
            "NS": SURREAL_NS,
            "DB": SURREAL_DB,
        }
        self.sql_url = f"{SURREAL_URL.rstrip('/')}/sql"
        self._initialized = False

    async def ensure_db(self):
        if self._initialized: return
        # Initialize schema
        setup_sql = f"""
        USE NS {SURREAL_NS} DB {SURREAL_DB};
        DEFINE TABLE chunk SCHEMAFULL;
        DEFINE FIELD content ON TABLE chunk TYPE string;
        DEFINE FIELD kb_id ON TABLE chunk TYPE string;
        DEFINE FIELD filename ON TABLE chunk TYPE string;
        DEFINE FIELD metadata ON TABLE chunk TYPE object;
        DEFINE FIELD embedding ON TABLE chunk TYPE array<float, 1024>;
        DEFINE FIELD timestamp ON TABLE chunk TYPE datetime DEFAULT time::now();
        
        DEFINE INDEX chunk_embedding_index ON TABLE chunk FIELDS embedding MTREE DIMENSION 1024 DIST EUCLIDEAN;
        """
        try:
            r = await self.client.post(self.sql_url, content=setup_sql, auth=self.auth, headers=self.headers)
            r.raise_for_status()
            logger.info("RAG Schema initialized in SurrealDB")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize RAG DB: {e}")

    async def get_embedding(self, text: str) -> List[float]:
        try:
            headers = {}
            if ROUTER_AUTH_TOKEN:
                headers["Authorization"] = f"Bearer {ROUTER_AUTH_TOKEN}"
            resp = await self.client.post(
                f"{GATEWAY_BASE}/v1/embeddings",
                json={"model": EMBED_MODEL, "input": text},
                headers=headers,
                timeout=10.0
            )
            if resp.status_code == 200:
                return resp.json()["data"][0]["embedding"]
        except Exception as e:
            logger.warning(f"Embedding failed: {e}")
        return [0.0] * 1024

    async def add_chunk(self, content: str, kb_id: str, filename: Optional[str] = None, metadata: Dict[str, Any] = {}):
        await self.ensure_db()
        embedding = await self.get_embedding(content)
        
        query = "CREATE chunk SET content = $content, kb_id = $kb, filename = $file, metadata = $meta, embedding = $emb;"
        params = {
            "content": content,
            "kb": kb_id,
            "file": filename or "unknown",
            "meta": metadata,
            "emb": embedding
        }
        
        # Build prefix for params
        prefix = f"USE NS {SURREAL_NS} DB {SURREAL_DB};\n"
        for k, v in params.items():
            prefix += f"LET ${k} = {json.dumps(v)};\n"
        
        try:
            r = await self.client.post(self.sql_url, content=prefix + query, auth=self.auth, headers=self.headers)
            r.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to store chunk: {e}")
            return False

    async def search(self, query_text: str, kb_id: str, limit: int = 5):
        await self.ensure_db()
        embedding = await self.get_embedding(query_text)
        
        sql = """
        USE NS $ns DB $db;
        SELECT *, vector::distance::euclidean(embedding, $emb) AS score 
        FROM chunk 
        WHERE kb_id = $kb
        ORDER BY score ASC 
        LIMIT $limit;
        """
        params = {
            "ns": SURREAL_NS,
            "db": SURREAL_DB,
            "emb": embedding,
            "kb": kb_id,
            "limit": limit
        }
        
        # Build prefix
        prefix = ""
        for k, v in params.items():
            prefix += f"LET ${k} = {json.dumps(v)};\n"
            
        try:
            r = await self.client.post(self.sql_url, content=prefix + sql, auth=self.auth, headers=self.headers)
            r.raise_for_status()
            results = r.json()
            if isinstance(results, list) and len(results) > 0:
                # Last statement result
                data = results[-1].get("result", [])
                # Normalize results
                cleaned = []
                for row in data:
                    row.pop("embedding", None)
                    cleaned.append(row)
                return cleaned
            return []
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

import json
rag_backend = RAGServer()

@app.post("/ingest")
async def ingest(req: IngestRequest):
    # Simple chunker (by paragraph for now)
    paragraphs = [p.strip() for p in req.content.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [req.content]
        
    success_count = 0
    logger.info(f"INGEST: Received {len(req.content)} chars for KB '{req.kb_id}' from file '{req.filename}'")
    for p in paragraphs:
        if await rag_backend.add_chunk(p, req.kb_id, req.filename, req.metadata):
            success_count += 1
            
    logger.info(f"INGEST COMPLETE: Created {success_count} chunks in SurrealDB")
    return {"ok": True, "chunks_ingested": success_count}

@app.post("/query")
async def query(req: QueryRequest):
    logger.info(f"QUERY: '{req.query}' [KB: {req.kb_id}, Limit: {req.limit}]")
    results = await rag_backend.search(req.query, req.kb_id, req.limit)
    
    # Format response for the Router
    context_text = "\n---\n".join([f"Source: {r.get('filename')}\n{r.get('content')}" for r in results])
    
    logger.info(f"QUERY COMPLETE: Found {len(results)} relevant chunks.")
    
    return {
        "ok": True,
        "answer": context_text, # Router expects the context in 'answer' or 'content'
        "context": results
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "db": SURREAL_URL}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5555)
