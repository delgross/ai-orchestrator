---
timestamp: 1767099716.439764
datetime: '2025-12-30T08:01:56.439764'
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
  anomaly_id: avg_response_time_1min_1767099716.439764
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 572.8040337562561
    baseline_value: 0.0064563751220703125
    deviation: 3969.5830122030616
    severity: critical
    percentage_change: 8871813.774002954
  system_state:
    active_requests: 1
    completed_requests_1min: 4
    error_rate_1min: 0.0
    avg_response_time_1min: 572.8040337562561
  metadata: {}
  efficiency:
    requests_per_second: 0.06666666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 572.80
- **Baseline Value**: 0.01
- **Deviation**: 3969.58 standard deviations
- **Change**: +8871813.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 4
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 572.80ms

### Efficiency Metrics

- **Requests/sec**: 0.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

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
    "current_value": 572.8040337562561,
    "baseline_value": 0.0064563751220703125,
    "deviation": 3969.5830122030616,
    "severity": "critical",
    "percentage_change": 8871813.774002954
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 4,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 572.8040337562561
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.06666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
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
