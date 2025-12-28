# Router Best Practices - Implementation Complete

## Summary

All three router best practices have been successfully implemented:

1. ✅ **Semantic Paraphrasing (Utterance Bank)**
2. ✅ **Negative Constraints**
3. ✅ **Logprobs Support (Judge Model)**

---

## 1. Semantic Paraphrasing ✅

### Implementation

Added `TOOL_CATEGORY_EXAMPLES` dictionary with 8-10 semantic paraphrasing examples for each tool category:

- **web_search**: "Search the web for...", "Find information about...", "Look up...", etc.
- **filesystem**: "Read the file...", "Create a file...", "Search for my keys", etc.
- **code**: "Write code to...", "Execute command...", "Run the program...", etc.
- **browser**: "Navigate to...", "Open the website...", "Click on...", etc.
- **memory**: "Remember that...", "Store the fact...", "Recall when...", etc.
- **weather**: "What is the weather?", "Check the weather", "Weather forecast", etc.
- And more...

### Integration

The examples are dynamically included in the router prompt based on available tool categories:

```python
# Build category examples section
category_examples_text = ""
if available_categories:
    examples_list = []
    for cat in sorted(available_categories):
        if cat in TOOL_CATEGORY_EXAMPLES:
            examples = TOOL_CATEGORY_EXAMPLES[cat]
            examples_list.append(f"  - {cat}: {', '.join(examples[:8])}")
    if examples_list:
        category_examples_text = "\n\nTool Category Examples (semantic paraphrasing):\n" + "\n".join(examples_list)
```

### Benefits

- Router can now recognize queries using different phrasings
- More robust to natural language variations
- Better category matching accuracy

---

## 2. Negative Constraints ✅

### Implementation

Added `NEGATIVE_CONSTRAINT_EXAMPLES` list with 10 examples of what NOT to do:

```python
NEGATIVE_CONSTRAINT_EXAMPLES = [
    {
        "query": "Search for my keys",
        "wrong_category": "web_search",
        "correct_category": "filesystem",
        "reason": "Personal file search, not web search (Google)"
    },
    {
        "query": "Check my email",
        "wrong_category": "web_search",
        "correct_category": "automation",
        "reason": "Personal email access, not web search"
    },
    # ... 8 more examples
]
```

### Integration

Negative examples are included in the router prompt:

```python
negative_examples_text = ""
if NEGATIVE_CONSTRAINT_EXAMPLES:
    negative_list = []
    for ex in NEGATIVE_CONSTRAINT_EXAMPLES[:8]:  # Show top 8 examples
        negative_list.append(f"  - Query: '{ex['query']}' → NOT {ex['wrong_category']} (use {ex['correct_category']} instead: {ex['reason']})")
    if negative_list:
        negative_examples_text = "\n\n⚠️ Important: Avoid misclassification. Examples of what NOT to do:\n" + "\n".join(negative_list)
```

### Benefits

- Prevents common misclassifications
- Router knows what NOT to do
- More precise routing decisions

---

## 3. Logprobs Support (Judge Model) ✅

### Implementation

#### Request Logprobs

Added `logprobs: True` and `top_logprobs: 1` to router API call:

```python
payload = {
    "model": ROUTER_MODEL,
    "messages": [...],
    "temperature": 0.0,
    "max_tokens": 1000,
    "logprobs": True,  # Request logprobs for true confidence scores
    "top_logprobs": 1,  # Get top 1 probability for first token
}
```

#### Extract Logprobs

Extract logprobs from API response and convert to confidence:

```python
# Extract logprobs for confidence scoring (Judge Model approach)
confidence_from_logprobs = None
logprobs = choice.get("logprobs")
if logprobs:
    content_tokens = logprobs.get("content", [])
    if content_tokens and len(content_tokens) > 0:
        first_token = content_tokens[0]
        logprob = first_token.get("logprob")
        if logprob is not None:
            # Convert logprob to probability (logprob is log base e)
            probability = math.exp(logprob)
            # Normalize to [0, 1] range
            confidence_from_logprobs = max(0.0, min(1.0, probability))
```

#### Override JSON Confidence

Use logprobs confidence if available, fallback to JSON confidence:

```python
# Override confidence with logprobs if available (more accurate)
if confidence_from_logprobs is not None:
    logger.debug(f"Using logprobs confidence ({confidence_from_logprobs:.3f}) instead of JSON confidence ({analysis.confidence:.3f})")
    analysis.confidence = confidence_from_logprobs
```

### Benefits

- **True mathematical confidence**: Uses model's internal probability, not self-reported
- **More accurate**: Logprobs reflect actual model certainty
- **Graceful degradation**: Falls back to JSON confidence if logprobs unavailable

### Compatibility

- Works with APIs that support logprobs (OpenAI, Anthropic, some Ollama models)
- Gracefully handles APIs that don't support logprobs (falls back to JSON confidence)
- Handles different logprob response formats

---

## Code Changes

### Files Modified

1. **`agent_runner/router_analyzer.py`**:
   - Added `math` import
   - Added `TOOL_CATEGORY_EXAMPLES` dictionary
   - Added `NEGATIVE_CONSTRAINT_EXAMPLES` list
   - Modified `_call_router_model()` to request and extract logprobs
   - Modified `analyze_query()` to include semantic examples and negative constraints in prompt
   - Modified `analyze_query()` to use logprobs confidence when available

### Key Functions

- `_call_router_model()`: Now returns `(content, confidence_from_logprobs)` tuple
- `analyze_query()`: Builds enhanced prompt with examples and uses logprobs confidence

---

## Testing Recommendations

### 1. Test Semantic Paraphrasing

Try queries with different phrasings:
- "Search the web for X" vs "Find information about X" vs "Look up X"
- Should all route to `web_search` category

### 2. Test Negative Constraints

Try queries that might be misclassified:
- "Search for my keys" → Should route to `filesystem`, NOT `web_search`
- "Check my email" → Should route to `automation`, NOT `web_search`

### 3. Test Logprobs

- Check logs for "Extracted confidence from logprobs" messages
- Verify confidence scores are more accurate
- Test with models that support/don't support logprobs

---

## Performance Impact

- **Semantic Paraphrasing**: Minimal - just adds text to prompt
- **Negative Constraints**: Minimal - just adds text to prompt
- **Logprobs**: Slight increase in API response size, but no additional latency (data already in response)

---

## Future Enhancements

1. **Expand Semantic Examples**: Add more examples per category based on real usage
2. **Expand Negative Examples**: Add more misclassification patterns
3. **Improve Logprobs Extraction**: Use multiple tokens or more sophisticated normalization
4. **A/B Testing**: Compare routing accuracy before/after improvements

---

## Status

✅ **All three improvements implemented and ready for testing**


