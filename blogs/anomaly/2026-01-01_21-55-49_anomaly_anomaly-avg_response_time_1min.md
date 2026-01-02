---
timestamp: 1767322549.552772
datetime: '2026-01-01T21:55:49.552772'
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
  anomaly_id: avg_response_time_1min_1767322549.552772
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 465.88307906627034
    baseline_value: 450.1491934809853
    deviation: 2.3734423228710217
    severity: warning
    percentage_change: 3.495260196650709
  system_state:
    active_requests: 6
    completed_requests_1min: 768
    error_rate_1min: 0.0
    avg_response_time_1min: 466.0378952200214
  metadata: {}
  efficiency:
    requests_per_second: 12.8
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 465.88
- **Baseline Value**: 450.15
- **Deviation**: 2.37 standard deviations
- **Change**: +3.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 768
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 466.04ms

### Efficiency Metrics

- **Requests/sec**: 12.80
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 465.88307906627034,
    "baseline_value": 450.1491934809853,
    "deviation": 2.3734423228710217,
    "severity": "warning",
    "percentage_change": 3.495260196650709
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 768,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 466.0378952200214
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.8,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
