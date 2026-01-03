---
timestamp: 1767378137.840117
datetime: '2026-01-02T13:22:17.840117'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: avg_response_time_1min_1767378137.840117
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 457.8678553849199
    baseline_value: 436.42201916924836
    deviation: 1.5337378696945525
    severity: warning
    percentage_change: 4.914013334270984
  system_state:
    active_requests: 7
    completed_requests_1min: 573
    error_rate_1min: 0.0
    avg_response_time_1min: 457.8678553849199
  metadata: {}
  efficiency:
    requests_per_second: 9.55
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 457.87
- **Baseline Value**: 436.42
- **Deviation**: 1.53 standard deviations
- **Change**: +4.9%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 573
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 457.87ms

### Efficiency Metrics

- **Requests/sec**: 9.55
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 457.8678553849199,
    "baseline_value": 436.42201916924836,
    "deviation": 1.5337378696945525,
    "severity": "warning",
    "percentage_change": 4.914013334270984
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 573,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 457.8678553849199
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 9.55,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
