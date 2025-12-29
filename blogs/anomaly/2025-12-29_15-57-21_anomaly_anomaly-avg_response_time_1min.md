---
timestamp: 1767041841.726298
datetime: '2025-12-29T15:57:21.726298'
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
  anomaly_id: avg_response_time_1min_1767041841.726298
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 56390.68913459778
    baseline_value: 1652.5703013116402
    deviation: 7.284194954193646
    severity: critical
    percentage_change: 3312.301981334207
  system_state:
    active_requests: 6
    completed_requests_1min: 6
    error_rate_1min: 0.0
    avg_response_time_1min: 56390.68913459778
  metadata: {}
  efficiency:
    requests_per_second: 0.1
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 56390.69
- **Baseline Value**: 1652.57
- **Deviation**: 7.28 standard deviations
- **Change**: +3312.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 6
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 56390.69ms

### Efficiency Metrics

- **Requests/sec**: 0.10
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

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
    "current_value": 56390.68913459778,
    "baseline_value": 1652.5703013116402,
    "deviation": 7.284194954193646,
    "severity": "critical",
    "percentage_change": 3312.301981334207
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 6,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 56390.68913459778
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.1,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
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
