# Unified Tracking System - Implementation Plan

## Problem Statement

The system has **5+ siloed tracking systems** that don't communicate:
1. Dashboard tracker → standalone
2. JSON event logging → standalone  
3. System blog → standalone (except anomaly detection)
4. Health monitor → only talks to notifications
5. Observability → comprehensive but isolated

**Result**: Events are tracked inconsistently, some systems miss important events, and troubleshooting requires checking multiple systems.

## Solution: Unified Tracking Layer

### Architecture

```
┌─────────────────────────────────────────┐
│   Unified Tracking API                  │
│   (common/unified_tracking.py)         │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────┐
│  Observability│  │ Notifications│
└──────────────┘  └──────────────┘
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────┐
│ JSON Events  │  │ System Blog  │
└──────────────┘  └──────────────┘
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────┐
│ Dashboard    │  │ (Future)     │
│ Tracker      │  │ Analytics    │
└──────────────┘  └──────────────┘
```

### Key Features

1. **Single Entry Point**: `track_event()` routes to all systems
2. **Automatic Routing**: Based on event category/severity
3. **Backward Compatible**: Old code still works
4. **Lazy Initialization**: Only loads systems that are available
5. **Error Resilient**: If one system fails, others still work

## Implementation Status

### ✅ Phase 1: Core System (COMPLETED)

- [x] Created `common/unified_tracking.py`
- [x] Unified tracker class with lazy initialization
- [x] Integration with all 5 tracking systems
- [x] Convenience functions for common patterns
- [x] Error handling and resilience

### 🔄 Phase 2: Migration (IN PROGRESS)

Priority components to migrate:

1. **Dashboard Tracker** (HIGH PRIORITY)
   - Already identified as siloed
   - Easy win - just update error handler
   - File: `dashboard/index.html`

2. **MCP Circuit Breakers** (HIGH PRIORITY)
   - Many events, high visibility
   - Currently uses JSON events + notifications
   - File: `agent_runner/agent_runner.py` (lines 289-451)

3. **Health Monitor** (MEDIUM PRIORITY)
   - Currently only uses notifications
   - File: `agent_runner/health_monitor.py`

4. **Background Tasks** (MEDIUM PRIORITY)
   - Task failures need comprehensive tracking
   - File: `agent_runner/background_tasks.py`

### 📋 Phase 3: Future Enhancements

- [ ] Async observability recording
- [ ] Event filtering/routing rules
- [ ] Performance batching for high-volume events
- [ ] Unified analytics dashboard
- [ ] Event correlation across systems

## Migration Checklist

### Dashboard Tracker
- [ ] Update `refreshModelServices` error handler
- [ ] Test dashboard error tracking
- [ ] Verify events appear in all systems

### MCP Circuit Breakers
- [ ] Replace `_record_mcp_failure` calls
- [ ] Replace `_reset_mcp_success` calls
- [ ] Test circuit breaker events
- [ ] Verify observability integration

### Health Monitor
- [ ] Replace notification-only calls
- [ ] Add health events to observability
- [ ] Test health event tracking

### Background Tasks
- [ ] Replace task failure tracking
- [ ] Add task events to observability
- [ ] Test task event tracking

## Testing Strategy

1. **Unit Tests**: Test unified tracker routing
2. **Integration Tests**: Verify events appear in all systems
3. **Backward Compatibility**: Ensure old code still works
4. **Performance**: Verify no significant overhead

## Rollout Plan

1. **Week 1**: Deploy unified tracking (non-breaking)
2. **Week 2**: Migrate dashboard tracker
3. **Week 3**: Migrate MCP circuit breakers
4. **Week 4**: Migrate health monitor
5. **Week 5**: Migrate background tasks
6. **Week 6**: Review and optimize

## Success Metrics

- ✅ All events tracked in at least 2 systems
- ✅ Critical events tracked in all 5 systems
- ✅ Zero breaking changes
- ✅ Improved troubleshooting visibility
- ✅ Reduced code duplication


