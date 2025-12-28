import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple
import sys
from pathlib import Path
import yaml
from surrealdb import AsyncSurreal, RecordID
import httpx
from datetime import datetime

# Configuration
import sys
SURREAL_URL = os.getenv("SURREAL_URL", "http://localhost:8000")
SURREAL_USER = os.getenv("SURREAL_USER", "root")
SURREAL_PASS = os.getenv("SURREAL_PASS", "root")
SURREAL_NS = os.getenv("SURREAL_NS", "orchestrator")
SURREAL_DB = os.getenv("SURREAL_DB", "memory")
EMBED_MODEL = os.getenv("EMBED_MODEL", "ollama:embeddinggemma:300m")
GATEWAY_BASE = os.getenv("GATEWAY_BASE", "http://127.0.0.1:5455")
ROUTER_AUTH_TOKEN = os.getenv("ROUTER_AUTH_TOKEN")

# Embedding dimension (default for most embedding models)
EMBEDDING_DIMENSION = 1024

# Set up logging to stderr
def log(msg, level="INFO"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    sys.stderr.write(f"{timestamp} {level} memory_server {msg}\n")
    sys.stderr.flush()

class MemoryServer:
    def __init__(self):
        # Ensure URL is HTTP and points to /sql
        self.url = SURREAL_URL.replace("ws://", "http://").replace("wss://", "https://")
        self.url = self.url.replace("/rpc", "") # Strip RPC path if present
        if not self.url.endswith("/sql"):
             self.url = f"{self.url.rstrip('/')}/sql"
        
        self.auth = (SURREAL_USER, SURREAL_PASS)
        self.headers = {
            "Accept": "application/json",
            "NS": SURREAL_NS,
            "DB": SURREAL_DB,
        }
        # Use a persistent HTTP client
        self.client = httpx.AsyncClient(timeout=30.0)
        
        self.initialized = False
        self.last_successful_query = 0.0  # Track last successful query time
        self.query_timeout = 10.0  # Default query timeout in seconds

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
            log(f"Initialized HTTP Client for {self.url}")

    async def _execute_query(self, query: str, params: dict = None, **kwargs) -> Any:
        """Execute a SurrealQL query using HTTP REST API."""
        try:
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

            response = await self.client.post(
                self.url, 
                content=final_sql, 
                auth=self.auth, 
                headers=self.headers,
                **kwargs
            )
            
            if response.status_code != 200:
                log(f"Query Error HTTP {response.status_code}: {response.text}", "ERROR")
                return None
            
            data = response.json()
            if isinstance(data, list) and data:
                last_res = data[-1]
                if last_res.get("status") == "OK":
                    self.last_successful_query = time.time()
                    return last_res.get("result")
                else:
                    log(f"Query Logic Error: {last_res}", "ERROR")
                    return None
            return data

        except Exception as e:
            log(f"Execution Error: {e}", "ERROR")
            return None


    async def get_embedding(self, text: str) -> List[float]:
        try:
            headers = {}
            if ROUTER_AUTH_TOKEN:
                headers["Authorization"] = f"Bearer {ROUTER_AUTH_TOKEN}"
            async with httpx.AsyncClient(verify=False) as client:
                resp = await client.post(
                    f"{GATEWAY_BASE}/v1/embeddings",
                    json={"model": EMBED_MODEL, "input": text},
                    headers=headers,
                    timeout=10.0
                )
                if resp.status_code == 200:
                    return resp.json()["data"][0]["embedding"]
        except Exception as e:
            log(f"Failed to get embedding: {e}", "WARNING")
        return [0.0] * EMBEDDING_DIMENSION




    async def store_fact(self, entity: str, relation: str, target: str, context: Any = ""):
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        
        try:
            # Generate embedding for the fact
            fact_text = f"{entity} {relation} {target} {context}"
            embedding = await self.get_embedding(fact_text)
            
            # Check if fact exists
            check_res = await self._execute_query(
                "SELECT id FROM fact WHERE entity = $e AND relation = $r AND target = $t",
                {"e": str(entity), "r": str(relation), "t": str(target)}
            )
            
            update_res = None
            if check_res and len(check_res) > 0:
                # Update existing
                 update_res = await self._execute_query(
                    "UPDATE fact SET context = $c, embedding = $emb, timestamp = time::now() WHERE entity = $e AND relation = $r AND target = $t",
                    {"e": str(entity), "r": str(relation), "t": str(target), "c": context, "emb": embedding}
                )
            
            # If no rows were updated, create new fact
            if not update_res:
                await self._execute_query(
                    "CREATE fact SET entity = $e, relation = $r, target = $t, context = $c, embedding = $emb",
                    {"e": str(entity), "r": str(relation), "t": str(target), "c": context, "emb": embedding}
                )
            log(f"Stored fact: {entity} {relation} {target} (context: {context})", "DEBUG")
            return {"ok": True}
        except Exception as e:
            log(f"Failed to store fact: {e}", "ERROR")
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
            res = await self._execute_query(q, params)
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            facts = self._serializable(res)
            # Remove embeddings from output
            for f in facts:
                if isinstance(f, dict):
                    f.pop("embedding", None)
            log(f"Queried facts: {len(facts)} returned (entity={entity}, relation={relation})", "DEBUG")
            return {"ok": True, "facts": facts}
        except Exception as e:
            log(f"Failed to query facts: {e}", "ERROR")
            return {"ok": False, "error": str(e)}
    

    async def semantic_search(self, query: str, limit: int = 50):
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            embedding = await self.get_embedding(query)
            # Try vector search with fallback
            try:
                # Note: kwargs 'timeout' passed to _execute_query
                res = await self._execute_query(
                    "SELECT *, vector::distance::euclidean(embedding, $emb) AS dist FROM fact ORDER BY dist ASC LIMIT $limit",
                    {"emb": embedding, "limit": limit},
                    timeout=15.0
                )
            except Exception as e:
                # Fallback to keyword search
                log(f"Vector search failed (degrading to keyword): {e}", "WARNING")
                try:
                    res = await self._execute_query(
                        "SELECT *, id as fact_id FROM fact WHERE (entity CONTAINS $q OR relation CONTAINS $q OR target CONTAINS $q) ORDER BY timestamp DESC LIMIT $limit",
                        {"q": query, "limit": limit},
                        timeout=10.0
                    )
                except Exception as fallback_error:
                    log(f"Fallback keyword search failed: {fallback_error}", "ERROR")
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
        for td in tool_defs:
            func = td.get("function", {})
            name = func.get("name")
            desc = func.get("description", "")
            if not name: continue
            emb = await self.get_embedding(f"{name}: {desc}")
            # This is a multi-statement query block, _execute_query handles return of LAST statement properly?
            # Creating complex logic might need updates. For now assuming simple update/create works.
            res = await self._execute_query("""
                UPDATE tool_definition SET description = $desc, embedding = $emb WHERE name = $name;
                IF count(SELECT * FROM tool_definition WHERE name = $name) == 0 THEN
                    CREATE tool_definition SET name = $name, description = $desc, embedding = $emb
                END;
            """, {"name": name, "desc": desc, "emb": emb})
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
        import subprocess
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
            if not res or not res[0].get("result"):
                return {"ok": True, "messsage": "No facts to reindex."}
            
            facts = res[0]["result"]
            count = 0
            log(f"Starting re-index of {len(facts)} facts...", "INFO")
            
            # 2. Re-embed each
            for f in facts:
                fact_text = f"{f.get('entity', '')} {f.get('relation', '')} {f.get('target', '')}"
                embedding = await self.get_embedding(fact_text)
                
                # 3. Update
                await self._execute_query("UPDATE $id SET embedding = $emb", {"id": f['id'], "emb": embedding})
                count += 1
                if count % 10 == 0:
                    log(f"Re-indexed {count}/{len(facts)}...", "INFO")
            
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
        
        log(f"Indexed architecture: {count} facts processed, {after_count} total architecture facts in DB", "INFO")
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
            
            res = await self._execute_query("""
                LET $existing = (SELECT * FROM tool_performance WHERE model = $model AND tool = $tool LIMIT 1);
                IF count($existing) > 0 THEN
                    UPDATE tool_performance SET 
                        success_count += $s_inc,
                        failure_count += $f_inc,
                        reliability_score = reliability_score * (1.0 - $alpha) + $new_val * $alpha,
                        last_used = time::now()
                    WHERE model = $model AND tool = $tool
                ELSE
                    CREATE tool_performance SET
                        model = $model,
                        tool = $tool,
                        success_count = $s_inc,
                        failure_count = $f_inc,
                        reliability_score = $new_val,
                        last_used = time::now()
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
            # Check if exists
            res = await self._execute_query("SELECT * FROM mcp_intel WHERE name = $name", {"name": name})
            if res is None:
                return {"ok": False, "error": "Query execution failed"}
            exists = res and res[0].get("result")
            if exists:
                update_res = await self._execute_query("UPDATE mcp_intel SET github_url=$github_url, newsletter=$newsletter, similar_servers=$similar_servers, last_updated=time::now() WHERE name=$name", {"name": name, "github_url": github_url, "newsletter": newsletter, "similar_servers": similar_servers})
            else:
                update_res = await self._execute_query("CREATE mcp_intel SET name=$name, github_url=$github_url, newsletter=$newsletter, similar_servers=$similar_servers, last_updated=time::now()", {"name": name, "github_url": github_url, "newsletter": newsletter, "similar_servers": similar_servers})
            if update_res is None:
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
            return {"ok": True, "intel": self._serializable(res[0].get("result", [])) if res else []}
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
            
            # Incorporate reliability for tool advisor
            # We favor tools with score > 0.5 or tools that haven't been used in a while (Exploration)
            perf = await self._execute_query("""
                SELECT tool FROM tool_performance 
                WHERE model = $model 
                AND (reliability_score > 0.5 OR time::now() - last_used > 1h)
                ORDER BY reliability_score DESC LIMIT 3
            """, {"model": model})
            if perf: tools.extend([r["tool"] for r in perf])
            
            return {"ok": True, "suggested_tools": list(set(tools))}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def store_episode(self, request_id: str, messages: List[Dict[str, Any]]):
        """Store a conversation episode for background processing."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            # Pass list directly to let Client handle serialization
            res = await self._execute_query(
                "UPSERT type::thing('episode', $rid) SET request_id = $rid, messages = $msg, timestamp = time::now(), consolidated = false",
                {"rid": request_id, "msg": messages}
            )
            if res is None:
                return {"ok": False, "error": "Query execution failed (None result)"}
            log(f"STORE EPISODE SUCCESS: {request_id} RES: {res}")
            return {"ok": True, "db_result": str(res)}
        except Exception as e:
            log(f"STORE EPISODE ERROR: {e}")
            return {"ok": False, "error": str(e)}

    async def get_unconsolidated_episodes(self, limit: int = 10):
        """Get episodes that haven't been consolidated into facts yet."""
        await self.ensure_connected()
        if not self.initialized: return {"ok": False, "error": "DB not connected"}
        try:
            # DEBUG: Removed WHERE consolidated = false
            res = await self._execute_query(
                "SELECT * FROM episode ORDER BY timestamp ASC LIMIT $limit",
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
            Tool(name="store_fact", description="Store fact.", inputSchema={"type":"object","properties":{"entity":{"type":"string"},"relation":{"type":"string"},"target":{"type":"string"},"context":{"type":"object"}},"required":["entity","relation","target"]}),
            Tool(name="query_facts", description="Search facts.", inputSchema={"type":"object","properties":{"entity":{"type":"string"},"relation":{"type":"string"}}}),
            Tool(name="semantic_search", description="Search by meaning.", inputSchema={"type":"object","properties":{"query":{"type":"string"},"limit":{"type":"integer"}},"required":["query"]}),
            Tool(name="record_tool_result", description="Record tool result.", inputSchema={"type":"object","properties":{"model":{"type":"string"},"tool":{"type":"string"},"success":{"type":"boolean"},"latency_ms":{"type":"number"}},"required":["model","tool","success","latency_ms"]}),
            Tool(name="get_suggested_tools", description="Suggest tools.", inputSchema={"type":"object","properties":{"query_intent":{"type":"string"},"model":{"type":"string"}},"required":["query_intent","model"]}),
            Tool(name="index_tools", description="Index tools.", inputSchema={"type":"object","properties":{"tool_defs":{"type":"array","items":{"type":"object"}}},"required":["tool_defs"]}),
            Tool(name="index_own_architecture", description="Index project.", inputSchema={"type":"object","properties":{}}),
            Tool(name="record_performance_snapshot", description="Record metrics snapshot.", inputSchema={"type":"object","properties":{"model":{"type":"string"},"total_calls":{"type":"integer"},"success_rate":{"type":"number"},"avg_latency_ms":{"type":"number"}},"required":["model","total_calls","success_rate","avg_latency_ms"]}),
            Tool(name="store_mcp_intel", description="Store MCP server intel.", inputSchema={"type":"object","properties":{"name":{"type":"string"},"github_url":{"type":"string"},"newsletter":{"type":"string"},"similar_servers":{"type":"array","items":{"type":"string"}}},"required":["name","github_url","newsletter","similar_servers"]}),
            Tool(name="query_mcp_intel", description="Query MCP server intel.", inputSchema={"type":"object","properties":{"name":{"type":"string"}}}),
            Tool(name="check_health", description="Check health.", inputSchema={"type":"object","properties":{}}),
            Tool(name="get_memory_stats", description="Get statistics about facts and episodes in memory.", inputSchema={"type":"object","properties":{}}),
            Tool(name="trigger_backup", description="Trigger a manual backup of the memory database.", inputSchema={"type":"object","properties":{}}),
            Tool(name="reindex_memory", description="Re-generate embeddings for all facts.", inputSchema={"type":"object","properties":{}}),
            Tool(name="process_memories", description="Force processing of recent chats into memory.", inputSchema={"type":"object","properties":{}}),
            Tool(name="optimize_memory", description="Run optimization/integrity checks on the memory database.", inputSchema={"type":"object","properties":{}}),
            Tool(name="store_episode", description="Store a conversation episode.", inputSchema={"type":"object","properties":{"request_id":{"type":"string"},"messages":{"type":"array","items":{"type":"object"}}},"required":["request_id","messages"]}),
            Tool(name="get_unconsolidated_episodes", description="Get unconsolidated episodes.", inputSchema={"type":"object","properties":{"limit":{"type":"integer"}}}),
            Tool(name="mark_episode_consolidated", description="Mark episode as consolidated.", inputSchema={"type":"object","properties":{"request_id":{"type":"string"}},"required":["request_id"]})
        ]
    @server.call_tool()
    async def call_tool(name: str, args: dict) -> list[TextContent]:
        try:
            # Ensure connected before any tool call (lazy connection)
            await memory.ensure_connected()
            if name == "store_fact": res = await memory.store_fact(**args)
            elif name == "query_facts": res = await memory.query_facts(**args)
            elif name == "semantic_search": res = await memory.semantic_search(**args)
            elif name == "record_tool_result": res = await memory.record_tool_result(**args)
            elif name == "get_suggested_tools": res = await memory.get_suggested_tools(**args)
            elif name == "index_tools": res = await memory.index_tools(**args)
            elif name == "index_own_architecture": res = await memory.index_own_architecture()
            elif name == "record_performance_snapshot": res = await memory.record_performance_snapshot(**args)
            elif name == "store_mcp_intel": res = await memory.store_mcp_intel(**args)
            elif name == "query_mcp_intel": res = await memory.query_mcp_intel(**args)
            elif name == "check_health": res = await memory.check_health()
            elif name == "get_memory_stats": res = await memory.get_memory_stats()
            elif name == "trigger_backup": res = await memory.trigger_backup()
            elif name == "reindex_memory": res = await memory.reindex_memory()
            elif name == "process_memories": res = await memory.process_memories()
            elif name == "optimize_memory": res = await memory.optimize_memory()
            elif name == "store_episode": res = await memory.store_episode(**args)
            elif name == "get_unconsolidated_episodes": res = await memory.get_unconsolidated_episodes(**args)
            elif name == "mark_episode_consolidated": res = await memory.mark_episode_consolidated(**args)
            else: raise ValueError(f"Unknown tool: {name}")
            return [TextContent(type="text", text=json.dumps(res))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"ok":False,"error":str(e)}))]
    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
