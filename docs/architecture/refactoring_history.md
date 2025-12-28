# Code Refactoring and Organization Plan

## Current State Analysis

### File Sizes (Lines of Code)
- `agent_runner/agent_runner.py`: **3,795 lines** ⚠️ Too large
- `dashboard/index.html`: **3,914 lines** ⚠️ Too large
- `router/router.py`: ~1,600 lines (acceptable)

### Issues Identified

1. **agent_runner.py is monolithic**
   - Contains: API routes, agent loop, MCP management, health checks, background tasks, config loading
   - Hard to navigate and maintain
   - Difficult to test individual components

2. **dashboard/index.html is monolithic**
   - Contains: HTML, CSS, and all JavaScript in one file
   - 3,914 lines makes it hard to find and fix issues
   - No separation of concerns
   - Difficult to debug

3. **No error learning system** (✅ Now fixed)
   - Errors weren't being tracked
   - No pattern detection
   - Can't learn from failures

4. **No user pattern tracking** (✅ Now fixed)
   - Can't learn from user behavior
   - Can't optimize based on usage

## Refactoring Plan

### Phase 1: Dashboard Error Learning (✅ COMPLETED)

**Status**: Implemented
- ✅ Created `dashboard_tracker.py` for error/interaction tracking
- ✅ Added tracking endpoints to agent-runner
- ✅ Added JavaScript error tracking to dashboard
- ✅ Global error handlers
- ✅ API call tracking

**Next**: Add component-specific tracking and insights dashboard

### Phase 2: Split agent_runner.py (Priority: High)

**Target Structure**:
```
agent_runner/
├── __init__.py
├── main.py              # FastAPI app initialization
├── api/
│   ├── __init__.py
│   ├── routes.py        # All @app.get/@app.post endpoints
│   ├── chat.py          # Chat completions endpoint
│   └── admin.py         # Admin endpoints
├── core/
│   ├── __init__.py
│   ├── agent_loop.py    # Main agent loop
│   ├── tool_execution.py # Tool call execution
│   └── mcp_proxy.py     # MCP tool proxy
├── monitoring/
│   ├── __init__.py
│   ├── health.py        # Health checks
│   ├── diagnostics.py   # Diagnostic endpoints
│   └── dashboard_tracker.py # ✅ Already created
└── config/
    ├── __init__.py
    └── loader.py        # Configuration loading
```

**Estimated Impact**: 
- Reduces main file from 3,795 → ~500 lines
- Each module ~200-400 lines (manageable)
- Better testability
- Clearer organization

### Phase 3: Split dashboard/index.html (Priority: High)

**Target Structure**:
```
dashboard/
├── index.html           # Main structure only (~200 lines)
├── css/
│   └── styles.css      # All styles (~500 lines)
└── js/
    ├── api.js           # API communication (~200 lines)
    ├── tracking.js      # Error/interaction tracking (~150 lines)
    ├── refresh.js       # Data refresh logic (~400 lines)
    ├── models.js        # Models tab (~300 lines)
    ├── scheduler.js     # Scheduler tab (~300 lines)
    ├── memory.js        # Memory tab (~300 lines)
    ├── tasks.js          # Tasks tab (~200 lines)
    ├── tools.js          # Tools & MCP tab (~300 lines)
    ├── utils.js          # Utility functions (~200 lines)
    └── main.js           # Initialization (~100 lines)
```

**Estimated Impact**:
- Reduces main file from 3,914 → ~200 lines
- Each JS module ~150-400 lines (manageable)
- Easier to find and fix issues
- Can test modules independently

### Phase 4: Dashboard Isolation (Priority: Medium)

**Option A: Separate Service** (Recommended long-term)
- Move dashboard to `dashboard_service/`
- Separate FastAPI app
- Communicates via API only
- Can be restarted independently
- Better error isolation

**Option B: Static Assets** (Simpler)
- Serve dashboard as static files
- No server-side processing
- Dashboard makes API calls
- Simplest isolation

**Recommendation**: Start with current structure, migrate to Option A when needed.

## Implementation Order

### Week 1: Error Learning & Tracking
- ✅ Dashboard error tracking
- ✅ User interaction tracking
- Add insights dashboard tab
- Add component-specific tracking

### Week 2: agent_runner.py Refactoring
- Extract API routes to `api/` module
- Extract agent loop to `core/` module
- Extract health checks to `monitoring/` module
- Update imports and tests

### Week 3: dashboard/index.html Refactoring
- Extract CSS to `css/styles.css`
- Extract JavaScript to `js/` modules
- Update HTML to load modules
- Test all functionality

### Week 4: Dashboard Isolation (Optional)
- Evaluate if separate service needed
- If yes, create dashboard service
- Migrate dashboard code
- Update router to proxy or redirect

## Benefits

1. **Maintainability**: Smaller files are easier to understand and modify
2. **Debuggability**: Errors are easier to locate in smaller modules
3. **Testability**: Can test individual components
4. **Learning**: System learns from errors and improves
5. **Performance**: Can optimize individual modules
6. **Collaboration**: Multiple developers can work on different modules

## Metrics to Track

- Error rates by component
- Time to fix errors (should decrease with better organization)
- Code complexity metrics
- Test coverage
- User satisfaction (fewer errors = better UX)






