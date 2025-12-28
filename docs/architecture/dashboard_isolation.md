# Dashboard Isolation and Refactoring Plan

## Current Issues

1. **Dashboard is embedded in router** - Single 3914-line HTML file served directly
2. **No error learning** - Errors happen but aren't tracked or learned from
3. **Code complexity** - `agent_runner.py` is 3795 lines, dashboard is 3914 lines
4. **No user pattern tracking** - Can't learn from user behavior

## Phase 1: Error Tracking & Learning (✅ Started)

### Completed
- ✅ Created `dashboard_tracker.py` for error and interaction tracking
- ✅ Added tracking endpoints to agent-runner
- ✅ Added JavaScript error tracking to dashboard
- ✅ Global error handlers for unhandled errors

### Next Steps
1. Add component-specific error tracking (models, scheduler, memory, etc.)
2. Create dashboard insights endpoint for viewing patterns
3. Add automatic error pattern detection

## Phase 2: Dashboard Isolation

### Option A: Separate Dashboard Service (Recommended)
- Move dashboard to its own FastAPI service
- Dashboard service communicates with router/agent via API
- Better separation of concerns
- Can be restarted independently
- Easier to test and debug

### Option B: Dashboard as Static Assets
- Serve dashboard as static files from nginx/simple server
- Dashboard makes API calls to router/agent
- No server-side rendering needed
- Simplest isolation

### Option C: Dashboard Module
- Extract dashboard into separate Python module
- Keep in same process but isolated code
- Easier refactoring path
- Can migrate to separate service later

**Recommendation**: Start with Option C (module), migrate to Option A (service) later.

## Phase 3: Code Refactoring

### agent_runner.py (3795 lines) → Split into:
- `agent_runner/core.py` - Core agent loop and tool execution
- `agent_runner/api.py` - FastAPI routes and endpoints
- `agent_runner/mcp_manager.py` - MCP server management
- `agent_runner/health.py` - Health checks and monitoring
- `agent_runner/config.py` - Configuration loading

### dashboard/index.html (3914 lines) → Split into:
- `dashboard/index.html` - Main structure and layout
- `dashboard/js/api.js` - API communication
- `dashboard/js/refresh.js` - Data refresh logic
- `dashboard/js/models.js` - Models tab logic
- `dashboard/js/scheduler.js` - Scheduler tab logic
- `dashboard/js/memory.js` - Memory tab logic
- `dashboard/js/tasks.js` - Tasks tab logic
- `dashboard/js/tracking.js` - Error/interaction tracking
- `dashboard/css/styles.css` - All styles

## Phase 4: User Pattern Learning

### Track:
- Which tabs are used most
- Which actions fail most often
- Time between interactions
- Common error sequences
- Performance patterns

### Learn:
- Optimize dashboard for common workflows
- Pre-load frequently accessed data
- Cache based on usage patterns
- Suggest improvements based on errors

## Implementation Priority

1. **High Priority** (Do Now):
   - ✅ Error tracking system
   - ✅ Interaction tracking
   - Add component-specific tracking
   - Create insights dashboard

2. **Medium Priority** (Next Sprint):
   - Extract dashboard JavaScript into modules
   - Split agent_runner.py into logical modules
   - Add user pattern analysis

3. **Low Priority** (Future):
   - Move dashboard to separate service
   - Full codebase refactoring
   - Advanced learning algorithms






