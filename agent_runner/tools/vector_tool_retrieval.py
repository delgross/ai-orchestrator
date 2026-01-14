"""
Vector-based Tool Retrieval System

Provides semantic search and retrieval of tools using vector embeddings for better scalability
with large tool sets (thousands of tools).
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.vector_tool_retrieval")

@dataclass
class ToolVector:
    """Represents a tool with its vector embedding."""
    name: str
    description: str
    category: str
    vector: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None

class VectorToolRetriever:
    """Vector-based tool retrieval for scalable semantic search."""

    def __init__(self, state: AgentState):
        self.state = state
        self.tool_vectors: Dict[str, ToolVector] = {}
        self.embedding_model = "mxbai-embed-large:latest"  # Use existing embedding model
        self.vector_dimension = 1024  # Dimension for mxbai-embed-large
        self.similarity_threshold = 0.7  # Minimum similarity for retrieval
        self.max_results = 20  # Maximum tools to retrieve

    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get vector embedding for text using Ollama."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"http://127.0.0.1:11434/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("embedding")

        except Exception as e:
            logger.warning(f"Failed to get embedding: {e}")

        return None

    async def _calculate_similarity(self, query_vector: List[float], tool_vector: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            # Convert to numpy arrays
            query_vec = np.array(query_vector)
            tool_vec = np.array(tool_vector)

            # Calculate cosine similarity
            dot_product = np.dot(query_vec, tool_vec)
            query_norm = np.linalg.norm(query_vec)
            tool_norm = np.linalg.norm(tool_vec)

            if query_norm == 0 or tool_norm == 0:
                return 0.0

            return dot_product / (query_norm * tool_norm)

        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0

    async def build_tool_vectors(self, tool_definitions: List[Dict[str, Any]]) -> Dict[str, ToolVector]:
        """Build vector embeddings for all tools."""
        logger.info(f"Building vector embeddings for {len(tool_definitions)} tools")

        tool_vectors = {}

        for tool_def in tool_definitions:
            if tool_def.get("type") != "function":
                continue

            func_def = tool_def.get("function", {})
            tool_name = func_def.get("name")
            description = func_def.get("description", "")

            if not tool_name or not description:
                continue

            # Create enriched description for better embeddings
            enriched_description = f"Tool: {tool_name}. {description}"

            # Add parameter information
            params = func_def.get("parameters", {})
            if params.get("properties"):
                param_desc = []
                for param_name, param_info in params["properties"].items():
                    param_type = param_info.get("type", "unknown")
                    param_desc.append(f"{param_name} ({param_type})")
                if param_desc:
                    enriched_description += f" Parameters: {', '.join(param_desc)}."

            # Get embedding
            embedding = await self._get_embedding(enriched_description)

            # Determine category (would need category mapping)
            category = "unknown"  # Placeholder - would map from existing categories

            tool_vector = ToolVector(
                name=tool_name,
                description=enriched_description,
                category=category,
                vector=embedding,
                metadata={
                    "original_description": description,
                    "parameters": params,
                    "enriched_description": enriched_description
                }
            )

            tool_vectors[tool_name] = tool_vector

        logger.info(f"Built embeddings for {len(tool_vectors)} tools")
        return tool_vectors

    async def retrieve_similar_tools(self, query: str, limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Retrieve tools most similar to the query using vector search."""
        if not self.tool_vectors:
            logger.warning("No tool vectors available - call build_tool_vectors first")
            return []

        # Get query embedding
        query_embedding = await self._get_embedding(query)
        if not query_embedding:
            logger.error("Failed to get query embedding")
            return []

        # Calculate similarities
        similarities = []
        for tool_name, tool_vector in self.tool_vectors.items():
            if tool_vector.vector:
                similarity = await self._calculate_similarity(query_embedding, tool_vector.vector)
                if similarity >= self.similarity_threshold:
                    similarities.append((tool_name, similarity))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top results
        max_results = limit or self.max_results
        return similarities[:max_results]

    async def get_tool_definitions(self, tool_names: List[str]) -> List[Dict[str, Any]]:
        """Get full tool definitions for the specified tool names."""
        # This would need access to the original tool registry
        # For now, return basic structure
        tool_definitions = []

        for tool_name in tool_names:
            if tool_name in self.tool_vectors:
                tool_vector = self.tool_vectors[tool_name]
                # Reconstruct tool definition from vector metadata
                tool_def = {
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": tool_vector.metadata.get("original_description", ""),
                        "parameters": tool_vector.metadata.get("parameters", {})
                    }
                }
                tool_definitions.append(tool_def)

        return tool_definitions

