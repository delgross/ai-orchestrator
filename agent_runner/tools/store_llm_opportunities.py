"""
Store LLM Opportunities and Medium Term Plan in Thinking System

This module provides tools to store structured planning information
in the thinking system for future reference.
"""

import logging
from typing import Dict, Any
from agent_runner.state import AgentState
from agent_runner.tools.thinking import ThinkingSession

logger = logging.getLogger("agent_runner.tools.store_llm_opportunities")


async def tool_store_llm_opportunities(state: AgentState) -> Dict[str, Any]:
    """
    Store LLM opportunities in the thinking system.
    
    Creates a thinking session with all 8 LLM opportunities categorized by priority.
    """
    if not hasattr(state, "memory") or not state.memory:
        return {"ok": False, "error": "Memory server not available"}
    
    session_id = "llm_opportunities_planning"
    session = ThinkingSession(session_id, state.memory)
    
    # LLM Opportunities Content
    opportunities_content = """
# LLM Opportunities - 8 Areas for Enhancement

## High Priority (Immediate Impact)

### 1. Tool Categorization
**Current**: Regex pattern matching
**Problem**: Brittle, misses novel tool names
**LLM Solution**: Semantic categorization
**Impact**: Automatic handling of new tools
**Cost**: ~50-100ms per tool (cached)

### 2. Feedback/Learning Loop
**Current**: Simple keyword matching
**Problem**: No semantic understanding
**LLM Solution**: Vector search for query similarity
**Impact**: Better tool suggestions
**Cost**: ~100-200ms (with caching)

## Medium Priority (Quality Improvements)

### 3. Startup Error Analysis
**Current**: Keyword matching
**Problem**: Brittle, misses context
**LLM Solution**: LLM classification and extraction
**Impact**: Better error understanding
**Cost**: ~200-300ms (startup only)

### 4. Trigger Matching
**Current**: Exact string matching
**Problem**: No variations, typos break it
**LLM Solution**: Semantic matching
**Impact**: More flexible commands
**Cost**: ~50-100ms (cached)

### 5. Content Quality Assessment
**Current**: Heuristic rules
**Problem**: False positives, misses subtle issues
**LLM Solution**: Semantic quality evaluation
**Impact**: Better ingestion quality
**Cost**: ~100-200ms (uncertain cases only)

## Low Priority (Nice to Have)

### 6. Knowledge Base Selection
**Current**: Simple string matching
**Problem**: Brittle KB name matching
**LLM Solution**: Semantic KB routing
**Impact**: Better KB selection
**Cost**: ~50-100ms (multiple KBs only)

### 7. Error Message Parsing
**Current**: Regex extraction
**Problem**: Fragile, breaks with different formats
**LLM Solution**: Structured extraction
**Impact**: Better error handling
**Cost**: ~50-100ms (complex errors only)

### 8. Tool Description Generation
**Current**: Use description as-is
**Problem**: Unclear or too technical
**LLM Solution**: Generate user-friendly summaries
**Impact**: Better tool discovery
**Cost**: ~50-100ms per tool (batched)
"""
    
    try:
        # Store as a thinking session
        thought_record = await session.add_thought(
            thought=opportunities_content,
            thought_number=1,
            total_thoughts=1,
            metadata={
                "type": "llm_opportunities",
                "priority": "planning",
                "categories": ["high", "medium", "low"]
            }
        )
        
        # Also store as a fact in memory for searchability
        await state.memory.store_fact(
            entity="LLMOpportunities",
            relation="documented",
            target="8 areas identified for LLM enhancement",
            context={
                "session_id": session_id,
                "high_priority": 2,
                "medium_priority": 3,
                "low_priority": 3,
                "total": 8
            },
            kb_id="system_architecture"
        )
        
        logger.info(f"Stored LLM opportunities in thinking session {session_id}")
        return {
            "ok": True,
            "session_id": session_id,
            "message": "LLM opportunities stored in thinking system",
            "thought_number": 1
        }
    except Exception as e:
        logger.error(f"Failed to store LLM opportunities: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def tool_store_medium_term_plan(state: AgentState) -> Dict[str, Any]:
    """
    Store medium term plan in the thinking system.
    
    Creates a thinking session with the medium term implementation plan.
    """
    if not hasattr(state, "memory") or not state.memory:
        return {"ok": False, "error": "Memory server not available"}
    
    session_id = "medium_term_plan"
    session = ThinkingSession(session_id, state.memory)
    
    # Medium Term Plan Content
    plan_content = """
# Medium Term Plan - Layer Control and LLM Enhancements

## Phase 1: Layer Control Tools (COMPLETED)
- ✅ Quality tier system (5 tiers)
- ✅ Refinement control
- ✅ Context pruning control
- ✅ Tool category filtering
- ✅ Layer status tool

## Phase 2: LLM Integration (Next Steps)

### High Priority LLM Opportunities
1. **Tool Categorization** - Replace regex with semantic understanding
   - Implementation: Use LLM as fallback when pattern matching fails
   - Performance: ~50-100ms per tool (cached)
   - Impact: Automatic handling of new tools

2. **Feedback/Learning Loop** - Vector search for query similarity
   - Implementation: Replace keyword matching with semantic similarity
   - Performance: ~100-200ms (with caching)
   - Impact: Better tool suggestions

### Medium Priority LLM Opportunities
3. **Startup Error Analysis** - LLM classification and extraction
4. **Trigger Matching** - Semantic matching instead of exact strings
5. **Content Quality Assessment** - Semantic quality evaluation

### Low Priority LLM Opportunities
6. **Knowledge Base Selection** - Semantic KB routing
7. **Error Message Parsing** - Structured extraction
8. **Tool Description Generation** - User-friendly summaries

## Phase 3: Advanced Layer Features
- Per-request quality override
- Layer enable/disable
- Layer configuration API
- Quality tier analytics
- Adaptive quality selection

## Phase 4: Integration and Testing
- Integrate quality tiers into engine
- Update system prompt construction
- Update tool filtering pipeline
- Performance testing and optimization
- Documentation and examples
"""
    
    try:
        # Store as a thinking session
        thought_record = await session.add_thought(
            thought=plan_content,
            thought_number=1,
            total_thoughts=1,
            metadata={
                "type": "medium_term_plan",
                "priority": "planning",
                "phases": 4
            }
        )
        
        # Also store as a fact in memory for searchability
        await state.memory.store_fact(
            entity="MediumTermPlan",
            relation="documented",
            target="Layer control and LLM enhancement roadmap",
            context={
                "session_id": session_id,
                "phases": 4,
                "phase_1_status": "completed",
                "phase_2_status": "pending"
            },
            kb_id="system_architecture"
        )
        
        logger.info(f"Stored medium term plan in thinking session {session_id}")
        return {
            "ok": True,
            "session_id": session_id,
            "message": "Medium term plan stored in thinking system",
            "thought_number": 1
        }
    except Exception as e:
        logger.error(f"Failed to store medium term plan: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}







