---
timestamp: 1767370411.417933
datetime: '2026-01-02T11:13:31.417933'
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
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767370411.417933
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2012.866994050833
    baseline_value: 1240.409267509472
    deviation: 3.163276188488826
    severity: critical
    percentage_change: 62.27442399655098
  system_state:
    active_requests: 16
    completed_requests_1min: 650
    error_rate_1min: 0.0
    avg_response_time_1min: 2012.866994050833
  metadata: {}
  efficiency:
    requests_per_second: 10.833333333333334
    cache_hit_rate: 0.0
    queue_depth: 16
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2012.87
- **Baseline Value**: 1240.41
- **Deviation**: 3.16 standard deviations
- **Change**: +62.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 16
- **Completed Requests (1min)**: 650
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2012.87ms

### Efficiency Metrics

- **Requests/sec**: 10.83
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 16

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 2012.866994050833,
    "baseline_value": 1240.409267509472,
    "deviation": 3.163276188488826,
    "severity": "critical",
    "percentage_change": 62.27442399655098
  },
  "system_state": {
    "active_requests": 16,
    "completed_requests_1min": 650,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2012.866994050833
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.833333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 16
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
