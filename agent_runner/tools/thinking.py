"""
Enhanced Sequential Thinking Tools with Session Management and State Persistence.

Provides:
- ThinkingSession: Manages thinking sessions with database persistence
- tool_sequential_thinking: Enhanced wrapper with session management and fallback
- tool_get_thinking_history: Retrieve previous thoughts
- tool_store_thinking_result: Store thinking results in memory
- _fallback_thinking: Direct LLM-based thinking when MCP servers fail
"""

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from agent_runner.state import AgentState
from agent_runner.db_utils import run_query_with_memory
from agent_runner.tools.mcp import tool_mcp_proxy

logger = logging.getLogger("agent_runner.tools.thinking")

# Rate limiting state
_thinking_rate_limits = defaultdict(list)  # {session_id: [timestamps]}
_MAX_THOUGHTS_PER_MINUTE = 10
_MAX_THOUGHTS_PER_SESSION = 50

# Thinking templates
THINKING_TEMPLATES = {
    "debugging": {
        "initial_thoughts": 5,
        "pattern": [
            "Identify the symptom",
            "Hypothesize root cause",
            "Test hypothesis",
            "Verify fix",
            "Document solution"
        ],
        "suggested_total": 5
    },
    "planning": {
        "initial_thoughts": 7,
        "pattern": [
            "Define goal",
            "Identify constraints",
            "Explore options",
            "Evaluate trade-offs",
            "Select approach",
            "Detail steps",
            "Validate plan"
        ],
        "suggested_total": 7
    },
    "analysis": {
        "initial_thoughts": 6,
        "pattern": [
            "Gather data",
            "Identify patterns",
            "Form hypothesis",
            "Test hypothesis",
            "Revise if needed",
            "Conclude"
        ],
        "suggested_total": 6
    }
}


