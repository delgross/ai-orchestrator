---
timestamp: 1767407199.0240881
datetime: '2026-01-02T21:26:39.024088'
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
  anomaly_id: avg_response_time_1min_1767407199.0240881
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 447.1999284442871
    baseline_value: 428.1293412305825
    deviation: 2.010719976265201
    severity: warning
    percentage_change: 4.454398560698861
  system_state:
    active_requests: 6
    completed_requests_1min: 867
    error_rate_1min: 0.0
    avg_response_time_1min: 447.1999284442871
  metadata: {}
  efficiency:
    requests_per_second: 14.45
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 447.20
- **Baseline Value**: 428.13
- **Deviation**: 2.01 standard deviations
- **Change**: +4.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 867
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 447.20ms

### Efficiency Metrics

- **Requests/sec**: 14.45
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 447.1999284442871,
    "baseline_value": 428.1293412305825,
    "deviation": 2.010719976265201,
    "severity": "warning",
    "percentage_change": 4.454398560698861
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 867,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 447.1999284442871
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.45,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