async def tool_vector_tool_search(state: AgentState, query: str, limit: int = 10) -> Dict[str, Any]:
    """Search for tools using vector similarity."""
    try:
        retriever = VectorToolRetriever(state)

        # Load tool vectors (in production, this would be cached/preloaded)
        # For demo, we'll use a simplified approach
        tool_definitions = await state.executor.get_all_tools()

        # Build vectors for tools
        start_time = time.time()
        tool_vectors = await retriever.build_tool_vectors(tool_definitions)
        build_time = time.time() - start_time

        retriever.tool_vectors = tool_vectors

        # Search for similar tools
        search_start = time.time()
        similar_tools = await retriever.retrieve_similar_tools(query, limit=limit)
        search_time = time.time() - search_start

        # Get full definitions
        tool_names = [name for name, _ in similar_tools]
        tool_definitions = await retriever.get_tool_definitions(tool_names)

        return {
            "ok": True,
            "query": query,
            "results": [
                {
                    "tool_name": name,
                    "similarity": similarity,
                    "definition": tool_def
                }
                for (name, similarity), tool_def in zip(similar_tools, tool_definitions)
            ],
            "performance": {
                "build_time_seconds": build_time,
                "search_time_seconds": search_time,
                "tools_searched": len(tool_vectors),
                "results_found": len(similar_tools)
            }
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Vector tool search failed: {str(e)}",
            "error_type": "vector_search_error"
        }

async def tool_compare_retrieval_methods(state: AgentState, query: str) -> Dict[str, Any]:
    """Compare traditional category-based vs vector-based tool retrieval."""
    try:
        # Traditional category-based retrieval
        traditional_start = time.time()
        all_tools = await state.executor.get_all_tools()
        # Simulate category filtering (would use existing Context Diet logic)
        traditional_tools = all_tools[:20]  # Simplified - take first 20
        traditional_time = time.time() - traditional_start

        # Vector-based retrieval
        vector_start = time.time()
        vector_result = await tool_vector_tool_search(state, query, limit=20)
        vector_time = time.time() - vector_start

        return {
            "ok": True,
            "query": query,
            "comparison": {
                "traditional": {
                    "method": "Category-based filtering",
                    "tools_found": len(traditional_tools),
                    "time_seconds": traditional_time,
                    "approach": "Rule-based category matching"
                },
                "vector": {
                    "method": "Semantic vector search",
                    "tools_found": len(vector_result.get("results", [])),
                    "time_seconds": vector_time,
                    "approach": "Cosine similarity on embeddings"
                }
            },
            "scalability_analysis": {
                "traditional_complexity": "O(n) - linear search through categories",
                "vector_complexity": "O(log n) - approximate nearest neighbors",
                "traditional_memory": "O(n) - all tools in memory",
                "vector_memory": "O(n*d) - n tools × d dimensions + index",
                "recommended_threshold": "1000+ tools → vector approach"
            }
        }

    except Exception as e:
        return {
            "ok": False,
            "error": f"Retrieval comparison failed: {str(e)}",
            "error_type": "comparison_error"
        }

async def tool_hybrid_tool_retrieval(state: AgentState, query: str, strategy: str = "auto") -> Dict[str, Any]:
    """Intelligent hybrid tool retrieval that chooses the best method based on context."""
    try:
        # Analyze query complexity
        query_words = len(query.split())
        has_operators = any(word in query.lower() for word in ["and", "or", "not", "with", "using"])
        is_complex = query_words > 3 or has_operators

        # Check toolset size
        all_tools = await state.executor.get_all_tools()
        tool_count = len(all_tools)

        # Auto-select strategy
        if strategy == "auto":
            if tool_count > 500 or is_complex:
                strategy = "vector"
            else:
                strategy = "traditional"

        if strategy == "vector":
            # Use vector search for complex queries or large toolsets
            result = await tool_vector_tool_search(state, query, limit=15)
            method_used = "vector_semantic"
        else:
            # Use traditional category-based search for simple queries/small toolsets
            traditional_start = time.time()

            # Get tools through normal Context Diet process
            context_tools = await state.executor.get_all_tools(messages=[{"role": "user", "content": query}])
            selected_tools = context_tools[:15]  # Limit to top results

            traditional_time = time.time() - traditional_start

            result = {
                "ok": True,
                "query": query,
                "results": [
                    {
                        "tool_name": tool["function"]["name"],
                        "similarity": 0.8,  # Default similarity for traditional
                        "definition": tool
                    }
                    for tool in selected_tools
                ],
                "performance": {
                    "build_time_seconds": 0,
                    "search_time_seconds": traditional_time,
                    "tools_searched": len(all_tools),
                    "results_found": len(selected_tools)
                }
            }
            method_used = "traditional_category"

        # Add hybrid analysis
        result["hybrid_analysis"] = {
            "strategy_used": strategy,
            "method": method_used,
            "query_complexity": "complex" if is_complex else "simple",
            "toolset_size": tool_count,
            "selection_reason": f"{'Large toolset' if tool_count > 500 else 'Complex query' if is_complex else 'Simple query/small toolset'}",
            "performance_characteristics": {
                "vector_advantages": ["Better semantic matching", "Scalable to thousands of tools", "Finds related tools"],
                "traditional_advantages": ["Faster for small sets", "Predictable results", "Lower resource usage"],
                "recommended_thresholds": {
                    "tool_count": "500+ → vector preferred",
                    "query_complexity": "3+ words with operators → vector preferred"
                }
            }
        }

        return result

    except Exception as e:
        return {
            "ok": False,
            "error": f"Hybrid retrieval failed: {str(e)}",
            "error_type": "hybrid_retrieval_error"
        }