---
timestamp: 1767349566.0621219
datetime: '2026-01-02T05:26:06.062122'
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
  anomaly_id: avg_response_time_1min_1767349566.0621219
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 448.90068539921543
    baseline_value: 439.27270619266005
    deviation: 2.642867886882306
    severity: warning
    percentage_change: 2.1918000073359116
  system_state:
    active_requests: 6
    completed_requests_1min: 805
    error_rate_1min: 0.0
    avg_response_time_1min: 448.90068539921543
  metadata: {}
  efficiency:
    requests_per_second: 13.416666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 448.90
- **Baseline Value**: 439.27
- **Deviation**: 2.64 standard deviations
- **Change**: +2.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 805
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 448.90ms

### Efficiency Metrics

- **Requests/sec**: 13.42
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 448.90068539921543,
    "baseline_value": 439.27270619266005,
    "deviation": 2.642867886882306,
    "severity": "warning",
    "percentage_change": 2.1918000073359116
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 805,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 448.90068539921543
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.416666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
