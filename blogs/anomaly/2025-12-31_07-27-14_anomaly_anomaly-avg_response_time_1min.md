---
timestamp: 1767184034.9076731
datetime: '2025-12-31T07:27:14.907673'
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
  anomaly_id: avg_response_time_1min_1767184034.9076731
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 122.98487313091755
    baseline_value: 104.43883761763573
    deviation: 1.5915354163942665
    severity: warning
    percentage_change: 17.757795793535436
  system_state:
    active_requests: 0
    completed_requests_1min: 128
    error_rate_1min: 0.0
    avg_response_time_1min: 122.98487313091755
  metadata: {}
  efficiency:
    requests_per_second: 2.1333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 122.98
- **Baseline Value**: 104.44
- **Deviation**: 1.59 standard deviations
- **Change**: +17.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 128
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 122.98ms

### Efficiency Metrics

- **Requests/sec**: 2.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 122.98487313091755,
    "baseline_value": 104.43883761763573,
    "deviation": 1.5915354163942665,
    "severity": "warning",
    "percentage_change": 17.757795793535436
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 128,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 122.98487313091755
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.1333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
