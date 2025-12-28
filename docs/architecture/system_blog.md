# System Blog

A machine and human-readable blog system for tracking system events, anomalies, decisions, and resolutions.

## Overview

The system blog provides a structured way to document system behavior that is:
- **Human-readable**: Markdown format for easy reading and understanding
- **Machine-readable**: YAML frontmatter and structured data for programmatic access
- **Actionable**: Includes suggested actions and resolution tracking

## Format

Each blog entry is a Markdown file with YAML frontmatter:

```markdown
---
timestamp: 1234567890.123
datetime: 2024-01-15T10:30:00
category: anomaly
severity: warning
title: Anomaly: avg_response_time_1min
source: anomaly_detector
tags: [anomaly, avg_response_time_1min, warning]
resolution_status: open
suggested_actions:
  - Check for slow upstream services
  - Review recent code changes
metadata:
  anomaly_id: avg_response_time_1min_1234567890.123
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 5000.0
    baseline_value: 1000.0
    deviation: 4.5
    severity: warning
  system_state:
    active_requests: 5
    error_rate_1min: 0.05
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 5000.00
- **Baseline Value**: 1000.00
- **Deviation**: 4.50 standard deviations
- **Change**: +400.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 5
- **Completed Requests (1min)**: 42
- **Error Rate (1min)**: 5.00%
- **Avg Response Time (1min)**: 5000.00ms

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
```

## Categories

- **anomaly** - Anomaly detection events (automatically created)
- **system_event** - General system events
- **decision** - System decisions and changes
- **resolution** - Problem resolutions
- **learning** - System learning and patterns
- **config_change** - Configuration changes

## API Endpoints

### List Blog Entries

```bash
GET /admin/blog
```

**Query Parameters**:
- `category` - Filter by category (anomaly, system_event, etc.)
- `severity` - Filter by severity (info, warning, critical)
- `resolution_status` - Filter by status (open, investigating, resolved, ignored)
- `limit` - Maximum entries to return (default: 100)

**Example**:
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:5460/admin/blog?category=anomaly&resolution_status=open"
```

### Get Anomaly Entries

```bash
GET /admin/blog/anomaly
```

### Get Open Anomalies

```bash
GET /admin/blog/anomaly/open
```

Returns unresolved anomaly entries.

### Resolve Blog Entry

```bash
POST /admin/blog/resolve
```

**Body**:
```json
{
  "timestamp": 1234567890.123,
  "status": "resolved",
  "notes": "Fixed by increasing timeout to 180s",
  "category": "anomaly"
}
```

**Status Values**:
- `open` - Issue not yet addressed
- `investigating` - Currently being investigated
- `resolved` - Issue has been fixed
- `ignored` - Issue determined to be non-critical

## Automatic Blogging

### Anomaly Detection

When anomalies are detected, blog entries are automatically created with:
- Full anomaly details (metric, values, deviation)
- System context (active requests, error rates, resource usage)
- Suggested actions based on anomaly type
- Structured data for machine processing

### Integration Points

The blog system can be extended to automatically write entries for:
- System events (startups, shutdowns, config changes)
- Decisions (parameter tuning, routing changes)
- Resolutions (when problems are fixed)
- Learning (patterns discovered, optimizations)

## Usage Workflow

### 1. Read Anomalies

```bash
# Get all open anomalies
curl http://localhost:5460/admin/blog/anomaly/open
```

### 2. Review Blog Entry

Read the Markdown file directly or via API. The entry includes:
- What happened (human-readable description)
- Context (system state at time)
- Suggested actions (what to do)

### 3. Decide on Actions

Review suggested actions and decide:
- Which actions to take
- Whether to investigate further
- If it's a false positive

### 4. Document Resolution

```bash
# Mark as resolved
curl -X POST http://localhost:5460/admin/blog/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": 1234567890.123,
    "status": "resolved",
    "notes": "Fixed by increasing timeout",
    "category": "anomaly"
  }'
```

### 5. Machine Learning (Future)

The structured data in blog entries can be used for:
- Pattern recognition (similar anomalies)
- Automated resolution suggestions
- Learning from past resolutions
- Predictive problem detection

## File Structure

```
blogs/
├── README.md
├── anomaly/
│   ├── 2024-01-15_10-30-00_anomaly_avg-response-time-1min.md
│   └── 2024-01-15_11-45-00_anomaly_error-rate-1min.md
├── system_event/
├── decision/
├── resolution/
├── learning/
└── config_change/
```

## Benefits

1. **Human Understanding**: Clear descriptions help you understand what happened
2. **Machine Processing**: Structured data enables automated analysis
3. **Decision Support**: Suggested actions guide problem resolution
4. **Historical Record**: Complete history of system behavior
5. **Learning Foundation**: Data for future ML/automation

## Future Enhancements

- Automated resolution suggestions based on past blog entries
- Pattern matching (similar anomalies → similar resolutions)
- Integration with LLM for resolution generation
- Dashboard UI for blog browsing
- Export/import for analysis





