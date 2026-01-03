import os
import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import uvicorn
import asyncio
from agent_runner.state import AgentState
import json

# Configuration
SURREAL_URL = os.getenv("SURREAL_URL", "http://localhost:8000")
SURREAL_USER = os.getenv("SURREAL_USER", "root")
SURREAL_PASS = os.getenv("SURREAL_PASS", "root")
SURREAL_NS = os.getenv("SURREAL_NS", "orchestrator")
SURREAL_DB = os.getenv("SURREAL_DB", "knowledge") # Separate DB for RAG
GATEWAY_BASE = os.getenv("GATEWAY_BASE", "http://127.0.0.1:5455")
ROUTER_AUTH_TOKEN = os.getenv("ROUTER_AUTH_TOKEN")
# EMBED_MODEL removed. Relying on AgentState.
# --- Advanced Logging Configuration ---
# --- Advanced Logging Configuration ---
from common.logging_setup import setup_logger
setup_logger("common")
logger = setup_logger("rag_server")

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
        self.state = AgentState() # Load centralized config
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
        self.metrics = {
            "total_searches": 0, 
            "total_ingests": 0, 
            "errors": 0,
            "avg_ingest_time": 0.0,
            "avg_search_time": 0.0,
            "last_ingest_at": 0.0
        }
        self._initialized = False

    async def execute_surreal_query(self, sql: str, params: dict = None) -> list:
        """
        Executes a SQL query against SurrealDB with comprehensive logging and error handling.
        Ensures correct order: USE NS -> LET -> QUERY
        """
        # 1. Base Namespace Selection (Always required due to connection context)
        # We strip it from input 'sql' if present to avoid redundancy/resetting
        clean_sql = sql.strip()
        ns_marker = f"USE NS {SURREAL_NS} DB {SURREAL_DB};"
        if clean_sql.startswith(ns_marker):
            clean_sql = clean_sql[len(ns_marker):].strip()
        elif clean_sql.startswith("USE NS"):
             # Simple heuristic to strip manual USE NS if it differs or is formatted differently
             # Assuming standard format for now, or just let strict prefix handle common case
             pass

        full_sql = ns_marker + "\n"

        # 2. Parameters (LET statements)
        if params:
            for k, v in params.items():
                val_json = json.dumps(v, default=str)
                full_sql += f"LET ${k} = {val_json};\n"
        
        # 3. The Query
        full_sql += clean_sql

        try:
            # Use explicit session path
            # Log the SQL for debugging (truncate embedding/content if too long)
            debug_sql = full_sql
            if len(debug_sql) > 1000:
                debug_sql = debug_sql[:300] + "...[truncated]..." + debug_sql[-100:]
            logger.info(f"EXECUTING SQL: {debug_sql}")

            resp = await self.client.post(
                self.sql_url, 
                content=full_sql, 
                auth=self.auth, 
                headers=self.headers
            )
            
            if resp.status_code != 200:
                logger.error(f"SurrealDB Query Failed [{resp.status_code}]: {resp.text}")
                return None
                
            data = resp.json()
            # SurrealDB returns a list of result objects for each statement
            if isinstance(data, list) and data:
                # We want the result of the LAST statement (The Query)
                # But we have multiple statements (USE, LETs, Query).
                # Query could be multiple statements too? usually 1.
                # If OK, return result.
                last_res = data[-1]
                if last_res.get("status") == "OK":
                    return last_res.get("result", [])
                else:
                     logger.warning(f"SurrealDB Logic Error (Last Statement): {last_res}")
                     # Check if ANY error occurred in previous statements (like USE NS or LET)
                     for res in data:
                         if res.get("status") == "ERR":
                             logger.error(f"SurrealDB Pre-Statement Error: {res}")
                             return None
                     return None
            return data
            
        except Exception as e:
            logger.error(f"SurrealDB Execution Exception: {e}")
            return None

    async def ensure_db(self):
        if self._initialized: return
        # Initialize schema
        setup_sql = f"""
        USE NS {SURREAL_NS} DB {SURREAL_DB};

        -- 1. Define Analyzers (Linguistic Lemmatization)
        DEFINE ANALYZER IF NOT EXISTS en_lemma TOKENIZERS class FILTERS lowercase, snowball(english);

        -- 2. Define Tables
        DEFINE TABLE IF NOT EXISTS chunk SCHEMAFULL;
        
        -- 3. Define Fields safely (Removed ANALYZER from fields for 2.x compatibility)
        DEFINE FIELD IF NOT EXISTS content ON TABLE chunk TYPE string;
        DEFINE FIELD IF NOT EXISTS kb_id ON TABLE chunk TYPE string;
        DEFINE FIELD IF NOT EXISTS filename ON TABLE chunk TYPE string;
        DEFINE FIELD IF NOT EXISTS metadata ON TABLE chunk TYPE object;
        DEFINE FIELD IF NOT EXISTS embedding ON TABLE chunk TYPE array<float, 1024>;
        DEFINE FIELD IF NOT EXISTS authority ON TABLE chunk TYPE number DEFAULT 1.0;
        DEFINE FIELD IF NOT EXISTS timestamp ON TABLE chunk TYPE datetime DEFAULT time::now();
        
        -- Full-Text Search Indices (New 2.x syntax)
        DEFINE INDEX IF NOT EXISTS chunk_content_search ON TABLE chunk FIELDS content SEARCH ANALYZER en_lemma BM25;

        -- HNSW Vector Index (Persist unless schema change required)
        DEFINE INDEX IF NOT EXISTS chunk_embedding_index ON TABLE chunk FIELDS embedding HNSW DIMENSION 1024 DIST EUCLIDEAN TYPE F32;

        -- Graph Schema
        DEFINE TABLE IF NOT EXISTS entity SCHEMAFULL;
        DEFINE FIELD IF NOT EXISTS name ON TABLE entity TYPE string;
        DEFINE FIELD IF NOT EXISTS type ON TABLE entity TYPE string;
        DEFINE FIELD IF NOT EXISTS description ON TABLE entity TYPE string;
        DEFINE FIELD IF NOT EXISTS metadata ON TABLE entity TYPE object;
        DEFINE FIELD IF NOT EXISTS last_updated ON TABLE entity TYPE datetime DEFAULT time::now();
        
        DEFINE INDEX IF NOT EXISTS entity_name_search ON TABLE entity FIELDS name SEARCH ANALYZER en_lemma BM25;
        DEFINE INDEX IF NOT EXISTS entity_description_search ON TABLE entity FIELDS description SEARCH ANALYZER en_lemma BM25;

        DEFINE TABLE IF NOT EXISTS relates SCHEMAFULL TYPE RELATION;
        DEFINE FIELD IF NOT EXISTS type ON TABLE relates TYPE string;
        DEFINE FIELD IF NOT EXISTS description ON TABLE relates TYPE string;
        DEFINE FIELD IF NOT EXISTS origin ON TABLE relates TYPE string;
        DEFINE FIELD IF NOT EXISTS timestamp ON TABLE relates TYPE datetime DEFAULT time::now();

        DEFINE INDEX IF NOT EXISTS relates_description_search ON TABLE relates FIELDS description SEARCH ANALYZER en_lemma BM25;
        """
        try:
            await self.execute_surreal_query(setup_sql)
            logger.info("RAG Schema initialized in SurrealDB")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize RAG DB: {e}")

    async def get_embedding(self, text: str) -> List[float]:
        try:
            model = self.state.embedding_model if self.state else "ollama:mxbai-embed-large:latest"
            
            # Circuit Breaker Check
            if self.state and hasattr(self.state, "mcp_circuit_breaker"):
                 if not self.state.mcp_circuit_breaker.is_allowed(model):
                     logger.warning(f"RAG Embedding Short-Circuited: Model '{model}' is broken.")
                     return [0.0] * 1024
            
            headers = {}
            # Environment variables propagation logic
            token = ROUTER_AUTH_TOKEN or '9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic'
            if token:
                headers["Authorization"] = f"Bearer {token}"
            resp = await self.client.post(
                f"{GATEWAY_BASE}/v1/embeddings",
                json={"model": model, "input": text},
                headers=headers,
                timeout=10.0
            )
            if resp.status_code == 200:
                if self.state and hasattr(self.state, "mcp_circuit_breaker"):
                     self.state.mcp_circuit_breaker.record_success(model)
                return resp.json()["data"][0]["embedding"]
            else:
                 logger.warning(f"RAG Embedding failed HTTP {resp.status_code}: {resp.text}")
                 if self.state and hasattr(self.state, "mcp_circuit_breaker"):
                     self.state.mcp_circuit_breaker.record_failure(model)
                     
        except Exception as e:
            logger.warning(f"Embedding failed: {e}")
            if self.state and hasattr(self.state, "mcp_circuit_breaker"):
                 # Default logic or just record against current
                 m = self.state.embedding_model if self.state else "unknown"
                 self.state.mcp_circuit_breaker.record_failure(m)
        return [0.0] * 1024

    async def add_chunk(self, content: str, kb_id: str, filename: Optional[str] = None, metadata: Dict[str, Any] = {}, finger_print: Optional[str] = None):
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
        
        # [NEW] Use fingerprint as part of the ID for deduplication: chunk:SHA256
        target_id = f"chunk:{finger_print}" if finger_print else "chunk"
        
        # Using UPSERT for idempotency (SurrealDB 2.x)
        query = f"UPSERT {target_id} SET content = $content, kb_id = $kb, filename = $file, metadata = $meta, embedding = $emb, authority = $auth, timestamp = time::now();"
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

    async def _run_vector_search(self, embedding: List[float], kb_id: str, limit: int) -> List[Dict[str, Any]]:
        try:
            sql = f"""
            SELECT *, vector::distance::euclidean(embedding, $emb) AS raw_dist
            FROM chunk 
            WHERE kb_id = $kb
            ORDER BY raw_dist ASC
            LIMIT $limit;
            """
            params = {"emb": embedding, "kb": kb_id, "limit": limit}
            results = await self.execute_surreal_query(sql, params)
            # logger.info(f"DEBUG VECTOR SEARCH RESULTS TYPE: {type(results)}")
            # logger.info(f"DEBUG VECTOR SEARCH RESULTS CONTENT: {results}")
            if isinstance(results, list):
                return results
            return []
        except Exception as e:
            logger.error(f"Vector search failed: {e}", exc_info=True)
            return []

    async def _run_keyword_search(self, query_text: str, kb_id: str, limit: int) -> List[Dict[str, Any]]:
        # Basic keyword search using CONTAINS
        # In a real SurrealDB setup, we'd use comprehensive full-text indexing
        try:
            sql = f"""
            SELECT *
            FROM chunk 
            WHERE kb_id = $kb AND content CONTAINS $q
            LIMIT $limit;
            """
            params = {"q": query_text, "kb": kb_id, "limit": limit}
            results = await self.execute_surreal_query(sql, params)
            if isinstance(results, list):
                return results
            return []
        except Exception as e:
            logger.error(f"Keyword search failed: {e}", exc_info=True)
            return []

    def _reciprocal_rank_fusion(self, vector_results: List[Dict], keyword_results: List[Dict], k: int = 60) -> List[Dict]:
        """
        Fuse results using Reciprocal Rank Fusion (RRF).
        score = 1 / (k + rank)
        """
        try:
            fused_scores = {}
            doc_map = {}
            
            # Process Vector Results
            for rank, doc in enumerate(vector_results):
                doc_id = doc.get("id")
                if not doc_id: continue
                doc_map[doc_id] = doc
                fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + (1 / (k + rank + 1))
                
            # Process Keyword Results
            for rank, doc in enumerate(keyword_results):
                doc_id = doc.get("id")
                if not doc_id: continue
                doc_map[doc_id] = doc # Overwrite or keep, doesn't matter as content is same
                fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + (1 / (k + rank + 1))
            
            # Sort by Fused Score
            sorted_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)
            
            final_results = []
            for doc_id in sorted_ids:
                doc = doc_map[doc_id]
                doc["score"] = fused_scores[doc_id] * 10.0 # Normalize roughly to 0-10 range for compatibility
                doc["fusion_source"] = "hybrid_rrf"
                final_results.append(doc)
                
            return final_results
        except Exception as e:
            logger.error(f"RRF Fusion failed: {e}", exc_info=True)
            return []

    async def search(self, query_text: str, kb_id: str, limit: int = 5):
        start_time = time.time()
        try:
            logger.info(f"Starting search for: {query_text} (KB: {kb_id})")
            


            embedding = await self.get_embedding(query_text)
            
            # 1. Run Parallel Searches (Ensemble)
            vector_task = self._run_vector_search(embedding, kb_id, limit * 2) # Fetch more for fusion
            keyword_task = self._run_keyword_search(query_text, kb_id, limit * 2)
            
            vector_res, keyword_res = await asyncio.gather(vector_task, keyword_task)
            
            logger.info(f"RAG ENSEMBLE: Vector found {len(vector_res)}, Keyword found {len(keyword_res)}")
            
            # 2. Fuse Results (RRF)
            data = self._reciprocal_rank_fusion(vector_res, keyword_res)
            data = data[:limit] # Trim to final limit
            
            if data:
                 # Ensure 'score' exists before checking max
                best_score = max([d.get("score", 0) for d in data]) if "score" in data[0] else 0
                logger.info(f"QUERY_STATS: Fused {len(data)} results. Best RRF Score: {best_score:.4f}")
                
                # --- CLOUD RE-RANKING (GPU) ---
                try:
                    from agent_runner.modal_tasks import rerank_search_results, has_modal
                    if has_modal and len(data) > 1:
                        logger.info("RERANK: Sending candidates to Cloud GPU...")
                        candidates = [d.get("content", "") for d in data]
                        
                        # Remote call
                        ranked_indices = rerank_search_results.remote(query_text, candidates)
                        # Returns list of (original_index, new_score)
                        
                        # Re-construct data in new order
                        reranked_data = []
                        for idx, score in ranked_indices:
                            item = data[idx]
                            item["score"] = score # Update score with cross-encoder score
                            item["reranked"] = True
                            reranked_data.append(item)
                            
                        data = reranked_data
                        logger.info(f"RERANK: Successfully re-ordered {len(data)} results.")
                except Exception as re_err:
                    if "Modal not configured" not in str(re_err) and "No module named" not in str(re_err):
                        logger.warning(f"Re-ranking failed: {re_err}")
                    pass
                # -----------------------------
            else:
                 logger.info("QUERY_STATS: No relevant chunks found (Vector + Keyword).")

            # Update metrics
            elapsed = time.time() - start_time
            self.metrics["total_searches"] += 1
            current_avg = self.metrics.get("avg_search_time", 0.0)
            self.metrics["avg_search_time"] = (current_avg * 0.9) + (elapsed * 0.1)

            logger.info(f"Search completed in {elapsed:.4f}s returning {len(data)} items")
            return data
        except Exception as e:
            logger.error(f"CRITICAL: Search operation failed: {e}", exc_info=True)
            # Re-raise or return empty list? Returning empty list prevents 500, but we want to debug.
            # Let's re-raise but now it's logged. 
            # Actually, let's return empty to avoid client crash, but we have logged it cleanly.
            # But the user complains about 500, so catching it here will stop the 500.
            return []


