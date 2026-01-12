import asyncio
import json
import os
import time
from typing import Any, Dict, List, Optional
import httpx
from datetime import datetime
import re
import threading

# Configuration
SURREAL_URL = os.getenv("SURREAL_URL", "http://localhost:8000")
SURREAL_USER = os.getenv("SURREAL_USER", "root")
SURREAL_PASS = os.getenv("SURREAL_PASS", "root")
SURREAL_NS = os.getenv("SURREAL_NS", "orchestrator")
SURREAL_DB = os.getenv("SURREAL_DB", "memory")
# EMBED_MODEL is now managed centrally via state.embedding.model
GATEWAY_BASE = os.getenv("GATEWAY_BASE", "http://127.0.0.1:5455")
ROUTER_AUTH_TOKEN = os.getenv("ROUTER_AUTH_TOKEN")

# Embedding dimension (default for most embedding models)
EMBEDDING_DIMENSION = 1024

# Timeout constants
HTTP_TIMEOUT = 30.0  # General HTTP timeout
QUERY_TIMEOUT = 10.0  # Default query timeout
KEEPALIVE_EXPIRY = 30.0  # Connection keepalive expiry
MAX_RETRIES = 3  # Maximum retry attempts
RETRY_DELAY_BASE = 0.5  # Base delay for exponential backoff

# Set up unified logging
import logging
logger = logging.getLogger(__name__)


