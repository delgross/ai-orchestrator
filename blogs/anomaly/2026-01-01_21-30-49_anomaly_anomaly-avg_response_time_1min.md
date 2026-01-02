---
timestamp: 1767321049.243071
datetime: '2026-01-01T21:30:49.243071'
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
  anomaly_id: avg_response_time_1min_1767321049.243071
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 466.9557819167254
    baseline_value: 456.4873284223128
    deviation: 1.6923029276630943
    severity: warning
    percentage_change: 2.2932626696546206
  system_state:
    active_requests: 6
    completed_requests_1min: 766
    error_rate_1min: 0.0
    avg_response_time_1min: 466.9557819167254
  metadata: {}
  efficiency:
    requests_per_second: 12.766666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 466.96
- **Baseline Value**: 456.49
- **Deviation**: 1.69 standard deviations
- **Change**: +2.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 766
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 466.96ms

### Efficiency Metrics

- **Requests/sec**: 12.77
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 466.9557819167254,
    "baseline_value": 456.4873284223128,
    "deviation": 1.6923029276630943,
    "severity": "warning",
    "percentage_change": 2.2932626696546206
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 766,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 466.9557819167254
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.766666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