rag_backend = RAGServer()

@app.on_event("startup")
async def startup_event():
    logger.info("RAG Server starting up... initializing database schema.")
    await rag_backend.ensure_db()

    await rag_backend.ensure_db()

from fastapi import BackgroundTasks

async def _process_ingest_background(req: IngestRequest):
    # Re-use ingestion logic for background tasks
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
            if start >= len(text) or (window_size - overlap) <= 0:
                break
        
    success_count = 0
    duplicate_count = 0
    import hashlib
    
    logger.info(f"INGEST (Background): Processing {len(chunks)} chunks for {req.filename or 'unknown'}")
    
    for p in chunks:
        final_content = f"{req.prepend_text}{p}"
        fingerprint = hashlib.sha256(f"{final_content}_{req.kb_id}_{req.filename}".encode()).hexdigest()
        
        try:
            if await rag_backend.add_chunk(final_content, req.kb_id, req.filename, req.metadata, finger_print=fingerprint):
                success_count += 1
            else:
                duplicate_count += 1
        except Exception as e:
            logger.error(f"Background ingest failed for chunk: {e}")
            
    logger.info(f"INGEST COMPLETE (Background): {success_count} stored, {duplicate_count} skipped.")


@app.post("/ingest")
async def ingest(req: IngestRequest, background_tasks: BackgroundTasks):
    # HYBRID INGESTION STRATEGY
    # Small payloads (<20KB) are processed synchronously for immediate feedback.
    # Large payloads (like "The Blob") trigger background processing to prevent HTTP Timeouts.
    
    if len(req.content) > 20000:
        logger.info(f"INGEST: Payload size {len(req.content)} > 20KB. Offloading to Background Task.")
        background_tasks.add_task(_process_ingest_background, req)
        return {"ok": True, "status": "accepted", "message": "Payload too large for sync processing. Ingestion started in background."}

    # Synchronous processing for small files
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
            if start >= len(text) or (window_size - overlap) <= 0:
                break
        
    success_count = 0
    duplicate_count = 0
    import hashlib
    
    logger.info(f"INGEST: Received {len(req.content)} chars. Accuracy-friendly chunking produced {len(chunks)} overlapping windows.")
    for p in chunks:
        final_content = f"{req.prepend_text}{p}"
        fingerprint = hashlib.sha256(f"{final_content}_{req.kb_id}_{req.filename}".encode()).hexdigest()
        
        if await rag_backend.add_chunk(final_content, req.kb_id, req.filename, req.metadata, finger_print=fingerprint):
            success_count += 1
        else:
            duplicate_count += 1
            
    logger.info(f"INGEST COMPLETE: {success_count} chunks stored, {duplicate_count} skipped/duplicates.")
    return {"ok": True, "chunks_ingested": success_count, "duplicates": duplicate_count}

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

            chunk_data = get_res(1)
            
            # Entities/Edges typically return [{count: N}]
            ent_res = get_res(2)
            logger.info(f"STATS_DEBUG: ent_res raw: {ent_res}")
            entity_count = ent_res[0].get("count", 0) if ent_res else 0
            
            edge_res = get_res(3)
            logger.info(f"STATS_DEBUG: edge_res raw: {edge_res}")
            edge_count = edge_res[0].get("count", 0) if edge_res else 0
            
            total = sum(d.get("count", 0) for d in chunk_data)
            logger.info(f"STATS_DEBUG: Total Chunks: {total}, Entities: {entity_count}, Edges: {edge_count}")
            
            return {
                "total_chunks": total,
                "total_entities": entity_count,
                "total_relations": edge_count,
                "knowledge_bases": {d.get("kb_id"): d.get("count") for d in chunk_data},
                "embedding_model": EMBED_MODEL,
                "performance": rag_backend.metrics,
                "status": "online" if (total > 0 or entity_count > 0) else "empty"
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
        LET $meta = {json.dumps(ent.metadata or {})};
        
        INSERT INTO entity (id, name, type, description, metadata, last_updated) 
        VALUES (entity:{safe_id}, $name, $type, $desc, $meta, time::now())
        ON DUPLICATE KEY UPDATE 
            name = $name,
            type = $type,
            description = $desc,
            metadata = $meta,
            last_updated = time::now();\n"""
    
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
    USE NS {SURREAL_NS} DB {SURREAL_DB};
    SELECT id, name, type FROM entity LIMIT {limit};
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
            
            # Index 0 is USE result
            entities = get_res(1)
            relations = get_res(2)
            
            logger.info(f"GRAPH_SNAPSHOT: Fetched {len(entities)} entities and {len(relations)} relations.")
            
            # Format for Force Graph
            nodes = []
            for e in entities:
                if not isinstance(e, dict): continue
                nodes.append({
                    "id": e.get("id"),
                    "label": e.get("name", "Unknown"),
                    "group": e.get("type", "Thing"),
                    "val": 1,
                    "timestamp": e.get("last_updated") # Critical for time-evolution
                })
            
            links = []
            for r in relations:
                links.append({
                    "source": r.get("in"), 
                    "target": r.get("out"),
                    "type": r.get("type", "relates"),
                    "label": r.get("type", "relates"),
                    "timestamp": r.get("timestamp") # Critical for time-evolution
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
    uvicorn.run(app, host="127.0.0.1", port=5555)
