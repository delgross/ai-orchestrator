# Router-Based Tool Filtering Design

## Overview
Enhance the existing router system to aggressively filter tools before sending to the agent, reducing context size and improving performance.

## Key Design Principles

### 1. Zero Extra Latency
- **Reuse existing router analysis** - No additional LLM calls
- **Leverage existing cache** - Router results are already cached (5 min TTL)
- **Synchronous filtering** - Tool filtering is instant (just list operations)

### 2. Smart Filtering Strategy
- **High confidence queries**: Use only recommended tools (3-5 tools)
- **Medium confidence**: Use category-based filtering (10-15 tools)
- **Low confidence**: Use all tools (fallback to current behavior)

### 3. Graceful Degradation
- If router fails → use all tools (current behavior)
- If no recommendations → use category filtering
- If categories empty → use all tools

## Implementation

### Configuration (config.yaml)
```yaml
agent_runner:
  router:
    tool_filtering:
      enabled: true
      mode: "aggressive"  # aggressive | moderate | disabled
      min_confidence: 0.7  # Only filter aggressively if confidence >= 0.7
      max_tools_aggressive: 5  # Max tools when aggressive filtering
      max_tools_moderate: 15  # Max tools when moderate filtering
```

### Filtering Logic

```python
def filter_tools_by_router_analysis(
    all_tools: List[Dict[str, Any]],
    router_analysis: RouterAnalysis,
    mode: str = "aggressive",
    min_confidence: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Filter tools based on router analysis.
    
    Strategy:
    1. If confidence >= min_confidence AND recommended_tools:
       - Use ONLY recommended_tools (aggressive)
    2. Else if tool_categories:
       - Use category-based filtering (moderate)
    3. Else:
       - Use all tools (fallback)
    """
    if mode == "disabled":
        return all_tools
    
    # High confidence + specific recommendations = aggressive filtering
    if (router_analysis.confidence >= min_confidence and 
        router_analysis.recommended_tools and
        mode == "aggressive"):
        return _filter_by_recommended_tools(all_tools, router_analysis.recommended_tools)
    
    # Category-based filtering (moderate)
    if router_analysis.tool_categories:
        filtered = filter_tools_by_categories(
            all_tools,
            router_analysis.tool_categories,
            router_analysis.recommended_tools
        )
        if mode == "moderate":
            # Limit to max_tools_moderate
            return filtered[:15]
        return filtered
    
    # Fallback: use all tools
    return all_tools
```

### Integration Point

The filtering happens in `_agent_loop()` right after router analysis:

```python
# Current code (line ~3832)
if router_analysis.tool_categories or router_analysis.recommended_tools:
    effective_tools = filter_tools_by_categories(...)

# Enhanced code
if ROUTER_TOOL_FILTERING_ENABLED:
    effective_tools = filter_tools_by_router_analysis(
        effective_tools,
        router_analysis,
        mode=ROUTER_FILTERING_MODE,
        min_confidence=ROUTER_FILTERING_MIN_CONFIDENCE
    )
```

## Performance Characteristics

### Latency Impact
- **Router analysis**: ~200-500ms (already happening, cached)
- **Tool filtering**: <1ms (synchronous list operations)
- **Total overhead**: **ZERO** (reuses existing router call)

### Context Reduction
- **Before**: 50+ tools in context
- **After (aggressive)**: 3-5 tools in context
- **Reduction**: ~90% fewer tools
- **Token savings**: ~2000-5000 tokens per request

### Cache Benefits
- Router analysis cached for 5 minutes
- Similar queries get same filtered tool set
- No re-analysis needed for repeated queries

## Example Scenarios

### Scenario 1: Weather Query
```
Query: "What is the weather?"
Router Analysis:
  - confidence: 0.95
  - recommended_tools: ["mcp_proxy"]
  - tool_categories: ["weather"]
  
Filtered Tools: [mcp_proxy] (1 tool)
Context Reduction: 50 → 1 tool (98% reduction)
```

### Scenario 2: File Operation
```
Query: "Read config.yaml and validate it"
Router Analysis:
  - confidence: 0.85
  - recommended_tools: ["read_text", "mcp_proxy"]
  - tool_categories: ["filesystem", "code"]
  
Filtered Tools: [read_text, write_text, mcp_proxy] (3 tools)
Context Reduction: 50 → 3 tools (94% reduction)
```

### Scenario 3: Ambiguous Query
```
Query: "Help me with something"
Router Analysis:
  - confidence: 0.3
  - recommended_tools: []
  - tool_categories: []
  
Filtered Tools: All tools (fallback)
Context Reduction: None (safety first)
```

## Configuration Options

### Aggressive Mode (Recommended)
- **Use case**: Production, high-traffic
- **Behavior**: Only recommended tools if confidence >= 0.7
- **Risk**: Might miss edge cases
- **Benefit**: Maximum performance, minimum cost

### Moderate Mode
- **Use case**: Development, testing
- **Behavior**: Category-based filtering, limit to 15 tools
- **Risk**: Low
- **Benefit**: Good balance of performance and flexibility

### Disabled Mode
- **Use case**: Debugging, troubleshooting
- **Behavior**: All tools (current behavior)
- **Risk**: None
- **Benefit**: Maximum flexibility

## Monitoring

### Metrics to Track
- Tool filtering rate (how often filtering happens)
- Average tools before/after filtering
- Router confidence distribution
- Fallback rate (how often we use all tools)

### Logging
```python
logger.info(
    "router_tool_filtering",
    extra={
        "mode": mode,
        "confidence": router_analysis.confidence,
        "tools_before": len(all_tools),
        "tools_after": len(filtered_tools),
        "reduction_pct": (1 - len(filtered_tools) / len(all_tools)) * 100,
        "used_recommended": bool(router_analysis.recommended_tools),
        "used_categories": bool(router_analysis.tool_categories),
    }
)
```

## Migration Path

1. **Phase 1**: Add filtering logic, default to "moderate" mode
2. **Phase 2**: Monitor for 1 week, collect metrics
3. **Phase 3**: Enable "aggressive" mode if metrics look good
4. **Phase 4**: Fine-tune confidence thresholds based on data

## Backward Compatibility

- Default: "moderate" mode (safe, backward compatible)
- Can disable via config (falls back to current behavior)
- No breaking changes to existing API


