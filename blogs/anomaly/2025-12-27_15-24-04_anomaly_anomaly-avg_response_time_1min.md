---
timestamp: 1766867044.2748318
datetime: '2025-12-27T15:24:04.274832'
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
  anomaly_id: avg_response_time_1min_1766867044.2748318
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 381.43281076775224
    baseline_value: 121.15328110856959
    deviation: 9.222722796481612
    severity: critical
    percentage_change: 214.8348994576031
  system_state:
    active_requests: 0
    completed_requests_1min: 61
    error_rate_1min: 0.0
    avg_response_time_1min: 381.43281076775224
  metadata: {}
  efficiency:
    requests_per_second: 1.0166666666666666
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 381.43
- **Baseline Value**: 121.15
- **Deviation**: 9.22 standard deviations
- **Change**: +214.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 61
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 381.43ms

### Efficiency Metrics

- **Requests/sec**: 1.02
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

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
    "current_value": 381.43281076775224,
    "baseline_value": 121.15328110856959,
    "deviation": 9.222722796481612,
    "severity": "critical",
    "percentage_change": 214.8348994576031
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 61,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 381.43281076775224
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0166666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
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
