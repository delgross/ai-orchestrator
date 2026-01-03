---
timestamp: 1767404040.006306
datetime: '2026-01-02T20:34:00.006306'
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
  anomaly_id: avg_response_time_1min_1767404040.006306
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 545.1242013981467
    baseline_value: 507.037100710718
    deviation: 2.00249472116408
    severity: warning
    percentage_change: 7.511698973120852
  system_state:
    active_requests: 1
    completed_requests_1min: 152
    error_rate_1min: 0.0
    avg_response_time_1min: 545.1242013981467
  metadata: {}
  efficiency:
    requests_per_second: 2.533333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 545.12
- **Baseline Value**: 507.04
- **Deviation**: 2.00 standard deviations
- **Change**: +7.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 152
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 545.12ms

### Efficiency Metrics

- **Requests/sec**: 2.53
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 545.1242013981467,
    "baseline_value": 507.037100710718,
    "deviation": 2.00249472116408,
    "severity": "warning",
    "percentage_change": 7.511698973120852
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 152,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 545.1242013981467
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.533333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
