---
timestamp: 1767100016.4596832
datetime: '2025-12-30T08:06:56.459683'
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
  anomaly_id: avg_response_time_1min_1767100016.4596832
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1261.5995407104492
    baseline_value: 8.714917063713074
    deviation: 7.338491982010508
    severity: critical
    percentage_change: 14376.322969996605
  system_state:
    active_requests: 2
    completed_requests_1min: 6
    error_rate_1min: 0.0
    avg_response_time_1min: 1261.5995407104492
  metadata: {}
  efficiency:
    requests_per_second: 0.1
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1261.60
- **Baseline Value**: 8.71
- **Deviation**: 7.34 standard deviations
- **Change**: +14376.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 6
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1261.60ms

### Efficiency Metrics

- **Requests/sec**: 0.10
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

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
    "current_value": 1261.5995407104492,
    "baseline_value": 8.714917063713074,
    "deviation": 7.338491982010508,
    "severity": "critical",
    "percentage_change": 14376.322969996605
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 6,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1261.5995407104492
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.1,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
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
