---
timestamp: 1767229785.057738
datetime: '2025-12-31T20:09:45.057738'
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
  anomaly_id: avg_response_time_1min_1767229785.057738
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 216.4276376847298
    baseline_value: 178.92138804158856
    deviation: 2.2637272400227486
    severity: warning
    percentage_change: 20.96241821823072
  system_state:
    active_requests: 3
    completed_requests_1min: 62
    error_rate_1min: 0.0
    avg_response_time_1min: 216.4276376847298
  metadata: {}
  efficiency:
    requests_per_second: 1.0333333333333334
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 216.43
- **Baseline Value**: 178.92
- **Deviation**: 2.26 standard deviations
- **Change**: +21.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 62
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 216.43ms

### Efficiency Metrics

- **Requests/sec**: 1.03
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 216.4276376847298,
    "baseline_value": 178.92138804158856,
    "deviation": 2.2637272400227486,
    "severity": "warning",
    "percentage_change": 20.96241821823072
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 62,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 216.4276376847298
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
