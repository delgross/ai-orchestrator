---
timestamp: 1767306098.169937
datetime: '2026-01-01T17:21:38.169937'
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
  anomaly_id: avg_response_time_1min_1767306098.169937
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 549.4089400084536
    baseline_value: 602.6273084723431
    deviation: 2.653753129354439
    severity: warning
    percentage_change: -8.83105822051075
  system_state:
    active_requests: 8
    completed_requests_1min: 802
    error_rate_1min: 0.0
    avg_response_time_1min: 549.4089400084536
  metadata: {}
  efficiency:
    requests_per_second: 13.366666666666667
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 549.41
- **Baseline Value**: 602.63
- **Deviation**: 2.65 standard deviations
- **Change**: -8.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 802
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 549.41ms

### Efficiency Metrics

- **Requests/sec**: 13.37
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 549.4089400084536,
    "baseline_value": 602.6273084723431,
    "deviation": 2.653753129354439,
    "severity": "warning",
    "percentage_change": -8.83105822051075
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 802,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 549.4089400084536
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.366666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
