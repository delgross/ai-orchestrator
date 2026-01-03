---
timestamp: 1767418908.692181
datetime: '2026-01-03T00:41:48.692181'
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
  anomaly_id: avg_response_time_1min_1767418908.692181
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1082.5365158819384
    baseline_value: 888.4284688409342
    deviation: 2.4968784213635677
    severity: warning
    percentage_change: 21.848472201058836
  system_state:
    active_requests: 32
    completed_requests_1min: 1705
    error_rate_1min: 0.0
    avg_response_time_1min: 1082.5365158819384
  metadata: {}
  efficiency:
    requests_per_second: 28.416666666666668
    cache_hit_rate: 0.0
    queue_depth: 32
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1082.54
- **Baseline Value**: 888.43
- **Deviation**: 2.50 standard deviations
- **Change**: +21.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 32
- **Completed Requests (1min)**: 1705
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1082.54ms

### Efficiency Metrics

- **Requests/sec**: 28.42
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 32

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1082.5365158819384,
    "baseline_value": 888.4284688409342,
    "deviation": 2.4968784213635677,
    "severity": "warning",
    "percentage_change": 21.848472201058836
  },
  "system_state": {
    "active_requests": 32,
    "completed_requests_1min": 1705,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1082.5365158819384
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 28.416666666666668,
    "cache_hit_rate": 0.0,
    "queue_depth": 32
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
