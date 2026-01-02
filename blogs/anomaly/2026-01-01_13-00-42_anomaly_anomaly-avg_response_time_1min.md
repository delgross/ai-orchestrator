---
timestamp: 1767290442.899196
datetime: '2026-01-01T13:00:42.899196'
category: anomaly
severity: critical
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- critical
resolution_status: open
suggested_actions:
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767290442.899196
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1246.0391393271825
    baseline_value: 236.28058392777402
    deviation: 8.918913444499793
    severity: critical
    percentage_change: 427.35570507480645
  system_state:
    active_requests: 3
    completed_requests_1min: 93
    error_rate_1min: 0.0
    avg_response_time_1min: 1246.0391393271825
  metadata: {}
  efficiency:
    requests_per_second: 1.55
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1246.04
- **Baseline Value**: 236.28
- **Deviation**: 8.92 standard deviations
- **Change**: +427.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 93
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1246.04ms

### Efficiency Metrics

- **Requests/sec**: 1.55
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1246.0391393271825,
    "baseline_value": 236.28058392777402,
    "deviation": 8.918913444499793,
    "severity": "critical",
    "percentage_change": 427.35570507480645
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 93,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1246.0391393271825
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.55,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Investigate immediately - critical system issue detected