class MemoryServer:
    def __init__(self, state=None):
        self.state = state
        # Thread lock for critical memory operations to prevent race conditions
        self._operation_lock = threading.Lock()

        # Ensure URL is HTTP and points to /sql
        self.url = SURREAL_URL.replace("ws://", "http://").replace("wss://", "https://")
        # [OPTIMIZATION] Force IPv4 to avoid localhost DNS latency (IPv6 checks) on macOS
        self.url = self.url.replace("localhost", "127.0.0.1")
        self.url = self.url.replace("/rpc", "") # Strip RPC path if present
        if not self.url.endswith("/sql"):
             self.url = f"{self.url.rstrip('/')}/sql"

        self.auth = (SURREAL_USER, SURREAL_PASS)
        self.headers = {
            "Accept": "application/json",
            "NS": SURREAL_NS,
            "DB": SURREAL_DB,
        }
        # Use a persistent HTTP client with connection pooling and IPv4 preference
        # CRITICAL: Configure for reliability and resilience
        self.client = httpx.AsyncClient(
            timeout=HTTP_TIMEOUT,
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
                keepalive_expiry=KEEPALIVE_EXPIRY
            ),
            # Prefer IPv4 to avoid IPv6 connection issues
            # httpx will try both, but this helps with reliability
        )
        
        self.initialized = False
        self.last_successful_query = 0.0  # Track last successful query time
        self.query_timeout = QUERY_TIMEOUT  # Default query timeout in seconds
        self.max_retries = MAX_RETRIES  # Retry connection failures
        self.retry_delay_base = RETRY_DELAY_BASE  # Base delay for exponential backoff

    def _serializable(self, obj: Any) -> Any:
        """Recursively convert SurrealDB objects to JSON-serializable types."""
        if isinstance(obj, list):
            return [self._serializable(item) for item in obj]
        if isinstance(obj, dict):
            return {k: self._serializable(v) for k, v in obj.items()}
        if isinstance(obj, datetime):
            return obj.isoformat()
        # Handle RecordID if strictly needed, mostly strings in result
        return str(obj)

    async def ensure_connected(self):
        """Ensure database connection is alive (Lazy HTTP check)."""
        if not self.initialized:
            self.initialized = True
            logger.info(f"Initialized HTTP Client for {self.url}")

    async def _execute_query(self, query: str, params: dict = None, raise_on_error: bool = False, **kwargs) -> Any:
        """Execute a SurrealQL query using HTTP REST API with retry logic for connection failures."""
        # SurrealQL safety check: block SQL-style patterns (HAVING/LIKE/SQL wildcards)
        upper_q = query.upper()
        if " HAVING " in upper_q or " LIKE " in upper_q or re.search(r"%[^\\s]*%", query):
            msg = f"SurrealQL validation failed: disallowed SQL pattern in query: {query}"
            logger.error(msg)
            if raise_on_error:
                raise ValueError(msg)
            return None

        # Check if this query contains transaction operations
        has_transaction = "BEGIN TRANSACTION" in upper_q or "COMMIT TRANSACTION" in upper_q or "ROLLBACK" in upper_q

        # Explicitly set NS/DB in SQL to avoid Header issues
        use_prefix = f"USE NS {SURREAL_NS} DB {SURREAL_DB};\n"

        final_sql = query
        if params:
            prefix = ""
            for k, v in params.items():
                val_json = json.dumps(v, default=str)
                prefix += f"LET ${k} = {val_json};\n"
            final_sql = prefix + query

        final_sql = use_prefix + final_sql

        # Retry logic for connection failures
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self.client.post(
                    self.url, 
                    content=final_sql, 
                    auth=self.auth, 
                    headers=self.headers,
                    **kwargs
                )
                
                if response.status_code != 200:
                    msg = f"Query Error HTTP {response.status_code}: {response.text}"
                    if raise_on_error:
                        raise Exception(msg)
                    # Log parse errors distinctly for monitoring
                    if "Parse error" in response.text:
                        logger.error(f"SURREAL_PARSE_ERROR: {msg}")
                    else:
                        logger.error(msg)
                    return None
                
                data = response.json()
                if isinstance(data, list) and data:
                    last_res = data[-1]
                    if last_res.get("status") == "OK":
                        self.last_successful_query = time.time()
                        return last_res.get("result")
                    else:
                        # Handle transaction failures - attempt rollback if transaction was active
                        if has_transaction and "TRANSACTION" in upper_q:
                            logger.warning("Transaction failed, attempting rollback...")
                            try:
                                await self._execute_query("ROLLBACK;", raise_on_error=False)
                                logger.info("Transaction rolled back successfully")
                            except Exception as rollback_error:
                                logger.error(f"Failed to rollback transaction: {rollback_error}")

                        # [PATCH] Silence "already exists" noise
                        result_msg = str(last_res.get("result", ""))
                        if "already exists" in result_msg:
                            logger.debug(f"DB entity already exists: {result_msg}")
                            return None

                        if raise_on_error:
                            raise Exception(f"Query Logic Error: {last_res}")
                        logger.error(f"Query Logic Error: {last_res}")
                        return None
                return data

            except (httpx.ConnectError, httpx.NetworkError, httpx.TimeoutException) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 0.5s, 1s, 2s
                    delay = self.retry_delay_base * (2 ** attempt)
                    logger.warning(f"Database connection failed (attempt {attempt + 1}/{self.max_retries}): {e}. Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Final attempt failed
                    if raise_on_error:
                        raise e
                    logger.error(f"Execution Error after {self.max_retries} attempts: {e}")
                    return None
            except Exception as e:
                # Non-connection errors don't retry
                if raise_on_error:
                    raise e
                logger.error(f"Execution Error: {e}")
                return None
        
        # Should never reach here, but handle it
        if raise_on_error and last_error:
            raise last_error
        return None

    async def execute_query(self, query: str, params: dict = None, raise_on_error: bool = False, **kwargs) -> Any:
        """
        Public facade for executing SurrealQL queries.
        Delegates to the internal _execute_query method which handles connection logic and retries.
        """
        return await self._execute_query(query, params=params, raise_on_error=raise_on_error, **kwargs)

    async def initialize(self):
        """Perform startup checks and index verification with startup retry logic."""
        if self.initialized:
            return
        
        logger.info("Initializing MemoryServer and ensuring schema...")
        await self.ensure_connected()
        
        # CRITICAL: Startup retry logic - database may not be ready immediately
        # Try up to 5 times with increasing delays (1s, 2s, 4s, 8s, 16s)
        max_startup_retries = 5
        startup_retry_delay = 1.0
        
        for startup_attempt in range(max_startup_retries):
            try:
                # Verify Connectivity Explicitly
                t0 = time.time()
                await self._execute_query("INFO FOR DB;", raise_on_error=True)
                latency = (time.time() - t0) * 1000
                logger.info(f"Database Connection Verified (Latency: {latency:.2f}ms)")
                break  # Success, exit retry loop
            except Exception as e:
                if startup_attempt < max_startup_retries - 1:
                    logger.warning(f"Database Connection FAILED (startup attempt {startup_attempt + 1}/{max_startup_retries}): {e}. Retrying in {startup_retry_delay:.1f}s...")
                    await asyncio.sleep(startup_retry_delay)
                    startup_retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    # Final attempt failed
                    logger.error(f"Database Connection FAILED after {max_startup_retries} startup attempts: {e}")
                    self.initialized = False
                    raise e  # Raise to allow caller to handle gracefully

        # Schema setup (only if connection succeeded)
        try:
            await self.ensure_schema()
            logger.info("MemoryServer initialization complete.")
        except Exception as e:
            # Schema errors are logged but don't prevent initialization
            logger.warning(f"Schema setup encountered errors (non-critical): {e}")
            # Still mark as initialized if connection works
            if self.initialized:
                logger.info("MemoryServer initialized (with schema warnings).")

    async def ensure_schema(self):
        """
        Define schema for the memory store.
        Uses DEFINE statements which are idempotent in SurrealQL, 
        but we suppress specific 'already exists' errors if the client raises them.
        """
        schema_queries = [
            # Fact Table
            "DEFINE TABLE fact SCHEMAFULL",
            "DEFINE FIELD entity ON TABLE fact TYPE string",
            "DEFINE FIELD relation ON TABLE fact TYPE string",
            "DEFINE FIELD target ON TABLE fact TYPE string",
            "DEFINE FIELD context ON TABLE fact TYPE string",
            "DEFINE FIELD content ON TABLE fact TYPE option<string>",
            "DEFINE FIELD kb_id ON TABLE fact TYPE string",
            "DEFINE FIELD confidence ON TABLE fact TYPE float",
            "DEFINE FIELD created_at ON TABLE fact TYPE datetime DEFAULT time::now()",
            "DEFINE FIELD embedding ON TABLE fact TYPE array<float>",
            "DEFINE INDEX idx_fact_kb ON TABLE fact COLUMNS kb_id",
            
            # Episode Table (Chat History)
            "DEFINE TABLE episode SCHEMAFULL",
            "DEFINE FIELD session_id ON TABLE episode TYPE string",
            "DEFINE FIELD role ON TABLE episode TYPE string",
            "DEFINE FIELD content ON TABLE episode TYPE string",
            "DEFINE FIELD timestamp ON TABLE episode TYPE datetime DEFAULT time::now()",
            "DEFINE FIELD embedding ON TABLE episode TYPE array",
            "DEFINE FIELD kb_id ON TABLE episode TYPE string",
            "DEFINE FIELD request_id ON TABLE episode TYPE string",
            "DEFINE FIELD consolidated ON TABLE episode TYPE bool DEFAULT false",
            "DEFINE INDEX idx_episode_kb ON TABLE episode COLUMNS kb_id",
            "DEFINE INDEX idx_episode_request ON TABLE episode COLUMNS request_id",
            "DEFINE INDEX idx_episode_embedding ON TABLE episode COLUMNS embedding MTREE DIMENSION 1024 DIST EUCLIDEAN",

            # Task Definitions (Sovereign Tasks)
            "DEFINE TABLE task_def SCHEMAFULL",
            "DEFINE FIELD name ON TABLE task_def TYPE string",
            "DEFINE FIELD type ON TABLE task_def TYPE string",
            "DEFINE FIELD enabled ON TABLE task_def TYPE bool",
            "DEFINE FIELD schedule ON TABLE task_def TYPE string",
            "DEFINE FIELD idle_only ON TABLE task_def TYPE bool DEFAULT false",
            "DEFINE FIELD priority ON TABLE task_def TYPE string DEFAULT 'low'",
            "DEFINE FIELD description ON TABLE task_def TYPE string",
            "DEFINE FIELD prompt ON TABLE task_def TYPE string",
            "DEFINE FIELD config ON TABLE task_def TYPE object",
            "DEFINE INDEX idx_task_name ON TABLE task_def COLUMNS name UNIQUE",
            
            # MCP Manager (Sovereign Tools)
            "DEFINE TABLE mcp_server SCHEMAFULL",
            "DEFINE FIELD name ON TABLE mcp_server TYPE string",
            "DEFINE FIELD command ON TABLE mcp_server TYPE string",
            "DEFINE FIELD args ON TABLE mcp_server TYPE array",
            "DEFINE FIELD env ON TABLE mcp_server TYPE object",
            "DEFINE FIELD enabled ON TABLE mcp_server TYPE bool",
            "DEFINE FIELD disabled_reason ON TABLE mcp_server TYPE option<string>",
            "DEFINE FIELD type ON TABLE mcp_server TYPE string DEFAULT 'stdio'",
            "DEFINE INDEX idx_mcp_name ON TABLE mcp_server COLUMNS name UNIQUE",

            # Source Table (Provenance)
            "DEFINE TABLE source SCHEMAFULL",
            "DEFINE FIELD url ON TABLE source TYPE string",
            "DEFINE FIELD title ON TABLE source TYPE string",
            "DEFINE FIELD author ON TABLE source TYPE string",
            "DEFINE FIELD reliability ON TABLE source TYPE float",
            "DEFINE FIELD summary ON TABLE source TYPE string",
            "DEFINE FIELD fingerprint ON TABLE source TYPE string",
            "DEFINE FIELD last_accessed ON TABLE source TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_source_url ON TABLE source COLUMNS url UNIQUE",

            # Config Tables
            "DEFINE TABLE memory_bank_config SCHEMAFULL",
            "DEFINE FIELD kb_id ON TABLE memory_bank_config TYPE string",
            "DEFINE FIELD owner ON TABLE memory_bank_config TYPE string",
            "DEFINE FIELD is_private ON TABLE memory_bank_config TYPE bool",
            "DEFINE INDEX idx_config_kb ON TABLE memory_bank_config COLUMNS kb_id UNIQUE",
            
            # [PHASE 44] System State Tables (Sovereignty)
            "DEFINE TABLE config_state SCHEMAFULL",
            "DEFINE FIELD key ON TABLE config_state TYPE string",
            "DEFINE FIELD value ON TABLE config_state TYPE string",
            "DEFINE FIELD source ON TABLE config_state TYPE string",
            "DEFINE FIELD last_updated ON TABLE config_state TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_config_key ON TABLE config_state COLUMNS key UNIQUE",
            
            "DEFINE TABLE system_state SCHEMAFULL",
            "DEFINE FIELD item ON TABLE system_state TYPE string",
            "DEFINE FIELD details ON TABLE system_state TYPE object",
            "DEFINE FIELD category ON TABLE system_state TYPE option<string>",
            "DEFINE FIELD last_updated ON TABLE system_state TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_system_item ON TABLE system_state COLUMNS item UNIQUE",

            # [PHASE 56] Advice Registry (User Rules)
            "DEFINE TABLE advice SCHEMAFULL",
            "DEFINE FIELD topic ON TABLE advice TYPE string",
            "DEFINE FIELD rule ON TABLE advice TYPE string",
            "DEFINE FIELD context ON TABLE advice TYPE string",
            "DEFINE FIELD created_at ON TABLE advice TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_advice_topic ON TABLE advice COLUMNS topic",
            
            # Advice Graph Edges
            "DEFINE TABLE related_to SCHEMAFULL TYPE RELATION",
            "DEFINE FIELD type ON TABLE related_to TYPE string",
            
            # Ingestion History (File Deduplication)
            "DEFINE TABLE ingestion_history SCHEMAFULL",
            "DEFINE FIELD file_hash ON TABLE ingestion_history TYPE string",
            "DEFINE FIELD ingested_at ON TABLE ingestion_history TYPE datetime DEFAULT time::now()",
            "DEFINE FIELD kb_id ON TABLE ingestion_history TYPE string",
            "DEFINE FIELD file_path ON TABLE ingestion_history TYPE string",
            "DEFINE FIELD file_size ON TABLE ingestion_history TYPE int",
            "DEFINE INDEX idx_ingestion_hash ON TABLE ingestion_history COLUMNS file_hash UNIQUE",
            "DEFINE INDEX idx_ingestion_kb ON TABLE ingestion_history COLUMNS kb_id",
            
            # Router Analysis Cache
            "DEFINE TABLE router_analysis_cache SCHEMAFULL",
            "DEFINE FIELD cache_key ON TABLE router_analysis_cache TYPE string",
            "DEFINE FIELD analysis_json ON TABLE router_analysis_cache TYPE string",
            "DEFINE FIELD created_at ON TABLE router_analysis_cache TYPE datetime DEFAULT time::now()",
            "DEFINE FIELD expires_at ON TABLE router_analysis_cache TYPE datetime",
            "DEFINE INDEX idx_router_cache_key ON TABLE router_analysis_cache COLUMNS cache_key UNIQUE",
            
            # Diagnostic Log (The Diagnostician)
            "DEFINE TABLE diagnostic_log SCHEMAFULL",
            "DEFINE FIELD timestamp ON TABLE diagnostic_log TYPE datetime DEFAULT time::now()",
            "DEFINE FIELD service ON TABLE diagnostic_log TYPE string",
            "DEFINE FIELD level ON TABLE diagnostic_log TYPE string",
            "DEFINE FIELD message ON TABLE diagnostic_log TYPE string",
            "DEFINE FIELD file ON TABLE diagnostic_log TYPE string",
            "DEFINE FIELD line ON TABLE diagnostic_log TYPE int",
            "DEFINE FIELD trace ON TABLE diagnostic_log TYPE string",
            "DEFINE FIELD handled ON TABLE diagnostic_log TYPE bool DEFAULT false",
            "DEFINE INDEX idx_diag_timestamp ON TABLE diagnostic_log COLUMNS timestamp",
            "DEFINE INDEX idx_diag_service ON TABLE diagnostic_log COLUMNS service",
            "DEFINE INDEX idx_diag_level ON TABLE diagnostic_log COLUMNS level",
            
            # Tool Definition (Semantic Tool Search)
            "DEFINE TABLE tool_definition SCHEMAFULL",
            "DEFINE FIELD name ON TABLE tool_definition TYPE string",
            "DEFINE FIELD description ON TABLE tool_definition TYPE string",
            "DEFINE FIELD embedding ON TABLE tool_definition TYPE array<float>",
            "DEFINE FIELD requires_admin ON TABLE tool_definition TYPE bool DEFAULT false",
            "DEFINE INDEX idx_tool_name ON TABLE tool_definition COLUMNS name UNIQUE",
            "DEFINE INDEX idx_tool_embedding ON TABLE tool_definition COLUMNS embedding MTREE DIMENSION 1024 DIST EUCLIDEAN",
            
            # Tool Performance (Reliability Tracking)
            "DEFINE TABLE tool_performance SCHEMAFULL",
            "DEFINE FIELD model ON TABLE tool_performance TYPE string",
            "DEFINE FIELD tool ON TABLE tool_performance TYPE string",
            "DEFINE FIELD success_count ON TABLE tool_performance TYPE int DEFAULT 0",
            "DEFINE FIELD failure_count ON TABLE tool_performance TYPE int DEFAULT 0",
            "DEFINE FIELD reliability_score ON TABLE tool_performance TYPE float",
            "DEFINE FIELD last_used ON TABLE tool_performance TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_tool_perf ON TABLE tool_performance COLUMNS model, tool UNIQUE",
            
            # Tool Rating (Comprehensive Evaluation)
            "DEFINE TABLE tool_rating SCHEMAFULL",
            "DEFINE FIELD tool_name ON TABLE tool_rating TYPE string",
            "DEFINE FIELD overall_rating ON TABLE tool_rating TYPE float",
            "DEFINE FIELD success_rate ON TABLE tool_rating TYPE float",
            "DEFINE FIELD avg_latency_ms ON TABLE tool_rating TYPE float",
            "DEFINE FIELD usage_count ON TABLE tool_rating TYPE int DEFAULT 0",
            "DEFINE FIELD error_frequency ON TABLE tool_rating TYPE float",
            "DEFINE FIELD last_evaluated ON TABLE tool_rating TYPE datetime DEFAULT time::now()",
            "DEFINE FIELD deprecated ON TABLE tool_rating TYPE bool DEFAULT false",
            "DEFINE FIELD deprecation_reason ON TABLE tool_rating TYPE option<string>",
            "DEFINE INDEX idx_tool_rating_name ON TABLE tool_rating COLUMNS tool_name UNIQUE",
            
            # Tool Version (Versioning System)
            "DEFINE TABLE tool_version SCHEMAFULL",
            "DEFINE FIELD tool_name ON TABLE tool_version TYPE string",
            "DEFINE FIELD version ON TABLE tool_version TYPE string",
            "DEFINE FIELD changelog ON TABLE tool_version TYPE option<string>",
            "DEFINE FIELD deprecated ON TABLE tool_version TYPE bool DEFAULT false",
            "DEFINE FIELD created_at ON TABLE tool_version TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_tool_version ON TABLE tool_version COLUMNS tool_name, version",
            
            # Tool Usage Analytics (Detailed Tracking)
            "DEFINE TABLE tool_usage_analytics SCHEMAFULL",
            "DEFINE FIELD tool_name ON TABLE tool_usage_analytics TYPE string",
            "DEFINE FIELD user_query ON TABLE tool_usage_analytics TYPE string",
            "DEFINE FIELD success ON TABLE tool_usage_analytics TYPE bool",
            "DEFINE FIELD latency_ms ON TABLE tool_usage_analytics TYPE float",
            "DEFINE FIELD context_length ON TABLE tool_usage_analytics TYPE int",
            "DEFINE FIELD model ON TABLE tool_usage_analytics TYPE string",
            "DEFINE FIELD timestamp ON TABLE tool_usage_analytics TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_tool_usage_tool ON TABLE tool_usage_analytics COLUMNS tool_name",
            "DEFINE INDEX idx_tool_usage_timestamp ON TABLE tool_usage_analytics COLUMNS timestamp",
            
            # Sentinel Rules (Monitoring)
            "DEFINE TABLE sentinel_rules SCHEMAFULL",
            "DEFINE FIELD name ON TABLE sentinel_rules TYPE string",
            "DEFINE FIELD pattern ON TABLE sentinel_rules TYPE string",
            "DEFINE FIELD action ON TABLE sentinel_rules TYPE string",
            "DEFINE FIELD enabled ON TABLE sentinel_rules TYPE bool DEFAULT true",
            "DEFINE INDEX idx_sentinel_name ON TABLE sentinel_rules COLUMNS name UNIQUE",
            
            # Registry Tables (Sovereign Configuration)
            "DEFINE TABLE registry_models SCHEMAFULL",
            "DEFINE FIELD key ON TABLE registry_models TYPE string",
            "DEFINE FIELD value ON TABLE registry_models TYPE string",
            "DEFINE FIELD source ON TABLE registry_models TYPE string",
            "DEFINE FIELD last_updated ON TABLE registry_models TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_reg_models_key ON TABLE registry_models COLUMNS key UNIQUE",
            
            "DEFINE TABLE registry_ports SCHEMAFULL",
            "DEFINE FIELD key ON TABLE registry_ports TYPE string",
            "DEFINE FIELD value ON TABLE registry_ports TYPE string",
            "DEFINE FIELD source ON TABLE registry_ports TYPE string",
            "DEFINE FIELD last_updated ON TABLE registry_ports TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_reg_ports_key ON TABLE registry_ports COLUMNS key UNIQUE",
            
            "DEFINE TABLE registry_policies SCHEMAFULL",
            "DEFINE FIELD key ON TABLE registry_policies TYPE string",
            "DEFINE FIELD value ON TABLE registry_policies TYPE string",
            "DEFINE FIELD source ON TABLE registry_policies TYPE string",
            "DEFINE FIELD last_updated ON TABLE registry_policies TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_reg_policies_key ON TABLE registry_policies COLUMNS key UNIQUE",
            
            "DEFINE TABLE registry_mcp SCHEMAFULL",
            "DEFINE FIELD key ON TABLE registry_mcp TYPE string",
            "DEFINE FIELD value ON TABLE registry_mcp TYPE string",
            "DEFINE FIELD source ON TABLE registry_mcp TYPE string",
            "DEFINE FIELD last_updated ON TABLE registry_mcp TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_reg_mcp_key ON TABLE registry_mcp COLUMNS key UNIQUE",
            
            # Model Presets (Named Model Configurations)
            "DEFINE TABLE model_preset SCHEMAFULL",
            "DEFINE FIELD name ON TABLE model_preset TYPE string",
            "DEFINE FIELD models ON TABLE model_preset TYPE object",
            "DEFINE FIELD models.* ON TABLE model_preset TYPE any",
            "DEFINE FIELD description ON TABLE model_preset TYPE string",
            "DEFINE FIELD created_at ON TABLE model_preset TYPE datetime DEFAULT time::now()",
            "DEFINE FIELD updated_at ON TABLE model_preset TYPE datetime DEFAULT time::now()",
            "DEFINE FIELD created_by ON TABLE model_preset TYPE string",
            "DEFINE INDEX idx_model_preset_name ON TABLE model_preset COLUMNS name UNIQUE",
            
            # Thinking Sessions (Sequential Thinking State)
            "DEFINE TABLE thinking_session SCHEMAFULL",
            "DEFINE FIELD session_id ON TABLE thinking_session TYPE string",
            "DEFINE FIELD thought_number ON TABLE thinking_session TYPE int",
            "DEFINE FIELD thought ON TABLE thinking_session TYPE string",
            "DEFINE FIELD total_thoughts ON TABLE thinking_session TYPE int",
            "DEFINE FIELD metadata ON TABLE thinking_session TYPE object",
            "DEFINE FIELD timestamp ON TABLE thinking_session TYPE datetime DEFAULT time::now()",
            "DEFINE FIELD latency_ms ON TABLE thinking_session TYPE float",
            "DEFINE FIELD success ON TABLE thinking_session TYPE bool",
            "DEFINE FIELD problem_type ON TABLE thinking_session TYPE string",
            "DEFINE INDEX idx_thinking_session ON TABLE thinking_session COLUMNS session_id, thought_number",
            "DEFINE INDEX idx_thinking_session_id ON TABLE thinking_session COLUMNS session_id",
            
            # Thinking Analytics
            "DEFINE TABLE thinking_analytics SCHEMAFULL",
            "DEFINE FIELD session_id ON TABLE thinking_analytics TYPE string",
            "DEFINE FIELD problem_type ON TABLE thinking_analytics TYPE string",
            "DEFINE FIELD total_thoughts ON TABLE thinking_analytics TYPE int",
            "DEFINE FIELD revisions_count ON TABLE thinking_analytics TYPE int",
            "DEFINE FIELD branches_count ON TABLE thinking_analytics TYPE int",
            "DEFINE FIELD avg_latency_ms ON TABLE thinking_analytics TYPE float",
            "DEFINE FIELD total_duration_ms ON TABLE thinking_analytics TYPE float",
            "DEFINE FIELD solved ON TABLE thinking_analytics TYPE bool",
            "DEFINE FIELD created_at ON TABLE thinking_analytics TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_thinking_analytics_session ON TABLE thinking_analytics COLUMNS session_id",
            "DEFINE INDEX idx_thinking_analytics_type ON TABLE thinking_analytics COLUMNS problem_type",

            # RAG/Long-term Memory Tables (Unified with main memory database)
            "DEFINE TABLE chunk SCHEMAFULL",
            "DEFINE FIELD content ON TABLE chunk TYPE string",
            "DEFINE FIELD kb_id ON TABLE chunk TYPE string",
            "DEFINE FIELD filename ON TABLE chunk TYPE string",
            "DEFINE FIELD metadata ON TABLE chunk TYPE object",
            "DEFINE FIELD embedding ON TABLE chunk TYPE array<float, 1024>",
            "DEFINE FIELD authority ON TABLE chunk TYPE number DEFAULT 1.0",
            "DEFINE FIELD timestamp ON TABLE chunk TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_chunk_kb ON TABLE chunk COLUMNS kb_id",
            "DEFINE INDEX idx_chunk_filename ON TABLE chunk COLUMNS filename",
            "DEFINE INDEX idx_chunk_content_search ON TABLE chunk FIELDS content SEARCH ANALYZER en_lemma BM25",
            "DEFINE INDEX idx_chunk_embedding ON TABLE chunk FIELDS embedding HNSW DIMENSION 1024 DIST EUCLIDEAN TYPE F32",

            "DEFINE TABLE entity SCHEMAFULL",
            "DEFINE FIELD name ON TABLE entity TYPE string",
            "DEFINE FIELD type ON TABLE entity TYPE string",
            "DEFINE FIELD description ON TABLE entity TYPE string",
            "DEFINE FIELD metadata ON TABLE entity TYPE object",
            "DEFINE FIELD last_updated ON TABLE entity TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_entity_name ON TABLE entity COLUMNS name",
            "DEFINE INDEX idx_entity_type ON TABLE entity COLUMNS type",
            "DEFINE INDEX idx_entity_name_search ON TABLE entity FIELDS name SEARCH ANALYZER en_lemma BM25",
            "DEFINE INDEX idx_entity_description_search ON TABLE entity FIELDS description SEARCH ANALYZER en_lemma BM25",

            "DEFINE TABLE relates SCHEMAFULL TYPE RELATION",
            "DEFINE FIELD relation ON TABLE relates TYPE string",
            "DEFINE FIELD description ON TABLE relates TYPE string",
            "DEFINE FIELD confidence ON TABLE relates TYPE float DEFAULT 1.0",
            "DEFINE FIELD created_at ON TABLE relates TYPE datetime DEFAULT time::now()",
            "DEFINE INDEX idx_relates_in ON TABLE relates COLUMNS in",
            "DEFINE INDEX idx_relates_out ON TABLE relates COLUMNS out",
        ]
        
        # [OPTIMIZATION] Batch execution to reduce HTTP round-trips
        # Previously ran ~50 queries sequentially (~4s latency). 
        # Now runs in 1 request.
        batch_query = ";\n".join(schema_queries) + ";"
        try:
            logger.debug(f"Applying Schema (Batch): {len(schema_queries)} definitions")
            # We don't raise on error for the batch because explicit "already exists" errors 
            # might block the whole batch if Surreal abhors them, 
            # but usually DEFINE is safe.
            # However, if one fails, we want others to proceed? 
            # Surreal script execution continues unless transaction fails. 
            # These are mostly DEFINEs.
            
            await self._execute_query(batch_query, raise_on_error=True)
            
        except Exception as e:
            # Fallback: If batch fails (e.g. strict safety mode), try sequential
            logger.warning(f"Batch schema update failed: {e}. Falling back to sequential.")
            for query in schema_queries:
                try:
                    await self._execute_query(query, raise_on_error=False)
                except Exception:
                    pass
        
        # Initialize DEFAULT_LOCATION if not exists
        try:
            init_query = """IF count(SELECT * FROM config_state WHERE key = 'DEFAULT_LOCATION') == 0 THEN
CREATE config_state SET
    key = 'DEFAULT_LOCATION',
    value = {
        city: 'Unknown',
        region: 'Unknown',
        postal_code: '',
        country: 'Unknown',
        lat: 0.0,
        lon: 0.0,
        timezone: 'UTC'
    };
END;"""
            await self._execute_query(init_query)
            logger.debug("DEFAULT_LOCATION initialized in database")
        except Exception as e:
            logger.debug(f"Failed to initialize DEFAULT_LOCATION (may already exist): {e}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the database connection.
        Returns status and latency information.
        """
        try:
            t0 = time.time()
            result = await self._execute_query("INFO FOR DB;", raise_on_error=True)
            latency = (time.time() - t0) * 1000
            
            return {
                "status": "healthy",
                "latency_ms": latency,
                "initialized": self.initialized,
                "last_successful_query": self.last_successful_query,
                "url": self.url
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "initialized": self.initialized,
                "url": self.url
            }
    
    async def reconnect(self) -> bool:
        """
        Attempt to reconnect to the database.
        Useful for recovery after connection failures.
        """
        try:
            # Close existing client if it exists
            if hasattr(self, 'client') and self.client:
                await self.client.aclose()
            
            # Create new client
            self.client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10,
                    keepalive_expiry=30.0
                )
            )
            
            # Test connection
            await self._execute_query("INFO FOR DB;", raise_on_error=True)
            self.initialized = True
            logger.info("Database reconnection successful")
            return True
        except Exception as e:
            logger.error(f"Database reconnection failed: {e}")
            self.initialized = False
            return False

    async def list_memory_banks(self):
        """List all unique memory bank IDs."""
        await self.ensure_connected()
        q = "SELECT kb_id FROM memory_bank_config"
        res = await self._execute_query(q)
        if res is None: return {"ok": False, "banks": []}
        return {"ok": True, "banks": self._serializable(res)}

    async def delete_memory_bank(self, kb_id: str):
        """Remove all facts/episodes and configuration for a bank."""
        logger.info(f"Deleting memory bank: {kb_id}")
        queries = [
            "BEGIN TRANSACTION;",
            f"DELETE fact WHERE kb_id = '{kb_id}';",
            f"DELETE episode WHERE kb_id = '{kb_id}';",
            f"DELETE memory_bank_config WHERE kb_id = '{kb_id}';",
            "COMMIT TRANSACTION;"
        ]
        
        for q in queries:
            await self._execute_query(q)
            
        return {"ok": True}

    async def get_embedding(self, text: str) -> List[float]:
        try:
            model = self.state.embedding_model if self.state else "ollama:mxbai-embed-large:latest"
            
            # Direct Ollama Bypass (Reliability)
            logger.debug(f"Using embed model: {model}")
            if "ollama" in model or "mxbai" in model:
                 try:
                     async with httpx.AsyncClient() as client:
                        # Strip "ollama:" prefix if present for some calls, though Ollama usually handles it if model name matches
                        # specifically mxbai-embed-large:latest
                        clean_model = model.replace("ollama:", "")
                        resp = await client.post(
                            "http://127.0.0.1:11434/api/embeddings",
                            json={"model": clean_model, "prompt": text},
                            timeout=30.0
                        )
                        if resp.status_code == 200:
                            return resp.json()["embedding"]
                        else:
                            logger.warning(f"Ollama Direct Embedding failed {resp.status_code}: {resp.text}")
                 except Exception as eo:
                     logger.warning(f"Ollama Direct failed: {eo}")
                     # Fallthrough to Gateway

            # Circuit Breaker Check
            if self.state and hasattr(self.state, "mcp_circuit_breaker"):
                 if not self.state.mcp_circuit_breaker.is_allowed(model):
                     logger.warning(f"Embedding Short-Circuited: Model '{model}' is broken.")
                     return [0.0] * EMBEDDING_DIMENSION
            
            headers = {}
            if ROUTER_AUTH_TOKEN:
                headers["Authorization"] = f"Bearer {ROUTER_AUTH_TOKEN}"
            async with httpx.AsyncClient(verify=False) as client:
                resp = await client.post(
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
                    logger.warning(f"Embedding failed HTTP {resp.status_code}: {resp.text}")
                    if self.state and hasattr(self.state, "mcp_circuit_breaker"):
                         self.state.mcp_circuit_breaker.record_failure(model)
                         
        except Exception as e:
            logger.warning(f"Failed to get embedding: {e}")
            if self.state and hasattr(self.state, "mcp_circuit_breaker"):
                 # Determine model variable if possible
                 m = self.state.embedding_model if self.state else "unknown"
                 self.state.mcp_circuit_breaker.record_failure(m)
                 
        return [0.0] * EMBEDDING_DIMENSION




    async def correct_fact(self, entity: str, relation: str, target: str, correction: str):
        """
        Explicitly correct a fact. 
        1. Finds any facts matching the entity/relation but with the OLD target.
        2. Penalizes their confidence (set to 0.1).
        3. Stores the NEW target with high confidence (0.95).
        """
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        
        try:
            # 1. Penalize old facts (Constraint: Same entity, Same relation, Different target)
            # This invalidates "Sky is Green" when we learn "Sky is Blue"
            penalize_sql = """
            BEGIN TRANSACTION;
            UPDATE fact SET confidence = 0.1, context = string::concat(context, ' [CORRECTED]') 
            WHERE entity = $e 
            AND relation = $r 
            AND target != $new_target 
            AND confidence > 0.1;
            COMMIT TRANSACTION;
            """
            await self._execute_query(penalize_sql, {
                "e": entity,
                "r": relation,
                "new_target": correction
            })
            
            # 2. Store new fact
            return await self.store_fact(entity, relation, correction, context="User Correction", confidence=0.95)
            
        except Exception as e:
            logger.error(f"Failed to correct fact: {e}")
            return {"ok": False, "error": str(e)}

    async def store_fact(self, entity: str, relation: str, target: str, context: Any = "", confidence: float = 1.0):
        """
        Store or update a fact with a 'truth/confidence' score.
        confidence 1.0 = User-provided / Ground Truth
        confidence 0.5-0.8 = Agent-inferred
        confidence < 0.4 = Vague/Suspect
        """
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}

        # Input validation to prevent data corruption
        if not entity or not isinstance(entity, (str, int, float)):
            return {"ok": False, "error": "Entity must be a non-empty string or number"}
        if not relation or not isinstance(relation, (str, int, float)):
            return {"ok": False, "error": "Relation must be a non-empty string or number"}
        if not target or not isinstance(target, (str, int, float)):
            return {"ok": False, "error": "Target must be a non-empty string or number"}

        # Validate confidence score
        try:
            confidence = float(confidence)
            if not (0.0 <= confidence <= 1.0):
                return {"ok": False, "error": "Confidence must be between 0.0 and 1.0"}
        except (ValueError, TypeError):
            return {"ok": False, "error": "Confidence must be a valid number"}

        # Sanitize inputs to prevent injection
        entity = str(entity).strip()[:500]  # Reasonable length limit
        relation = str(relation).strip()[:500]
        target = str(target).strip()[:2000]  # Allow longer targets
        if len(entity) == 0 or len(relation) == 0 or len(target) == 0:
            return {"ok": False, "error": "Entity, relation, and target cannot be empty after sanitization"}
        
        # Default to 'default' if no kb_id provided
        kb_id = str(context).split("extracted from ")[-1] if "extracted from" in str(context) else "default"
        # We'll allow explicit kb_id via a kwarg in a moment, but for now we detect or default.
        if isinstance(context, dict) and "kb_id" in context:
            kb_id = context["kb_id"]
        elif not context:
            kb_id = "default"
        
        try:
            # Use lock for critical database operations to prevent race conditions
            with self._operation_lock:
                # Generate embedding for the fact
                fact_text = f"{entity} {relation} {target} {context}"
                embedding = await self.get_embedding(fact_text)

                # Atomic UPSERT with Confidence Logic using SurrealQL logic
                # If we hear it again, confidence increases (math::max of old and new).
                sql = """
                BEGIN TRANSACTION;
                LET $existing = (SELECT id, confidence FROM fact WHERE entity = $e AND relation = $r AND target = $t AND kb_id = $kb LIMIT 1);
                IF count($existing) > 0 THEN
                    UPDATE fact SET
                        context = $c,
                        content = $txt,
                        embedding = $emb,
                        confidence = math::min([1.0, math::max([$existing[0].confidence, $conf])]),
                        created_at = time::now()
                    WHERE entity = $e AND relation = $r AND target = $t AND kb_id = $kb;
                ELSE
                    CREATE fact SET
                        entity = $e,
                        relation = $r,
                        target = $t,
                        context = $c,
                        content = $txt,
                        embedding = $emb,
                        kb_id = $kb,
                        confidence = $conf;
                END;
                COMMIT TRANSACTION;
                """

                await self._execute_query(sql, {
                    "e": str(entity),
                    "r": str(relation),
                    "t": str(target),
                    "c": str(context),
                    "txt": fact_text,
                    "emb": embedding,
                    "conf": confidence,
                    "kb": kb_id
                })
            logger.debug(f"Stored fact: {entity} {relation} {target} (Confidence: {confidence})")
            return {"ok": True}
        except Exception as e:
            logger.error(f"Failed to store fact: {e}")
            return {"ok": False, "error": str(e)}

    async def sync_sovereign_file(self, kb_id: str, content: str):
        """
        Sovereign Mode Sync:
        1. Deletes ALL facts associated with this kb_id (Wipe).
        2. Ingests the new content as fresh facts (Replace).
        This ensures the database remains a strict mirror of the file.

        Uses atomic operations with rollback on failure to prevent data corruption.
        """
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}

        # Input validation
        if not kb_id or not isinstance(kb_id, str):
            return {"ok": False, "error": "kb_id must be a non-empty string"}
        if not isinstance(content, str):
            return {"ok": False, "error": "content must be a string"}
        kb_id = kb_id.strip()[:200]  # Reasonable length limit
        if len(kb_id) == 0:
            return {"ok": False, "error": "kb_id cannot be empty after sanitization"}

        logger.info(f"Syncing Sovereign File: {kb_id}")

        try:
            # Use lock for critical sync operations to prevent race conditions
            with self._operation_lock:
                # Use atomic transaction for the entire sync operation
                # This ensures either all changes succeed or all are rolled back
                sync_sql = f"""
                BEGIN TRANSACTION;

                -- Delete existing facts and episodes for this kb_id
                DELETE fact WHERE kb_id = '{kb_id}';
                DELETE episode WHERE kb_id = '{kb_id}';

                -- Insert sovereign source fact
                CREATE fact SET
                    entity = 'SovereignFile',
                    relation = 'has_content',
                    target = '{kb_id}',
                    context = {{kb_id: '{kb_id}', sovereign: true}},
                    content = 'Sovereign file content for {kb_id}',
                    kb_id = '{kb_id}',
                    confidence = 1.0;

                COMMIT TRANSACTION;
                """

                # Execute the sync transaction
                result = await self._execute_query(sync_sql, raise_on_error=True)
                if result is None:
                    return {"ok": False, "error": "Sync transaction failed"}

            # Now safely add content chunks outside the critical transaction
            # (since chunking is not critical for data integrity)
            await self._add_content_chunks(kb_id, content)

            logger.info(f"Successfully synced Sovereign File: {kb_id}")
            return {"ok": True}
        except Exception as e:
            logger.error(f"Failed to sync sovereign file {kb_id}: {e}")
            return {"ok": False, "error": str(e)}

    async def _add_content_chunks(self, kb_id: str, content: str):
        """
        Add content chunks for a sovereign file.
        This is done outside the main transaction since chunking failures
        shouldn't prevent the file sync from succeeding.
        """
        try:
            # Basic splitting (paragraph based)
            chunks = [p for p in content.split('\n\n') if p.strip()]

            for i, chunk in enumerate(chunks):
                if not chunk.strip(): continue
                # Store chunk as a separate fact for searchability
                await self.store_fact(
                    entity=f"ContentChunk_{i}",
                    relation="belongs_to",
                    target=f"kb_{kb_id}",
                    context={"kb_id": kb_id, "chunk_index": i, "sovereign": True},
                    confidence=0.8  # Lower confidence for auto-chunked content
                )
        except Exception as e:
            logger.warning(f"Failed to add content chunks for {kb_id}: {e}")
            # Don't fail the whole sync for chunking issues
            
            # 2. Ingest New Content
            # We need to parse valid facts/chunks from the content.
            # Ideally we'd use an LLM or specific parser.
            # For now, we store the *Document* itself as a single "Fact" of content, 
            # and potentially chunks if we had a chunker here.
            # To be useful for RAG, we should likely chunk it.
            # Relying on 'content' field in fact table.
            
            # Store the whole document as a primary "Sovereign Source" fact
            await self.store_fact(
                entity="SovereignFile", 
                relation="has_content", 
                target=f"{kb_id}", 
                context={"kb_id": kb_id, "sovereign": True}, 
                confidence=1.0
            )

            # Store the actual text in a way retrievable by semantic search.
            # For now, simplistic: One big matching chunk if < 4k chars, else just reference?
            # Better: We insert a "Content Block" fact.
            
            # Assuming 'chunks' logic is upstream or we do basic splitting here.
            # Basic splitting (paragraph based)
            chunks = [p for p in content.split('\n\n') if p.strip()]
            
            for i, chunk in enumerate(chunks):
                if not chunk.strip(): continue
                # We store these as facts where 'content' is the chunk
                # Entity=File, Relation=contains_chunk, Target=Index
                await self.store_fact(
                    entity=kb_id, 
                    relation="contains_chunk", 
                    target=f"{i}", 
                    context=chunk, # The text itself is the context/content for RAG
                    confidence=1.0 
                )
                
            logger.info(f"Sovereign Sync Complete for {kb_id}: {len(chunks)} chunks synced.")
            return {"ok": True, "chunks": len(chunks)}

        except Exception as e:
            logger.error(f"Sovereign Sync Failed: {e}")
            return {"ok": False, "error": str(e)}

    async def check_sovereign_state(self, kb_id: str):
        """
        Check if a sovereign file exists and return its metadata (timestamp).
        """
        await self.ensure_connected()
        if not self.initialized: return None
        
        try:
            # Check the "SovereignFile" fact we stored
            q = "SELECT created_at FROM fact WHERE entity = 'SovereignFile' AND relation = 'has_content' AND target = $kb_id LIMIT 1"
            res = await self._execute_query(q, {"kb_id": kb_id})
            
            if res and len(res) > 0:
                return res[0].get("created_at")
            return None
        except Exception as e:
            logger.error(f"Failed to check sovereign state: {e}")
            return None

    async def get_sovereign_file_content(self, kb_id: str) -> Optional[str]:
        """
        Retrieve the full content of a sovereign file from the database.
        Reconstructs content from chunks stored as facts.
        
        Args:
            kb_id: The knowledge base ID (e.g., "system/lexicon")
            
        Returns:
            Full content as string, or None if not found
        """
        await self.ensure_connected()
        if not self.initialized: return None
        
        try:
            # Retrieve all chunks for this kb_id, ordered by index
            q = """
            SELECT target, context 
            FROM fact 
            WHERE entity = $kb_id 
            AND relation = 'contains_chunk'
            ORDER BY target ASC
            """
            res = await self._execute_query(q, {"kb_id": kb_id})
            
            if not res:
                return None
            
            # Reconstruct content by joining chunks
            chunks = [str(r.get("context", "")) for r in res]
            return "\n\n".join(chunks)
        except Exception as e:
            logger.error(f"Failed to retrieve sovereign file content for {kb_id}: {e}")
            return None

    async def list_sovereign_files(self) -> List[Dict[str, Any]]:
        """
        List all sovereign files stored in the database.
        
        Returns:
            List of dicts with kb_id and metadata
        """
        await self.ensure_connected()
        if not self.initialized: return []
        
        try:
            q = """
            SELECT target as kb_id, created_at, timestamp
            FROM fact 
            WHERE entity = 'SovereignFile' 
            AND relation = 'has_content'
            ORDER BY created_at DESC
            """
            res = await self._execute_query(q)
            return res if res else []
        except Exception as e:
            logger.error(f"Failed to list sovereign files: {e}")
            return []

    async def delete_fact(self, fact_id: str):
        """Permanently remove a fact by its ID."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        
        try:
            # Check if exists
            check = await self._execute_query("SELECT id FROM fact WHERE id = type::thing('fact', $id)", {"id": fact_id})
            if not check:
                # Try raw ID if not typed
                check = await self._execute_query("SELECT id FROM fact WHERE id = $id", {"id": fact_id})
            
            if not check:
                return {"ok": False, "error": "Fact not found"}
                
            await self._execute_query("DELETE fact WHERE id = $id", {"id": check[0]["id"]})
            logger.info(f"Deleted fact: {fact_id}")
            return {"ok": True}
        except Exception as e:
            logger.error(f"Failed to delete fact {fact_id}: {e}")
            return {"ok": False, "error": str(e)}

    async def query_facts(self, entity: Optional[str] = None, relation: Optional[str] = None, limit: int = 1000):
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            q = "SELECT *, id as fact_id FROM fact"
            params = {}
            if entity or relation:
                q += " WHERE "
                parts = []
                if entity:
                    parts.append("entity = $e")
                    params["e"] = str(entity)
                if relation:
                    parts.append("relation = $r")
                    params["r"] = str(relation)
                q += " AND ".join(parts)
            q += f" ORDER BY timestamp DESC LIMIT {limit}"
            
            # [DEBUG] Log the query attempt
            # logger.debug(f"Executing query_facts. Query: {q} Params: {params}")

            res = await self._execute_query(q, params)
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            facts = self._serializable(res)
            # Remove embeddings from output
            for f in facts:
                if isinstance(f, dict):
                    f.pop("embedding", None)
            logger.debug(f"Queried facts: {len(facts)} returned (entity={entity}, relation={relation})")
            return {"ok": True, "facts": facts}
        except Exception as e:
            logger.error(f"Failed to query facts: {e}")
            return {"ok": False, "error": str(e)}
    

    async def semantic_search(self, query: str, limit: int = 50):
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            embedding = await self.get_embedding(query)
            # Try vector search with fallback
            try:
                # Note: kwargs 'timeout' passed to _execute_query
                # Vector search + Confidence weighting
                # We can filter by kb_id if needed, but for now we search all visible ones
                res = await self._execute_query(
                    "SELECT *, vector::distance::euclidean(embedding, $emb) AS dist FROM fact WHERE confidence > 0.3 ORDER BY dist ASC LIMIT $limit",
                    {"emb": embedding, "limit": limit},
                    timeout=15.0
                )
            except Exception as e:
                # Fallback to keyword search
                logger.info(f"Vector search failed (degrading to keyword): {e}")
                try:
                    res = await self._execute_query(
                        "SELECT *, id as fact_id FROM fact WHERE (entity CONTAINS $q OR relation CONTAINS $q OR target CONTAINS $q) ORDER BY timestamp DESC LIMIT $limit",
                        {"q": query, "limit": limit},
                        timeout=10.0
                    )
                except Exception as fallback_error:
                    logger.error(f"Fallback keyword search failed: {fallback_error}")
                    res = None
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            facts = self._serializable(res)
            for f in facts:
                if isinstance(f, dict):
                    f.pop("embedding", None)
            return {"ok": True, "facts": facts}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def index_tools(self, tool_defs: List[Dict[str, Any]]):
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        count = 0
        
        # Import security defaults
        from agent_runner.tool_security import tool_requires_admin
        
        for td in tool_defs:
            func = td.get("function", {})
            name = func.get("name")
            desc = func.get("description", "")
            if not name: continue
            emb = await self.get_embedding(f"{name}: {desc}")
            
            # Get security requirement from code defaults
            requires_admin = tool_requires_admin(name)
            
            # This is a multi-statement query block, _execute_query handles return of LAST statement properly?
            # Creating complex logic might need updates. For now assuming simple update/create works.
            res = await self._execute_query("""
                UPDATE tool_definition SET 
                    description = $desc, 
                    embedding = $emb,
                    requires_admin = $requires_admin
                WHERE name = $name;
                IF count(SELECT * FROM tool_definition WHERE name = $name) == 0 THEN
                    CREATE tool_definition SET 
                        name = $name, 
                        description = $desc, 
                        embedding = $emb,
                        requires_admin = $requires_admin
                END;
            """, {"name": name, "desc": desc, "emb": emb, "requires_admin": requires_admin})
            if res is not None:
                count += 1
        return {"ok": True, "indexed": count}

    async def get_memory_stats(self):
        """Get statistics about the database tables."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            # Fact stats
            fact_res = await self._execute_query("SELECT count() FROM fact GROUP ALL")
            # Result is now a list of rows, e.g. [{count: 10}]
            fact_count = fact_res[0].get("count", 0) if fact_res and len(fact_res) > 0 else 0
            
            # Episode stats
            ep_res = await self._execute_query("SELECT count() FROM episode GROUP ALL")
            ep_count = ep_res[0].get("count", 0) if ep_res and len(ep_res) > 0 else 0
            
            # Tool performance stats
            perf_res = await self._execute_query("SELECT count() FROM tool_performance GROUP ALL")
            perf_count = perf_res[0].get("count", 0) if perf_res and len(perf_res) > 0 else 0
            
            return {
                "ok": True,
                "fact_count": fact_count,
                "episode_count": ep_count,
                "tool_performance_count": perf_count,
                "timestamp": time.time()
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def trigger_backup(self):
        """Execute the backup shell script."""
        try:
            # Path to the backup script
            script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "backup_memory.sh")
            process = await asyncio.create_subprocess_exec(
                "bash", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                return {"ok": True, "message": stdout.decode().splitlines()[-1]}
            else:
                return {"ok": False, "error": stderr.decode()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def reindex_memory(self):
        """Regenerate embeddings for all facts using the current embedding model."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            # 1. Fetch all facts
            res = await self._execute_query("SELECT id, entity, relation, target FROM fact")
            if not res:
                return {"ok": True, "messsage": "No facts to reindex."}
            
            facts = res
            count = 0
            logger.info(f"Starting re-index of {len(facts)} facts...")
            
            # 2. Re-embed each
            for f in facts:
                fact_text = f"{f.get('entity', '')} {f.get('relation', '')} {f.get('target', '')}"
                embedding = await self.get_embedding(fact_text)
                # logger.info(f"DEBUG: Embedding Len: {len(embedding)} Sample: {embedding[:3]}")
                
                # 3. Update
                upd_res = await self._execute_query("UPDATE fact SET embedding = $emb WHERE id = type::thing($id) RETURN AFTER", {"id": f['id'], "emb": embedding})
                # logger.info(f"DEBUG: Update Result: {upd_res}")
                count += 1
                if count % 10 == 0:
                    logger.info(f"Re-indexed {count}/{len(facts)}...")
            
            return {"ok": True, "reindexed_count": count}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def optimize_memory(self):
        """Run SurrealDB optimization/integrity checks."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            # SurrealDB doesn't have a direct 'VACUUM' like SQLite, 
            # but INFO and basic counts serve as sanity/integrity checks.
            res = await self._execute_query("INFO FOR DB;")
            return {"ok": True, "info": str(res)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def process_memories(self):
        """Trigger the Agent Runner to consolidate episodes into facts immediately."""
        url = "http://127.0.0.1:5460/admin/tasks/consolidation"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, timeout=5.0)
                if resp.status_code == 200:
                    return {"ok": True, "message": "Triggered background processing."}
                return {"ok": False, "error": f"Failed: {resp.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def index_own_architecture(self):
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        # Get count before indexing
        try:
            before_res = await self._execute_query("SELECT count() FROM fact WHERE context = 'Architecture' GROUP ALL")
            before_count = 0
            if before_res and len(before_res) > 0 and len(before_res[0].get("result", [])) > 0:
                before_count = before_res[0]["result"][0].get("count", 0)
        except Exception:
            before_count = 0
        
        
        # Use additive approach - store_fact now uses upsert, so we don't delete
        facts = [
            ("project", "contains_module", "router"),
            ("project", "contains_module", "agent_runner"),
            ("project", "contains_config", "config/config.yaml"),
            ("router", "implements", "API Gateway"),
            ("agent_runner", "implements", "Agent Loop"),
            ("project-memory", "uses", "SurrealDB"),
        ]
        count = 0
        for e, r, t in facts:
            res = await self.store_fact(e, r, t, context="Architecture")
            if res.get("ok"): count += 1
        
        # Get count after indexing
        try:
            after_res = await self._execute_query("SELECT count() FROM fact WHERE context = 'Architecture' GROUP ALL")
            after_count = 0
            if after_res and len(after_res) > 0 and len(after_res[0].get("result", [])) > 0:
                after_count = after_res[0]["result"][0].get("count", 0)
        except Exception:
            after_count = count
        
        logger.info(f"Indexed architecture: {count} facts processed, {after_count} total architecture facts in DB")
        return {"ok": True, "indexed_count": count, "total_architecture_facts": after_count}

    async def record_tool_result(self, model: str, tool: str, success: bool, latency_ms: float):
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            # Alpha for moving average (0.1 means newer results have 10% weight)
            alpha = 0.2
            s_inc = 1 if success else 0
            f_inc = 0 if success else 1
            new_val = 1.0 if success else 0.0
            
            # Use UPSERT with LET for idempotent updates
            res = await self._execute_query("""
                LET $existing = (SELECT * FROM tool_performance WHERE model = $model AND tool = $tool LIMIT 1);
                IF count($existing) > 0 THEN
                    UPDATE tool_performance SET 
                        success_count = $existing[0].success_count + $s_inc,
                        failure_count = $existing[0].failure_count + $f_inc,
                        reliability_score = $existing[0].reliability_score * (1.0 - $alpha) + $new_val * $alpha,
                        last_used = time::now()
                    WHERE model = $model AND tool = $tool;
                ELSE
                    CREATE tool_performance SET
                        model = $model,
                        tool = $tool,
                        success_count = $s_inc,
                        failure_count = $f_inc,
                        reliability_score = $new_val,
                        last_used = time::now();
                END;
            """, {"model": model, "tool": tool, "s_inc": s_inc, "f_inc": f_inc, "new_val": new_val, "alpha": alpha})
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def record_performance_snapshot(self, model: str, total_calls: int, success_rate: float, avg_latency_ms: float):
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            res = await self._execute_query(
                "CREATE performance_snapshot SET model = $model, total_calls = $total, success_rate = $rate, avg_latency_ms = $latency",
                {"model": model, "total": total_calls, "rate": success_rate, "latency": avg_latency_ms}
            )
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def store_mcp_intel(self, name: str, github_url: str, newsletter: str, similar_servers: List[str]):
        """Store intelligence about an MCP server."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            sql = """
            LET $existing = (SELECT id FROM mcp_intel WHERE name = $name LIMIT 1);
            IF count($existing) > 0 THEN
                UPDATE mcp_intel SET 
                    github_url = $github_url, 
                    newsletter = $newsletter, 
                    similar_servers = $similar_servers, 
                    last_updated = time::now() 
                WHERE name = $name;
            ELSE
                CREATE mcp_intel SET 
                    name = $name, 
                    github_url = $github_url, 
                    newsletter = $newsletter, 
                    similar_servers = $similar_servers, 
                    last_updated = time::now();
            END;
            """
            res = await self._execute_query(sql, {
                "name": name,
                "github_url": github_url,
                "newsletter": newsletter,
                "similar_servers": similar_servers
            })
            if res is None:
                # _execute_query logs errors
                return {"ok": False, "error": "Query execution failed"}
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def query_mcp_intel(self, name: Optional[str] = None):
        """Query MCP intelligence."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            q = "SELECT * FROM mcp_intel"
            params = {}
            if name:
                q += " WHERE name = $name"
                params["name"] = name
            res = await self._execute_query(q, params)
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            # res is already the list of results
            return {"ok": True, "intel": self._serializable(res) if res else []}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # [PHASE 43] Source Authority Tools
    async def store_source(self, url: str, title: str, author: str = "", reliability: float = 0.5, summary: str = ""):
        """Store or update a trusted source."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            # UPSERT by URL (Unique Index)
            sql = """
            LET $existing = (SELECT id FROM source WHERE url = $url LIMIT 1);
            IF count($existing) > 0 THEN
                UPDATE source SET 
                    title = $title, 
                    author = $author, 
                    reliability = $reliability, 
                    summary = $summary, 
                    last_accessed = time::now() 
                WHERE url = $url;
            ELSE
                CREATE source SET 
                    url = $url, 
                    title = $title, 
                    author = $author, 
                    reliability = $reliability, 
                    summary = $summary, 
                    last_accessed = time::now();
            END;
            """
            res = await self._execute_query(sql, {
                "url": url,
                "title": title,
                "author": author,
                "reliability": reliability,
                "summary": summary
            })
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def list_sources(self, limit: int = 50):
        """List trusted sources."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            res = await self._execute_query("SELECT * FROM source ORDER BY reliability DESC LIMIT $limit", {"limit": limit})
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            # res is already the list of results
            return {"ok": True, "sources": self._serializable(res) if res else []}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def get_suggested_tools(self, query_intent: str, model: str):
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            embedding = await self.get_embedding(query_intent)
            try:
                res = await self._execute_query(
                    "SELECT name, vector::distance::euclidean(embedding, $emb) as dist FROM tool_definition WHERE vector::distance::euclidean(embedding, $emb) < 0.7 ORDER BY dist ASC LIMIT 5",
                    {"emb": embedding},
                    timeout=15.0
                )
            except Exception:
                res = await self._execute_query("SELECT name FROM tool_definition LIMIT 5")
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            tools = [r["name"] for r in res] if res else []
            
            # Incorporate reliability AND ratings for tool advisor
            # We favor tools with:
            # 1. High reliability score (> 0.5) OR
            # 2. High overall rating (> 0.7) OR
            # 3. Haven't been used in a while (Exploration)
            # Exclude deprecated tools
            perf = await self._execute_query("""
                SELECT tp.tool, tp.reliability_score, tr.overall_rating
                FROM tool_performance tp
                LEFT JOIN tool_rating tr ON tr.tool_name = tp.tool
                WHERE tp.model = $model
                AND (tp.reliability_score > 0.5 OR tr.overall_rating > 0.7 OR time::now() - tp.last_used > 1h)
                AND (tr.deprecated IS NULL OR tr.deprecated = false)
                ORDER BY COALESCE(tr.overall_rating, tp.reliability_score, 0.5) DESC
                LIMIT 5
            """, {"model": model})
            if perf: 
                tools.extend([r["tool"] for r in perf])
            
            return {"ok": True, "suggested_tools": list(set(tools))}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def store_episode(self, request_id: str, messages: List[Dict[str, Any]]):
        """Store a conversation episode with vector indexing."""
        # logger.info(f"DEBUG: Entering store_episode for {request_id}")
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        
        try:
            # Sanitize messages to ensure content is string
            safe_messages = []
            for m in messages:
                sm = m.copy()
                if sm.get("content") is None:
                    sm["content"] = ""
                safe_messages.append(sm)
            
            # Extract role from first message, default to "user"
            role = safe_messages[0].get("role", "user") if safe_messages else "user"
            
            # Flatten messages to text for embedding
            full_text = "\n".join([f"{m.get('role','?')}: {m.get('content','')}" for m in safe_messages])
            
            # Generate Embedding (Simulated or Real)
            embedding = await self.get_embedding(full_text)
            
            # Set required fields: kb_id defaults to "default", session_id uses request_id
            res = await self._execute_query(
                "UPSERT type::thing('episode', $rid) SET request_id = $rid, session_id = $session_id, role = $role, kb_id = $kb_id, messages = $msg, content = $full_text, embedding = $emb, timestamp = time::now(), consolidated = false",
                {
                    "rid": request_id,
                    "session_id": request_id,  # Use request_id as session_id
                    "role": role,
                    "kb_id": "default",
                    "msg": safe_messages,
                    "full_text": full_text,
                    "emb": embedding
                }
            )
            
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            return {"ok": True}
        except Exception as e:
            # logger.error(f"DEBUG: Error in store_episode: {e}")
            return {"ok": False, "error": str(e)}

    async def get_unconsolidated_episodes(self, limit: int = 10):
        """Get episodes that haven't been consolidated into facts yet."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            # Fixed: Restore WHERE consolidated = false
            res = await self._execute_query(
                "SELECT * FROM episode WHERE consolidated = false ORDER BY timestamp ASC LIMIT $limit",
                {"limit": limit}
            )
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            # Removed print to avoid breaking MCP protocol
            return {"ok": True, "episodes": self._serializable(res)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def mark_episode_consolidated(self, request_id: str):
        """Mark an episode as processed."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            await self._execute_query("UPDATE type::thing('episode', $rid) SET consolidated = true", {"rid": request_id})
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def prune_offboarded_mcp_servers(self, active_servers: List[str]):
        """Remove MCP servers from intelligence that are no longer configured."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            # Delete any mcp_intel record where name is NOT in the active_servers list
            sql = "DELETE mcp_intel WHERE name NOT IN $active_servers"
            res = await self._execute_query(sql, {"active_servers": active_servers})
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            return {"ok": True, "details": str(res)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # [PHASE 56] Advice Registry Methods
    async def store_advice(self, topic: str, rule: str, context: str = ""):
        """Store a heuristic rule or advice for a specific topic."""
        await self.ensure_connected()
        try:
            # Check for dupes by rule content to avoid spam
            check = await self._execute_query("SELECT * FROM advice WHERE topic = $topic AND rule = $rule", {"topic": topic, "rule": rule})
            if check:
                 return {"ok": True, "message": "Advice already exists", "id": check[0]["id"]}

            sql = "CREATE advice SET topic = $topic, rule = $rule, context = $context"
            res = await self._execute_query(sql, {"topic": topic, "rule": rule, "context": context})
            if res:
                return {"ok": True, "id": res[0]["id"], "message": f"Advice on '{topic}' stored."}
            return {"ok": False, "error": "Database write failed"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def consult_advice(self, topic: str):
        """Retrieve advice for a specific topic, INCLUDING graph traversal (Parents). Never raises."""
        await self.ensure_connected()
        try:
            # 1. Find Node

            # We used a Sanitized ID logic in ingest. We need to replicate it or Search by topic field.
            # Search by topic field is safer.
            nodes = await self._execute_query("SELECT id, topic, rule FROM advice WHERE topic = $topic", {"topic": topic})
            if not nodes:
                 # Graceful exit - NOT an error
                 return {"ok": True, "advice": [], "message": f"No advice node found for '{topic}'"}
            
            target_node = nodes[0]
            
            # 2. Traverse Up (Find Parents)
            # SurrealQL: SELECT <-related_to<-advice FROM $id
            # This fetches the immediate parents. Ideally we recurse, but Surreal recursion is tricky.
            # For now, 1 level up is huge improvement.
            parents_q = f"SELECT <-related_to<-advice.rule as parent_rules, <-related_to<-advice.topic as parent_topics FROM {target_node['id']}"
            parents_res = await self._execute_query(parents_q)
            
            # Formulate Context
            advice_chain = []
            
            # Parents first (High level rules)
            if parents_res and parents_res[0]:
                 p_topics = parents_res[0].get("parent_topics", [])
                 p_rules = parents_res[0].get("parent_rules", [])
                 for i, p_topic in enumerate(p_topics):
                      if p_rules[i]:
                           advice_chain.append(f"Parent Context ({p_topic}): {p_rules[i]}")
            
            # Then specific rule
            if target_node.get("rule"):
                advice_chain.append(f"Direct Advice ({target_node['topic']}): {target_node['rule']}")
            
            return {"ok": True, "advice": advice_chain, "structure": "Tree Path"}

        except Exception as e:
            logger.error(f"Consult Advice Error (Suppressed): {e}")
            return {"ok": True, "advice": [], "error_suppressed": str(e)}

    async def ingest_advice_tree(self, markdown_content: str):
        """Parse a Markdown tree and sync it to the Advice Graph."""
        await self.ensure_connected()
        lines = markdown_content.split('\n')
        stack = [] # [(indent_level, topic_id_string)]
        trace = []
        
        try:
            # Clear existing table roughly (or we could do diffing, but full rebuild is safer for 'Sovereign' sync)
            # For Safety, let's just Upsert. Relations might duplicate if we don't clear edges.
            # Let's clear edges first?
            await self._execute_query("DELETE related_to")
            await self._execute_query("DELETE advice")
            trace.append("Deleted related_to and advice")
            
            for line in lines:
                if not line.strip() or line.strip().startswith('#'): continue
                
                logger.info(f"DEBUG INGEST: Processing '{line}'")
                
                # Calculate indent
                indent = len(line) - len(line.lstrip())
                content = line.strip()
                if content.startswith('- '): content = content[2:]
                
                # Check for Rule
                rule_text = ""
                topic_name = content
                if "Rule:" in content:
                    parts = content.split("Rule:", 1)
                    topic_name = parts[0].strip() # Might be empty if it's just a rule node?
                    rule_text = parts[1].strip()
                    if not topic_name: topic_name = "RuleNode" # Should arguably attach rule to parent?
                
                # Handle hierarchy
                while stack and stack[-1][0] >= indent:
                    stack.pop()
                
                parent_topic = stack[-1][1] if stack else None
                
                # If it's just a rule for the parent, update the parent
                if topic_name == "RuleNode" or (not topic_name and rule_text):
                     if parent_topic:
                         # Append rule to parent? Or create a rule node?
                         # Let's make it a property of the parent for simplicity if possible,
                         # OR strictly: Everything is a Node.
                         # Let's assume the user format: "- Topic" ... "- Rule: ..." means Rule belongs to Topic.
                         # Actually, usually "- Rule:" is indented UNDER the topic.
                         pass 
                
                # Create/Update Node
                # We use topic_name as ID key roughly
                # Sanitize ID
                valid_id = "".join(x for x in topic_name if x.isalnum() or x in ['_','-']).lower()
                if not valid_id: valid_id = f"node_{int(time.time()*1000)}"
                
                # If it is a distinct topic line
                if topic_name and topic_name != "RuleNode":
                    # Upsert Node
                    nid_slug = valid_id
                    nid = f"advice:{nid_slug}"
                    
                    # Store via INSERT with explicit type string construction to avoid ambiguity
                    # Use UPSERT for SurrealDB (handles duplicates automatically)
                    q = "UPSERT type::thing('advice', $slug) SET topic = $topic, rule = $rule, context = 'Registry';"
                    params = {"slug": nid_slug, "topic": topic_name, "rule": rule_text or ""}
                    
                    await self._execute_query(q, params)
                    trace.append(f"Upserted Node: {nid} ({topic_name})")
                    
                    # Create Edge
                    if parent_topic:
                        # RELATE parent -> child
                        # type: 'subcategory'
                        rel_q = f"RELATE {parent_topic}->related_to->{nid} SET type = 'subcategory'"
                        await self._execute_query(rel_q)
                        trace.append(f"Linked {parent_topic} -> {nid}")
                    
                    stack.append((indent, nid))
                
                elif rule_text and parent_topic:
                     # It's a rule line attached to the parent
                     # We might want to append it to a list of rules, or just update the 'rule' field (last wins?)
                     # Better: Create a distinct node for the rule?
                     # OR: Let's just append to a 'rules' array on the parent node? 
                     # Schema defined 'rule' as string. Let's append text.
                     # Fetch current
                     curr = await self._execute_query(f"SELECT rule FROM {parent_topic}")
                     curr_rule = curr[0].get("rule", "") if curr else ""
                     new_rule = f"{curr_rule}\n- {rule_text}".strip()
                     
                     # Update via UPDATE (clean ID)
                     u_q = f"UPDATE {parent_topic} SET rule = $r"
                     await self._execute_query(u_q, {"r": new_rule})
                     trace.append(f"Appended rule to {parent_topic}")
            
            # Verify Count
            count_res = await self._execute_query("SELECT count() FROM advice")
            trace.append(f"Final Count: {count_res}")
            
            return {"ok": True, "message": "Advice Tree Synced", "trace": trace}

        except Exception as e:
            return {"ok": False, "error": str(e), "trace": trace}

    async def check_health(self) -> Dict[str, Any]:
        """Check server health status."""
        try:
            await self.ensure_connected()
            if not self.initialized:
                return {"ok": False, "connected": False, "error": "DB not connected", "timestamp": time.time()}
            
            # Quick health check
            res = await self._execute_query("INFO FOR DB;")
            if res is None:
                return {"ok": False, "connected": False, "error": "Health check query failed", "timestamp": time.time()}
                
            return {"ok": True, "connected": True, "timestamp": time.time()}
        except Exception as e:
            self.initialized = False
            return {"ok": False, "connected": False, "error": str(e), "timestamp": time.time()}

async def main():
    from mcp.server.stdio import stdio_server
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    server = Server("orchestrator-memory")
    memory = MemoryServer()
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name="store_fact", description="Store a fact in long-term memory with an optional confidence score.", inputSchema={"type":"object","properties":{"entity":{"type":"string"},"relation":{"type":"string"},"target":{"type":"string"},"context":{"type":"object"},"confidence":{"type":"number", "description": "1.0 for user-confirmed ground truth, lower for agent-inferred guesses."}},"required":["entity","relation","target"]}),
            Tool(name="delete_fact", description="Permanently delete a fact.", inputSchema={"type":"object","properties":{"fact_id":{"type":"string"}},"required":["fact_id"]}),
            Tool(name="query_facts", description="Search facts.", inputSchema={"type":"object","properties":{"entity":{"type":"string"},"relation":{"type":"string"}}}),
            Tool(name="semantic_search", description="Search by meaning.", inputSchema={"type":"object","properties":{"query":{"type":"string"},"limit":{"type":"integer"}},"required":["query"]}),
            Tool(name="record_tool_result", description="Record tool result.", inputSchema={"type":"object","properties":{"model":{"type":"string"},"tool":{"type":"string"},"success":{"type":"boolean"},"latency_ms":{"type":"number"}},"required":["model","tool","success","latency_ms"]}),
            Tool(name="get_suggested_tools", description="Suggest tools.", inputSchema={"type":"object","properties":{"query_intent":{"type":"string"},"model":{"type":"string"}},"required":["query_intent","model"]}),
            Tool(name="index_tools", description="Index tools.", inputSchema={"type":"object","properties":{"tool_defs":{"type":"array","items":{"type":"object"}}},"required":["tool_defs"]}),
            Tool(name="index_own_architecture", description="Index project.", inputSchema={"type":"object","properties":{}}),
            Tool(name="record_performance_snapshot", description="Record metrics snapshot.", inputSchema={"type":"object","properties":{"model":{"type":"string"},"total_calls":{"type":"integer"},"success_rate":{"type":"number"},"avg_latency_ms":{"type":"number"}},"required":["model","total_calls","success_rate","avg_latency_ms"]}),
            Tool(name="store_mcp_intel", description="Store MCP server intel.", inputSchema={"type":"object","properties":{"name":{"type":"string"},"github_url":{"type":"string"},"newsletter":{"type":"string"},"similar_servers":{"type":"array","items":{"type":"string"}}},"required":["name","github_url","newsletter","similar_servers"]}),
            Tool(name="query_mcp_intel", description="Query MCP server intel.", inputSchema={"type":"object","properties":{"name":{"type":"string"}}}),
            Tool(name="prune_offboarded_mcp_servers", description="Remove stale MCP server intel.", inputSchema={"type":"object","properties":{"active_servers":{"type":"array","items":{"type":"string"}}},"required":["active_servers"]}),
            Tool(name="check_health", description="Check health.", inputSchema={"type":"object","properties":{}}),
            Tool(name="get_memory_stats", description="Get statistics about facts and episodes in memory.", inputSchema={"type":"object","properties":{}}),
            Tool(name="trigger_backup", description="Trigger a manual backup of the memory database.", inputSchema={"type":"object","properties":{}}),
            Tool(name="reindex_memory", description="Re-generate embeddings for all facts.", inputSchema={"type":"object","properties":{}}),
            Tool(name="process_memories", description="Force processing of recent chats into memory.", inputSchema={"type":"object","properties":{}}),
            Tool(name="optimize_memory", description="Run optimization/integrity checks on the memory database.", inputSchema={"type":"object","properties":{}}),
            Tool(name="store_episode", description="Store a conversation episode.", inputSchema={"type":"object","properties":{"request_id":{"type":"string"},"messages":{"type":"array","items":{"type":"object"}}},"required":["request_id","messages"]}),
            Tool(name="get_unconsolidated_episodes", description="Get unconsolidated episodes.", inputSchema={"type":"object","properties":{"limit":{"type":"integer"}}}),
            Tool(name="mark_episode_consolidated", description="Mark episode as consolidated.", inputSchema={"type":"object","properties":{"request_id":{"type":"string"}},"required":["request_id"]}),
            # Source Authority
            Tool(name="store_source", description="Store/Update a trusted source.", inputSchema={"type":"object","properties":{"url":{"type":"string"},"title":{"type":"string"},"author":{"type":"string"},"reliability":{"type":"number"},"summary":{"type":"string"}},"required":["url","title"]}),
            Tool(name="list_sources", description="List trusted sources.", inputSchema={"type":"object","properties":{"limit":{"type":"integer"}}}),
            # Advice Registry
            Tool(name="store_advice", description="Store a rule/advice for a topic.", inputSchema={"type":"object","properties":{"topic":{"type":"string", "description": "e.g. 'weather_errors'"},"rule":{"type":"string", "description": "The advice/rule"},"context":{"type":"string"}},"required":["topic","rule"]}),
            Tool(name="consult_advice", description="Check advice for a topic.", inputSchema={"type":"object","properties":{"topic":{"type":"string"}},"required":["topic"]}),
            Tool(name="sync_advice_tree", description="Ingest advice_registry.md from disk.", inputSchema={"type":"object","properties":{}})
        ]
    @server.call_tool()
    async def call_tool(name: str, args: dict) -> list[TextContent]:
        try:
            # Ensure connected before any tool call (lazy connection)
            await memory.ensure_connected()
            if name == "store_fact": res = await memory.store_fact(**args)
            elif name == "delete_fact": res = await memory.delete_fact(**args)
            elif name == "query_facts": res = await memory.query_facts(**args)
            elif name == "semantic_search": res = await memory.semantic_search(**args)
            elif name == "record_tool_result": res = await memory.record_tool_result(**args)
            elif name == "get_suggested_tools": res = await memory.get_suggested_tools(**args)
            elif name == "index_tools": res = await memory.index_tools(**args)
            elif name == "index_own_architecture": res = await memory.index_own_architecture()
            elif name == "record_performance_snapshot": res = await memory.record_performance_snapshot(**args)
            elif name == "store_mcp_intel": res = await memory.store_mcp_intel(**args)
            elif name == "query_mcp_intel": res = await memory.query_mcp_intel(**args)
            elif name == "prune_offboarded_mcp_servers": res = await memory.prune_offboarded_mcp_servers(**args)
            elif name == "check_health": res = await memory.check_health()
            elif name == "get_memory_stats": res = await memory.get_memory_stats()
            elif name == "trigger_backup": res = await memory.trigger_backup()
            elif name == "reindex_memory": res = await memory.reindex_memory()
            elif name == "process_memories": res = await memory.process_memories()
            elif name == "optimize_memory": res = await memory.optimize_memory()
            elif name == "store_episode": res = await memory.store_episode(**args)
            elif name == "get_unconsolidated_episodes": res = await memory.get_unconsolidated_episodes(**args)
            elif name == "mark_episode_consolidated": res = await memory.mark_episode_consolidated(**args)
            elif name == "store_source": res = await memory.store_source(**args)
            elif name == "list_sources": res = await memory.list_sources(**args)
            elif name == "store_advice": res = await memory.store_advice(**args)
            elif name == "consult_advice": res = await memory.consult_advice(**args)
            elif name == "sync_advice_tree": 
                # Read file from here
                try:
                    # Use async file I/O
                    import aiofiles
                    async with aiofiles.open("/Users/bee/Sync/Antigravity/ai/config/advice_registry.md", "r") as f:
                        content = await f.read()
                    res = await memory.ingest_advice_tree(content)
                except Exception as e: res = {"ok": False, "error": str(e)}
            else: raise ValueError(f"Unknown tool: {name}")
            return [TextContent(type="text", text=json.dumps(res))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"ok":False,"error":str(e)}))]
    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
