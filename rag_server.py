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
# --- Advanced Logging Configuration ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("rag_server")

# --- Performance Timer Context ---
from contextlib import asynccontextmanager

@asynccontextmanager
async def log_time(operation_name: str, level=logging.DEBUG):
    t0 = time.time()
    try:
        yield
    finally:
        duration = time.time() - t0
        logger.log(level, f"PERF: {operation_name} completed in {duration:.4f}s")

# Silence noisy third-party loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("multipart").setLevel(logging.WARNING)

app = FastAPI(title="Antigravity RAG Server")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    window_size: int = 1000
    overlap: int = 200
    prepend_text: str = ""

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
            "Authorization": f"Bearer {ROUTER_AUTH_TOKEN}" if ROUTER_AUTH_TOKEN else ""
        }
        self.sql_url = f"{SURREAL_URL}/sql"
        # Metrics - used for stats endpoint
        self.metrics = {"total_searches": 0, "total_ingests": 0, "errors": 0}
        self._initialized = False

    async def execute_surreal_query(self, sql: str, params: dict = None) -> list:
        """
        Executes a SQL query against SurrealDB with comprehensive logging and error handling.
        """
        # If params exist, prepend them as LET statements (sanitized) to the SQL
        # This mirrors the behavior we had inline before, but centralizes it.
        full_sql = sql
        if params:
            prefix = ""
            for k, v in params.items():
                prefix += f"LET ${k} = {json.dumps(v)};\n"
            full_sql = prefix + sql

        try:
            async with log_time("SurrealDB Query Execution"):
                logger.debug(f"DB_REQ: {full_sql[:500]}..." if len(full_sql) > 500 else f"DB_REQ: {full_sql}")
                
                r = await self.client.post(self.sql_url, content=full_sql, auth=self.auth, headers=self.headers)
                
                if r.status_code != 200:
                    logger.error(f"DB_HTTP_ERR: {r.status_code} - {r.text}")
                    r.raise_for_status()
                
                results = r.json()
                
                # Check for SurrealDB-level errors in the response
                for idx, res in enumerate(results):
                    if res.get("status") == "ERR":
                        logger.error(f"DB_SQL_ERR (Statement {idx}): {res.get('result') or res.get('detail')}")
                        logger.error(f"FAULTY QUERY: {full_sql}")
                
                logger.debug(f"DB_RESP_SUMMARY: Received {len(results)} result sets.")
                return results

        except Exception as e:
            logger.error(f"DB_EXEC_FAILED: {e}")
            self.metrics["errors"] += 1
            raise e
        self.sql_url = f"{SURREAL_URL.rstrip('/')}/sql"
        self._initialized = False
        # Performance Telemetry
        self.metrics = {
            "total_searches": 0,
            "total_ingests": 0,
            "avg_search_time": 0.0,
            "avg_ingest_time": 0.0,
            "last_ingest_at": None,
            "errors": 0
        }

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
        DEFINE FIELD authority ON TABLE chunk TYPE number DEFAULT 1.0;
        DEFINE FIELD timestamp ON TABLE chunk TYPE datetime DEFAULT time::now();
        
        -- Remove legacy MTREE index if it exists (for migration to HNSW)
        REMOVE INDEX IF EXISTS chunk_embedding_index ON TABLE chunk;

        DEFINE INDEX chunk_embedding_index ON TABLE chunk FIELDS embedding HNSW DIMENSION 1024 DIST EUCLIDEAN TYPE F32;

        -- Graph Schema
        DEFINE TABLE entity SCHEMAFULL;
        DEFINE FIELD name ON TABLE entity TYPE string;
        DEFINE FIELD type ON TABLE entity TYPE string;
        DEFINE FIELD description ON TABLE entity TYPE string;
        DEFINE FIELD metadata ON TABLE entity TYPE object;
        DEFINE FIELD last_updated ON TABLE entity TYPE datetime DEFAULT time::now();
        
        DEFINE TABLE relates SCHEMAFULL TYPE RELATION;
        DEFINE FIELD type ON TABLE relates TYPE string;
        DEFINE FIELD description ON TABLE relates TYPE string;
        DEFINE FIELD origin ON TABLE relates TYPE string;
        DEFINE FIELD timestamp ON TABLE relates TYPE datetime DEFAULT time::now();
        """
        try:
            await self.execute_surreal_query(setup_sql)
            logger.info("RAG Schema initialized in SurrealDB")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize RAG DB: {e}")

    async def get_embedding(self, text: str) -> List[float]:
        try:
            headers = {}
            # TODO: Clean this up once env vars propagate correctly
            token = ROUTER_AUTH_TOKEN or '9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic'
            if token:
                headers["Authorization"] = f"Bearer {token}"
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
        start_time = time.time()
        await self.ensure_db()
        embedding = await self.get_embedding(content)
        
        # QUALITY CONTROL: Authority Scoring by source type
        authority = 1.0
        if filename:
            ext = filename.split(".")[-1].lower()
            if ext in ["pdf", "docx"]: authority = 1.0 # High quality official docs
            elif ext in ["yaml", "yml", "json", "conf"]: authority = 0.9 # Structural state
            elif ext in ["nmap", "csv", "log"]: authority = 0.8 # Structured evidence
            elif ext in ["txt", "md"]: authority = 0.7 # Casual notes
        
        query = "CREATE chunk SET content = $content, kb_id = $kb, filename = $file, metadata = $meta, embedding = $emb, authority = $auth;"
        params = {
            "content": content,
            "kb": kb_id,
            "file": filename or "unknown",
            "meta": metadata,
            "emb": embedding,
            "auth": authority
        }
        
        # Build prefix for params
        prefix = f"USE NS {SURREAL_NS} DB {SURREAL_DB};\n"
        for k, v in params.items():
            prefix += f"LET ${k} = {json.dumps(v)};\n"
        
        try:
            r = await self.client.post(self.sql_url, content=prefix + query, auth=self.auth, headers=self.headers)
            r.raise_for_status()
            
            # Update metrics
            elapsed = time.time() - start_time
            self.metrics["total_ingests"] += 1
            self.metrics["avg_ingest_time"] = (self.metrics["avg_ingest_time"] * 0.9) + (elapsed * 0.1)
            self.metrics["last_ingest_at"] = time.time()
            
            return True
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Failed to store chunk: {e}")
            return False

    async def search(self, query_text: str, kb_id: str, limit: int = 5):
        start_time = time.time()
        embedding = await self.get_embedding(query_text)
        
        sql = f"""
        USE NS {SURREAL_NS} DB {SURREAL_DB};
        SELECT content, 
               filename, 
               metadata, 
               kb_id, 
               authority, 
               timestamp,
               vector::distance::euclidean(embedding, $emb) AS raw_dist,
               (
                 (vector::distance::euclidean(embedding, $emb) * 10.0) 
                 - (authority * 2.0)
                 - (math::max([0, (time::now() - timestamp).days() / 365.0]) * 0.5)
               ) AS score
        FROM chunk 
        WHERE kb_id = $kb
        ORDER BY score ASC
        LIMIT $limit;
        """
        params = {
            "emb": embedding,
            "kb": kb_id,
            "limit": limit
        }
        
        try:
            results = await self.execute_surreal_query(sql, params)
            if isinstance(results, list) and len(results) > 0:
                # Last statement result
                data = results[-1].get("result", [])
                
                # Filter out None results (if any)
                if data is None: data = []
                
                # Calculate Audit Metrics
                if data:
                    # Ensure 'score' exists before trying to find max
                    best_score = max([d.get("score", 0) for d in data]) if "score" in data[0] else 0
                    logger.info(f"QUERY_STATS: Found {len(data)} chunks. Best Score: {best_score:.4f}")
                else:
                    logger.info("QUERY_STATS: No relevant chunks found.")

                # Update metrics
                elapsed = time.time() - start_time
                self.metrics["total_searches"] += 1
                current_avg = self.metrics.get("avg_search_time", 0.0)
                self.metrics["avg_search_time"] = (current_avg * 0.9) + (elapsed * 0.1)

                return data
            
            # HYBRID FALLBACK: If vector search is empty/poor, try exact keyword matching
            logger.info(f"HYBRID FALLBACK: Vector search found no high-confidence matches. Trying keyword search for '{query_text}'...")
            keyword_sql = """
            USE NS $ns DB $db;
            SELECT *, 1.0 AS score FROM chunk 
            WHERE kb_id = $kb AND content CONTAINS $q
            LIMIT $limit;
            """
            params["q"] = query_text
            
            r = await self.client.post(self.sql_url, content=prefix + keyword_sql, auth=self.auth, headers=self.headers)
            if r.status_code == 200:
                results = r.json()
                if isinstance(results, list) and len(results) > 0:
                    data = results[-1].get("result", [])
                    logger.info(f"HYBRID SUCCESS: Keyword search found {len(data)} literal matches.")
                    for row in data: row.pop("embedding", None)
                    return data
            return []
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Search failed: {e}")
            return []

import json
rag_backend = RAGServer()

@app.on_event("startup")
async def startup_event():
    logger.info("RAG Server starting up... initializing database schema.")
    await rag_backend.ensure_db()

@app.post("/ingest")
async def ingest(req: IngestRequest):
    # ACCURACY UPGRADE: Adaptive Sliding Window Chunking
    text = req.content
    window_size = req.window_size
    overlap = req.overlap
    
    chunks = []
    if len(text) <= window_size:
        chunks = [text]
    else:
        start = 0
        while start < len(text):
            end = start + window_size
            chunks.append(text[start:end])
            start += (window_size - overlap)
            # Prevent infinite loop if overlap >= window_size
            if start >= len(text) or (window_size - overlap) <= 0:
                break
        
    success_count = 0
    logger.info(f"INGEST: Received {len(req.content)} chars. Accuracy-friendly chunking produced {len(chunks)} overlapping windows.")
    for p in chunks:
        # Global Context Injection: Prepend the summary if provided
        final_content = f"{req.prepend_text}{p}"
        if await rag_backend.add_chunk(final_content, req.kb_id, req.filename, req.metadata):
            success_count += 1
            
    logger.info(f"INGEST COMPLETE: {success_count} chunks stored in SurrealDB.")
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

@app.get("/stats")
async def stats():
    """Get a summary of the Knowledge Base contents."""
    await rag_backend.ensure_db()
    sql = f"""
    USE NS {SURREAL_NS} DB {SURREAL_DB}; 
    SELECT count() AS count, kb_id FROM chunk GROUP BY kb_id;
    SELECT count() AS count FROM entity GROUP ALL;
    SELECT count() AS count FROM relates GROUP ALL;
    """
    try:
        r = await rag_backend.client.post(rag_backend.sql_url, content=sql, auth=rag_backend.auth, headers=rag_backend.headers)
        if r.status_code == 200:
            res = r.json()
            
            # Helper to safely get list from result
            def get_res(idx):
                if idx < len(res):
                    val = res[idx].get("result")
                    return val if val is not None else []
                return []

            chunk_data = get_res(0)
            
            # Entities/Edges typically return [{count: N}]
            ent_res = get_res(1)
            entity_count = ent_res[0].get("count", 0) if ent_res else 0
            
            edge_res = get_res(2)
            edge_count = edge_res[0].get("count", 0) if edge_res else 0
            
            total = sum(d.get("count", 0) for d in chunk_data)
            return {
                "total_chunks": total,
                "total_entities": entity_count,
                "total_relations": edge_count,
                "knowledge_bases": {d.get("kb_id"): d.get("count") for d in chunk_data},
                "embedding_model": EMBED_MODEL,
                "performance": rag_backend.metrics,
                "status": "online" if total > 0 else "empty"
            }
    except Exception as e:
        logger.error(f"Stats check failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
    return {"error": "Could not connect to knowledge database"}

# --- Graph Capabilities ---

class GraphEntity(BaseModel):
    name: str # Unique identifier/name
    type: str # Person, Organization, Location, CodeClass, Function, etc.
    description: Optional[str] = ""
    metadata: Dict[str, Any] = {}

class GraphRelation(BaseModel):
    source: str # Name of source entity
    target: str # Name of target entity
    relation: str # writes_to, calls, knows, contains
    description: Optional[str] = ""

class GraphIngestRequest(BaseModel):
    entities: List[GraphEntity]
    relations: List[GraphRelation]
    origin_file: Optional[str] = None # Linking these facts to a source document

@app.post("/ingest/graph")
async def ingest_graph(req: GraphIngestRequest):
    """
    Ingest structural knowledge (Entities and Relations) into the Graph DB.
    Idempotent: Updates details if entity exists, creates new edges.
    """
    start = time.time()
    await rag_backend.ensure_db()
    
    # 1. Upsert Entities first
    entity_sql = ""
    for ent in req.entities:
        # Sanitize ID: replace spaces with underscores, lowercase
        safe_id = ent.name.strip().replace(" ", "_").lower()
        # Clean specific chars that break Surreal IDs (keep it simple)
        safe_id = "".join([c for c in safe_id if c.isalnum() or c in "_-"])
        
        if not safe_id: continue

        # We use proper ID record syntax: entity:id
        # CONTENT logic: MERGE to update description/metadata without wiping existing info
        entity_sql += f"""
        LET $name = {json.dumps(ent.name)};
        LET $type = {json.dumps(ent.type)};
        LET $desc = {json.dumps(ent.description)};
        LET $meta = {json.dumps(ent.metadata)};
        
        UPDATE entity:{safe_id} MERGE {{
            name: $name,
            type: $type,
            description: $desc,
            metadata: $meta,
            last_updated: time::now()
        }};\n"""
    
    if entity_sql:
        full_sql = f"USE NS {SURREAL_NS} DB {SURREAL_DB};\n{entity_sql}"
        try:
            await rag_backend.execute_surreal_query(full_sql)
        except Exception as e:
            logger.error(f"Graph Entity Ingest Failed: {e}")
            return {"error": str(e)}

    # 2. Create Relations
    rel_sql = ""
    for rel in req.relations:
        src_id = "".join([c for c in rel.source.strip().replace(" ", "_").lower() if c.isalnum() or c in "_-"])
        tgt_id = "".join([c for c in rel.target.strip().replace(" ", "_").lower() if c.isalnum() or c in "_-"])
        
        if not src_id or not tgt_id: continue

        # Clean relation type
        rel_type = rel.relation.strip().replace(" ", "_").lower()
        
        rel_sql += f"""
        RELATE entity:{src_id}->relates->entity:{tgt_id} CONTENT {{
            type: {json.dumps(rel_type)},
            description: {json.dumps(rel.description or "")},
            origin: {json.dumps(req.origin_file or "unknown")},
            timestamp: time::now()
        }};\n"""

    if rel_sql:
        full_sql = f"USE NS {SURREAL_NS} DB {SURREAL_DB};\n{rel_sql}"
        try:
            await rag_backend.execute_surreal_query(full_sql)
        except Exception as e:
            logger.error(f"Graph Relation Ingest Failed: {e}")
            return {"error": str(e)}

    count = len(req.entities) + len(req.relations)
    logger.info(f"GRAPH INGEST: Processed {len(req.entities)} entities and {len(req.relations)} relations in {time.time()-start:.2f}s")
    return {"ok": True, "processed": count}

@app.get("/graph/snapshot")
async def graph_snapshot(limit: int = 1000):
    """
    Get a snapshot of the graph for visualization.
    Returns nodes and links in D3/force-graph format.
    """
    await rag_backend.ensure_db()
    
    sql = f"""
    SELECT * FROM entity LIMIT {limit};
    SELECT * FROM relates LIMIT {limit};
    """
    
    try:
        r = await rag_backend.client.post(rag_backend.sql_url, content=sql, auth=rag_backend.auth, headers=rag_backend.headers)
        if r.status_code == 200:
            res = r.json()
            
            # Helper safely get list
            def get_res(idx):
                if idx < len(res):
                    val = res[idx].get("result")
                    return val if val is not None else []
                return []
            
            entities = get_res(0)
            relations = get_res(1)
            
            logger.info(f"GRAPH_SNAPSHOT: Fetched {len(entities)} entities and {len(relations)} relations.")
            
            # Format for Force Graph
            nodes = []
            for e in entities:
                # Surreal ID is "entity:name", we just want the ID part or the full thing
                # let's use the full ID as the unique key
                nodes.append({
                    "id": e.get("id"),
                    "label": e.get("name", "Unknown"),
                    "group": e.get("type", "Thing"),
                    "val": 1 # size
                })
                
            links = []
            for r in relations:
                links.append({
                    "source": r.get("in"), # Surreal Relate uses 'in' for source
                    "target": r.get("out"), # Surreal Relate uses 'out' for target
                    "type": r.get("type", "relates"),
                    "label": r.get("type", "relates")
                })
                
            return {
                "nodes": nodes,
                "links": links
            }
            
    except Exception as e:
        logger.error(f"Graph snapshot failed: {e}")
        return {"nodes": [], "links": []}
    
    return {"nodes": [], "links": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5555)
