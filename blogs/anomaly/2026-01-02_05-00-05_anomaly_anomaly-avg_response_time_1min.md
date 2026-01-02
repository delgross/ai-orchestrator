---
timestamp: 1767348005.8648891
datetime: '2026-01-02T05:00:05.864889'
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
  anomaly_id: avg_response_time_1min_1767348005.8648891
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 432.10516027163777
    baseline_value: 436.8271062904256
    deviation: 1.70502214533936
    severity: warning
    percentage_change: -1.0809645168055195
  system_state:
    active_requests: 6
    completed_requests_1min: 838
    error_rate_1min: 0.0
    avg_response_time_1min: 432.10516027163777
  metadata: {}
  efficiency:
    requests_per_second: 13.966666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 432.11
- **Baseline Value**: 436.83
- **Deviation**: 1.71 standard deviations
- **Change**: -1.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 838
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 432.11ms

### Efficiency Metrics

- **Requests/sec**: 13.97
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 432.10516027163777,
    "baseline_value": 436.8271062904256,
    "deviation": 1.70502214533936,
    "severity": "warning",
    "percentage_change": -1.0809645168055195
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 838,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 432.10516027163777
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.966666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
