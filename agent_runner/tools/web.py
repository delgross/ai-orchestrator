import logging
import asyncio
from typing import Dict, Any, List

try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        HAS_DDGS = True
    except ImportError:
        HAS_DDGS = False
        DDGS = None

from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.web")

async def tool_search_web(state: AgentState, query: str) -> Dict[str, Any]:
    """
    Search the web using DuckDuckGo (Keyless/Free).
    Returns a summary of search results.
    """
    if not HAS_DDGS:
        # Log for user awareness - this tool should have been filtered if unavailable
        logger.warning("Web search tool called but duckduckgo_search module not installed (tool should have been filtered)")
        track_event(
            event="web_search_unavailable",
            message="Web search attempted but duckduckgo_search module not installed",
            severity=EventSeverity.MEDIUM,
            category=EventCategory.TASK,
            component="web_search",
            metadata={"query": query}
        )
        return {"ok": False, "error": "Web search unavailable"}
    
    if not state.internet_available:
        logger.warning("Web search tool called but internet is offline (tool should have been filtered)")
        track_event(
            event="web_search_offline",
            message="Web search attempted but internet is offline",
            severity=EventSeverity.MEDIUM,
            category=EventCategory.TASK,
            component="web_search",
            metadata={"query": query}
        )
        return {"ok": False, "error": "Internet unavailable"}
    
    try:
        logger.info(f"Searching Web for: '{query}'")
        
        # DDGS() is usually synchronous, but fast. We can run it in thread if needed.
        # But for now, let's try direct call or run_in_executor if it blocks.
        
        def _search():
            results = []
            with DDGS() as ddgs:
                # Get text results
                for r in ddgs.text(query, max_results=5):
                    results.append(r)
            return results

        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(None, _search)
        
        if not results:
            return {"ok": True, "message": "No results found for query."}
            
        summary = f"### 🌐 Web Search: '{query}'\n\n"
        for i, res in enumerate(results):
            title = res.get("title", "No Title")
            href = res.get("href", "#")
            body = res.get("body", "No content.")
            summary += f"**{i+1}. [{title}]({href})**\n{body}\n\n"
            
        return {"ok": True, "result": summary}

    except Exception as e:
        logger.error(f"Web Search Failed: {e}", exc_info=True)
        track_event(
            event="web_search_error",
            message=f"Web search failed: {str(e)}",
            severity=EventSeverity.HIGH,
            category=EventCategory.TASK,
            component="web_search",
            metadata={"query": query, "error": str(e)}
        )
        return {"ok": False, "error": "Search failed"}
