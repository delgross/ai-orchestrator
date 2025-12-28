# System Blog

This directory contains machine and human-readable blog entries documenting system events, anomalies, decisions, and resolutions.

## Structure

Blog entries are organized by category:
- `anomaly/` - Anomaly detection events
- `system_event/` - General system events
- `decision/` - System decisions and changes
- `resolution/` - Problem resolutions
- `learning/` - System learning and patterns
- `config_change/` - Configuration changes

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
---

# Anomaly: avg_response_time_1min

[Human-readable content here...]
```

## Reading Blog Entries

### Via API

```bash
# Get all anomaly entries
GET /admin/blog/anomaly

# Get open (unresolved) anomalies
GET /admin/blog/anomaly/open

# Get entries by category
GET /admin/blog?category=anomaly&severity=critical

# Resolve an entry
POST /admin/blog/resolve
{
  "timestamp": 1234567890.123,
  "status": "resolved",
  "notes": "Fixed by increasing timeout"
}
```

### Via File System

Blog entries are stored as `.md` files in category subdirectories. You can:
- Read them directly as Markdown
- Parse the YAML frontmatter for machine processing
- Use any Markdown viewer

## Machine Readability

The YAML frontmatter contains all structured data:
- Timestamps and metadata
- Structured data (JSON-compatible)
- Suggested actions
- Resolution status

Programs can:
1. Parse YAML frontmatter for structured data
2. Read Markdown content for human context
3. Update resolution status via API
4. Query entries by category, severity, status

## Human Readability

The Markdown body provides:
- Clear descriptions
- Context and explanations
- Suggested actions
- Resolution notes (when resolved)

Humans can:
1. Read entries directly
2. Understand what happened
3. Decide on actions
4. Document resolutions





