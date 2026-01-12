import logging
import time
from typing import List, Dict, Any, Optional

# Constants
# Relevance threshold for vector similarity (0.0 to 1.0)
# Lower = more permissive, Higher = stricter
# Note: SurrealDB <|4|> operator usage depends on distance function. 
# For Euclidean, lower distance = closer. 
# For Cosine similarity (if configured), higher = closer.
# Our MemoryServer uses Euclidean for embeddings usually.
# Let's assume we sort by relevance/score.

logger = logging.getLogger("fast_selector")

class FastToolSelector:
    """
    High-performance tool selector using Vector Search (RAG) instead of LLM reasoning.
    Reduces tool selection latency from ~4s (LLM) to <100ms (DB).
    """

    @staticmethod
    async def select_tools(
        query: str, 
        all_tools: List[Dict[str, Any]], 
        memory_server: Any,
        limit: int = 15, 
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Select relevant tools for a query using vector embeddings.
        
        Args:
            query: User's query string.
            all_tools: Full list of available tool definitions (as fallback/reference).
            memory_server: Instance of MemoryServer (connected to SurrealDB).
            limit: Max number of tools to return.
            threshold: (Unused currently) Similarity threshold.
            
        Returns:
            List[Dict[str, Any]]: Filtered list of tool definitions.
        """
        if not query or not memory_server or not memory_server.initialized:
            # Fallback: Return all tools if we can't search
            return all_tools

        t0 = time.time()
        
        try:
            # 1. Get Query Embedding
            # This uses the restored RAG infrastructure
            embedding = await memory_server.get_embedding(query)
            if not embedding or all(x == 0 for x in embedding):
                logger.warning("FastSelector: Failed to generate embedding (zero vector). Returning all tools.")
                return all_tools

            # 2. Vector Search against 'tool_definition' table
            # We assume tools are already indexed in this table.
            # We select name and score.
            # Using <|4|> (Euclidean k-NN) for efficient retrieval.
            # Note: 1024 is the dimension from schema.
            
            sql = """
            SELECT name, 
                   vector::similarity::cosine(embedding, $emb) as score 
            FROM tool_definition 
            WHERE embedding <|4|> $emb 
            ORDER BY score DESC 
            LIMIT $limit;
            """
            
            results = await memory_server.execute_query(sql, {"emb": embedding, "limit": limit})
            
            if not results:
                # If no results found (maybe empty DB?), fallback to keyword search or return all
                logger.info("FastSelector: No vector matches found. Falling back to all tools.")
                # Optional: We could do a keyword search fallback here if we wanted.
                return all_tools

            # 3. Map Results to Tool Definitions
            # Create a set of selected tool names for O(1) lookup
            selected_names = {r["name"] for r in results}
            
            # Filter the input list
            filtered_tools = [t for t in all_tools if t["function"]["name"] in selected_names]
            
            # [SAFETY NET] Always include critical system tools
            # We force-include "memory" or "filesystem" tools if they look relevant or just always?
            # Actually, "The Librarian" concept implies we trust the search.
            # But let's ensure we don't return an empty list if results existed but names didn't match (sync issue).
            
            if not filtered_tools:
                logger.warning(f"FastSelector: Matches found ({selected_names}) but did not match known tools. Sync issue? Returning all.")
                return all_tools

            latency = (time.time() - t0) * 1000
            logger.info(f"FastSelector: Selected {len(filtered_tools)}/{len(all_tools)} tools in {latency:.2f}ms")
            
            return filtered_tools

        except Exception as e:
            logger.error(f"FastSelector Error: {e}")
            # Fail Open: Return all tools
            return all_tools

    @staticmethod
    async def sync_tools(tools: List[Dict[str, Any]], memory_server: Any):
        """
        Sync available tools to the vector database.
        Should be called periodically or on startup.
        """
        if not memory_server or not memory_server.initialized:
            return

        try:
            count = 0
            for tool in tools:
                name = tool["function"]["name"]
                desc = tool["function"].get("description", "")
                
                # Check if exists (Simple check to avoid re-embedding everything on every turn)
                # In a real system we'd check hash. Here we just UPSERT if missing or force update.
                # Let's check existence first to save embedding cost.
                existing = await memory_server.execute_query(f"SELECT id FROM tool_definition WHERE name = '{name}' LIMIT 1")
                if not existing:
                    # Embed description (+ name)
                    text = f"{name}: {desc}"
                    embedding = await memory_server.get_embedding(text)
                    
                    if embedding:
                        await memory_server.execute_query("""
                            CREATE tool_definition CONTENT {
                                name: $name,
                                description: $desc,
                                embedding: $emb
                            }
                        """, {"name": name, "desc": desc, "emb": embedding})
                        count += 1
            
            if count > 0:
                logger.info(f"FastSelector: Indexed {count} new tools.")
                
        except Exception as e:
            logger.error(f"FastSelector Sync Failed: {e}")