class ThinkingSession:
    """Manages a thinking session with database persistence."""
    
    def __init__(self, session_id: str, memory_server: Any):
        self.session_id = session_id
        self.memory = memory_server
        self.thoughts: List[Dict[str, Any]] = []
        self._cache_loaded = False
    
    async def _ensure_connected(self):
        """Ensure memory server is connected."""
        if not self.memory.initialized:
            await self.memory.initialize()
        await self.memory.ensure_connected()
    
    async def add_thought(
        self, 
        thought: str, 
        thought_number: int,
        total_thoughts: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a thought to the session and persist to database."""
        await self._ensure_connected()
        
        thought_record = {
            "session_id": self.session_id,
            "thought_number": thought_number,
            "thought": thought,
            "total_thoughts": total_thoughts,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        
        try:
            # Store in database
            import json
            record_id = f"thinking_session:{self.session_id}:{thought_number}"
            safe_thought = thought.replace("'", "''")  # Escape single quotes
            safe_metadata = json.dumps(metadata or {})
            
            query = f"""
            CREATE {record_id} SET
                session_id = '{self.session_id}',
                thought_number = {thought_number},
                thought = '{safe_thought}',
                total_thoughts = {total_thoughts},
                metadata = {safe_metadata},
                timestamp = time::now(),
                latency_ms = NULL,
                success = NULL,
                problem_type = NULL;
            """
            await run_query_with_memory(self.memory, query)
            
            # Update cache
            self.thoughts.append(thought_record)
            self.thoughts.sort(key=lambda x: x["thought_number"])
            
            logger.debug(f"Stored thought {thought_number} for session {self.session_id[:8]}")
            return thought_record
        except Exception as e:
            logger.error(f"Failed to store thought in database: {e}", exc_info=True)
            # Still add to cache even if DB fails
            self.thoughts.append(thought_record)
            return thought_record
    
    async def get_thoughts(self) -> List[Dict[str, Any]]:
        """Retrieve all thoughts for this session from database."""
        await self._ensure_connected()
        
        if not self._cache_loaded:
            try:
                query = f"""
                SELECT * FROM thinking_session 
                WHERE session_id = '{self.session_id}' 
                ORDER BY thought_number ASC;
                """
                results = await run_query_with_memory(self.memory, query)
                if results:
                    import json
                    self.thoughts = []
                    for r in results:
                        # Handle metadata (could be string or dict)
                        metadata = r.get("metadata", {})
                        if isinstance(metadata, str):
                            try:
                                metadata = json.loads(metadata)
                            except:
                                metadata = {}
                        
                        self.thoughts.append({
                            "session_id": r.get("session_id"),
                            "thought_number": r.get("thought_number"),
                            "thought": r.get("thought"),
                            "total_thoughts": r.get("total_thoughts"),
                            "metadata": metadata,
                            "timestamp": r.get("timestamp")
                        })
                    self._cache_loaded = True
                    logger.debug(f"Loaded {len(self.thoughts)} thoughts for session {self.session_id[:8]}")
            except Exception as e:
                logger.error(f"Failed to load thoughts from database: {e}", exc_info=True)
        
        return self.thoughts
    
    async def get_thought(self, thought_number: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific thought by number."""
        thoughts = await self.get_thoughts()
        return next((t for t in thoughts if t["thought_number"] == thought_number), None)
    
    async def get_latest_thought(self) -> Optional[Dict[str, Any]]:
        """Get the most recent thought."""
        thoughts = await self.get_thoughts()
        return thoughts[-1] if thoughts else None
    
    async def update_thought_metrics(
        self,
        thought_number: int,
        latency_ms: float,
        success: bool
    ) -> None:
        """Update performance metrics for a thought."""
        await self._ensure_connected()
        try:
            record_id = f"thinking_session:{self.session_id}:{thought_number}"
            query = f"""
            UPDATE {record_id} SET
                latency_ms = {latency_ms},
                success = {str(success).lower()};
            """
            await run_query_with_memory(self.memory, query)
        except Exception as e:
            logger.debug(f"Failed to update thought metrics: {e}")


async def _check_rate_limit(session_id: str, state: AgentState) -> Dict[str, Any]:
    """Check if thinking rate limit is exceeded."""
    now = datetime.now()
    minute_ago = now - timedelta(minutes=1)
    
    # Clean old timestamps
    _thinking_rate_limits[session_id] = [
        ts for ts in _thinking_rate_limits[session_id]
        if ts > minute_ago
    ]
    
    # Check per-minute limit
    if len(_thinking_rate_limits[session_id]) >= _MAX_THOUGHTS_PER_MINUTE:
        return {
            "ok": False,
            "error": f"Rate limit exceeded: {_MAX_THOUGHTS_PER_MINUTE} thoughts per minute"
        }
    
    # Check per-session limit (from database)
    try:
        session = ThinkingSession(session_id, state.memory)
        thoughts = await session.get_thoughts()
        if len(thoughts) >= _MAX_THOUGHTS_PER_SESSION:
            return {
                "ok": False,
                "error": f"Session limit exceeded: {_MAX_THOUGHTS_PER_SESSION} thoughts per session"
            }
    except Exception as e:
        # Fail closed: if we can't verify, deny access
        logger.error(f"Failed to check thinking session limit: {e}", exc_info=True)
        return {
            "ok": False,
            "error": "Unable to verify session limits. Access denied for safety."
        }
    
    # Record this call
    _thinking_rate_limits[session_id].append(now)
    return {"ok": True}


async def _select_relevant_thoughts(
    session: ThinkingSession,
    current_thought: str,
    max_context: int = 3
) -> List[Dict[str, Any]]:
    """Select most relevant previous thoughts for context."""
    all_thoughts = await session.get_thoughts()
    
    if len(all_thoughts) <= max_context:
        return all_thoughts
    
    # Strategy 1: Always include latest thoughts
    latest = all_thoughts[-2:]
    
    # Strategy 2: Include thoughts with revisions (important)
    revised = [t for t in all_thoughts if t.get("metadata", {}).get("isRevision")]
    
    # Strategy 3: Include branching points
    branches = [t for t in all_thoughts if t.get("metadata", {}).get("branchFromThought")]
    
    # Combine and deduplicate
    relevant = list({t["thought_number"]: t for t in latest + revised + branches}.values())
    
    # Fill to max_context if needed
    if len(relevant) < max_context:
        remaining = [t for t in all_thoughts if t not in relevant]
        relevant.extend(remaining[:max_context - len(relevant)])
    
    return sorted(relevant, key=lambda x: x["thought_number"])


async def _validate_thinking_sequence(
    session: ThinkingSession,
    current_thought: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate thinking sequence for consistency."""
    issues = []
    
    previous_thoughts = await session.get_thoughts()
    
    # Check 1: Thought number consistency
    expected_number = len(previous_thoughts) + 1
    if current_thought["thought_number"] != expected_number:
        issues.append(f"Thought number mismatch: expected {expected_number}, got {current_thought['thought_number']}")
    
    # Check 2: Revision references
    if current_thought.get("isRevision") and current_thought.get("revisesThought"):
        revises_num = current_thought["revisesThought"]
        if not any(t["thought_number"] == revises_num for t in previous_thoughts):
            issues.append(f"Revision references non-existent thought {revises_num}")
    
    # Check 3: Branch references
    if current_thought.get("branchFromThought"):
        branch_num = current_thought["branchFromThought"]
        if not any(t["thought_number"] == branch_num for t in previous_thoughts):
            issues.append(f"Branch references non-existent thought {branch_num}")
    
    # Check 4: Total thoughts consistency
    if previous_thoughts:
        last_total = previous_thoughts[-1].get("total_thoughts")
        current_total = current_thought.get("total_thoughts")
        if last_total and current_total and abs(current_total - last_total) > 3:
            issues.append(f"Total thoughts changed significantly: {last_total} -> {current_total}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


async def _track_thinking_metrics(
    state: AgentState,
    session_id: str,
    thought_number: int,
    latency_ms: float,
    success: bool,
    metadata: Dict[str, Any]
) -> None:
    """Track thinking performance metrics (async, fire-and-forget)."""
    from agent_runner.task_utils import create_safe_task
    
    async def _track():
        if not hasattr(state, "memory") or not state.memory:
            return
        
        try:
            session = ThinkingSession(session_id, state.memory)
            await session.update_thought_metrics(thought_number, latency_ms, success)
            
            # Also track in tool_performance (for reliability)
            model = state.agent_model
            await state.memory.record_tool_result(
                model, 
                "sequential_thinking", 
                success, 
                latency_ms
            )
        except Exception as e:
            logger.debug(f"Failed to track thinking metrics: {e}")
    
    # Fire-and-forget (doesn't block)
    create_safe_task(
        _track(),
        task_name="track_thinking_metrics",
        log_errors=False
    )


async def tool_sequential_thinking(
    state: AgentState,
    thought: str,
    thoughtNumber: int,
    totalThoughts: int,
    session_id: Optional[str] = None,
    nextThoughtNeeded: bool = True,
    isRevision: bool = False,
    revisesThought: Optional[int] = None,
    branchFromThought: Optional[int] = None,
    branchId: Optional[str] = None,
    needsMoreThoughts: bool = False,
    problem_type: Optional[str] = None,
    needs_more_time: bool = False, # [PATCH] Alias for needsMoreThoughts
    **kwargs # [PATCH] Absorb extra hallucinations
) -> Dict[str, Any]:
    """
    Enhanced sequential thinking with session management and state persistence.
    
    This is a wrapper around the MCP sequentialthinking tool that adds:
    - Session management (persistent state across calls)
    - Database persistence (thoughts stored in database)
    - Thought history retrieval
    - Integration with memory system
    - Automatic context injection
    - Retry logic
    - Rate limiting
    - Performance tracking
    """
    # Get or create session
    if not session_id:
        # Generate new session ID
        session_id = f"think_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        logger.info(f"Created new thinking session: {session_id[:16]}")
    
    session = ThinkingSession(session_id, state.memory)
    
    # Rate limiting check
    rate_check = await _check_rate_limit(session_id, state)
    if not rate_check.get("ok"):
        return {
            "ok": False,
            "session_id": session_id,
            "error": rate_check.get("error"),
            "thought_number": thoughtNumber
        }
    
    # Prepare metadata
    metadata = {
        "nextThoughtNeeded": nextThoughtNeeded,
        "isRevision": isRevision,
        "revisesThought": revisesThought,
        "branchFromThought": branchFromThought,
        "branchId": branchId,
        "needsMoreThoughts": needsMoreThoughts,
        "problem_type": problem_type
    }
    
    # Store thought in session (before calling MCP server)
    thought_record = await session.add_thought(
        thought=thought,
        thought_number=thoughtNumber,
        total_thoughts=totalThoughts,
        metadata=metadata
    )
    
    # Validate thinking sequence
    validation = await _validate_thinking_sequence(session, thought_record)
    if not validation["valid"]:
        logger.warning(f"Thinking validation issues: {validation['issues']}")
        # Continue anyway, but log for debugging
    
    # Get previous thoughts for automatic context injection
    previous_thoughts = await session.get_thoughts()
    relevant_thoughts = await _select_relevant_thoughts(session, thought, max_context=3)
    
    # Build context summary (automatic context injection)
    context_summary = ""
    if relevant_thoughts and thoughtNumber > 1:
        context_summary = "\n\nPrevious thoughts for context:\n"
        for t in relevant_thoughts:
            thought_text = t['thought'][:200] + "..." if len(t['thought']) > 200 else t['thought']
            context_summary += f"Thought {t['thought_number']}: {thought_text}\n"
    
    # Enhance thought with context
    enhanced_thought = f"{thought}{context_summary}"
    
    # Try MCP servers in order: primary "thinking", then alternatives
    # With retry logic
    mcp_result = None
    tried_servers = []
    max_retries = 3
    retry_delay = 0.5
    
    # 1. Try primary "thinking" server (with retries)
    if "thinking" in state.mcp_servers:
        tried_servers.append("thinking")
        for attempt in range(max_retries):
            exec_start = time.time()
            mcp_result = await tool_mcp_proxy(
                state, 
                "thinking", 
                "sequentialthinking", 
                {
                    "thought": enhanced_thought,  # Use enhanced thought with context
                    "thoughtNumber": thoughtNumber,
                    "totalThoughts": totalThoughts,
                    "nextThoughtNeeded": nextThoughtNeeded,
                    "isRevision": isRevision,
                    "revisesThought": revisesThought,
                    "branchFromThought": branchFromThought,
                    "branchId": branchId,
                    "needsMoreThoughts": needsMoreThoughts
                },
                bypass_circuit_breaker=False
            )
            
            if mcp_result and mcp_result.get("ok"):
                break
            
            if attempt < max_retries - 1:
                logger.warning(f"Thinking attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error(f"All {max_retries} thinking attempts failed for 'thinking' server")
    
    # 2. If primary failed, try alternative servers that provide sequentialthinking
    if not mcp_result or not mcp_result.get("ok"):
        # Find alternative servers with sequentialthinking tool
        for server_name, server_cfg in state.mcp_servers.items():
            if server_name == "thinking" or server_name in tried_servers:
                continue
            
            # Check if this server has sequentialthinking (from tool cache)
            from agent_runner.agent_runner import get_shared_engine
            try:
                engine = get_shared_engine()
                server_tools = engine.executor.mcp_tool_cache.get(server_name, [])
                has_sequential_thinking = any(
                    t.get("function", {}).get("name") == "sequentialthinking"
                    for t in server_tools
                )
                
                if has_sequential_thinking:
                    tried_servers.append(server_name)
                    logger.info(f"Trying alternative thinking server: {server_name}")
                    mcp_result = await tool_mcp_proxy(
                        state,
                        server_name,
                        "sequentialthinking",
                        {
                            "thought": enhanced_thought,  # Use enhanced thought with context
                            "thoughtNumber": thoughtNumber,
                            "totalThoughts": totalThoughts,
                            "nextThoughtNeeded": nextThoughtNeeded,
                            "isRevision": isRevision,
                            "revisesThought": revisesThought,
                            "branchFromThought": branchFromThought,
                            "branchId": branchId,
                            "needsMoreThoughts": needsMoreThoughts
                        },
                        bypass_circuit_breaker=False
                    )
                    if mcp_result and mcp_result.get("ok"):
                        logger.info(f"Successfully used alternative thinking server: {server_name}")
                        break
            except Exception as e:
                logger.debug(f"Failed to check/use alternative server {server_name}: {e}")
                continue
    
    # 3. If all MCP servers failed, use fallback LLM-based thinking
    if not mcp_result or not mcp_result.get("ok"):
        logger.warning(f"All MCP thinking servers failed (tried: {tried_servers}). Using LLM fallback.")
        mcp_result = await _fallback_thinking(
            state,
            thought,
            thoughtNumber,
            totalThoughts,
            nextThoughtNeeded,
            session_id,
            await session.get_thoughts()
        )
    
    # Calculate execution latency
    exec_latency = (time.time() - exec_start) * 1000  # ms
    
    # Track performance metrics (async, fire-and-forget)
    success = mcp_result and mcp_result.get("ok", False)
    await _track_thinking_metrics(
        state, session_id, thoughtNumber, exec_latency, success, metadata
    )
    
    # Enhance result with session info
    if mcp_result and mcp_result.get("ok"):
        # Get all thoughts for context
        all_thoughts = await session.get_thoughts()
        
        result = {
            "ok": True,
            "session_id": session_id,
            "thought_number": thoughtNumber,
            "total_thoughts": totalThoughts,
            "mcp_result": mcp_result.get("result"),
            "thought_history": [
                {
                    "number": t["thought_number"],
                    "thought": t["thought"],
                    "timestamp": t.get("timestamp")
                }
                for t in all_thoughts
            ],
            "next_thought_needed": nextThoughtNeeded,
            "latency_ms": exec_latency
        }
        
        # Automatic summarization (every 5 thoughts, async)
        if thoughtNumber % 5 == 0 and thoughtNumber > 0:
            from agent_runner.task_utils import create_safe_task
            create_safe_task(
                _summarize_thinking_session(state, session, all_thoughts),
                task_name="summarize_thinking",
                log_errors=True
            )
        
        # If this is the final thought, store conclusion and cache result
        if not nextThoughtNeeded:
            await _store_thinking_conclusion(state, session_id, all_thoughts)
            # Cache for future similar problems
            cache_key = _create_cache_key(thought, problem_type)
            _set_cached_thinking(cache_key, session_id, all_thoughts)
        
        return result
    else:
        return {
            "ok": False,
            "session_id": session_id,
            "error": mcp_result.get("error", "Unknown error") if mcp_result else "All thinking methods failed",
            "thought_number": thoughtNumber,
            "tried_servers": tried_servers,
            "fallback_used": mcp_result is None or (not mcp_result.get("ok") and len(tried_servers) > 0)
        }


async def _fallback_thinking(
    state: AgentState,
    thought: str,
    thoughtNumber: int,
    totalThoughts: int,
    nextThoughtNeeded: bool,
    session_id: str,
    previous_thoughts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Fallback thinking implementation using direct LLM calls.
    Provides sequential reasoning when MCP servers are unavailable.
    
    This is a simplified but effective fallback that maintains the same interface
    as the MCP sequentialthinking tool.
    """
    try:
        # Build context from previous thoughts
        context_parts = []
        if previous_thoughts:
            context_parts.append("\n\nPrevious thoughts in this session:")
            for t in previous_thoughts:
                context_parts.append(f"\nThought {t['thought_number']}: {t['thought']}")
        
        context_str = "\n".join(context_parts) if context_parts else ""
        
        # Build prompt for sequential thinking
        prompt = f"""You are performing sequential thinking for problem-solving.

Current Thought ({thoughtNumber} of {totalThoughts}): {thought}{context_str}

Your task:
1. Analyze the current thought in the context of previous thoughts
2. Provide reasoning and insights
3. Determine if more thinking is needed

{"This is a revision of a previous thought." if thoughtNumber > 1 else ""}
{"This thought branches from an earlier thought." if thoughtNumber > 1 else ""}

Respond with a JSON object:
{{
    "analysis": "Your analysis and reasoning",
    "insights": ["key insight 1", "key insight 2"],
    "nextThoughtNeeded": {str(nextThoughtNeeded).lower()},
    "confidence": 0.0-1.0
}}"""

        # Call LLM directly via gateway
        client = await state.get_http_client()
        url = f"{state.gateway_base}/v1/chat/completions"
        
        # Use agent model (or fallback if circuit broken)
        model = state.agent_model
        if not state.mcp_circuit_breaker.is_allowed(model):
            model = state.fallback_model or "ollama:llama3.3:70b"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert at sequential reasoning and problem-solving. Provide clear, structured analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
            "max_tokens": 500
        }
        
        resp = await client.post(url, json=payload, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        
        content = data["choices"][0]["message"]["content"]
        result_data = json.loads(content)
        
        # Format to match MCP sequentialthinking response
        return {
            "ok": True,
            "result": {
                "thought": thought,
                "thoughtNumber": thoughtNumber,
                "totalThoughts": totalThoughts,
                "analysis": result_data.get("analysis", ""),
                "insights": result_data.get("insights", []),
                "nextThoughtNeeded": result_data.get("nextThoughtNeeded", nextThoughtNeeded),
                "confidence": result_data.get("confidence", 0.8),
                "fallback": True  # Mark as fallback
            }
        }
        
    except Exception as e:
        logger.error(f"Fallback thinking failed: {e}", exc_info=True)
        return {
            "ok": False,
            "error": f"Fallback thinking failed: {str(e)}",
            "fallback": True
        }


async def tool_get_thinking_history(
    state: AgentState,
    session_id: str,
    thought_numbers: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Retrieve thinking history for a session.
    
    Args:
        session_id: The thinking session ID
        thought_numbers: Optional list of specific thought numbers to retrieve
    
    Returns:
        Dictionary with session info and thoughts
    """
    session = ThinkingSession(session_id, state.memory)
    thoughts = await session.get_thoughts()
    
    if thought_numbers:
        thoughts = [t for t in thoughts if t["thought_number"] in thought_numbers]
    
    return {
        "ok": True,
        "session_id": session_id,
        "thoughts": [
            {
                "number": t["thought_number"],
                "thought": t["thought"],
                "total_thoughts": t.get("total_thoughts"),
                "metadata": t.get("metadata", {}),
                "timestamp": t.get("timestamp")
            }
            for t in thoughts
        ],
        "total_thoughts": len(thoughts)
    }


async def tool_start_thinking_session(
    state: AgentState,
    problem_type: str,
    initial_problem: str
) -> Dict[str, Any]:
    """
    Start a thinking session with a template.
    
    Templates provide pre-defined thinking patterns for common problem types.
    """
    template = THINKING_TEMPLATES.get(problem_type, {})
    session_id = f"think_{problem_type}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    session = ThinkingSession(session_id, state.memory)
    await session.add_thought(
        f"Starting {problem_type} thinking: {initial_problem}",
        thought_number=0,
        total_thoughts=template.get("suggested_total", 5),
        metadata={
            "template": problem_type,
            "pattern": template.get("pattern", []),
            "problem_type": problem_type
        }
    )
    
    return {
        "ok": True,
        "session_id": session_id,
        "template": problem_type,
        "suggested_thoughts": template.get("suggested_total", 5),
        "pattern": template.get("pattern", [])
    }


async def tool_start_thinking_branch(
    state: AgentState,
    session_id: str,
    branch_from_thought: int,
    branch_description: str
) -> Dict[str, Any]:
    """Start a parallel thinking branch."""
    session = ThinkingSession(session_id, state.memory)
    thoughts = await session.get_thoughts()
    
    # Find the thought we're branching from
    base_thought = next((t for t in thoughts if t["thought_number"] == branch_from_thought), None)
    if not base_thought:
        return {"ok": False, "error": f"Thought {branch_from_thought} not found"}
    
    # Create new branch
    branch_id = f"branch_{uuid.uuid4().hex[:8]}"
    next_number = max([t["thought_number"] for t in thoughts], default=0) + 1
    
    await session.add_thought(
        f"[BRANCH: {branch_description}] {base_thought['thought']}",
        thought_number=next_number,
        total_thoughts=base_thought.get("total_thoughts", 5),
        metadata={
            "branchId": branch_id,
            "branchFromThought": branch_from_thought,
            "isBranch": True
        }
    )
    
    return {
        "ok": True,
        "session_id": session_id,
        "branch_id": branch_id,
        "thought_number": next_number
    }


async def tool_get_thinking_progress(
    state: AgentState,
    session_id: str
) -> Dict[str, Any]:
    """Get progress metrics for a thinking session."""
    session = ThinkingSession(session_id, state.memory)
    thoughts = await session.get_thoughts()
    
    if not thoughts:
        return {"ok": False, "error": "Session not found"}
    
    latest = thoughts[-1]
    total_thoughts = latest.get("total_thoughts", 1)
    current = latest["thought_number"]
    
    # Calculate progress
    progress_pct = (current / total_thoughts) * 100 if total_thoughts > 0 else 0
    
    # Count revisions and branches
    revisions = sum(1 for t in thoughts if t.get("metadata", {}).get("isRevision"))
    branches = sum(1 for t in thoughts if t.get("metadata", {}).get("branchFromThought"))
    
    # Calculate average latency
    latencies = [t.get("latency_ms", 0) for t in thoughts if t.get("latency_ms")]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    return {
        "ok": True,
        "session_id": session_id,
        "progress": {
            "current": current,
            "total": total_thoughts,
            "percentage": progress_pct,
            "revisions": revisions,
            "branches": branches,
            "avg_latency_ms": avg_latency
        }
    }


async def tool_analyze_thinking_efficiency(
    state: AgentState,
    session_id: str
) -> Dict[str, Any]:
    """Analyze thinking session and suggest optimizations."""
    session = ThinkingSession(session_id, state.memory)
    thoughts = await session.get_thoughts()
    
    if len(thoughts) < 3:
        return {"ok": False, "error": "Not enough thoughts to analyze"}
    
    # Analyze patterns
    revisions_pct = (sum(1 for t in thoughts if t.get("metadata", {}).get("isRevision")) / len(thoughts)) * 100
    latencies = [t.get("latency_ms", 0) for t in thoughts if t.get("latency_ms")]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    suggestions = []
    
    if revisions_pct > 30:
        suggestions.append("High revision rate (>30%). Consider more initial planning.")
    
    if avg_latency > 1000:
        suggestions.append("High latency per thought. Check thinking server performance.")
    
    if len(thoughts) > 20:
        suggestions.append("Long thinking chain. Consider breaking into sub-problems.")
    
    return {
        "ok": True,
        "session_id": session_id,
        "metrics": {
            "total_thoughts": len(thoughts),
            "revisions_pct": revisions_pct,
            "avg_latency_ms": avg_latency
        },
        "suggestions": suggestions
    }


async def tool_repair_thinking_session(
    state: AgentState,
    session_id: str
) -> Dict[str, Any]:
    """Repair a corrupted or incomplete thinking session."""
    session = ThinkingSession(session_id, state.memory)
    thoughts = await session.get_thoughts()
    
    if not thoughts:
        return {"ok": False, "error": "Session not found"}
    
    # Check for gaps in thought numbers
    expected_numbers = set(range(1, len(thoughts) + 1))
    actual_numbers = {t["thought_number"] for t in thoughts}
    gaps = expected_numbers - actual_numbers
    
    if gaps:
        logger.warning(f"Found gaps in thinking session: {gaps}")
    
    # Check for inconsistencies
    issues = []
    for i, thought in enumerate(thoughts):
        if i > 0:
            prev = thoughts[i-1]
            if thought["thought_number"] <= prev["thought_number"]:
                issues.append(f"Thought {thought['thought_number']} out of order")
    
    return {
        "ok": True,
        "session_id": session_id,
        "issues_found": len(issues),
        "issues": issues,
        "gaps": list(gaps) if gaps else []
    }


async def _find_similar_thinking_session(
    state: AgentState,
    current_problem: str
) -> Optional[Dict[str, Any]]:
    """Find similar past thinking sessions using semantic search."""
    try:
        from agent_runner.tools.mcp import tool_mcp_proxy
        
        search_result = await tool_mcp_proxy(
            state,
            "project-memory",
            "semantic_search",
            {
                "query": current_problem,
                "limit": 5,
                "kb_id": "thinking_sessions"
            }
        )
        
        if search_result.get("ok"):
            chunks = search_result.get("result", {}).get("chunks", [])
            if chunks:
                return chunks[0]  # Return most similar session
    except Exception as e:
        logger.debug(f"Failed to find similar thinking session: {e}")
    
    return None


def _create_cache_key(thought: str, problem_type: Optional[str] = None) -> str:
    """Create a cache key from thought and problem type."""
    import hashlib
    key_str = f"{problem_type or 'general'}:{thought[:200]}"
    return hashlib.sha256(key_str.encode()).hexdigest()[:16]


async def _get_cached_thinking(
    cache_key: str,
    state: AgentState
) -> Optional[Dict[str, Any]]:
    """Get cached thinking result if available and not expired."""
    if cache_key not in _thinking_cache:
        return None
    
    cached = _thinking_cache[cache_key]
    cached_time = cached.get("timestamp", 0)
    
    # Check TTL
    if time.time() - cached_time > _CACHE_TTL:
        del _thinking_cache[cache_key]
        return None
    
    # Return cached session info
    session_id = cached.get("session_id")
    if session_id:
        session = ThinkingSession(session_id, state.memory)
        thoughts = await session.get_thoughts()
        return {
            "session_id": session_id,
            "thoughts": thoughts,
            "cached": True
        }
    
    return None


def _set_cached_thinking(
    cache_key: str,
    session_id: str,
    thoughts: List[Dict[str, Any]]
) -> None:
    """Cache thinking result for future similar problems."""
    # Evict oldest if at limit
    if len(_thinking_cache) >= _CACHE_MAX_SIZE:
        oldest_key = min(_thinking_cache.keys(), key=lambda k: _thinking_cache[k].get("timestamp", 0))
        del _thinking_cache[oldest_key]
    
    _thinking_cache[cache_key] = {
        "session_id": session_id,
        "thoughts": thoughts,
        "timestamp": time.time()
    }


async def tool_store_thinking_result(
    state: AgentState,
    session_id: str,
    conclusion: str,
    key_insights: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Store thinking results as facts in the memory system.
    
    This makes thinking results searchable and part of the knowledge graph.
    """
    if not hasattr(state, "memory") or not state.memory:
        return {"ok": False, "error": "Memory server not available"}
    
    session = ThinkingSession(session_id, state.memory)
    thoughts = await session.get_thoughts()
    
    try:
        await state.memory.ensure_connected()
        
        # Store conclusion as fact
        await state.memory.store_fact(
            entity="ThinkingSession",
            relation="concluded",
            target=conclusion,
            context={
                "session_id": session_id,
                "thought_count": len(thoughts),
                "key_insights": key_insights or []
            },
            kb_id="system_architecture"
        )
        
        # Store key insights as facts
        stored_count = 1
        for insight in (key_insights or []):
            await state.memory.store_fact(
                entity="ThinkingSession",
                relation="discovered",
                target=insight,
                context={"session_id": session_id},
                kb_id="system_architecture"
            )
            stored_count += 1
        
        logger.info(f"Stored {stored_count} thinking results for session {session_id[:16]}")
        return {"ok": True, "stored": stored_count, "session_id": session_id}
    except Exception as e:
        logger.error(f"Failed to store thinking results: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def _store_thinking_conclusion(
    state: AgentState,
    session_id: str,
    thoughts: List[Dict[str, Any]]
) -> None:
    """Helper to automatically store conclusion when thinking completes."""
    if not thoughts:
        return
    
    # Extract conclusion from last thought
    last_thought = thoughts[-1]
    conclusion = last_thought.get("thought", "")
    
    # Extract key insights (thoughts marked as important or revisions)
    key_insights = []
    for t in thoughts:
        metadata = t.get("metadata", {})
        if metadata.get("isRevision") or "hypothesis" in t.get("thought", "").lower():
            key_insights.append(t.get("thought", "")[:200])  # Truncate long thoughts
    
    # Store in background (fire-and-forget)
    from agent_runner.task_utils import create_safe_task
    create_safe_task(
        tool_store_thinking_result(state, session_id, conclusion, key_insights),
        task_name="store_thinking_result",
        log_errors=True
    )

