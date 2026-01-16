import logging
import asyncio
import json
from typing import List, Dict, Any, Optional

logger = logging.getLogger("agent_runner.vector_store")

class ToolsetVectorIndex:
    """
    Manages semantic search for tool definitions using SurrealDB (vector search)
    and shared embeddings from state.memory.
    """
    
    def __init__(self, state):
        self.state = state
        # self.memory accessed dynamically via property or state
        self.last_index_time = 0
        self.indexed_count = 0
        
    @property
    def memory(self):
        return self.state.memory
        
    async def index_tools(self, tools: List[Dict[str, Any]]):
        """
        Embed and upsert tool definitions into the 'tool_definition' table.
        This allows the Maître d' to find 'memory' tools when user asks for 'recall'.
        """
        if not tools:
            return

        # Wait for memory to be initialized (proper async signaling)
        # Executor spawns this task before AgentState.initialize() completes
        try:
            await asyncio.wait_for(self.state.memory_initialized_event.wait(), timeout=30.0)
        except asyncio.TimeoutError:
            logger.warning("Timed out waiting for MemoryServer initialization. Skipping tool indexing.")
            return

        
        logger.info(f"Indexing {len(tools)} tools into Vector Store...")
        
        # [FIX] Clear existing tools to prevent ID collisions (Random vs Deterministic IDs)
        # We are switching to deterministic IDs based on tool name.
        try:
            await self.memory.execute_query("DELETE FROM tool_definition RETURN NONE;")
        except Exception as e:
            logger.warning(f"Failed to clear tool_definitions: {e}")

        # We index concurrently for speed
        tasks = []
        for tool in tools:
            tasks.append(self._upsert_tool(tool))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("ok"))
        self.indexed_count = success_count
        self.last_index_time = asyncio.get_event_loop().time()
        logger.info(f"Vector Store Indexing Complete: {success_count}/{len(tools)} tools active.")

    async def _upsert_tool(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single tool: Embed -> Upsert."""
        try:
            # Handle both flat and OpenAI-style nested tool definitions
            if "function" in tool:
                name = tool["function"].get("name")
                description = tool["function"].get("description", "")
            else:
                name = tool.get("name")
                description = tool.get("description", "")
            
            if not name:
                logger.warning(f"Skipping index for malformed tool: {tool}")
                return {"ok": False}
                
            # Combine name and description for semantic richness
            # "tavily-search: Search the web for current events..."
            embedding_text = f"{name}: {description}"
            
            # Use shared embedding logic (Ollama/Gateway)
            # If memory is not ready or fails, this might be None
            vector = await self.memory.get_embedding(embedding_text)
            
            if vector is None:
                 logger.warning(f"Skipping index for {name}: Embedding returned None.")
                 return {"ok": False}
            
            # Check for zero-vector (failure)
            if all(v == 0.0 for v in vector):
                logger.warning(f"Skipping index for {name}: Extraction failed (Zero Vector).")
                return {"ok": False}
                
            # Upsert into SurrealDB
            # We use `tool_definition` table defined in memory_server schema
            q = """
            UPSERT type::thing("tool_definition", $name) SET
                name = $name,
                description = $desc,
                embedding = $emb,
                requires_admin = $admin;
            """
            
            await self.memory.execute_query(q, {
                "name": name,
                "desc": description,
                "emb": vector,
                "admin": "admin" in name or "system" in name
            })
            return {"ok": True}
            
        except Exception as e:
            safe_name = tool.get('name') if isinstance(tool, dict) else 'Unknown'
            logger.error(f"Failed to upsert tool {safe_name}: {e}")
            return {"ok": False, "error": str(e)}

    async def search_tools(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search for tools relevant to the query.
        Returns a list of tool definitions (name, description, score).
        """
        if not self.memory or not self.memory.initialized:
            return []

        try:
            # 1. Embed user query
            vector = await self.memory.get_embedding(query)
            
            # 2. Vector Search (Cosine Similarity)
            # vector::similarity::cosine(embedding, $query_vector)
            q = """
            SELECT *, vector::similarity::cosine(embedding, $vec) as score 
            FROM tool_definition 
            WHERE score > 0.4
            ORDER BY score DESC 
            LIMIT $limit;
            """
            
            results = await self.memory.execute_query(q, {
                "vec": vector,
                "limit": limit
            })
            
            return results if results else []
            
        except Exception as e:
            logger.error(f"Vector Tool Search failed: {e}")
            return []
