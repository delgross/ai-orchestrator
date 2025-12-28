---
timestamp: 1766889005.62914
datetime: '2025-12-27T21:30:05.629140'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions:
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
metadata:
  anomaly_id: avg_response_time_1min_1766889005.62914
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 409.14869626363117
    baseline_value: 135.63101119225442
    deviation: 4.484921293777868
    severity: warning
    percentage_change: 201.66308771647402
  system_state:
    active_requests: 1
    completed_requests_1min: 75
    error_rate_1min: 0.0
    avg_response_time_1min: 409.14869626363117
  metadata: {}
  efficiency:
    requests_per_second: 1.25
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 409.15
- **Baseline Value**: 135.63
- **Deviation**: 4.48 standard deviations
- **Change**: +201.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 75
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 409.15ms

### Efficiency Metrics

- **Requests/sec**: 1.25
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 409.14869626363117,
    "baseline_value": 135.63101119225442,
    "deviation": 4.484921293777868,
    "severity": "warning",
    "percentage_change": 201.66308771647402
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 75,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 409.14869626363117
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.25,
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
