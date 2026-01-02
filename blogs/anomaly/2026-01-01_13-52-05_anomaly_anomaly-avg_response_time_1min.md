---
timestamp: 1767293525.351439
datetime: '2026-01-01T13:52:05.351439'
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
  anomaly_id: avg_response_time_1min_1767293525.351439
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 470.365683751268
    baseline_value: 450.333524834026
    deviation: 1.534788169038675
    severity: warning
    percentage_change: 4.448293944943374
  system_state:
    active_requests: 6
    completed_requests_1min: 619
    error_rate_1min: 0.0
    avg_response_time_1min: 470.365683751268
  metadata: {}
  efficiency:
    requests_per_second: 10.316666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 470.37
- **Baseline Value**: 450.33
- **Deviation**: 1.53 standard deviations
- **Change**: +4.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 619
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 470.37ms

### Efficiency Metrics

- **Requests/sec**: 10.32
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 470.365683751268,
    "baseline_value": 450.333524834026,
    "deviation": 1.534788169038675,
    "severity": "warning",
    "percentage_change": 4.448293944943374
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 619,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 470.365683751268
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.316666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
